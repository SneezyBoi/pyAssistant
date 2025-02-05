import sounddevice as sd
import soundfile as sf
import os
import time
import datetime
import logging
import threading
import keyboard  # pip install keyboard
import numpy as np


# Configuration
SAMPLE_RATE = 44100
CHUNK_DURATION = 5  # seconds
NUM_CHUNKS_TO_KEEP = 5
RECORD_DIR = "aMRec"
LOG_DIR = "amLog"
HOTKEY = 'ctrl+shift+space'

# Global variables
recording_active = True  # controls the recording thread
audio_data_chunks = []   # Stores the raw audio data of recent chunks
chunk_index = 0
device_index = None

def setup_logging():
    """Sets up the logging system."""
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
    log_filename = os.path.join(LOG_DIR, f"recording_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
    logging.basicConfig(filename=log_filename, level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')
    logging.info("Logging initialized.")

def get_audio_devices():
    """Retrieves available audio input devices."""
    try:
        devices = sd.query_devices()
        input_devices = [d for d in devices if d['max_input_channels'] > 0]
        logging.info(f"Available input devices: {input_devices}")
        return input_devices
    except Exception as e:
        logging.error(f"Error getting audio devices: {e}")
        return None

def select_input_device():
    """Prompts the user to select an audio input device."""
    devices = get_audio_devices()
    if not devices:
        return None
    print("Available Audio Input Devices:")
    for i, device in enumerate(devices):
        print(f"{i + 1}. {device['name']}")
    try:
        choice = int(input("Select an input device (number): ")) - 1
        if 0 <= choice < len(devices):
            logging.info(f"User selected device: {devices[choice]['name']}")
            return devices[choice]['index']
        else:
            logging.warning("Invalid device selection.")
            return None
    except ValueError:
        logging.warning("Invalid input (not a number).")
        return None

def record_audio_chunk(device_index):
    """Records audio for a single chunk."""
    logging.info(f"Recording audio chunk for {CHUNK_DURATION} seconds.")
    try:
        audio_data = sd.rec(int(SAMPLE_RATE * CHUNK_DURATION), samplerate=SAMPLE_RATE, channels=1, dtype='int16', device=device_index)
        sd.wait()  # Wait until recording is finished
        logging.info("Finished recording audio chunk.")
        return audio_data
    except Exception as e:
        logging.error(f"Error during recording: {e}")
        return None

def combine_audio_chunks(audio_data_chunks, output_filename):
    """Combines multiple audio chunks into a single file."""
    if not audio_data_chunks:
         logging.warning("No audio to combine.")
         return False
    try:
        # concatenate all the audio data
        combined_data = np.concatenate(audio_data_chunks, axis=0)
        sf.write(output_filename, combined_data, SAMPLE_RATE)
        logging.info(f"Combined audio saved to: {output_filename}")
        return True
    except Exception as e:
         logging.error(f"Error combining audio chunks: {e}")
         return False


def recording_thread():
    """Thread that continuously records audio chunks."""
    global recording_active, audio_data_chunks, chunk_index, device_index
    while recording_active:
        audio_data = record_audio_chunk(device_index)
        if audio_data is not None:
            audio_data_chunks.append(audio_data)
            if len(audio_data_chunks) > NUM_CHUNKS_TO_KEEP:
                 audio_data_chunks.pop(0)  # remove the oldest

            chunk_index += 1



def hotkey_callback():
    """Callback function for the hotkey."""
    global recording_active, audio_data_chunks
    logging.info("Hotkey pressed: combining audio chunks")
    recording_active = False  # Stop the recording thread
    time.sleep(0.5) # allow the recording thread to stop

    output_filename = os.path.join(RECORD_DIR, f"combined_audio_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.wav")
    combine_audio_chunks(audio_data_chunks, output_filename)

    audio_data_chunks = [] #clear the stored chunk files

    recording_active = True  # Restart the recording thread
    start_recording_thread()


def start_recording_thread():
     """Starts the recording thread"""
     global recording_active
     recording_active = True
     thread = threading.Thread(target=recording_thread)
     thread.daemon = True  # Allow the main thread to exit without waiting
     thread.start()


def main():
    """Main function to control the audio recording process."""
    setup_logging()
    if not os.path.exists(RECORD_DIR):
        os.makedirs(RECORD_DIR)
    
    global recording_active, device_index
    device_index = select_input_device()
    if device_index is None:
        logging.error("No input device selected. Exiting.")
        return

    start_recording_thread()

    keyboard.add_hotkey(HOTKEY, hotkey_callback)
    logging.info(f"Listening for hotkey: {HOTKEY}")
    try:
        keyboard.wait()  # Keep the main thread alive until we receive a hotkey combo.
    except KeyboardInterrupt:
        logging.info("Program interrupted by user.  Stopping recording.")
        recording_active = False

    logging.info("Program finished.")


if __name__ == "__main__":
    main()
