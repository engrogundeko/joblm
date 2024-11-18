# app_logger.py
import logging
from logging.handlers import RotatingFileHandler
import os

# Get the name of the script being run dynamically
script_name = os.path.splitext(os.path.basename(__file__))[0]

# Create the main logger
logger = logging.getLogger(script_name)
logger.setLevel(logging.DEBUG)  # Capture all log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)

# Format for log messages
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

# WARNING level handler (will log warnings and higher to a file)
# warning_handler = RotatingFileHandler(f"{script_name}_warning.log", maxBytes=5 * 1024 * 1024, backupCount=3)
# warning_handler.setLevel(logging.WARNING)
# warning_handler.setFormatter(formatter)

# ERROR level handler (will log errors and higher to a file)
error_handler = RotatingFileHandler(f"{script_name}_error.log", maxBytes=5 * 1024 * 1024, backupCount=3)
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(formatter)

# Console handler for real-time output (set to DEBUG or any desired level)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(formatter)

# Add handlers to the logger
# logger.addHandler(warning_handler)  # Only warning and higher will be written to the file
logger.addHandler(error_handler)    # Only error and higher will be written to the file
logger.addHandler(console_handler)  # Console output for all levels (DEBUG, INFO, etc.)
