import os
import subprocess
import sys

# Project directories (assuming the test file is in 'tests' dir)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAIN_FILE = os.path.join(BASE_DIR, "main.py")

# ANSI escape codes for colors
RED = '\033[91m'
GREEN = '\033[92m'
RESET = '\033[0m'


def run_test():
    results = {"tests": [], "success": True}
    
    # File existence check
    if not os.path.exists(MAIN_FILE):
        results["tests"].append({"name": "Check file existence", "result": "Failed", "error": f"Error: {MAIN_FILE} does not exist."})
        results["success"] = False
        return results
    else:
        results["tests"].append({"name": "Check file existence", "result": "Success"})
    
    # main execution check
    try:
      process = subprocess.Popen([sys.executable, MAIN_FILE], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
      stdout, stderr = process.communicate()
      if process.returncode != 0:
          results["tests"].append({"name":"Run main.py", "result":"Failed", "error": f"Failed to execute {MAIN_FILE}. Stderr: {stderr.decode()}"})
          results["success"] = False
          return results
      else:
          results["tests"].append({"name":"Run main.py", "result":"Success"})
    except Exception as e:
        results["tests"].append({"name":"Exception Thrown", "result":"Failed", "error": str(e)})
        results["success"] = False
        return results
    
    # Check for Shutdown Message
    if "Program Shutting Down" not in stdout.decode():
        results["tests"].append({"name":"Check for Shutdown message", "result":"Failed", "error":"Shutdown message not found in stdout, or script did not fully execute."})
        results["success"] = False
    else:
        results["tests"].append({"name":"Check for Shutdown message", "result":"Success"})
    
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
