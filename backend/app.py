from flask import Flask , render_template,session,redirect,url_for,jsonify,request
import google.generativeai as genai
# import openai
# from openai import OpenAI
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from auth import auth
from routes import routes
from flask import Flask, send_from_directory
from config import db
from models import User
from routes import student_bp
from routes import *
import requests
# from google.auth import exceptions
# from google.oauth2.credentials import Credentials
import json
# from google_auth_oauthlib.flow import Flow
# from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
# from pymongo import MongoClient
from bson import ObjectId
from compiler import run_code
from bson.errors import InvalidId

# app = Flask(__name__, static_folder='backend/static')

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'your-unique-secret-key' 
app.config["JWT_SECRET_KEY"] = "your_secret_key"
jwt = JWTManager(app)

GEMINI_API_KEY = "AIzaSyCVp40VbNxEyiQ2Nk0xioMH8LCty1eoYSU"  # Replace with your Gemini API Key

genai.configure(api_key=GEMINI_API_KEY)
models = genai.list_models()
for model in models:
    print(model.name)

def get_gemini_answer(question):
    try:
        # model = genai.GenerativeModel("gemini-1.5-pro-latest")  # ✅ Use the correct model
        model = genai.GenerativeModel("gemini-2.0-flash")
        response = model.generate_content(question)

        if response and hasattr(response, 'text'):
            return response.text.replace("**", "").replace("\n", "<br>")  # ✅ Fix formatting
        return "No response from Gemini AI."
    except Exception as e:
        return f"Gemini API Error: {str(e)}"

@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    question = data.get("question", "").strip()
    category = data.get("category", "others").strip()

    if not question:
        return jsonify({"error": "Please provide a valid question."})

    # Modify the question to include category context
    category_context = {
        "dsa": "This question is related to Data Structures and Algorithms.",
        "java": "This question is related to Java programming.",
        "python": "This question is related to Python programming.",
        "AI": "This question is related to Artificial Intelligence.",
        "ds": "This question is related to Data Science.",
        "others": "This is a general question."
    }

    full_question = f"{category_context.get(category, 'General Question')}\n{question}"

    # Get AI response
    gemini_answer = get_gemini_answer(full_question)

    return jsonify({"gemini_answer": gemini_answer})

@app.route("/interview_question", methods=["POST"])
def interview_question():
    data = request.json
    category = data.get("category", "general").strip()

    category_context = {
        "dsa": "Give me only an interview question related to Data Structures and Algorithms. Do not provide an answer, explanation, or hints.",
        "java": "Give me only an interview question related to Java programming. Do not provide an answer, explanation, or hints.",
        "python": "Give me only an interview question related to Python programming. Do not provide an answer, explanation, or hints.",
        "AI": "Give me only an interview question related to Artificial Intelligence. Do not provide an answer, explanation, or hints.",
        "ds": "Give me only an interview question related to Data Science. Do not provide an answer, explanation, or hints.",
        "hr": "Give me only an interview question related to HR. Do not provide an answer, explanation, or hints.",
        "Programming": "Give me only an interview question related to various Programming Languages. Do not provide an answer, explanation, or hints.",
        "others": "Give me only a general interview question. Do not provide an answer, explanation, or hints."
    }

    prompt = f"{category_context.get(category, 'General Question')}"
    question = get_gemini_answer(prompt)  # AI generates question
    
    return jsonify({"question": question})

@app.route("/evaluate_answer", methods=["POST"])
def evaluate_answer():
    data = request.json
    question = data.get("question", "").strip()
    user_answer = data.get("answer", "").strip()

    if not user_answer:
        return jsonify({"error": "Please provide an answer."})

    prompt = f"Evaluate this answer:\nQuestion: {question}\nUser Answer: {user_answer}\nProvide feedback and correct answer."
    evaluation = get_gemini_answer(prompt)

    return jsonify({"feedback": evaluation})

app.register_blueprint(routes)  # Remove url_prefix="/api"
app.register_blueprint(student_bp)
app.register_blueprint(auth, url_prefix="/auth")
# app.register_blueprint(routes, url_prefix="/api")

@app.route("/")  # Add this route to serve the login page
def home():
    return render_template("index.html")

@app.route('/login')
def login():
    return render_template("login.html")

#user Logout route
@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))

#admin Logout route
@app.route('/logout', methods=['POST'])
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('home'))

@app.route("/student_profile")
def student_profile():
    return render_template("student_profile.html")

@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory("uploads", filename)

@app.route("/ask_me")
def ask_me():
    return render_template("ask_me.html")

@app.route("/interview")
def interview_practice():
    return render_template("interview.html")

@app.route("/get_ready")
def get_ready_for_placement():
    return render_template("get_ready.html")

@app.route("/code_editor")
def code_editor():
    return render_template("code_editor.html")

@app.route('/run', methods=['POST']) 
def run_code_api():
    return run_code()  # Calls the function from compiler.py

# Get all courses (For User Dashboard)
@app.route("/courses", methods=["GET"])
def get_all_courses():
    try:
        courses = Course.get_all_courses()
        return jsonify(courses), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Get courses by category (For User Dashboard)
@app.route("/courses/<category>", methods=["GET"])
def get_courses_by_category(category):
    courses = Course.get_courses_by_category(category)
    return jsonify(courses)

# Admin Add Course
@app.route("/admin/add_course", methods=["POST"])
def add_course():
    data = request.get_json()
    title = data.get("title")
    category = data.get("category")
    description = data.get("description")
    link = data.get("link")
    
    if not all([title, category, description, link]):
        return jsonify({"message": "All fields are required"}), 400

    new_course = Course(title, category, description, link)
    new_course.save()
    return jsonify({"message": "Course added successfully"}), 201

