import os
import subprocess
import sys
import tempfile
import cv2
import numpy as np

# Project directories (assuming the test file is in 'tests' dir)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEPENDENCIES_DIR = os.path.join(BASE_DIR, "dependencies")

# ANSI escape codes for colors
RED = '\033[91m'
GREEN = '\033[92m'
RESET = '\033[0m'

def run_test():
    results = {"tests": [], "success": True}
    media_converter_path = os.path.join(DEPENDENCIES_DIR, "media_converter.py")
    
    # File Existence Check
    if not os.path.exists(media_converter_path):
        results["tests"].append({"name": "Check file existence", "result": "Failed", "error": f"Error: {media_converter_path} does not exist."})
        results["success"] = False
        return results
    else:
        results["tests"].append({"name": "Check file existence", "result": "Success"})

    # Create a dummy avi file for testing
    try:
        with tempfile.NamedTemporaryFile(suffix=".avi", delete = False) as tmp_avi:
            dummy_video = np.zeros((100, 100, 3), dtype=np.uint8)
            video_writer = cv2.VideoWriter(tmp_avi.name, cv2.VideoWriter_fourcc(*'DIVX'), 30, (100, 100))
            for _ in range(30):
               video_writer.write(dummy_video)
            video_writer.release()
    except Exception as e:
        results["tests"].append({"name": "Dummy avi Creation", "result": "Failed", "error": f"Error creating dummy avi: {str(e)}"})
        results["success"] = False
        return results

    # Module Execution Check
    try:
        process = subprocess.Popen([sys.executable, media_converter_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        if process.returncode != 0:
           results["tests"].append({"name":"Run media_converter.py", "result":"Failed", "error":f"Failed to execute {media_converter_path}. Stderr: {stderr.decode()}"})
           results["success"] = False
           if os.path.exists(tmp_avi.name):
             os.remove(tmp_avi.name)
           return results
        else:
           results["tests"].append({"name":"Run media_converter.py", "result":"Success"})
           
    except Exception as e:
        results["tests"].append({"name":"Exception Thrown", "result":"Failed", "error": str(e)})
        results["success"] = False
        if os.path.exists(tmp_avi.name):
          os.remove(tmp_avi.name)
        return results
    
    # Error Message Check
    if "Error" in stdout.decode() or "None" in stdout.decode():
        results["tests"].append({"name":"Check for error messages", "result":"Failed", "error":f"Could not find a filepath from the output: {stdout.decode()}"})
        results["success"] = False
        if os.path.exists(tmp_avi.name):
          os.remove(tmp_avi.name)
        return results
    else:
       results["tests"].append({"name":"Check for error messages", "result":"Success"})
    
    # MP4 File Creation Check
    output_path = stdout.decode().strip()
    if not os.path.exists(output_path):
        results["tests"].append({"name": "Check mp4 file creation", "result":"Failed", "error": "File not created."})
        results["success"] = False
        if os.path.exists(tmp_avi.name):
           os.remove(tmp_avi.name)
        return results
    else:
        results["tests"].append({"name": "Check mp4 file creation", "result":"Success"})
        
    # MP4 File Read Check
    try:
         cap = cv2.VideoCapture(output_path)
         if not cap.isOpened():
             results["tests"].append({"name":"Check if mp4 file is valid", "result": "Failed", "error": "Could not open the mp4 file with cv2."})
             results["success"] = False
             cap.release()
             if os.path.exists(output_path):
               os.remove(output_path)
             if os.path.exists(tmp_avi.name):
               os.remove(tmp_avi.name)
             return results
         else:
             results["tests"].append({"name":"Check if mp4 file is valid", "result": "Success"})
             cap.release()
             if os.path.exists(output_path):
               os.remove(output_path)
    except Exception as e:
          results["tests"].append({"name":"Exception Thrown when opening mp4", "result":"Failed", "error":f"Failed to read the mp4 file with cv2: {e}"})
          results["success"] = False
          if os.path.exists(tmp_avi.name):
             os.remove(tmp_avi.name)
          if os.path.exists(output_path):
             os.remove(output_path)
          return results

    if os.path.exists(tmp_avi.name):
      os.remove(tmp_avi.name)
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
