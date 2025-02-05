# Modified main.py
import logging
import time
import os
import sys
import threading
import collections  # For the deque
import inspect  # For logging function names
from datetime import datetime

# Import your modules
from dependencies import recording_module
from dependencies import hotkey_module
from dependencies import media_converter
from dependencies import tts_module
from dependencies import gemini_api_module
from dependencies import error_handling_module

# Set up log folder and file name
LOG_FOLDER = "logs"
if not os.path.exists(LOG_FOLDER):
    os.makedirs(LOG_FOLDER)

now = datetime.now()
timestamp = now.strftime("%Y-%m-%d_%H-%M-%S")
LOG_FILE = os.path.join(LOG_FOLDER, f"app_log_{timestamp}.txt")

# Setup Logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(LOG_FILE)
file_handler.setLevel(logging.DEBUG)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(module)s - %(funcName)s - %(lineno)d - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(console_handler)


# Global variable for the recording state
#is_recording = True
global restart_recording
restart_recording = False # Flag to trigger recording restart

# Recording Parameters
RECORDING_DURATION = 30  # Seconds
FRAME_RATE = 30  # Frames per second

# Rolling buffer to store video/audio data
audio_buffer = collections.deque(maxlen=int(RECORDING_DURATION * recording_module.sample_rate))  # Ensure that maxlen matches the sample rate


def log_function_call(func, *args, **kwargs):
    """Logs function calls with arguments and values."""
    try:
        arg_values = ', '.join(f'{arg}={repr(val)}' for arg, val in zip(inspect.getfullargspec(func).args, args))
        kwarg_values = ', '.join(f'{key}={repr(val)}' for key, val in kwargs.items())
        logger.debug(f"Entering function: {func.__name__}({arg_values}{', ' if arg_values and kwarg_values else ''}{kwarg_values})")
        file_handler.flush()
    except Exception as e:
        print(f"Error logging function call: {e}")


def log_function_return(func, return_value):
    """Logs function returns with values."""
    try:
        logger.debug(f"Exiting function: {func.__name__} returning: {repr(return_value)}")
        file_handler.flush()
    except Exception as e:
        print(f"Error logging function return: {e}")


def on_hotkey_press():
    global is_recording, restart_recording
    log_function_call(on_hotkey_press)

    logger.info("Hotkey pressed. Processing recording.")
    file_handler.flush()

    # Stop the current recording by ending the recording thread
    restart_recording = True
    logger.debug(f"Setting restart_recording to True. restart_recording = {restart_recording}")
    file_handler.flush()
    #is_recording = False
    #logger.debug(f"Setting is_recording to False. is_recording = {is_recording}")
    #file_handler.flush()
    #time.sleep(1)  # Give the recording thread some time to finish, since setting is_recording = False does not instantly stop it
    logger.debug(f"Finished sleep. is_recording = {is_recording}")
    file_handler.flush()


    try:
        # Convert the rolling buffer to MP4. This will require modifications to the recording_module.
        logger.debug("Calling media_converter.convert_to_mp4 with audio_buffer")
        file_handler.flush()
        mp4_filepath = media_converter.convert_to_mp4(audio_buffer)
        logger.debug(f"Returned mp4_filepath from media_converter.convert_to_mp4 = {mp4_filepath}")
        file_handler.flush()

        # Send to Gemini
        gemini_prompt = "Analyze the following video and provide a detailed summary"
        logger.debug(f"Calling gemini_api_module.generate_text with prompt: '{gemini_prompt}' and mp4_filepath: '{mp4_filepath}'")
        file_handler.flush()
        gemini_response = gemini_api_module.generate_text(gemini_prompt, mp4_filepath)  # We'll need to update the Gemini module to have the filepath input
        logger.debug(f"Returned gemini_response from gemini_api_module.generate_text = {gemini_response}")
        file_handler.flush()

        if gemini_response:
            # Read response with TTS
            logger.debug("Calling tts_module.read_text with gemini_response")
            file_handler.flush()
            tts_module.read_text(gemini_response)
        else:
            logger.error("No response from Gemini. ")
            file_handler.flush()

    except Exception as e:
        logger.error(f"Error processing hotkey press: {e}")
        file_handler.flush()
        error_handling_module.handle_exception(e, "main.py")  # For now, just the generic error handling, but can add specific cases later

    # Start new recording by resetting the global is_recording and calling recording
    #is_recording = True
    #logger.debug(f"Setting is_recording to True. is_recording = {is_recording}")
    #file_handler.flush()
    #start_recording_thread()
    log_function_return(on_hotkey_press, None)


def start_recording_thread():
    log_function_call(start_recording_thread)

    # Start a recording thread
    recording_thread = threading.Thread(target=continuous_recording)
    recording_thread.daemon = True  # So it closes when the main process ends
    logger.debug(f"Starting recording thread: {recording_thread}")
    file_handler.flush()
    recording_thread.start()
    log_function_return(start_recording_thread, None)


def continuous_recording():
    global is_recording, audio_buffer, restart_recording
    log_function_call(continuous_recording)

    is_recording = True # local is_recording variable
    while is_recording:
        try:
            # Start Recording. This will need to return each frame and append to the audio_buffer.
            logger.info("Starting recording...")
            file_handler.flush()
            logger.debug("Calling recording_module.record_frame")
            file_handler.flush()
            frame = recording_module.record_frame()
            logger.debug(f"Returned frame from recording_module.record_frame = {frame}")
            file_handler.flush()

            logger.debug(f"Appending frame to audio_buffer. audio_buffer.maxlen = {audio_buffer.maxlen}, audio_buffer.len = {len(audio_buffer)}")
            file_handler.flush()
            audio_buffer.append(frame)
            time.sleep(1 / FRAME_RATE)  # Sleep to control frame rate
        except Exception as e:
            logger.error(f"Error during continuous recording: {e}")
            file_handler.flush()
            error_handling_module.handle_exception(e, "main.py")
            file_handler.flush()

        # Ensure that the recording loop stops when the program is done
        if restart_recording:
            restart_recording = False
            logger.info("Restarting recording thread")
            file_handler.flush()
            break
    
    logger.info("Recording Thread Exiting.")
    file_handler.flush()
    start_recording_thread()
    log_function_return(continuous_recording, None)


def main():
    log_function_call(main)
    
    # Initialize hotkey listener
    logger.debug("Calling hotkey_module.register_hotkey")
    file_handler.flush()
    hotkey_module.register_hotkey(lambda: on_hotkey_press())  # Pass filepath to function

    # Start recording thread in a separate thread
    logger.debug("Calling start_recording_thread")
    file_handler.flush()
    start_recording_thread()
    file_handler.flush()

    try:
        # Keep the main thread alive, and the hotkeys running. It will be killed by `sys.exit()`
        while True:
            time.sleep(1)  # Let it sleep, since all other processing is done in other threads

    except KeyboardInterrupt:
        logger.info("Keyboard Interrupt Detected. Closing program")
        file_handler.flush()
    except Exception as e:
        logger.error(f"An unexpected error occurred in the main function: {e}")
        file_handler.flush()
        error_handling_module.handle_exception(e, "main.py")
        file_handler.flush()
    finally:
        logger.info("Closing program")
        file_handler.flush()
        log_function_return(main, None)
        file_handler.flush()
        sys.exit(0)  # Exit if all else fails


if __name__ == "__main__":
    log_function_call(main)
    main()
    log_function_return(main, None)