# Admin Update Course
@app.route("/admin/update_course/<course_id>", methods=["PUT"])
def update_course(course_id):
    data = request.get_json()
    title = data.get("title")
    category = data.get("category")
    description = data.get("description")
    link = data.get("link")
    
    if not all([title, category, description, link]):
        return jsonify({"message": "All fields are required"}), 400

    Course.update_course(course_id, title, category, description, link)
    return jsonify({"message": "Course updated successfully"}), 200

# Admin Delete Course
@app.route("/admin/delete_course/<course_id>", methods=["DELETE"])
def delete_course(course_id):
    Course.delete_course(course_id)
    return jsonify({"message": "Course deleted successfully"}), 200

@app.route("/admin_course")
def admin_course():
    return render_template("admin_course.html")

@app.route("/view_jobs")
def view_jobs():
    return render_template("view_jobs.html")

@app.route("/manage_jobs")
def manage_jobs():
    return render_template("manage_jobs.html")

#Aptitude Practice
@app.route("/aptitude_question", methods=["POST"])
def aptitude_question():
    data = request.json
    category = data.get("category", "general").strip()

    prompt_map = {
        "logical": "Give me one logical aptitude multiple-choice question with 4 options. Clearly label the options A, B, C, and D. Do not provide answer and its explanation.",
        "reasoning": "Give me one reasoning aptitude multiple-choice question with 4 options. Clearly label the options A, B, C, and D.Do not include questions that require visual elements, images, diagrams, or figures. Do not provide answer and its explanation.",
        "quantitative": "Give me one quantitative aptitude multiple-choice question with 4 options.Clearly label the options A, B, C, and D.Do not provide answer and its explanation.",
    }

    prompt = prompt_map.get(category, prompt_map["logical"])
    question = get_gemini_answer(prompt)

    return jsonify({"question": question})

@app.route("/aptitude_evaluate", methods=["POST"])
def aptitude_evaluate():
    data = request.json
    question = data.get("question", "").strip()
    user_answer = data.get("answer", "").strip()

    prompt = f"""Evaluate the following aptitude question and the user's answer:
Question:
{question}

User's Answer: {user_answer}

Tell if it is correct or wrong. If wrong, give the correct answer and a short explanation.
"""

    evaluation = get_gemini_answer(prompt)
    return jsonify({"feedback": evaluation})

@app.route("/apti_practice")
def apti_practice():
    return render_template("apti_practice.html")

# Job Management Routes (Admin Only)
@app.route("/admin/jobs", methods=["POST"])
# @jwt_required()
def add_job():
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ["title", "company", "location", "salary", "description", "jobType"]
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

        # Add additional fields with defaults if not provided
        job_data = {
            "title": data["title"],
            "company": data["company"],
            "location": data["location"],
            "salary": data["salary"],
            "description": data["description"],
            "jobType": data["jobType"],
            "requirements": data.get("requirements", ""),
            "postedDate": datetime.now()
        }

        # Insert into database
        result = jobs.insert_one(job_data)
        
        # Return success response with created job data
        job_data["_id"] = str(result.inserted_id)
        return jsonify({
            "message": "Job added successfully",
            "job": job_data
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/admin/jobs/<job_id>", methods=["PUT"])
# @jwt_required()
def update_job(job_id):
    try:
        data = request.get_json()
        
        # Validate ObjectId
        try:
            job_obj_id = ObjectId(job_id)
        except InvalidId:
            return jsonify({"error": "Invalid job ID"}), 400
        
        # Validate required fields
        required_fields = ["title", "company", "location", "salary", "description", "jobType"]
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({"error": f"Missing required fields: {', '.join(missing_fields)}"}), 400

        # Prepare update data (exclude immutable fields)
        update_data = {
            "title": data["title"],
            "company": data["company"],
            "location": data["location"],
            "salary": data["salary"],
            "description": data["description"],
            "jobType": data["jobType"],
            "requirements": data.get("requirements", "")
        }

        # Update job in database
        result = jobs.update_one(
            {"_id": ObjectId(job_id)},
            {"$set": update_data}
        )

        if result.matched_count == 0:
            return jsonify({"error": "Job not found"}), 404

        # Return updated job data
        updated_job = jobs.find_one({"_id": ObjectId(job_id)})
        updated_job["_id"] = str(updated_job["_id"])
        return jsonify({
            "message": "Job updated successfully",
            "job": updated_job
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/admin/jobs/<job_id>", methods=["DELETE"])
# @jwt_required()
def delete_job(job_id):
    try:
        # First check if job exists
        job = jobs.find_one({"_id": ObjectId(job_id)})
        if not job:
            return jsonify({"error": "Job not found"}), 404

        # Delete the job
        result = jobs.delete_one({"_id": ObjectId(job_id)})
        
        # Also delete related applications
        applications.delete_many({"job_id": job_id})

        # Return success response with deleted job data
        job["_id"] = str(job["_id"])
        return jsonify({
            "message": "Job deleted successfully",
            "deleted_job": job
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Get all jobs (for admin and users)
@app.route("/jobs", methods=["GET"])
def get_all_jobs():
    try:
        jobs_list = list(jobs.find({}))
        # Convert ObjectId to string for JSON serialization
        for job in jobs_list:
            job["_id"] = str(job["_id"])
        return jsonify(jobs_list), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Get single job details
@app.route("/jobs/<job_id>", methods=["GET"])
def get_job_details(job_id):
    try:
        job = jobs.find_one({"_id": ObjectId(job_id)})
        if not job:
            return jsonify({"error": "Job not found"}), 404
            
        job["_id"] = str(job["_id"])
        return jsonify(job), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    


if __name__ == "__main__":
    app.run(debug=True)