# media_converter.py
import logging
from dependencies import recording_module

logger = logging.getLogger(__name__)

def convert_to_mp4(buffer):
    """
    Converts the rolling buffer of audio and video frames to an MP4 file.

    Args:
        buffer (deque): A deque of (audio_frame, video_frame) tuples

    Returns:
        str: The file path to the created MP4 file, or None on failure
    """
    try:
        logger.debug("Calling recording_module.convert_rolling_buffer with buffer")
        file_path = recording_module.convert_rolling_buffer(buffer)
        logger.debug(f"Returned file_path = {file_path}")
        return file_path
    except Exception as e:
         logger.error(f"Error converting to MP4: {e}")
         return None

if __name__ == '__main__':
    # Example Usage (this won't work without setting up recording_module to return a deque)
    # and a way to import deque, and the rest of the dependencies
    # Also, recording_module.convert_rolling_buffer can not return None
    class FakeBuffer:
         def __init__(self):
            self.buffer = []
            
         def __getitem__(self, index):
            return self.buffer[index]

         def __len__(self):
            return len(self.buffer)

    fake_buffer = FakeBuffer()
    fake_buffer.buffer = [("audio1","video1"),("audio2","video2")] 
    output_path = convert_to_mp4(fake_buffer)
    if output_path:
        print(f"MP4 file created at: {output_path}")
    else:
        print("MP4 conversion failed")
