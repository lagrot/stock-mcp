"""
Centralized logging configuration.
"""

import logging
import sys
from pathlib import Path

# Get the project root relative to this file's location
PROJECT_ROOT = Path(__file__).parent.parent.parent.absolute()
LOG_FILE = PROJECT_ROOT / "mcp_server.log"


def setup_logging(debug: bool = False):
    """Set up logging to stderr exclusively for journald/systemd capture."""
    level = logging.DEBUG if debug else logging.INFO

    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stderr)],
        force=True,
    )

    # Silence extremely noisy libraries
    logging.getLogger("yfinance").setLevel(logging.INFO)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("mcp").setLevel(logging.INFO)
    logging.getLogger("asyncio").setLevel(logging.WARNING)

    logging.info("--- mcp-yahoo-stock: Session Started ---")
