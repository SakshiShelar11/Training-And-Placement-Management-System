import subprocess
import tempfile
import os
import logging
import re

GPP_PATH = r"C:\MinGW\bin\g++.exe"

def check_interpreter(language):
    """Check if the required interpreter/compiler is available."""
    interpreters = {
        "python": "python",
        "javascript": "node",
        "c": "gcc",
        "cpp": "g++",
        "java": "javac",
        "php": "php"
    }
    return interpreters.get(language, None)

def is_interpreter_available(interpreter):
    """Check if the interpreter/compiler is available in PATH."""
    try:
        result = subprocess.run(["where", interpreter], capture_output=True, text=True)
        return result.returncode == 0
    except Exception:
        return False

def execute_code(code, language, timeout=5):
    """Execute the given code in the specified language."""
    interpreter = check_interpreter(language)
    if interpreter is None:
        return "Unsupported language", "Error: Language not supported."

    # Ensure interpreter is available
    if not is_interpreter_available(interpreter):
        return "Interpreter not found", f"Error: {interpreter} not found in PATH."

    try:
        file_extension = get_file_extension(language)
        if not file_extension:
            return "Unsupported language", "Error: Invalid file extension."

        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            temp_file.write(code.encode())
            temp_file_path = temp_file.name

        # Execution logic
        if language == "python":
            cmd = ["python", temp_file_path]

        elif language == "javascript":
            cmd = ["node", temp_file_path]

        elif language == "c":
            exe_file = temp_file_path.replace(".c", ".exe")
            compile_result = subprocess.run(["gcc", temp_file_path, "-o", exe_file], capture_output=True, text=True)
            if compile_result.returncode != 0:
                return "", f"Compilation Error:\n{compile_result.stderr}"
            cmd = [exe_file]

        elif language == "cpp":
            exe_file = temp_file_path.replace(".cpp", ".exe")
            compile_result = subprocess.run([GPP_PATH, temp_file_path, "-o", exe_file], capture_output=True, text=True)
            if compile_result.returncode != 0:
                return "", f"Compilation Error:\n{compile_result.stderr}"
            cmd = [exe_file]

        elif language == "java":
            class_name = extract_java_class_name(code)
            if not class_name:
                return "", "Error: No valid Java class found!"

            java_file_path = os.path.join(os.path.dirname(temp_file_path), f"{class_name}.java")
            os.rename(temp_file_path, java_file_path)

            compile_process = subprocess.run(["javac", java_file_path], capture_output=True, text=True)
            if compile_process.returncode != 0:
                return "", f"Compilation Error:\n{compile_process.stderr}"

            cmd = ["java", "-cp", os.path.dirname(java_file_path), class_name]

        elif language == "php":
            cmd = ["php", temp_file_path]

        else:
            return "Unsupported language", "Error"

        # Execute the program
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        output, error = result.stdout.strip(), result.stderr.strip()
        logging.debug("Command executed: %s", ' '.join(cmd))

    except subprocess.TimeoutExpired:
        output, error = "", "Execution timed out."
    except Exception as e:
        output, error = "", str(e)
    finally:
        cleanup_files(temp_file_path, exe_file if 'exe_file' in locals() else None)

    return output, error

def get_file_extension(language):
    """Returns file extension based on language."""
    return {
        "python": ".py",
        "javascript": ".js",
        "c": ".c",
        "cpp": ".cpp",
        "java": ".java",
        "php": ".php"
    }.get(language, "")

def extract_java_class_name(code):
    """Extracts the class name from Java code using regex."""
    match = re.search(r'public\s+class\s+(\w+)', code)
    return match.group(1) if match else None

def cleanup_files(*files):
    """Deletes temporary files."""
    for file in files:
        if file and os.path.exists(file):
            try:
                os.remove(file)
            except PermissionError:
                logging.warning(f"Could not delete file: {file}")
