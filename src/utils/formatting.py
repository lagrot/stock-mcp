"""
Formatting utilities for timestamps and data.
"""

import datetime
from typing import Any


def format_timestamp(ts: Any) -> str | None:
    """Safely convert various timestamp formats to ISO string (preferring UTC)."""
    if not ts:
        return None
    try:
        if isinstance(ts, (int, float)):
            return datetime.datetime.fromtimestamp(ts, tz=datetime.timezone.utc).isoformat()
        
        if hasattr(ts, "isoformat"):
            # If it's a pandas/datetime object, ensure it's aware or handle consistently
            if hasattr(ts, "tzinfo") and ts.tzinfo:
                return ts.astimezone(datetime.timezone.utc).isoformat()
            return ts.isoformat()
    except Exception:
        pass
    return str(ts)
