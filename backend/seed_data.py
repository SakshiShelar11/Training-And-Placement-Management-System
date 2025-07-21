from config import db,users, jobs,admins,courses
import bcrypt
from datetime import datetime, timedelta

email = "admin@example.com"
password = "admin123"
hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

admins.insert_one({
    "name": "Admin User",
    "email": email,
    "password": hashed_pw,
    "role": "admin"
})
print("Admin user created!")


email = "test@example.com"
password = "password123"
hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

users.insert_one({
    "name": "Test User",
    "email": email,
    "password": hashed_pw,
    "role": "user"
})
print("Test user created!")

# Get jobs collection
jobs = db["jobs"]

# Delete existing jobs to prevent duplicates
jobs.delete_many({})  # Clears the jobs collection

# Insert fresh data
jobs.insert_many([
    {"_id": "1", "title": "Software Engineer", "company": "Google"},
    {"_id": "2", "title": "Data Analyst", "company": "Amazon"},
    {"_id": "3", "title": "Backend Developer", "company": "Microsoft"}
])

print("Test job data inserted successfully!")

jobs.delete_many({})

# Insert sample jobs
sample_jobs = [
    {
        "title": "Software Engineer",
        "company": "Google",
        "location": "Mountain View, CA",
        "salary": "120,000 - 150,000",
        "description": "Develop and maintain software applications for Google's core products.",
        "requirements": "Bachelor's degree in CS or related field\n3+ years of experience\nStrong problem-solving skills",
        "jobType": "Full-time",
        "postedDate": datetime.now() - timedelta(days=2)
    },
    {
        "title": "Data Scientist",
        "company": "Amazon",
        "location": "Seattle, WA (Remote)",
        "salary": "110,000 - 140,000",
        "description": "Analyze large datasets to derive business insights and build predictive models.",
        "requirements": "Master's degree in Data Science\nPython and SQL proficiency\nExperience with ML algorithms",
        "jobType": "Remote",
        "postedDate": datetime.now() - timedelta(days=5)
    },
    {
        "title": "Frontend Developer",
        "company": "Microsoft",
        "location": "Redmond, WA",
        "salary": "105,000 - 135,000",
        "description": "Build responsive and accessible user interfaces for Microsoft products.",
        "requirements": "2+ years of React experience\nStrong CSS skills\nUnderstanding of web accessibility",
        "jobType": "Full-time",
        "postedDate": datetime.now() - timedelta(days=1)
    },
    {
        "title": "DevOps Engineer",
        "company": "Netflix",
        "location": "Los Gatos, CA",
        "salary": "130,000 - 160,000",
        "description": "Design and maintain cloud infrastructure for high-availability streaming services.",
        "requirements": "AWS/GCP experience\nCI/CD pipeline expertise\nContainerization knowledge",
        "jobType": "Full-time",
        "postedDate": datetime.now() - timedelta(days=3)
    },
    {
        "title": "UX Designer",
        "company": "Apple",
        "location": "Cupertino, CA",
        "salary": "115,000 - 145,000",
        "description": "Create intuitive user experiences for Apple's ecosystem of products.",
        "requirements": "Portfolio required\n5+ years of UX design\nFamiliarity with Apple HIG",
        "jobType": "Full-time",
        "postedDate": datetime.now() - timedelta(days=7)
    }
]

jobs.insert_many(sample_jobs)
print("Sample jobs with complete details added!")

# Add to your initialization code
db.jobs.create_index([("title", "text"), ("company", "text"), ("description", "text")])
db.jobs.create_index("postedDate")
db.applications.create_index("job_id")
db.applications.create_index("student_email")
# Add to your initialization code
db.applications.create_index([("user_email", 1), ("job_id", 1)], unique=True)

initial_courses = [
    {
        "title": "Mastering Data Structures and Algorithms",
        "category": "DSA",
        "description": "Comprehensive guide on DSA with coding exercises.",
        "link": "https://www.youtube.com/watch?v=RBSGKlAvoiM"
    },
    {
        "title": "Aptitude and Logical Reasoning",
        "category": "Aptitude",
        "description": "Sharpen your aptitude skills for placement exams.",
        "link": "https://www.youtube.com/watch?v=3wMxTUU9lMk"
    },
    {
        "title": "System Design Crash Course",
        "category": "System Design",
        "description": "Learn system design fundamentals for interviews.",
        "link": "https://www.youtube.com/watch?v=7WtmxNzPlPs"
    },
]

courses.insert_many(initial_courses)
print("Sample placement courses added!")