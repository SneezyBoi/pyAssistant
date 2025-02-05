import os
import subprocess
import sys

# Project directories (assuming the test file is in 'tests' dir)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEPENDENCIES_DIR = os.path.join(BASE_DIR, "dependencies")

# ANSI escape codes for colors
RED = '\033[91m'
GREEN = '\033[92m'
RESET = '\033[0m'

def run_test():
    results = {"tests": [], "success": True}
    tts_module_path = os.path.join(DEPENDENCIES_DIR, "tts_module.py")
    
    # File Existence Check
    if not os.path.exists(tts_module_path):
        results["tests"].append({"name":"Check file existence", "result":"Failed", "error": f"Error: {tts_module_path} does not exist."})
        results["success"] = False
        return results
    else:
        results["tests"].append({"name":"Check file existence", "result":"Success"})
    
    # Module Execution Check
    try:
        process = subprocess.Popen([sys.executable, tts_module_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            results["tests"].append({"name": "Run tts_module.py", "result": "Failed", "error": f"Failed to execute {tts_module_path}. Stderr: {stderr.decode()}"})
            results["success"] = False
            return results
        else:
            results["tests"].append({"name":"Run tts_module.py", "result":"Success"})
    except Exception as e:
        results["tests"].append({"name":"Exception Thrown", "result":"Failed", "error":str(e)})
        results["success"] = False
        return results

    # Error Message Check (expecting no error if tts works)
    if "Error" in stdout.decode():
        results["tests"].append({"name":"Check for errors", "result":"Failed", "error":"Error detected from tts module."})
        results["success"] = False
    else:
         results["tests"].append({"name":"Check for errors", "result":"Success"})

    # Check if any text was spoken (by checking for a print statement)
    if "Sample Text" not in stdout.decode():
          results["tests"].append({"name":"Check if text was spoken", "result":"Failed", "error":"No text was spoken, or print message not detected."})
          results["success"] = False
    else:
         results["tests"].append({"name":"Check if text was spoken", "result":"Success"})
    
    return results


if __name__ == "__main__":
    test_results = run_test()
    if test_results:
        if test_results["tests"]:
            for test in test_results["tests"]:
                result_color = GREEN if test["result"] == "Success" else RED
                print(f"    - {test['name']}: {result_color}{test['result']}{RESET}")
                if "error" in test:
                  print(f"      Error: {test['error']}")
