# tts_module.py
import pyttsx3
import logging

logger = logging.getLogger(__name__)

engine = None # Global engine variable

def initialize_tts():
    """Initializes the text-to-speech engine. This is to avoid initializing
        each time, and should only run once, on program start.
    """
    global engine
    try:
        if engine is None:
            logger.debug("Initializing TTS Engine")
            engine = pyttsx3.init()
            logger.info("TTS engine initialized.")
    except Exception as e:
        logger.error(f"Error initializing TTS engine: {e}")

def read_text(text):
    """
    Reads the given text aloud using the text-to-speech engine.

    Args:
        text (str): The text to be read aloud.
    """
    global engine
    try:
        if engine is None:
            initialize_tts() # Always try to initialize first.
        if engine is None:
            logger.error("TTS engine is not initialized! Can not read text.")
            return

        logger.debug(f"Reading text: {text}")
        engine.say(text)
        engine.runAndWait()
        logger.info("Text read successfully.")
    except Exception as e:
        logger.error(f"Error reading text with TTS: {e}")

if __name__ == '__main__':
    initialize_tts()
    read_text("This is a test of the text to speech module.")
    read_text("Another example is to read multiple lines of text. If that is all, then I will stop talking.")
