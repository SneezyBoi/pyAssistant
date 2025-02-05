import os
import subprocess
import sys
import json
import tempfile
import cv2
import numpy as np

# Project directories (assuming the test file is in 'tests' dir)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEPENDENCIES_DIR = os.path.join(BASE_DIR, "dependencies")
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")


# ANSI escape codes for colors
RED = '\033[91m'
GREEN = '\033[92m'
RESET = '\033[0m'

def run_test():
    results = {"tests": [], "success": True}
    gemini_api_module_path = os.path.join(DEPENDENCIES_DIR, "gemini_api_module.py")
    
    # Helper function to execute module and capture output
    def execute_module(config_override=None):
        # Create a temporary config file if config_override is given
        if config_override:
            try:
                with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp_config:
                  json.dump(config_override, tmp_config)
                  tmp_config_path = tmp_config.name
            except Exception as e:
                 results["tests"].append({"name":"Temporary Config Error", "result":"Failed", "error":f"Error creating temporary config file: {e}"})
                 results["success"] = False
                 return None, None

        command = [sys.executable, gemini_api_module_path]
        # set env variable to override config path
        if config_override:
          process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env = {"CONFIG_FILE": tmp_config_path})
        else:
          process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        if config_override:
            os.remove(tmp_config_path)  # Clean up the temporary file
            
        return stdout.decode(), stderr.decode(), process.returncode
    
    # File Existence Check
    if not os.path.exists(gemini_api_module_path):
        results["tests"].append({"name": "Check file existence", "result": "Failed", "error": f"Error: {gemini_api_module_path} does not exist."})
        results["success"] = False
        return results
    else:
        results["tests"].append({"name": "Check file existence", "result": "Success"})

    # Module Execution Check
    stdout, stderr, returncode = execute_module()
    if returncode != 0:
        results["tests"].append({"name": "Run gemini_api_module.py", "result": "Failed", "error": f"Failed to execute {gemini_api_module_path}. Stderr: {stderr}"})
        results["success"] = False
        return results
    else:
        results["tests"].append({"name": "Run gemini_api_module.py", "result":"Success"})
        
    # Check for errors in the normal case
    if "Error" in stdout or "None" in stdout:
        results["tests"].append({"name":"Check for error messages in output", "result":"Failed", "error":"Error detected from gemini api module."})
        results["success"] = False
        return results
    else:
        results["tests"].append({"name":"Check for error messages in output", "result":"Success"})
    
    # Gemini Response Check
    if "Response:" not in stdout:
        results["tests"].append({"name":"Check if response returned", "result": "Failed", "error":"Response from the model not returned."})
        results["success"] = False
        return results
    else:
        results["tests"].append({"name":"Check if response returned", "result":"Success"})

    # check response is a string
    response_str = stdout.split("Response: ", 1)[1].strip()
    if not isinstance(response_str, str):
        results["tests"].append({"name": "Check if response is a string", "result": "Failed", "error":"Response is not a string"})
        results["success"] = False
        return results
    else:
        results["tests"].append({"name": "Check if response is a string", "result": "Success"})

    # Check if response is not empty
    if not response_str:
       results["tests"].append({"name": "Check if response is empty", "result": "Failed", "error":"Response is empty"})
       results["success"] = False
       return results
    else:
        results["tests"].append({"name":"Check if response is empty", "result":"Success"})
    
    # Test error handling with invalid api key
    config_override = {"gemini_api_key": "bad_api_key", "gemini_model": "gemini-2.0-flash-exp"}
    stdout, stderr, returncode = execute_module(config_override)
    
    if returncode == 0 and ("Error" in stdout or "None" in stdout) :
        results["tests"].append({"name":"Check error handling with bad api key", "result": "Success"})
    elif returncode != 0:
       results["tests"].append({"name":"Check error handling with bad api key", "result":"Failed", "error":f"Module exited with non-zero error code with bad api key:{stderr}"})
       results["success"] = False
    else:
        results["tests"].append({"name":"Check error handling with bad api key", "result":"Failed", "error":"No error detected with bad api key"})
        results["success"] = False
        
    # Test error handling when model is not found
    config_override = {"gemini_api_key": "YOUR_API_KEY_HERE", "gemini_model": "bad_gemini_model"}
    stdout, stderr, returncode = execute_module(config_override)
    if returncode == 0 and ("Error" in stdout or "None" in stdout):
        results["tests"].append({"name":"Check error handling with bad model name", "result":"Success"})
    elif returncode != 0:
        results["tests"].append({"name":"Check error handling with bad model name", "result":"Failed", "error":f"Module exited with non-zero error code with bad model name: {stderr}"})
        results["success"] = False
    else:
        results["tests"].append({"name":"Check error handling with bad model name", "result":"Failed", "error":"No error detected with bad model name"})
        results["success"] = False

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
