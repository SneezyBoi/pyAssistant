import json
import os
import unittest
import sys
from unittest.mock import patch
# Adjust the sys.path for the location of the python files
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config_module import load_config


class TestConfigModule(unittest.TestCase):

    CONFIG_FILE = 'config.json'
    
    def setUp(self):
        # Create a dummy config file for testing
        self.test_config_data = {
            "gemini_api_key": "test_api_key",
            "gemini_model": "gemini-2.0-pro",
            "hotkey": "ctrl+shift+a"
        }
        with open(self.CONFIG_FILE, 'w') as f:
            json.dump(self.test_config_data, f)

    def tearDown(self):
        # Remove the dummy config file
        if os.path.exists(self.CONFIG_FILE):
            os.remove(self.CONFIG_FILE)
    
    def test_load_config_success(self):
        config = load_config(self.CONFIG_FILE)
        self.assertEqual(config['gemini_api_key'], 'test_api_key')
        self.assertEqual(config['gemini_model'], 'gemini-2.0-pro')
        self.assertEqual(config['hotkey'], 'ctrl+shift+a')
        
    def test_load_config_file_not_found(self):
        # Remove test file
        os.remove(self.CONFIG_FILE)
        
        # Attempt to load without file
        with self.assertRaises(FileNotFoundError) as context:
            load_config(self.CONFIG_FILE)
        self.assertIn("Config file not found", str(context.exception))


    def test_missing_key(self):
        # Create config missing a key
        missing_key_data = {
            "gemini_api_key": "test_api_key",
            "hotkey": "ctrl+shift+a"
        }
        with open(self.CONFIG_FILE, 'w') as f:
             json.dump(missing_key_data, f)
        
        with self.assertRaises(ValueError) as context:
           load_config(self.CONFIG_FILE)
        self.assertIn("Missing required key in config", str(context.exception))
    
    def test_empty_key(self):
         # Create config with empty key
        missing_key_data = {
            "gemini_api_key": "",
            "gemini_model": "gemini-2.0-pro",
            "hotkey": "ctrl+shift+a"
        }
        with open(self.CONFIG_FILE, 'w') as f:
             json.dump(missing_key_data, f)
             
        with self.assertRaises(ValueError) as context:
            load_config(self.CONFIG_FILE)
        self.assertIn("Value for key 'gemini_api_key' cannot be empty.", str(context.exception))
    
    def test_invalid_type(self):
        # Create config with invalid type
        missing_key_data = {
            "gemini_api_key": 123,
            "gemini_model": "gemini-2.0-pro",
            "hotkey": "ctrl+shift+a"
        }
        with open(self.CONFIG_FILE, 'w') as f:
             json.dump(missing_key_data, f)
        
        with self.assertRaises(ValueError) as context:
            load_config(self.CONFIG_FILE)
        self.assertIn("Value for key 'gemini_api_key' must be a string.", str(context.exception))

    def test_invalid_hotkey_format_1(self):
         # Create config with empty key
        missing_key_data = {
            "gemini_api_key": "test_api_key",
            "gemini_model": "gemini-2.0-pro",
            "hotkey": "ctrl+a"
        }
        with open(self.CONFIG_FILE, 'w') as f:
             json.dump(missing_key_data, f)
             
        with self.assertRaises(ValueError) as context:
            load_config(self.CONFIG_FILE)
        self.assertIn("Invalid hotkey format", str(context.exception))
   
    def test_invalid_hotkey_format_2(self):
         # Create config with empty key
        missing_key_data = {
            "gemini_api_key": "test_api_key",
            "gemini_model": "gemini-2.0-pro",
            "hotkey": "ctrl+a+b+c"
        }
        with open(self.CONFIG_FILE, 'w') as f:
             json.dump(missing_key_data, f)
             
        with self.assertRaises(ValueError) as context:
            load_config(self.CONFIG_FILE)
        self.assertIn("Invalid hotkey format", str(context.exception))

    
    
def run_test():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestConfigModule))
    runner = unittest.TextTestRunner()
    runner.run(suite)
   
if __name__ == '__main__':
    run_test()
