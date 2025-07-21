from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from config import jobs, applications,courses
from flask import Blueprint, render_template
from flask import redirect
routes = Blueprint("routes", __name__, template_folder="templates")
from models import Student,Course,Job
from config import db
from werkzeug.utils import secure_filename
import os
from bson import ObjectId
from datetime import datetime, timedelta


# def role_required(required_role):
#     def decorator(func):
#         def wrapper(*args, **kwargs):
#             user = get_jwt_identity()
#             if user["role"] != required_role:
#                 return jsonify({"message": "Access denied"}), 403
#             return func(*args, **kwargs)
#         return jwt_required()(wrapper)
#     return decorator

from functools import wraps
# routes = Blueprint("routes", __name__)

def role_required(required_role):
    def decorator(func):
        @wraps(func)  # Preserve original function name
        def wrapper(*args, **kwargs):
            user = get_jwt_identity()
            if user["role"] != required_role:
                return jsonify({"message": "Access denied"}), 403
            return func(*args, **kwargs)
        return jwt_required()(wrapper)
    return decorator

@routes.route("/user_dashboard", endpoint="user_dashboard_view")
def user_dashboard():
    print("User Dashboard route hit!")  # Check if this prints in the terminal
    return render_template("user_dashboard.html")


student_bp = Blueprint("student", __name__)

UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

