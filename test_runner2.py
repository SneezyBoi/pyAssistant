import os
import json
import subprocess
import sys
import logging

# Get the absolute path to the project's base directory
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__)))
CONFIG_FILE = 'config.json'
DEPENDENCIES_DIR = os.path.join(BASE_DIR, 'dependencies')


# Set up logging (without INFO prefix)
logging.basicConfig(level=logging.INFO, format='%(message)s')

def create_test_config_file():
    logging.info('==================================================================')
    logging.info('   Creating Test Config File')
    logging.info('==================================================================')

    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            try:
                config_data = json.load(f)
            except json.JSONDecodeError:
                config_data = {}
        logging.info(f"    - {CONFIG_FILE} already exists at: {os.path.abspath(CONFIG_FILE)}")
        logging.info("    - config.json contents:")
        for key, value in config_data.items():
            logging.info(f"      - {key}: {value}")
    else:
        default_config = {
            "gemini_api_key": "YOUR_API_KEY_HERE",
            "gemini_model": "gemini-2.0-flash-exp",
            "hotkey": "ctrl+lshift+space"
        }
        with open(CONFIG_FILE, 'w') as f:
            json.dump(default_config, f, indent=2)
        logging.info(f"    - {CONFIG_FILE} created at: {os.path.abspath(CONFIG_FILE)}")
        logging.info("    - config.json contents:")
        for key, value in default_config.items():
            logging.info(f"      - {key}: {value}")

def run_test(module_name):
    logging.info('==================================================================')
    logging.info(f'   Running Test: {module_name}')
    logging.info('==================================================================')
    
    # Add the project dependencies directory to the Python path
    sys.path.insert(0, DEPENDENCIES_DIR)

    test_file_path = os.path.join(BASE_DIR, 'tests', f'test_{module_name}.py')
    
    if not os.path.exists(test_file_path):
      logging.error(f"Error: Test file not found at {test_file_path}")
      return False
    
    try:
       # Execute the test file as a script and capture output
        process = subprocess.run([sys.executable, test_file_path], check=True, capture_output=True, text=True)
        if process.stdout:
            logging.info(f"    - Output:\n{process.stdout}")
        return True
    except subprocess.CalledProcessError as e:
       logging.error(f"Error running test {module_name}: {e}")
       logging.error(f"  - Error Output:\n{e.stderr}")
       return False
    except Exception as e:
       logging.error(f"Unexpected error running test {module_name}: {e}")
       return False

def main():
    create_test_config_file()
    test_modules = [
        "config_module",
        "recording_module",
        "media_converter_module",
        "gemini_api_module",
        "tts_module",
        "hotkey_module",
        "error_handling_module",
        "main_file"
    ]
    failed_test_count = 0
    for module_name in test_modules:
       if not run_test(module_name):
          failed_test_count += 1
    logging.info('==================================================================')
    logging.info('   Test Run Complete')
    logging.info('==================================================================')
    if failed_test_count > 0:
        logging.info(f" {failed_test_count} test(s) failed!")
    else:
        logging.info("All tests passed!")
    return failed_test_count

if __name__ == '__main__':
    failed_test_count = main()
    if failed_test_count > 0 :
        print(f"There were {failed_test_count} failed tests. See log for more details")
