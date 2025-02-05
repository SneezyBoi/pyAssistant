import os
import subprocess
import sys
import io
import traceback
import tempfile
import json
import time
import cv2
import numpy as np
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEPENDENCIES_DIR = os.path.join(BASE_DIR, "dependencies")
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
MAIN_FILE = os.path.join(BASE_DIR, "main.py")
# ANSI escape codes for colors
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_section_header(title):
    print(f"\n{BLUE}=================================================================={RESET}")
    print(f"{BLUE}   {title}{RESET}")
    print(f"{BLUE}=================================================================={RESET}")


def create_test_config_file():
    print_section_header("Creating Test Config File")
    default_config = {
        "gemini_api_key": "YOUR_API_KEY_HERE",
        "gemini_model": "gemini-pro-vision",
        "hotkey": "ctrl+alt+r"
    }

    if not os.path.exists(CONFIG_FILE):
       print(f"    - {YELLOW}config.json not found. Creating...{RESET}")
       with open(CONFIG_FILE, 'w') as f:
           json.dump(default_config, f, indent=4)
       print(f"    - {GREEN}config.json created at: {CONFIG_FILE}{RESET}")
    else:
        print(f"    - {YELLOW}config.json already exists at: {CONFIG_FILE}{RESET}")

    # Check the contents of the file
    try:
        with open(CONFIG_FILE, 'r') as f:
           config_data = json.load(f)
           print(f"    - {YELLOW}config.json contents:{RESET}")
           for key, value in config_data.items():
             print(f"      - {key}: {value}")
    except Exception as e:
        print(f"    - {RED}Error reading config.json: {e}{RESET}")
    
    return CONFIG_FILE


