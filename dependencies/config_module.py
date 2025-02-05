import json
import os
import sys

def load_config(config_path=None):
    """
    Loads configuration from a JSON file.

    Args:
        config_path (str, optional): Path to the config file. Defaults to None, which uses the CONFIG_PATH environment variable.

    Returns:
        dict: A dictionary containing the configuration settings.

    Raises:
        FileNotFoundError: If the config file is not found.
        json.JSONDecodeError: If the config file is not valid JSON.
        ValueError: If required keys are missing or have invalid values, or if the hotkey format is incorrect.
        PermissionError: If there is a permissions issue reading the file.
    """
    if config_path is None:
        config_path = os.environ.get("CONFIG_PATH")
        if config_path is None:
           config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.json")

    try:
        with open(config_path, 'r') as f:
            config_data = json.load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"Config file not found at: {config_path}")
    except json.JSONDecodeError:
        raise json.JSONDecodeError(f"Invalid JSON format in config file at: {config_path}", "", 0)
    except PermissionError:
        raise PermissionError(f"No read permissions for config file at: {config_path}")
    
    required_keys = ["gemini_api_key", "gemini_model", "hotkey"]
    for key in required_keys:
        if key not in config_data:
            raise ValueError(f"Missing required key in config: {key}")
        if not config_data[key]:
            raise ValueError(f"Value for key '{key}' cannot be empty.")
        if not isinstance(config_data[key], str):
             raise ValueError(f"Value for key '{key}' must be a string.")
    
    hotkey = config_data["hotkey"]
    if not (len(hotkey.split("+")) == 3 or len(hotkey.split("+")) == 2):
          raise ValueError("Invalid hotkey format. Must be in the format 'modifier+key' or 'modifier+modifier+key' i.e. ctrl+r or ctrl+alt+r")
    
    return config_data


if __name__ == '__main__':
    try:
        config = load_config()
        print("Config loaded successfully:")
        print(config)
    except Exception as e:
        print(f"Error loading configuration: {e}")
