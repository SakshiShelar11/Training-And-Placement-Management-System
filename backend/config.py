from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/TNPdatabase")
db = client["placement_db"]
users = db["users"]
admins=db["admins"]
jobs = db["jobs"]
students=db["students"]
courses = db["courses"]
applications = db["applications"]
