# Modified hotkey_module.py
# hotkey_module.py
import keyboard
import logging
import sys
import threading

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def register_hotkey(callback, hotkey_combination = "ctrl+shift+a"):
    """Registers a hotkey combination to trigger a callback function.

    Args:
        callback (function): The function to call when the hotkey is pressed.
        hotkey_combination (str): String representing hotkey combination like 'ctrl+shift+a'
    """
    try:
         if not callable(callback):
              logger.error("Error: callback needs to be a function!")
              return # Don't register a hotkey if callback isn't a function

         keyboard.add_hotkey(hotkey_combination, _hotkey_callback_wrapper(callback))
         logger.info(f"Hotkey '{hotkey_combination}' registered.")
    except Exception as e:
          logger.error(f"Error registering hotkey: {e}")


def start_listening():
    """
    Starts listening for hotkey presses.
    This is handled by keyboard library, so this is a passthrough method for testing purposes.
    """
    try:
        logger.info("Started listening for hotkey presses...")
        # keyboard.wait() # Blocks the program until a key is pressed. Does not need to be used here.
    except Exception as e:
        logger.error(f"Error listening for hotkey: {e}")

def start_listening_thread():
        """Starts a hotkey listening thread"""
        listening_thread = threading.Thread(target=start_listening)
        listening_thread.daemon = True # So it closes when the main process ends
        listening_thread.start()


def _hotkey_callback_wrapper(callback):
        """Wraps the callback to add more logging"""
        def wrapper():
                logger.debug(f"Hotkey triggered. Calling callback function: {callback.__name__}")
                callback() # Call the original function.
                logger.debug(f"Callback function completed: {callback.__name__}")
        return wrapper


if __name__ == '__main__':

    def example_callback():
        print("Hotkey was triggered!")

    register_hotkey(example_callback)
    start_listening()
    # Code below is never reached as the listener blocks the code
    print("Code Finished")
