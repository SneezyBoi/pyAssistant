import logging
import google.generativeai as genai
import os
from dependencies import config_module  # Import config_module to load API key


logger = logging.getLogger(__name__)


def generate_text(prompt, video_filepath):
    """
    Sends a prompt and video to the Gemini API and returns the response.

    Args:
        prompt (str): The prompt for the Gemini API.
        video_filepath (str): The filepath to the video being used

    Returns:
        str: The response from the Gemini API, or None on error.
    """
    try:
        logger.info(f"Attempting to process the video at {video_filepath} with prompt: {prompt}")

        # Load the config so we get the API key
        config = config_module.load_config()
        api_key = config["gemini_api_key"]
        gemini_model = config["gemini_model"]

        if not api_key:
            raise ValueError("No API key was found in the config file.")

        genai.configure(api_key=api_key)  # Initialize the Gemini API with the API key.
        model = genai.GenerativeModel(
            gemini_model
        )  # Get Gemini model, uses gemini-pro-vision if not specified in config

        # Check if the video file exists
        if not os.path.exists(video_filepath):
            raise FileNotFoundError(f"Video file not found at: {video_filepath}")

        # Read the video file
        with open(video_filepath, "rb") as video_file:
            video_data = video_file.read()

        # Generate Content
        response = model.generate_content(
            [
                prompt,
                {"mime_type": "video/mp4", "data": video_data},
            ]  # pass video data and mime type
        )

        if response.text:
            logger.info(f"Gemini API returned a response.")
            return response.text
        else:
            logger.error("Gemini API returned an empty response.")
            return None
    except Exception as e:
        logger.error(f"Error generating text from Gemini API: {e}")
        return None
