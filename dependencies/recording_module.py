import cv2
import numpy as np
import pyaudio
import wave
import time
import threading
from collections import deque
from datetime import datetime
import keyboard  # For detecting hotkeys
import mss  # For screen capture

class RollingVideoBuffer:
    def __init__(self, video_duration=30, audio_duration=30, frame_rate=30, audio_rate=44100):
        self.video_duration = video_duration  # in seconds
        self.audio_duration = audio_duration  # in seconds
        self.frame_rate = frame_rate
        self.audio_rate = audio_rate
        self.video_buffer = deque(maxlen=video_duration * frame_rate)  # buffer for frames
        self.audio_buffer = deque(maxlen=audio_duration * audio_rate)  # buffer for audio samples
        self.running = False
        #no more main monitor attribute
        self.audio_stream = None
        self.lock = threading.Lock()

    def start(self):
        self.running = True
        
        # Setup PyAudio for audio capture
        self.audio_stream = pyaudio.PyAudio()
        self.stream = self.audio_stream.open(format=pyaudio.paInt16,
                                             channels=1,
                                             rate=self.audio_rate,
                                             input=True,
                                             frames_per_buffer=1024)
        
        # Start video capture thread
        video_thread = threading.Thread(target=self._capture_video)
        video_thread.start()
        
        # Start audio capture thread
        audio_thread = threading.Thread(target=self._capture_audio)
        audio_thread.start()

    def _capture_video(self):
        # Create a new mss context for this thread
        monitor = mss.mss()

        while self.running:
             try:
                # Capture screen using mss
                screen_capture = monitor.grab(monitor.monitors[1])
                frame = np.array(screen_capture)
                frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2BGR)  # Convert RGBA to BGR

                # Store the frame in the video buffer
                with self.lock:
                    self.video_buffer.append(frame)

                # Sleep for the frame rate
                time.sleep(1 / self.frame_rate)
             except Exception as e:
                print(f"Error in _capture_video: {e}")
                break # or handle appropriately


        monitor.close() #Close mss context


    def _capture_audio(self):
        while self.running:
            audio_data = self.stream.read(1024)
            audio_samples = np.frombuffer(audio_data, dtype=np.int16)

            # Store the audio data in the audio buffer
            with self.lock:
                self.audio_buffer.append(audio_samples)

    def stop(self):
        self.running = False
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        if self.audio_stream:
            self.audio_stream.terminate()

    def dump_to_disk(self, video_filename=None, audio_filename=None):
        # Dump video buffer to disk
        if video_filename:
            with self.lock:
                if not self.video_buffer:  # Check if the buffer is empty
                    print("No video frames in the buffer to write.")
                    return
                
                # Get the dimensions from the first frame in the buffer
                first_frame = self.video_buffer[0]
                height, width, _ = first_frame.shape  # Correct unpacking for color frames
                
                # Choose a better codec and filename extension for wider compatibility
                fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # or 'avc1' for linux
                out_video = cv2.VideoWriter(video_filename, fourcc, self.frame_rate, (width, height))

                for frame in self.video_buffer:
                    out_video.write(frame)

                out_video.release()
        
        # Dump audio buffer to disk
        if audio_filename:
            with self.lock:
                audio_data = np.concatenate(list(self.audio_buffer))

            with wave.open(audio_filename, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)  # 16-bit samples
                wf.setframerate(self.audio_rate)
                wf.writeframes(audio_data.tobytes())

    def get_video_buffer(self):
        with self.lock:
            return list(self.video_buffer)

    def get_audio_buffer(self):
        with self.lock:
            return list(self.audio_buffer)

if __name__ == "__main__":
    buffer = RollingVideoBuffer()

    # Start capturing video and audio
    buffer.start()

    print("Press 'd' to dump buffers to disk...")

    # Run in a loop to listen for hotkey
    try:
        while True:
            time.sleep(0.1)  # Small sleep to avoid high CPU usage

            if keyboard.is_pressed('d'):  # Hotkey 'd' to dump buffers
                print(f"Dumping buffers at {datetime.now()}")
                buffer.dump_to_disk('screen_output.mp4', 'audio_output.wav')
                print("Buffers dumped to disk.")
                time.sleep(1)  # Prevent continuous dumping while holding down the key

    except KeyboardInterrupt:
        # Stop recording
        print("Stopping capture...")
        buffer.stop()
