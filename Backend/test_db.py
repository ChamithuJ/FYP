print("🚀 test_db.py is running")

from database import db

print("📦 database imported")

try:
    collections = db.list_collection_names()
    print("✅ Connected to MongoDB!")
    print("Collections:", collections)
except Exception as e:
    print("❌ Connection failed:", e)