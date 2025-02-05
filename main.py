# main.py
import logging
import time
import sys
import os
import threading
from collections import deque
from dependencies import hotkey_module, tts_module, media_converter, gemini_api_module, recording_module, error_handling_module, config_module
import signal

# --- Logging Setup ---
LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "app.log")

# Create the log directory if it doesn't exist
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE), # Add this handler, so output gets sent to file
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)
# --- End of Logging Setup ---

# Global variables
#rolling_buffer = deque(maxlen=10) # 10 frames should be about 1/3 of a second of recording, at 30fps # REMOVE
is_recording = True
exit_event = threading.Event() # Used to signal threads that program should end.
recording_module_instance = None # REMOVE


def main():
    """Main function to run the video and audio processing."""
    global is_recording
    global recording_module_instance
    try:
       logger.info("Starting the application.")

        # Load Configuration
       config = config_module.load_config()
       logger.info(f"Configuration loaded: {config}")

        # Initialize TTS engine
       tts_module.initialize_tts()

        # Configure the hotkey
       hotkey_module.register_hotkey(process_recording, hotkey_combination = config["hotkey"]) # register hotkey
       hotkey_module.start_listening_thread() # Start listening for the hotkey in the background.

        # Start recording module
       recording_module_instance = recording_module.RecordingModule()
       recording_module_instance.start_recording() # Starts recording in the background thread

        # Set up signal handlers
       signal.signal(signal.SIGINT, signal_handler)  # Handle Ctrl+C
       signal.signal(signal.SIGTERM, signal_handler) # Handle kill command

       logger.info("Main thread is now waiting...")
       while not exit_event.is_set():
             time.sleep(1)
    except Exception as e:
        error_handling_module.handle_exception(e, "main.py")
    finally:
        is_recording = False # Signal that the recording should end.
        logger.info("Application finished.")
        # save_buffer_on_exit() # Save the buffer, if any. REMOVE - buffer no longer in use


# def record_loop(): # REMOVE
#     """Records video and audio and puts them into a rolling buffer."""
#     global rolling_buffer
#     global is_recording
#     logger.info("Starting record loop on its own thread.")
#     try:
#         while is_recording and not exit_event.is_set():
#             for _ in range(int(recording_module.frame_rate * recording_module.recording_duration)): # Loop for the total duration
#                 frame_pair = recording_module.record_frame()
#                 if frame_pair:
#                     rolling_buffer.append(frame_pair)
#                 # time.sleep(1/recording_module.frame_rate) # REMOVE SLEEP STATEMENT

#     except Exception as e:
#         error_handling_module.handle_exception(e, "main.py")
#     finally:
#         logger.info("Record loop finished.")


def process_recording():
    """Processes the recorded audio and video when the hotkey is triggered."""
    try:
        logger.info("Hotkey triggered. Processing recording...")
        global recording_module_instance
        config = config_module.load_config()

        # Get List of video files from recording module
        segment_list = recording_module_instance.stop_recording_and_get_files()

        if not segment_list:
             logger.error("Failed to get video segments from the recording module. Cannot send to Gemini API.")
             return
        # Convert the video files
        video_filepath = media_converter.combine_videos(segment_list)
        if not video_filepath:
            logger.error("Failed to combine videos. Cannot send to Gemini API.")
            return
        
        # Get AI String response from Gemini API
        prompt = "Please summarize the contents of this video." # TODO Make prompt configurable in config.json
        response = gemini_api_module.generate_text(prompt, video_filepath)

        if response:
           # Read AI response to user with TTS
           tts_module.read_text(response)
        else:
            logger.error("Gemini API failed to return a response.")
        
        # Restart Recording module after the request
        recording_module_instance.start_recording()


    except Exception as e:
        error_handling_module.handle_exception(e, "main.py")


def signal_handler(sig, frame):
    """Handles signals (e.g., Ctrl+C) to exit the program gracefully."""
    logger.info(f"Signal {sig} received. Exiting...")
    exit_event.set() # Set the exit signal for all threads to recognize.


# def save_buffer_on_exit(): # REMOVE
#      """Saves the buffer on exit, only if it contains something."""
#      global rolling_buffer
#      if rolling_buffer:
#          logger.info("Saving rolling buffer to video file.")
#          video_filepath = media_converter.convert_to_mp4(rolling_buffer)
#          if video_filepath:
#              logger.info(f"Video saved to: {video_filepath}")
#          else:
#              logger.error("Failed to save video on exit.")
#      else:
#         logger.info("Rolling buffer empty, not saving.")


if __name__ == '__main__':
    main()
