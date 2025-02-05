import sounddevice as sd
from moviepy.editor import *
import numpy as np
import logging
import sys
import threading
import time
from moviepy.audio.AudioClip import AudioClip
import moviepy.audio.tools.cuts as cuts
import cv2  # Import OpenCV
import mss  # Import MSS for screen capture
import mss.tools # Needed to use the to_png method

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Recording Parameters
sample_rate = 44100  # Hz
channels = 2  # Stereo
recording_duration = 4  # Seconds (changed to 4)
frame_rate = 30  # Frames per second

# Global variable to store the selected input device
global selected_input_device
selected_input_device = None


class AudioArrayClip(AudioClip):
    """
    A custom Audio Clip that can read raw audio data from a Numpy array.
    """
    def __init__(self, arr, fps):
        """
        Args:
            arr (np.ndarray): Raw audio data of shape (n_frames, n_channels).
            fps (int): Number of frames per second.
        """
        if len(arr.shape) != 2:
            raise ValueError(f"Audio array must have 2 dimensions (n_frames, n_channels), but has {len(arr.shape)} dimensions.")
        if arr.shape[1] <= 0:
            raise ValueError(f"Number of channels must be greater than 0, but it was {arr.shape[1]}")
        
        self.arr = arr
        self.fps = fps
        duration = len(self.arr) / fps

        AudioClip.__init__(self) # Call parent __init__ method.
        self.duration = duration # Set duration.
        self.nchannels = arr.shape[1] # Set number of channels.

    def make_frame(self, t):
        """
        Returns the frame corresponding to time t (in seconds).
        """
        if isinstance(t, np.ndarray):
            frame = []
            for time_val in t:
                time_val = float(time_val)  # Ensure time_val is treated as a single float
                if time_val > self.duration or time_val < 0:
                    frame_val = np.zeros(self.nchannels).tolist() # Return silence
                else:
                    i = int(time_val * self.fps)
                    frame_val = self.arr[i].tolist()
                frame.append(frame_val)
            return frame
        else:
            t = float(t)  # Ensure 't' is treated as a single float
            if t > self.duration or t < 0:
                return np.zeros(self.nchannels).tolist() # Return silence
            else:
                i = int(t * self.fps)
                return self.arr[i].tolist()


def get_available_devices():
    """
    Returns a list of available audio input devices.
    """
    try:
         devices = sd.query_devices()
         input_devices = [device for device in devices if device['max_input_channels'] > 0]
         return input_devices
    except Exception as e:
          logger.error(f"Error getting available devices: {e}")
          return None


def choose_input_device():
    """
    Allows the user to choose an input device by printing the list of available devices
    and having them choose a number.
    """
    devices = get_available_devices()
    if devices is None:
         return None

    print("Available input devices:")
    for i, device in enumerate(devices):
        print(f"{i}: {device['name']}")

    while True:
          try:
             choice = int(input("Please choose an input device by entering a number: "))
             if 0 <= choice < len(devices):
                 return devices[choice]
             else:
                 print("Invalid choice. Please choose a number within the range.")
          except ValueError:
                 print("Invalid input. Please enter a number.")


def initialize_input_device():
    """
    Initializes the selected audio input device once at the start.
    """
    global selected_input_device
    if selected_input_device is None:
        selected_input_device = choose_input_device()
        if selected_input_device is None:
            logger.error("No input device selected during initialization. Aborting.")
            return False
        logger.info(f"Input device selected: {selected_input_device['name']}")
    return True


def record_frame():
    """
    Records a single frame of audio and video (from screen).

    Returns:
        tuple: A tuple containing (audio_frame, video_frame)
    """
    try:
        global selected_input_device

        if not initialize_input_device():
            return None

        # Record Audio Frame
        audio_frame = sd.rec(int(sample_rate / frame_rate), samplerate=sample_rate, channels=channels, device=selected_input_device['index'])
        sd.wait()  # Wait for the audio recording to finish

        # --- Screen Capture using MSS ---
        with mss.mss() as sct:
           monitor_number = 1 # Monitor 1
           mon = sct.monitors[monitor_number] # Get information about the monitor we want to capture

            # Get a screenshot of the specified monitor
           sct_img = sct.grab(mon)
           
           # Convert the raw pixels to an image to numpy array with cv2
           video_frame = np.array(sct_img)
           video_frame = cv2.cvtColor(video_frame, cv2.COLOR_RGBA2BGR) # Convert to BGR
        # --- End of Screen Capture ---

        return (audio_frame, video_frame)
    except Exception as e:
        logger.error(f"Error recording frame: {e}")
        return None


def convert_rolling_buffer(buffer):
    """
    Converts the rolling buffer of audio and video frames to a video file.

    Args:
        buffer (deque): A deque of (audio_frame, video_frame) tuples

    Returns:
        str: The file path to the created video file
    """
    try:
        if not buffer:
            raise ValueError("Rolling buffer is empty. Cannot convert to video.")
        
        buffer = buffer.copy() # copy the buffer so we do not mutate during iteration

        output_filename = "temp_rolling_buffer.mp4"  # Set file path
        first_frame = buffer[0]
        video_frame = first_frame[1]
        height, width, _ = video_frame.shape

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Define codec
        out = cv2.VideoWriter(output_filename, fourcc, frame_rate, (width, height))  # Create writer

        all_audio = []
        # Write video and save audio
        for frame_pair in buffer:
            audio_frame, video_frame = frame_pair
            if video_frame is not None:
                out.write(video_frame)
            if audio_frame is not None:
                all_audio.append(audio_frame)
        out.release()  # Release writer

        # Ensure audio is not empty
        if not all_audio:
            raise ValueError("Audio buffer is empty. Cannot add to video file.")
        audio = np.concatenate(all_audio, axis=0)  # Combine audio frames

        # Save audio to an audio clip, and then to the video file
        audio_clip = AudioArrayClip(audio, fps=sample_rate)
        video_clip = VideoFileClip(output_filename)
        video_clip = video_clip.set_audio(audio_clip)
        video_clip.write_videofile(output_filename, codec='libx264', audio_codec='aac')  # Writes to the output file.

        return output_filename
    except Exception as e:
        logger.error(f"Error converting rolling buffer to video: {e}")
        return None