ALLOWED_EXTENSIONS = {"pdf", "doc", "docx", "jpg", "png"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# Create Student Profile
@student_bp.route("/create_student", methods=["POST"])
def create_student():
    email = request.form.get("email")
    if db.students.find_one({"email": email}):
        return jsonify({"message": "Student already exists"}), 400

    name = request.form.get("name")
    phone = request.form.get("phone")
    skills = request.form.get("skills")
    preferences = request.form.get("preferences")

    
    # Initialize empty paths for resume and certifications
    resume_path = ""
    certification_paths = []

    # Handle resume upload
    if "resume" in request.files:
        resume = request.files["resume"]
        if resume and allowed_file(resume.filename):
            filename = secure_filename(resume.filename)
            resume_save_path = os.path.join(UPLOAD_FOLDER, filename)
            resume.save(resume_save_path)
            resume_path = f"/uploads/{filename}"
    
    # Handle certifications upload
    if "certifications" in request.files:
        certifications = request.files.getlist("certifications")
        for cert in certifications:
            if cert and allowed_file(cert.filename):
                filename = secure_filename(cert.filename)
                cert_save_path = os.path.join(UPLOAD_FOLDER, filename)
                cert.save(cert_save_path)
                certification_paths.append(f"/uploads/{filename}")
    
    # Build student document
    student_data = {
        "name": name,
        "email": email,
        "phone": phone,
        "skills": skills,
        "preferences": preferences,
        "resume": resume_path,
        "certifications": certification_paths
    }
    
    db.students.insert_one(student_data)
    return jsonify({"message": "Student profile created successfully!"}), 201


# View Student Profile
@student_bp.route("/view_student/<email>", methods=["GET"])
def view_student(email):
    student = Student.find_by_email(email)
    
    if student:
        # Convert ObjectId to string if it exists, or remove the field
        if "_id" in student:
            student["_id"] = str(student["_id"])
        return jsonify(student), 200
    return jsonify({"message": "Student not found"}), 404



# Update Student Profile
@student_bp.route("/update_student", methods=["PUT"])
def update_student():
    email = request.form.get("email")
    
    if not email:
        return jsonify({"message": "Email is required"}), 400

    student = Student.find_by_email(email)
    if not student:
        return jsonify({"message": "Student not found"}), 404

    update_data = {
        # "name": request.form.get("name", student.get("name", "")),
        "phone": request.form.get("phone", student.get("phone", "")),
        "skills": request.form.get("skills", student.get("skills", "")),
        "preferences": request.form.get("preferences", student.get("preferences", ""))
    }

    # Handle Resume Upload
    if "resume" in request.files:
        resume = request.files["resume"]
        if resume and allowed_file(resume.filename):
            filename = secure_filename(resume.filename)
            resume_path = os.path.join(UPLOAD_FOLDER, filename)
            resume.save(resume_path)
            update_data["resume"] = f"/uploads/{filename}"

    # Handle Certifications Upload
    certification_paths = []
    if "certifications" in request.files:
        certifications = request.files.getlist("certifications")
        for cert in certifications:
            if cert and allowed_file(cert.filename):
                filename = secure_filename(cert.filename)
                cert_path = os.path.join(UPLOAD_FOLDER, filename)
                cert.save(cert_path)
                certification_paths.append(f"/uploads/{filename}")

    if certification_paths:
        update_data["certifications"] = certification_paths

    Student.update_student(email, update_data)
    return jsonify({"message": "Profile updated successfully!"}), 200


# Delete Student Profile
@student_bp.route("/delete_student/<email>", methods=["DELETE"])
def delete_student(email):
    student = Student.find_by_email(email)
    
    if not student:
        return jsonify({"message": "Student not found"}), 404

    if "resume" in student:
        resume_path = student["resume"].replace("/uploads/", "uploads/")
        if os.path.exists(resume_path):
            os.remove(resume_path)

    if "certifications" in student:
        for cert_path in student["certifications"]:
            cert_file_path = cert_path.replace("/uploads/", "uploads/")
            if os.path.exists(cert_file_path):
                os.remove(cert_file_path)

    Student.delete_student(email)
    return jsonify({"message": "Student profile deleted successfully!"}), 200


@routes.route("/admin_dashboard")
# @jwt_required()
def admin_dashboard():
    return render_template("admin_dashboard.html")

@routes.route("/jobs", methods=["GET"])
def get_jobs():
    try:
        search_term = request.args.get("search", "").strip()
        job_type = request.args.get("type", "").strip()
        filter_type = request.args.get("filter", "all").strip()
        
        query = {}
        
        if search_term:
            query["$or"] = [
                {"title": {"$regex": search_term, "$options": "i"}},
                {"company": {"$regex": search_term, "$options": "i"}},
                {"description": {"$regex": search_term, "$options": "i"}}
            ]
        
        if job_type:
            query["jobType"] = job_type
        
        # Apply additional filters
        if filter_type == "recent":
            query["postedDate"] = {"$gte": datetime.now() - timedelta(days=7)}
        elif filter_type == "high-salary":
            query["$or"] = [
                {"salary": {"$regex": "\\$\\d{5,}", "$options": "i"}},
                {"salary": {"$regex": "\\d{5,}", "$options": "i"}}
            ]
        elif filter_type == "popular":
            query["company"] = {
                "$in": ["Google", "Microsoft", "Amazon", "Apple", "Facebook"]
            }
        
        jobs_list = list(jobs.find(query).sort("postedDate", -1))
        
        # Convert ObjectId to string
        for job in jobs_list:
            job["_id"] = str(job["_id"])
        
        return jsonify(jobs_list), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    


@routes.route("/apply", methods=["POST"])
@jwt_required()
def apply_job():
    # Debug: Print headers and raw data first
    print("Request headers:", request.headers)
    print("Raw request data:", request.data)
    
    try:
        # Check content type
        if request.content_type != 'application/json':
            return jsonify({"error": "Content-Type must be application/json"}), 415
        
        # Parse JSON data
        try:
            data = request.get_json()
            print("Parsed JSON data:", data)
        except Exception as e:
            print("JSON parse error:", str(e))
            return jsonify({"error": "Invalid JSON format"}), 400
        
        # Validate required fields
        if not data or "job_id" not in data:
            print("Missing job_id in data")
            return jsonify({"error": "job_id is required in request body"}), 422
        
        job_id = data["job_id"]
        print("Received job_id:", job_id)
        
        # Validate job_id format
        if not job_id or not isinstance(job_id, str) or not ObjectId.is_valid(job_id):
            print("Invalid job_id format:", job_id)
            return jsonify({"error": "Invalid job_id format - must be a valid MongoDB ObjectId"}), 422
        
        user = get_jwt_identity()
        print("User identity:", user)
        
        
        # Check if job exists
        job = jobs.find_one({"_id": ObjectId(job_id)})
        if not job:
            print("Job not found for id:", job_id)
            return jsonify({"error": "Job not found"}), 404
        
        # Check for existing application
        existing = applications.find_one({
            "user_email": user["email"],
            "job_id": job_id
        })
        if existing:
            print("Duplicate application found")
            return jsonify({"error": "You have already applied for this job"}), 400
        
        # Create application
        application_data = {
            "user_email": user["email"],
            "job_id": job_id,
            "status": "Applied",
            "applied_date": datetime.now(),
            "job_title": job["title"],
            "company": job["company"],
            "user_id": str(user["_id"])  # Store user ID from JWT
        }

        
        # Insert and return response
        result = applications.insert_one(application_data)
        application_data["_id"] = str(result.inserted_id)
        
        print("Application successful:", application_data)
        return jsonify({
            "message": "Application submitted successfully!",
            "application": application_data
        }), 201
        
    except Exception as e:
        print("Unexpected error:", str(e))
        return jsonify({"error": "Internal server error"}), 500


@routes.route("/admin/applications", methods=["GET"])
@role_required("admin")
def get_all_applications():
    try:
        apps = list(applications.aggregate([
            {
                "$lookup": {
                    "from": "jobs",
                    "localField": "job_id",
                    "foreignField": "_id",
                    "as": "job"
                }
            },
            {
                "$unwind": "$job"
            },
            {
                "$project": {
                    "_id": {"$toString": "$_id"},
                    "job_title": "$job.title",
                    "job_id": {"$toString": "$job._id"},
                    "student_name": 1,
                    "student_email": 1,
                    "status": 1,
                    "applied_date": 1,
                    "resume": 1,
                    "skills": 1
                }
            },
            {
                "$sort": {"applied_date": -1}
            }
        ]))
        
        return jsonify(apps), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@routes.route("/admin/applications/<app_id>", methods=["GET"])
@role_required("admin")
def get_application(app_id):
    try:
        app = applications.find_one({"_id": ObjectId(app_id)})
        if not app:
            return jsonify({"error": "Application not found"}), 404
        
        job = jobs.find_one({"_id": ObjectId(app["job_id"])})
        
        response = {
            "_id": str(app["_id"]),
            "job_title": job["title"] if job else "Job not found",
            "student_name": app.get("student_name", ""),
            "student_email": app.get("student_email", ""),
            "status": app.get("status", "Applied"),
            "applied_date": app.get("applied_date", ""),
            "resume": app.get("resume", ""),
            "skills": app.get("skills", "")
        }
        
        return jsonify(response), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@routes.route("/admin/applications/<app_id>", methods=["PUT"])
@role_required("admin")
def update_application(app_id):
    try:
        data = request.json
        status = data.get("status")
        
        if not status:
            return jsonify({"error": "Status is required"}), 400
        
        result = applications.update_one(
            {"_id": ObjectId(app_id)},
            {"$set": {"status": status}}
        )
        
        if result.modified_count == 0:
            return jsonify({"error": "Application not found or no changes made"}), 404
        
        return jsonify({"message": "Application status updated"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500