import random
from faker import Faker
import pymysql
from datetime import datetime

# Initialize Faker and random seed
fake = Faker()
random.seed(datetime.now().timestamp())

# Database connection configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'kk123123',
    'database': 'student_db',
    'charset': 'utf8mb4'
}

# Create database connection
conn = pymysql.connect(**db_config)
cursor = conn.cursor()

# SQL statements for table creation
create_tables = [
    """CREATE TABLE IF NOT EXISTS Faculty (
        id INT AUTO_INCREMENT PRIMARY KEY,
        faculty_id VARCHAR(10) NOT NULL ,
        name VARCHAR(50) NOT NULL,
        subject VARCHAR(50) NOT NULL  -- Subject must be unique
    )""",
    
    """CREATE TABLE IF NOT EXISTS Students (
        id INT AUTO_INCREMENT PRIMARY KEY,
        student_id VARCHAR(10) NOT NULL,
        name VARCHAR(50) NOT NULL,
        age INT NOT NULL,
        faculty_id VARCHAR(10)
    )""",
    
    """CREATE TABLE IF NOT EXISTS Grade (
        id INT AUTO_INCREMENT PRIMARY KEY,
        student_id VARCHAR(10) NOT NULL,
        subject VARCHAR(50) NOT NULL,
        score INT NOT NULL
    )"""
]

# Execute table creation
for sql in create_tables:
    cursor.execute(sql)

# Generate faculty data
faculties = [
    ("CS", "Computer", ["Data Structure", "Algorithm", "Database"]),
    ("MA", "Mathematics", ["Advanced Mathematics", "Linear Algebra", "Probability Theory"]),
    ("PH", "Physics", ["Mechanics", "Electromagnetism", "Quantum Physics"]),
    ("CH", "Chemistry", ["Organic Chemistry", "Inorganic Chemistry", "Physical Chemistry"]),
    ("BI", "Biology", ["Molecular Biology", "Ecology", "Genetics"])
]

faculty_data = []
for fid, name, subjects in faculties:
    for subject in subjects:
        faculty_data.append((fid, name, subject))

# Insert faculty data
faculty_insert = "INSERT INTO Faculty (faculty_id, name, subject) VALUES (%s, %s, %s)"
cursor.executemany(faculty_insert, faculty_data)

# Generate student data (150 students)
students = []
for i in range(1, 151):
    student_id = f"S{str(i).zfill(4)}"  # S0001-S0150
    name = fake.name()
    age = random.randint(18, 25)
    faculty = random.choice(faculties)[0]  # Randomly assign faculty
    students.append((student_id, name, age, faculty))

# Insert student data
student_insert = """INSERT INTO Students (student_id, name, age, faculty_id)
                    VALUES (%s, %s, %s, %s)"""
cursor.executemany(student_insert, students)

# Generate grade data (3-5 courses per student)
grade_data = []
subjects = [subj for _, _, subs in faculties for subj in subs]  # All subjects

for student in students:
    student_id = student[0]
    num_courses = random.randint(3, 5)
    for _ in range(num_courses):
        subject = random.choice(subjects)
        score = random.randint(50, 100)  # Score between 50-100
        grade_data.append((student_id, subject, score))

# Insert grade data
grade_insert = "INSERT INTO Grade (student_id, subject, score) VALUES (%s, %s, %s)"
cursor.executemany(grade_insert, grade_data)

# Commit transaction and close connection
conn.commit()
print("Data inserted successfully! Count:")
print(f"- Faculty data: {len(faculty_data)} records")
print(f"- Student data: {len(students)} records")
print(f"- Grade data: {len(grade_data)} records")

cursor.close()
conn.close()
