import pymongo
from pymongo import MongoClient
from faker import Faker
import random
from datetime import datetime, timedelta

# Initialize Faker and MongoDB connection
# Replace your_username and your_password with actual credentials
client = MongoClient("mongodb://admin:kk123123@localhost:27017/?authSource=admin")
db = client['school_social_db']
collection = db['student_social']

# Data generation configuration
PLATFORMS = ["WeChat", "Weibo", "QQ", "TikTok", "Bilibili"]
CLUBS = ["Photography Association", "Anime Club", "Esports Club", "Street Dance Club", "Literature Club"]
EVENTS = ["Esports Competition", "Music Festival", "Comic Exhibition", "Sports Event", "Academic Lecture"]
DEVICES = ["iPhone 15", "Huawei Mate60", "Xiaomi 14", "OPPO Find X7", "vivo X100"]

def generate_social_data(num_records):
    data = []
    for _ in range(num_records):
        # Generate dynamic data
        posts = [{
            "content": f"{fake.sentence()}",
            "likes": random.randint(10, 200),
            "shares": random.randint(0, 50),
            "post_time": fake.date_time_between(start_date="-30d", end_date="now")
        } for _ in range(random.randint(1, 5))]

        # Build complete document
        doc = {
            "student_social": {
                "social_id": f"SNS_{fake.unique.random_number(digits=4)}",
                "platforms": random.sample(PLATFORMS, k=random.randint(1,3)),
                "friends_count": random.randint(50, 500),
                "daily_online_hours": round(random.uniform(1.0, 6.0), 1),
                "recent_posts": posts
            },
            "hobbies": {
                "clubs": random.sample(CLUBS, k=random.randint(0,3)),
                "preferred_events": random.sample(EVENTS, k=random.randint(1,3))
            },
            "device_usage": {
                "primary_device": random.choice(DEVICES),
                "app_usage": {
                    "social_media": random.randint(30, 180),
                    "games": random.randint(0, 120),
                    "video": random.randint(30, 150)
                }
            }
        }
        data.append(doc)
    return data

fake = Faker()
# Insert 100 test records
test_data = generate_social_data(100)
collection.insert_many(test_data)

print(f"Successfully inserted {len(test_data)} social behavior records!")