def test_config_module():
    print_section_header("Testing config_module.py")
    results = {"tests": [], "success": True}
    config_module_path = os.path.join(DEPENDENCIES_DIR, "config_module.py")
    
    # Detailed file existence check
    print("  - Checking file existence:")
    if not os.path.exists(config_module_path):
      results["tests"].append({"name": "Check file existence", "result": "Failed", "error": f"Error: {config_module_path} does not exist."})
      print(f"    - {RED}Failed: config_module.py not found at {config_module_path}{RESET}")
      results["success"] = False
      return results
    else:
      results["tests"].append({"name": "Check file existence", "result": "Success"})
      print(f"    - {GREEN}Success: config_module.py found at {config_module_path}{RESET}")

    # Detailed module execution check
    print("  - Executing config_module.py:")
    try:
        process = subprocess.Popen([sys.executable, config_module_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        
        if process.returncode != 0:
            results["tests"].append({"name": "Run config_module.py", "result": "Failed", "error": f"Failed to execute {config_module_path}. Stderr: {stderr.decode()}"})
            print(f"    - {RED}Failed: Execution failed with return code {process.returncode}{RESET}")
            print(f"      {RED}Stderr:{RESET}\n{stderr.decode()}")
            results["success"] = False
            return results
        else:
             results["tests"].append({"name": "Run config_module.py", "result": "Success"})
             print(f"    - {GREEN}Success: config_module.py executed successfully{RESET}")
             
        # Check for print statement
        if "YOUR_API_KEY_HERE" in stdout.decode():
           results["tests"].append({"name": "Check for default API Key", "result": "Failed", "error":"Default API Key Detected."})
           print(f"    - {RED}Failed: Default API Key Detected in output. Please replace in config.json{RESET}")
           results["success"] = False
        else:
          results["tests"].append({"name": "Check for default API Key", "result": "Success"})
          print(f"    - {GREEN}Success: API Key not defaulted{RESET}")
    except Exception as e:
        results["tests"].append({"name": "Exception thrown", "result": "Failed", "error": str(e)})
        print(f"    - {RED}Exception Thrown during execution: {e}{RESET}")
        results["success"] = False
        
    # Print output
    if stdout:
        print(f"    - {YELLOW}Standard Output:{RESET}\n{stdout.decode()}")
    if stderr:
        print(f"    - {RED}Standard Error:{RESET}\n{stderr.decode()}")
        
    return results


def test_recording_module():
    print_section_header("Testing recording_module.py")
    results = {"tests": [], "success": True}
    recording_module_path = os.path.join(DEPENDENCIES_DIR, "recording_module.py")
    
    # File existence check
    print("  - Checking file existence:")
    if not os.path.exists(recording_module_path):
        results["tests"].append({"name": "Check file existence", "result": "Failed", "error": f"Error: {recording_module_path} does not exist."})
        print(f"    - {RED}Failed: recording_module.py not found at {recording_module_path}{RESET}")
        results["success"] = False
        return results
    else:
        results["tests"].append({"name": "Check file existence", "result": "Success"})
        print(f"    - {GREEN}Success: recording_module.py found at {recording_module_path}{RESET}")

    # Module execution check
    print("  - Executing recording_module.py:")
    try:
      process = subprocess.Popen([sys.executable, recording_module_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
      stdout, stderr = process.communicate()
      if process.returncode != 0:
          results["tests"].append({"name": "Run recording_module.py", "result": "Failed", "error": f"Failed to execute {recording_module_path}. Stderr: {stderr.decode()}"})
          print(f"    - {RED}Failed: Execution failed with return code {process.returncode}{RESET}")
          print(f"      {RED}Stderr:{RESET}\n{stderr.decode()}")
          results["success"] = False
          return results
      else:
        results["tests"].append({"name": "Run recording_module.py", "result": "Success"})
        print(f"    - {GREEN}Success: recording_module.py executed successfully{RESET}")
    except Exception as e:
        results["tests"].append({"name": "Exception Thrown", "result": "Failed", "error": str(e)})
        print(f"    - {RED}Exception Thrown during execution: {e}{RESET}")
        results["success"] = False
        return results
    
    # Output Error Check
    print("  - Checking for Error messages:")
    if "Error" in stdout.decode():
        results["tests"].append({"name":"Check for error messages", "result": "Failed", "error": "Error detected from recording module."})
        print(f"    - {RED}Failed: Error message detected from recording module. Check logs{RESET}")
        results["success"] = False
    else:
        results["tests"].append({"name":"Check for error messages", "result": "Success"})
        print(f"    - {GREEN}Success: No error messages found in output{RESET}")

    # Avi File Check
    print("  - Checking for avi export:")
    if "exported to" not in stdout.decode():
         results["tests"].append({"name":"Check for avi export", "result": "Failed", "error": "No avi file was exported, or print message not found."})
         print(f"    - {RED}Failed: 'exported to' message not found in standard output. No avi file was exported{RESET}")
         results["success"] = False
    else:
        output_path = stdout.decode().strip().split("exported to ")[1]
        if not os.path.exists(output_path):
            results["tests"].append({"name":"Check for avi export", "result": "Failed", "error": "File was not created."})
            print(f"    - {RED}Failed: File was not created at {output_path}{RESET}")
            results["success"] = False
        else:
          results["tests"].append({"name":"Check for avi export", "result": "Success"})
          print(f"    - {GREEN}Success: avi file was created at {output_path}{RESET}")
          os.remove(output_path)
          print(f"    - {YELLOW}Clean up: Removed temporary avi file at {output_path}{RESET}")
            
    # Print output
    if stdout:
        print(f"    - {YELLOW}Standard Output:{RESET}\n{stdout.decode()}")
    if stderr:
        print(f"    - {RED}Standard Error:{RESET}\n{stderr.decode()}")
    
    return results


def test_media_converter_module():
    print_section_header("Testing media_converter.py")
    results = {"tests": [], "success": True}
    media_converter_path = os.path.join(DEPENDENCIES_DIR, "media_converter.py")
    
    # File Existence Check
    print("  - Checking file existence:")
    if not os.path.exists(media_converter_path):
        results["tests"].append({"name": "Check file existence", "result": "Failed", "error": f"Error: {media_converter_path} does not exist."})
        print(f"    - {RED}Failed: media_converter.py not found at {media_converter_path}{RESET}")
        results["success"] = False
        return results
    else:
        results["tests"].append({"name": "Check file existence", "result": "Success"})
        print(f"    - {GREEN}Success: media_converter.py found at {media_converter_path}{RESET}")

    # Create a dummy avi file
    print("  - Creating a dummy avi file for testing:")
    try:
        with tempfile.NamedTemporaryFile(suffix=".avi", delete = False) as tmp_avi:
            dummy_video = np.zeros((100, 100, 3), dtype=np.uint8)
            video_writer = cv2.VideoWriter(tmp_avi.name, cv2.VideoWriter_fourcc(*'DIVX'), 30, (100, 100))
            for _ in range(30):
               video_writer.write(dummy_video)
            video_writer.release()
        print(f"    - {GREEN}Success: Dummy avi file created at {tmp_avi.name}{RESET}")
    except Exception as e:
        results["tests"].append({"name": "Dummy avi Creation", "result": "Failed", "error": f"Error creating dummy avi: {str(e)}"})
        print(f"    - {RED}Failed: Error when creating dummy avi file: {e}{RESET}")
        results["success"] = False
        return results

    # Module Execution Check
    print("  - Executing media_converter.py:")
    try:
        process = subprocess.Popen([sys.executable, media_converter_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        if process.returncode != 0:
           results["tests"].append({"name":"Run media_converter.py", "result":"Failed", "error":f"Failed to execute {media_converter_path}. Stderr: {stderr.decode()}"})
           print(f"    - {RED}Failed: Execution failed with return code {process.returncode}{RESET}")
           print(f"      {RED}Stderr:{RESET}\n{stderr.decode()}")
           results["success"] = False
           os.remove(tmp_avi.name)
           print(f"      {YELLOW}Clean up: Removed temporary avi file at {tmp_avi.name}{RESET}")
           return results
        else:
           results["tests"].append({"name":"Run media_converter.py", "result":"Success"})
           print(f"    - {GREEN}Success: media_converter.py executed successfully{RESET}")
    except Exception as e:
        results["tests"].append({"name":"Exception Thrown", "result":"Failed", "error": str(e)})
        print(f"    - {RED}Exception Thrown during execution: {e}{RESET}")
        results["success"] = False
        os.remove(tmp_avi.name)
        print(f"      {YELLOW}Clean up: Removed temporary avi file at {tmp_avi.name}{RESET}")
        return results
    
    # Error Message Check
    print("  - Checking for error messages:")
    if "Error" in stdout.decode() or "None" in stdout.decode():
        results["tests"].append({"name":"Check for error messages", "result":"Failed", "error":f"Could not find a filepath from the output: {stdout.decode()}"})
        print(f"    - {RED}Failed: Could not find a file path in output, or encountered 'Error' or 'None' in the output{RESET}")
        results["success"] = False
        os.remove(tmp_avi.name)
        print(f"      {YELLOW}Clean up: Removed temporary avi file at {tmp_avi.name}{RESET}")
        return results
    else:
       results["tests"].append({"name":"Check for error messages", "result":"Success"})
       print(f"    - {GREEN}Success: No error message detected{RESET}")
    
    # MP4 File Creation Check
    print("  - Checking for mp4 file creation:")
    output_path = stdout.decode().strip()
    if not os.path.exists(output_path):
        results["tests"].append({"name": "Check mp4 file creation", "result":"Failed", "error": "File not created."})
        print(f"    - {RED}Failed: mp4 file was not created at {output_path}{RESET}")
        results["success"] = False
        os.remove(tmp_avi.name)
        print(f"      {YELLOW}Clean up: Removed temporary avi file at {tmp_avi.name}{RESET}")
        return results
    else:
        results["tests"].append({"name": "Check mp4 file creation", "result":"Success"})
        print(f"    - {GREEN}Success: mp4 file created at {output_path}{RESET}")
        
    # MP4 File Read Check
    print("  - Checking if mp4 file is valid:")
    try:
        cap = cv2.VideoCapture(output_path)
        if not cap.isOpened():
           results["tests"].append({"name":"Check if mp4 file is valid", "result": "Failed", "error": "Could not open the mp4 file with cv2."})
           print(f"    - {RED}Failed: Could not open the mp4 file at {output_path} with cv2{RESET}")
           results["success"] = False
           cap.release()
           os.remove(output_path)
           print(f"      {YELLOW}Clean up: Removed temporary mp4 file at {output_path}{RESET}")
           os.remove(tmp_avi.name)
           print(f"      {YELLOW}Clean up: Removed temporary avi file at {tmp_avi.name}{RESET}")
           return results
        else:
           results["tests"].append({"name":"Check if mp4 file is valid", "result": "Success"})
           print(f"    - {GREEN}Success: mp4 file at {output_path} can be opened with cv2{RESET}")
           cap.release()
           os.remove(output_path)
           print(f"      {YELLOW}Clean up: Removed temporary mp4 file at {output_path}{RESET}")
    except Exception as e:
        results["tests"].append({"name":"Exception Thrown when opening mp4", "result":"Failed", "error":f"Failed to read the mp4 file with cv2: {e}"})
        print(f"    - {RED}Failed: Exception occurred while reading the mp4 file with cv2: {e}{RESET}")
        results["success"] = False
        os.remove(tmp_avi.name)
        print(f"      {YELLOW}Clean up: Removed temporary avi file at {tmp_avi.name}{RESET}")
        os.remove(output_path)
        print(f"      {YELLOW}Clean up: Removed temporary mp4 file at {output_path}{RESET}")
        return results

    os.remove(tmp_avi.name)
    print(f"      {YELLOW}Clean up: Removed temporary avi file at {tmp_avi.name}{RESET}")

    # Print output
    if stdout:
        print(f"    - {YELLOW}Standard Output:{RESET}\n{stdout.decode()}")
    if stderr:
        print(f"    - {RED}Standard Error:{RESET}\n{stderr.decode()}")
    
    return results


def test_gemini_api_module():
    print_section_header("Testing gemini_api_module.py")
    results = {"tests": [], "success": True}
    gemini_api_module_path = os.path.join(DEPENDENCIES_DIR, "gemini_api_module.py")
    
    # File Existence Check
    print("  - Checking file existence:")
    if not os.path.exists(gemini_api_module_path):
        results["tests"].append({"name": "Check file existence", "result": "Failed", "error": f"Error: {gemini_api_module_path} does not exist."})
        print(f"    - {RED}Failed: gemini_api_module.py not found at {gemini_api_module_path}{RESET}")
        results["success"] = False
        return results
    else:
        results["tests"].append({"name": "Check file existence", "result": "Success"})
        print(f"    - {GREEN}Success: gemini_api_module.py found at {gemini_api_module_path}{RESET}")

    # Module Execution Check
    print("  - Executing gemini_api_module.py:")
    try:
        process = subprocess.Popen([sys.executable, gemini_api_module_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        
        if process.returncode != 0:
            results["tests"].append({"name": "Run gemini_api_module.py", "result": "Failed", "error": f"Failed to execute {gemini_api_module_path}. Stderr: {stderr.decode()}"})
            print(f"    - {RED}Failed: Execution failed with return code {process.returncode}{RESET}")
            print(f"      {RED}Stderr:{RESET}\n{stderr.decode()}")
            results["success"] = False
            return results
        else:
            results["tests"].append({"name": "Run gemini_api_module.py", "result":"Success"})
            print(f"    - {GREEN}Success: gemini_api_module.py executed successfully{RESET}")
    except Exception as e:
        results["tests"].append({"name":"Exception Thrown", "result":"Failed", "error":str(e)})
        print(f"    - {RED}Exception Thrown during execution: {e}{RESET}")
        results["success"] = False
        return results
    
    # Error message check
    print("  - Checking for Error messages:")
    if "Error" in stdout.decode() or "None" in stdout.decode():
       results["tests"].append({"name":"Check for error messages", "result":"Failed", "error":"Error detected from gemini api module."})
       print(f"    - {RED}Failed: Error message detected from gemini api module, or got a None value{RESET}")
       results["success"] = False
       return results
    else:
      results["tests"].append({"name":"Check for error messages", "result":"Success"})
      print(f"    - {GREEN}Success: No error message detected from the gemini api module.{RESET}")

    # Gemini Response Check
    print("  - Checking if a response was returned:")
    if "Response:" not in stdout.decode():
         results["tests"].append({"name":"Check if response returned", "result": "Failed", "error":"Response from the model not returned."})
         print(f"    - {RED}Failed: Response not found in standard output{RESET}")
         results["success"] = False
    else:
        results["tests"].append({"name":"Check if response returned", "result":"Success"})
        print(f"    - {GREEN}Success: Response was found in standard output{RESET}")
    
    # Print output
    if stdout:
        print(f"    - {YELLOW}Standard Output:{RESET}\n{stdout.decode()}")
    if stderr:
        print(f"    - {RED}Standard Error:{RESET}\n{stderr.decode()}")

    return results


def test_tts_module():
    print_section_header("Testing tts_module.py")
    results = {"tests": [], "success": True}
    tts_module_path = os.path.join(DEPENDENCIES_DIR, "tts_module.py")
    
    # File Existence Check
    print("  - Checking file existence:")
    if not os.path.exists(tts_module_path):
        results["tests"].append({"name":"Check file existence", "result":"Failed", "error": f"Error: {tts_module_path} does not exist."})
        print(f"    - {RED}Failed: tts_module.py not found at {tts_module_path}{RESET}")
        results["success"] = False
        return results
    else:
        results["tests"].append({"name":"Check file existence", "result":"Success"})
        print(f"    - {GREEN}Success: tts_module.py found at {tts_module_path}{RESET}")
    
    # Module Execution Check
    print("  - Executing tts_module.py:")
    try:
        process = subprocess.Popen([sys.executable, tts_module_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            results["tests"].append({"name": "Run tts_module.py", "result": "Failed", "error": f"Failed to execute {tts_module_path}. Stderr: {stderr.decode()}"})
            print(f"    - {RED}Failed: Execution failed with return code {process.returncode}{RESET}")
            print(f"      {RED}Stderr:{RESET}\n{stderr.decode()}")
            results["success"] = False
            return results
        else:
            results["tests"].append({"name":"Run tts_module.py", "result":"Success"})
            print(f"    - {GREEN}Success: tts_module.py executed successfully{RESET}")
    except Exception as e:
        results["tests"].append({"name":"Exception Thrown", "result":"Failed", "error":str(e)})
        print(f"    - {RED}Exception Thrown during execution: {e}{RESET}")
        results["success"] = False
        return results

    # Error Message Check
    print("  - Checking for errors from the tts_module.py:")
    if "Error" in stdout.decode():
        results["tests"].append({"name":"Check for errors", "result":"Failed", "error":"Error detected from tts module."})
        print(f"    - {RED}Failed: Error message detected from tts module{RESET}")
        results["success"] = False
    else:
        results["tests"].append({"name":"Check for errors", "result":"Success"})
        print(f"    - {GREEN}Success: No error message detected from tts module{RESET}")
        
    # Print output
    if stdout:
        print(f"    - {YELLOW}Standard Output:{RESET}\n{stdout.decode()}")
    if stderr:
        print(f"    - {RED}Standard Error:{RESET}\n{stderr.decode()}")

    return results


def test_hotkey_module():
    print_section_header("Testing hotkey_module.py")
    results = {"tests": [], "success": True}
    hotkey_module_path = os.path.join(DEPENDENCIES_DIR, "hotkey_module.py")
    
    # File existence check
    print("  - Checking file existence:")
    if not os.path.exists(hotkey_module_path):
        results["tests"].append({"name":"Check file existence", "result":"Failed", "error": f"Error: {hotkey_module_path} does not exist."})
        print(f"    - {RED}Failed: hotkey_module.py not found at {hotkey_module_path}{RESET}")
        results["success"] = False
        return results
    else:
         results["tests"].append({"name":"Check file existence", "result":"Success"})
         print(f"    - {GREEN}Success: hotkey_module.py found at {hotkey_module_path}{RESET}")
    
    # Module Execution Check
    print("  - Executing hotkey_module.py:")
    try:
        process = subprocess.Popen([sys.executable, hotkey_module_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            results["tests"].append({"name": "Run hotkey_module.py", "result":"Failed", "error": f"Failed to execute {hotkey_module_path}. Stderr: {stderr.decode()}"})
            print(f"    - {RED}Failed: Execution failed with return code {process.returncode}{RESET}")
            print(f"      {RED}Stderr:{RESET}\n{stderr.decode()}")
            results["success"] = False
            return results
        else:
           results["tests"].append({"name": "Run hotkey_module.py", "result":"Success"})
           print(f"    - {GREEN}Success: hotkey_module.py executed successfully{RESET}")
    except Exception as e:
         results["tests"].append({"name":"Exception Thrown", "result":"Failed", "error":str(e)})
         print(f"    - {RED}Exception Thrown during execution: {e}{RESET}")
         results["success"] = False
    
    # Print output
    if stdout:
        print(f"    - {YELLOW}Standard Output:{RESET}\n{stdout.decode()}")
    if stderr:
        print(f"    - {RED}Standard Error:{RESET}\n{stderr.decode()}")
    
    return results


def test_error_handling_module():
    print_section_header("Testing error_handling_module.py")
    results = {"tests": [], "success": True}
    error_handling_module_path = os.path.join(DEPENDENCIES_DIR, "error_handling_module.py")
    
    # File Existence Check
    print("  - Checking file existence:")
    if not os.path.exists(error_handling_module_path):
        results["tests"].append({"name":"Check file existence", "result":"Failed", "error":f"Error: {error_handling_module_path} does not exist."})
        print(f"    - {RED}Failed: error_handling_module.py not found at {error_handling_module_path}{RESET}")
        results["success"] = False
        return results
    else:
        results["tests"].append({"name":"Check file existence", "result":"Success"})
        print(f"    - {GREEN}Success: error_handling_module.py found at {error_handling_module_path}{RESET}")

    # Module Execution Check
    print("  - Executing error_handling_module.py:")
    try:
        process = subprocess.Popen([sys.executable, error_handling_module_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            results["tests"].append({"name": "Run error_handling_module.py", "result":"Failed", "error": f"Failed to execute {error_handling_module_path}. Stderr: {stderr.decode()}"})
            print(f"    - {RED}Failed: Execution failed with return code {process.returncode}{RESET}")
            print(f"      {RED}Stderr:{RESET}\n{stderr.decode()}")
            results["success"] = False
            return results
        else:
            results["tests"].append({"name": "Run error_handling_module.py", "result":"Success"})
            print(f"    - {GREEN}Success: error_handling_module.py executed successfully{RESET}")
    except Exception as e:
        results["tests"].append({"name":"Exception Thrown", "result":"Failed", "error":str(e)})
        print(f"    - {RED}Exception Thrown during execution: {e}{RESET}")
        results["success"] = False
        return results

    # Shutdown message Check
    print("  - Checking for shutdown message:")
    if "Program Shutting Down" not in stdout.decode():
        results["tests"].append({"name": "Check for shutdown message", "result":"Failed", "error": "Error detected from error handling module, did not print shutdown message."})
        print(f"    - {RED}Failed: Shutdown message was not found in standard output{RESET}")
        results["success"] = False
    else:
        results["tests"].append({"name":"Check for shutdown message", "result":"Success"})
        print(f"    - {GREEN}Success: Shutdown message was found in standard output{RESET}")
    
    # Print output
    if stdout:
        print(f"    - {YELLOW}Standard Output:{RESET}\n{stdout.decode()}")
    if stderr:
        print(f"    - {RED}Standard Error:{RESET}\n{stderr.decode()}")
    
    return results


def test_main_file():
    print_section_header("Testing main.py")
    results = {"tests": [], "success": True}
    
    # File existence check
    print("  - Checking file existence:")
    if not os.path.exists(MAIN_FILE):
        results["tests"].append({"name": "Check file existence", "result": "Failed", "error": f"Error: {MAIN_FILE} does not exist."})
        print(f"    - {RED}Failed: main.py not found at {MAIN_FILE}{RESET}")
        results["success"] = False
        return results
    else:
        results["tests"].append({"name": "Check file existence", "result": "Success"})
        print(f"    - {GREEN}Success: main.py found at {MAIN_FILE}{RESET}")
    
    # main execution check
    print("  - Executing main.py:")
    try:
      process = subprocess.Popen([sys.executable, MAIN_FILE], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
      stdout, stderr = process.communicate()
      if process.returncode != 0:
          results["tests"].append({"name":"Run main.py", "result":"Failed", "error": f"Failed to execute {MAIN_FILE}. Stderr: {stderr.decode()}"})
          print(f"    - {RED}Failed: Execution failed with return code {process.returncode}{RESET}")
          print(f"      {RED}Stderr:{RESET}\n{stderr.decode()}")
          results["success"] = False
          return results
      else:
          results["tests"].append({"name":"Run main.py", "result":"Success"})
          print(f"    - {GREEN}Success: main.py executed successfully{RESET}")
    except Exception as e:
        results["tests"].append({"name":"Exception Thrown", "result":"Failed", "error": str(e)})
        print(f"    - {RED}Exception Thrown during execution: {e}{RESET}")
        results["success"] = False
        return results
    
    # Check for Shutdown Message
    print("  - Checking for the Shutdown Message:")
    if "Program Shutting Down" not in stdout.decode():
        results["tests"].append({"name":"Check for Shutdown message", "result":"Failed", "error":"Shutdown message not found in stdout, or script did not fully execute."})
        print(f"    - {RED}Failed: Shutdown message not found in main.py execution{RESET}")
        results["success"] = False
    else:
        results["tests"].append({"name":"Check for Shutdown message", "result":"Success"})
        print(f"    - {GREEN}Success: Shutdown message found in standard output{RESET}")
    
    # Print output
    if stdout:
        print(f"    - {YELLOW}Standard Output:{RESET}\n{stdout.decode()}")
    if stderr:
        print(f"    - {RED}Standard Error:{RESET}\n{stderr.decode()}")
    
    return results

def main():
    tests = {
        "config_module.py": test_config_module,
        "recording_module.py": test_recording_module,
        "media_converter.py": test_media_converter_module,
        "gemini_api_module.py": test_gemini_api_module,
        "tts_module.py": test_tts_module,
        "hotkey_module.py": test_hotkey_module,
        "error_handling_module.py": test_error_handling_module,
        "main.py": test_main_file,
    }
    
    failed_test_count = 0
    print("\nTest Results Summary:")
    for file_name, test_func in tests.items():
        test_results = test_func()
        print(f"\nTesting {file_name}:")
        if test_results["tests"]:
            for test in test_results["tests"]:
                result_color = GREEN if test["result"] == "Success" else RED
                print(f"    - {test['name']}: {result_color}{test['result']}{RESET}")
                if "error" in test:
                  print(f"      Error: {test['error']}")
        if not test_results["success"]:
             failed_test_count += 1
             
    return failed_test_count

if __name__ == "__main__":
    if not os.path.exists(DEPENDENCIES_DIR):
        print(f"{RED}Error: Dependencies directory not found at {DEPENDENCIES_DIR}. Please ensure it exists and contains the required modules.{RESET}")
        sys.exit(1)
    failed_test_count = main()
    sys.exit(failed_test_count)
