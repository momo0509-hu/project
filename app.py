from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
import pymongo
import mysql.connector
import requests
import re

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database configuration
DATABASE_CONFIG = {
    "mysql": {
        "host": "127.0.0.1",
        "user": "root",
        "password": "kk123123",
        "database": "student_db"
    },
    "mongo": {
        "host": "mongodb://admin:kk123123@localhost:27017/school_social_db?authSource=admin",
        "database": "school_social_db"
    }
}

# LLM API configuration
LLM_API_URL = "https://api.siliconflow.cn/v1/chat/completions"
LLM_HEADERS = {
    "Authorization": "Bearer sk-uehxupddirrjvogjpjzdqxgpzjlhfrbxcqdqvikzimwtyjrb",
    "Content-Type": "application/json"
}

@app.post("/nl2sql")
async def natural_to_sql(query: dict):
    """Natural language to SQL interface"""
    system_prompt = f"""You are an SQL generator, Never output any content unrelated to SQL statements, do not explain the output.
    please generate accurate SQL statements based on the following database structure:

    MySQL database:
    - Database name: student_db
    - Available tables: 
      * Faculty(fields: id, faculty_id, name, subject)
      * Grade(fields: id, student_id, subject, score)
      * Students(fields: id, student_id, name, age, faculty_id)

    Generation rules:
    1. Use standard SQL syntax
    2. Only output SQL statements without any unrelated content
    3. Output in plain text format only, no markdown or other formatting
    4. Always include USE student_db; at the beginning of the query
    5. Ensure SQL statements are safe and follow best practices
    """
    
    payload = {
        "model": "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query.get("query", "")}
        ],
        "temperature": 0.3,
        "max_tokens": 512,
        "response_format": {
            "type": "text"
        }
    }
    
    try:
        response = requests.post(LLM_API_URL, json=payload, headers=LLM_HEADERS, timeout=15)
        response.raise_for_status()
        result = response.json()
        generated_sql = result['choices'][0]['message']['content'].strip()
        generated_sql = generated_sql.replace('```sql', '').replace('```', '').strip()
        return {"sql": generated_sql}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM API error: {str(e)}")

@app.post("/nl2mongo")
async def natural_to_mongo(query: dict):
    """Natural language to MongoDB operations interface"""
    system_prompt = """You are a MongoDB operations generator, Never output any content unrelated to MongoDB operations, do not explain the output.
    please generate accurate MongoDB operations based on the following database structure:
    Your operations must start with db., i.e.: db.student_social.<operation>, and must end with a semicolon.
    Example: db.student_social.find({});
    To query all information use db.student_social.find({});
    If unsure which operation to use, return db.student_social.find({});
    Don't guess blindly, if unclear try to return db.student_social.find({}); You can use db.student_social.find({}).limit(10); to limit the returned results.
 
    MongoDB database:
    - Database name: school_social_db
    - Available collections: 
     student_social(fields: social_id, platforms, friends_count, daily_online_hours, recent_posts),
     hobbies(fields: clubs, preferred_events), 
     device_usage(fields: primary_device, app_usage(fields: social_media, games, video))

    Generation rules:
    1. Use standard MongoDB operations (find, insertOne, updateOne, deleteOne, etc.)
    2. Only output MongoDB operations without any unrelated content
    3. Output in plain text format only, no markdown or other formatting
    4. Always specify the collection name
    5. Use proper MongoDB query syntax and operators
    6. For complex queries, use proper MongoDB aggregation pipeline syntax
    7. Ensure operations are safe and follow best practices
    """
    
    payload = {
        "model": "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query.get("query", "")}
        ],
        "temperature": 0.1,
        "max_tokens": 512,
        "response_format": {
            "type": "text"
        }
    }
    
    try:
        response = requests.post(LLM_API_URL, json=payload, headers=LLM_HEADERS, timeout=15)
        response.raise_for_status()
        result = response.json()
        generated_mongo = result['choices'][0]['message']['content'].strip()
        generated_mongo = generated_mongo.replace('```javascript', '').replace('```', '').strip()
        return {"mongo": generated_mongo}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM API error: {str(e)}")

@app.post("/execute-sql")
async def execute_sql(sql: dict):
    """SQL execution endpoint"""
    query = sql.get("query", "").strip()
    if not query:
        raise HTTPException(status_code=400, detail="Empty query")
    
    try:
        # Remove USE statement if present
        clean_query = re.sub(r'USE\s+[a-zA-Z_]+\s*;', '', query, flags=re.IGNORECASE).strip()
        return await execute_mysql(clean_query)
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Execution error: {str(e)}")

@app.post("/execute-mongodb")
async def execute_mongodb(mongo: dict):
    """MongoDB operations execution endpoint"""
    print(mongo)
    operation = mongo.get("query", "").strip()
    if not operation:
        raise HTTPException(status_code=400, detail="Empty operation")
    
    try:
        return await execute_mongo(operation)
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Execution error: {str(e)}")

async def execute_mysql(query: str):
    """Execute MySQL query"""
    try:
        conn = mysql.connector.connect(**DATABASE_CONFIG["mysql"])
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute(query)
        
        if query.strip().lower().startswith("select"):
            result = cursor.fetchall()
        else:
            conn.commit()
            result = {"affected_rows": cursor.rowcount}
            
        return {"status": "success", "data": result}
        
    except mysql.connector.Error as e:
        raise HTTPException(status_code=400, detail=f"MySQL error: {str(e)}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

async def execute_mongo(operation: str):
    """Execute MongoDB operation"""
    try:
        client = MongoClient(DATABASE_CONFIG["mongo"]["host"])
        db = client[DATABASE_CONFIG["mongo"]["database"]]
        
        # Parse and execute MongoDB operation
        if operation.startswith("db."):
            # Remove "db." prefix and trailing semicolon
            operation = operation.replace("db.", "").rstrip(";")
            
            # Add 'student_social' collection to the execution context
            context = {"db": db}
            # add the collection to the context
            context["student_social"] = db["student_social"]
            
            # Execute the operation directly using exec
            exec(f"result = {operation}", context)
            # Get the result from the context
            result = context.get("result", None)
            
            # Handle different types of results
            if isinstance(result, pymongo.cursor.Cursor):
                # For find operations, limit results and exclude _id field
                result = list(result.limit(100))
                for doc in result:
                    doc.pop("_id", None)
                return_result = {"data": result}
            elif isinstance(result, pymongo.results.InsertOneResult):
                # For insert operations
                return_result = {"inserted_id": str(result.inserted_id)}
            elif isinstance(result, pymongo.results.UpdateResult):
                # For update operations
                return_result = {
                    "matched_count": result.matched_count,
                    "modified_count": result.modified_count
                }
            elif isinstance(result, pymongo.results.DeleteResult):
                # For delete operations
                return_result = {"deleted_count": result.deleted_count}
            else:
                # For other operations or when no result is returned
                return_result = {"message": "Operation executed successfully"}
            
            return {"status": "success", "data": return_result}
        else:
            raise ValueError("Operation must start with 'db.'")
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"MongoDB error: {str(e)}")
    finally:
        if 'client' in locals():
            client.close()
