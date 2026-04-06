"""
Centralized logging configuration.
"""

import contextlib
import logging
import os
import sys
from pathlib import Path

# Get the project root relative to this file's location
PROJECT_ROOT = Path(__file__).parent.parent.parent.absolute()
LOG_FILE = PROJECT_ROOT / "mcp_server.log"


def setup_logging(debug: bool = False):
    """Set up logging to both file and stderr."""
    level = logging.DEBUG if debug else logging.INFO

    # Create formatters and handlers
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # File handler (Append mode 'a' is critical for seeing history)
    file_handler = logging.FileHandler(LOG_FILE, mode='a', encoding='utf-8')
    file_handler.setFormatter(formatter)

    # Stream handler (logging to stderr is safe for MCP)
    stream_handler = logging.StreamHandler(sys.stderr)
    stream_handler.setFormatter(formatter)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Forcefully clear existing handlers to ensure our configuration takes precedence
    if root_logger.handlers:
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

    root_logger.addHandler(file_handler)
    root_logger.addHandler(stream_handler)

    # Ensure everything is flushed immediately during setup
    for handler in root_logger.handlers:
        handler.flush()

    logging.info("--- MCP Server Session Started ---")
