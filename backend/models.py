from config import db
from bson import ObjectId
from datetime import datetime, timedelta


class User:
    def __init__(self, name, email, password, role="user"):
        self.name = name
        self.email = email
        self.password = password
        self.role = role

    def save(self):
        db.users.insert_one(self.__dict__)

    @staticmethod
    def find_by_email(email):
        return db.users.find_one({"email": email})
    
class Admin:
    def __init__(self, name, email, password, role="admin"):
        self.name = name
        self.email = email
        self.password = password
        self.role = role

    def save(self):
        db.admins.insert_one(self.__dict__)

    @staticmethod
    def find_by_email(email):
        return db.admins.find_one({"email": email})

class Student:
    def __init__(self, name, email, phone, resume, skills, certifications, preferences):
        self.name = name
        self.email = email
        self.phone = phone
        self.resume = resume
        self.skills = skills
        self.certifications = certifications
        self.preferences = preferences

    def save(self):
        db.students.insert_one(self.__dict__)

    @staticmethod
    def find_by_email(email):
        return db.students.find_one({"email": email})

    @staticmethod
    def update_student(email, update_data):
        db.students.update_one({"email": email}, {"$set": update_data})

    @staticmethod
    def delete_student(email):
        db.students.delete_one({"email": email})

class Course:
    def __init__(self, title, category, description, link):
        self.title = title
        self.category = category
        self.description = description
        self.link = link

    def save(self):
        db.courses.insert_one(self.__dict__)

    @staticmethod
    def get_all_courses():
        courses = db.courses.find({}, {"_id": 1, "title": 1, "category": 1, "description": 1, "link": 1})
        # Convert _id to string
        return [
            {**course, "_id": str(course["_id"])}  # Convert ObjectId to string
            for course in courses
        ]

    @staticmethod
    def get_courses_by_category(category):
        courses = db.courses.find({"category": category}, {"_id": 1, "title": 1, "category": 1, "description": 1, "link": 1})
        # Convert _id to string
        return [
            {**course, "_id": str(course["_id"])}  # Convert ObjectId to string
            for course in courses
        ]

    @staticmethod
    def update_course(course_id, title, category, description, link):
        db.courses.update_one(
            {"_id": ObjectId(course_id)}, 
            {"$set": {"title": title, "category": category, "description": description, "link": link}}
        )

    @staticmethod
    def delete_course(course_id):
        db.courses.delete_one({"_id": ObjectId(course_id)})


class Job:
    @staticmethod
    def search_jobs(search_term="", job_type="", filter_type="all"):
        query = {}
        
        if search_term:
            query["$or"] = [
                {"title": {"$regex": search_term, "$options": "i"}},
                {"company": {"$regex": search_term, "$options": "i"}},
                {"description": {"$regex": search_term, "$options": "i"}},
                {"requirements": {"$regex": search_term, "$options": "i"}},
                {"location": {"$regex": search_term, "$options": "i"}}
            ]
        
        if job_type:
            query["jobType"] = job_type
        
        if filter_type == "recent":
            query["postedDate"] = {"$gte": datetime.now() - timedelta(days=7)}
        elif filter_type == "high-salary":
            query["salary"] = {"$regex": "\\$\\d{5,}|\\d{5,}", "$options": "i"}
        elif filter_type == "popular":
            popular_companies = ["Google", "Microsoft", "Amazon", "Apple", "Facebook"]
            query["company"] = {"$in": popular_companies}
        
        jobs_list = list(db.jobs.find(query).sort("postedDate", -1))
        
        for job in jobs_list:
            job["_id"] = str(job["_id"])
        
        return jobs_list

    @staticmethod
    def get_job_applications(job_id):
        return list(db.applications.find({"job_id": job_id}))
    
    @staticmethod
    def create_job(data):
        return db.jobs.insert_one(data)

    @staticmethod
    def get_all_jobs():
        job_list = list(db.jobs.find({}))
        # Convert ObjectId to string
        for job in job_list:
            job["_id"] = str(job["_id"])
        return job_list

    @staticmethod
    def get_job_by_id(job_id):
        job = db.jobs.find_one({"_id": ObjectId(job_id)})
        if job:
            job["_id"] = str(job["_id"])
        return job

    @staticmethod
    def update_job(job_id, update_data):
        return db.jobs.update_one(
            {"_id": ObjectId(job_id)},
            {"$set": update_data}
        )

    @staticmethod
    def delete_job(job_id):
        return db.jobs.delete_one({"_id": ObjectId(job_id)})