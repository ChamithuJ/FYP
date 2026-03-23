from pymongo import MongoClient
from dotenv import load_dotenv
import os
import certifi

# Load environment variables
load_dotenv()

MongoDB_URI = os.getenv("MongoDB_URI")

# Connect to MongoDB Atlas with SSL fix
client = MongoClient(
    MongoDB_URI,
    tls=True,
    tlsCAFile=certifi.where()
)

# Create database
db = client["fitness_app"]

# Collections
users_collection = db["users"]
calibration_collection = db["calibration"]

print("MongoDB connected successfully!")