"""
Formatting utilities for timestamps and data.
"""

import datetime
from typing import Any


def format_timestamp(ts: Any) -> str | None:
    """Safely convert various timestamp formats to ISO string (preferring UTC)."""
    if ts is None:
        return None
    try:
        if isinstance(ts, (int, float)):
            return datetime.datetime.fromtimestamp(ts, tz=datetime.timezone.utc).isoformat()

        if hasattr(ts, "isoformat"):
            if hasattr(ts, "tzinfo") and ts.tzinfo:
                return str(ts.astimezone(datetime.timezone.utc).isoformat())
            return str(ts.isoformat())
    except Exception:
        pass
    return str(ts)
