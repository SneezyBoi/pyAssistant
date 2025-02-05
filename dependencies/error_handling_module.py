# error_handling_module.py
import logging

logger = logging.getLogger(__name__)

def handle_exception(exception, source):
    """
    Logs an exception with additional context.
    
    Args:
        exception (Exception): The exception that occurred.
        source (str): A string representing the source of the exception (e.g. "main.py", "recording_module.py").
    """
    logger.error(f"Exception in {source}: {exception}")
    # You can add more advanced error handling logic here, such as reporting errors to a service
    # or saving stack traces.
