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
    recording_module_path = os.path.join(DEPENDENCIES_DIR, "recording_module.py")
    
    # File existence check
    if not os.path.exists(recording_module_path):
        results["tests"].append({"name": "Check file existence", "result": "Failed", "error": f"Error: {recording_module_path} does not exist."})
        results["success"] = False
        return results
    else:
        results["tests"].append({"name": "Check file existence", "result": "Success"})

    # Module execution check
    try:
      process = subprocess.Popen([sys.executable, recording_module_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
      stdout, stderr = process.communicate()
      if process.returncode != 0:
          results["tests"].append({"name": "Run recording_module.py", "result": "Failed", "error": f"Failed to execute {recording_module_path}. Stderr: {stderr.decode()}"})
          results["success"] = False
          return results
      else:
        results["tests"].append({"name": "Run recording_module.py", "result": "Success"})
    except Exception as e:
        results["tests"].append({"name": "Exception Thrown", "result": "Failed", "error": str(e)})
        results["success"] = False
        return results
    
    # Output Error Check
    if "Error" in stdout.decode():
        results["tests"].append({"name":"Check for error messages", "result": "Failed", "error": "Error detected from recording module."})
        results["success"] = False
    else:
        results["tests"].append({"name":"Check for error messages", "result": "Success"})

    # Avi File Check
    if "exported to" not in stdout.decode():
         results["tests"].append({"name":"Check for avi export", "result": "Failed", "error": "No avi file was exported, or print message not found."})
         results["success"] = False
    else:
        output_path = stdout.decode().strip().split("exported to ")[1]
        if not os.path.exists(output_path):
            results["tests"].append({"name":"Check for avi export", "result": "Failed", "error": "File was not created."})
            results["success"] = False
        else:
          results["tests"].append({"name":"Check for avi export", "result": "Success"})
          os.remove(output_path)

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
