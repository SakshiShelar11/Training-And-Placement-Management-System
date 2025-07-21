from flask import Blueprint, request, jsonify
from config import users,admins
import bcrypt
from flask_jwt_extended import create_access_token

auth = Blueprint("auth", __name__)

@auth.route("/register", methods=["POST"])
def register():
    data = request.json
    if users.find_one({"email": data["email"]}):
        return jsonify({"message": "User already exists"}), 400
    hashed_pw = bcrypt.hashpw(data["password"].encode("utf-8"), bcrypt.gensalt())
    role = data.get("role", "user")
    users.insert_one({"name": data["name"], "email": data["email"], "password": hashed_pw, "role": role})
    return jsonify({"message": "User registered"}), 201

# @auth.route("/login", methods=["POST"])
# def login():
#     data = request.json
#     print("Login Request Data:", data)  # Debugging
    
#     user = users.find_one({"email": data["email"]})
#     print("User Found in DB:", user)  # Debugging

#     if user and bcrypt.checkpw(data["password"].encode("utf-8"), user["password"]):
#         token = create_access_token(identity={"email": data["email"], "role": user["role"]})
#         print("Login Successful!")  # Debugging
#         return jsonify({"token": token, "role": user["role"]}), 200

#     print("Invalid Credentials")  # Debugging
#     return jsonify({"message": "Invalid credentials"}), 401


@auth.route("/login", methods=["POST"])
def login():
    data = request.json
    print("Login Request Data:", data)  # Debugging
    
    # Check if the user exists in the admins collection first
    admin = admins.find_one({"email": data["email"]})
    print("Admin found in DB:", admin)  # Debugging

    if admin:
        # If admin, verify the password
        if bcrypt.checkpw(data["password"].encode("utf-8"), admin["password"]):
            # Create JWT token for admin
            token = create_access_token(identity={"email": data["email"], "role": "admin"})
            print("Admin Login Successful!")  # Debugging
            return jsonify({"token": token, "role": "admin"}), 200
        else:
            print("Invalid Admin Credentials")  # Debugging
            return jsonify({"message": "Invalid credentials"}), 401
    
    # If not an admin, check the users collection
    user = users.find_one({"email": data["email"]})
    print("User found in DB:", user)  # Debugging

    if user:
        # If user, verify the password
        if bcrypt.checkpw(data["password"].encode("utf-8"), user["password"]):
            # Create JWT token for regular user
            token = create_access_token(identity={"email": data["email"], "role": "user"})
            print("User Login Successful!")  # Debugging
            return jsonify({"token": token, "role": "user"}), 200
        else:
            print("Invalid User Credentials")  # Debugging
            return jsonify({"message": "Invalid credentials"}), 401
    
    # If no user is found in either collection
    print("User not found")  # Debugging
    return jsonify({"message": "Invalid credentials"}), 401

