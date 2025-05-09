from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import mysql.connector

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database configuration
db_config = {
    "host": "10.2.0.3",
    "user": "root",
    "password": "kk123123",
    "database": "student_db"
}

@app.post("/execute-sql")
async def execute_sql(sql: dict):
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)
        
        cursor.execute(sql["query"])
        
        if sql["query"].strip().lower().startswith("select"):
            result = cursor.fetchall()
        else:
            connection.commit()
            result = {"affected_rows": cursor.rowcount}
            
        return {"status": "success", "data": result}  # No translation needed for "success" as it's standard
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if 'connection' in locals():
            connection.close()
