from flask import Flask, request, jsonify,Blueprint
import logging
from flask_cors import CORS
from execute import execute_code

compiler_bp = Blueprint('compiler', __name__)  # Define Blueprint
CORS(compiler_bp) 

# @app.route('/')
# def home():
#     return "Flask server is running! Use /run to execute code."

# @app.route('/run', methods=['POST']) 
@compiler_bp.route('/run', methods=['POST']) 
def run_code():
    logging.basicConfig(level=logging.DEBUG)  # Set up logging
    logging.debug("Received request: %s", request.json)

    data = request.json
    code = data.get("code", "")
    language = data.get("language", "")

    if not code or not language:
        return jsonify({"error": "Missing code or language."}), 400

    output, error = execute_code(code, language) 
    logging.debug("Execution output: %s", output)
    logging.debug("Execution error: %s", error)

    if error:
        return jsonify({"error": error}), 500
    
    return jsonify({"output": output})

# if __name__ == '__main__':
#     app.run(debug=True)
