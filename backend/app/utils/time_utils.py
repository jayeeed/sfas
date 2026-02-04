"""
Time and date utilities.
"""
from datetime import date, datetime, timezone, timedelta

def get_current_time_bd() -> datetime:
    """Get current datetime in Bangladesh Time (UTC+6)."""
    return datetime.now(timezone(timedelta(hours=6)))

def utc_now() -> datetime:
    """Get current UTC datetime."""
    return datetime.now(timezone.utc)


def today() -> date:
    """Get current date."""
    return date.today()


def format_datetime(dt: datetime | None) -> str | None:
    """Format datetime to ISO string."""
    if dt is None:
        return None
    return dt.isoformat()


def format_date(d: date | None) -> str | None:
    """Format date to ISO string."""
    if d is None:
        return None
    return d.isoformat()


def parse_date(date_str: str) -> date:
    """Parse date from ISO string."""
    return date.fromisoformat(date_str)


def parse_datetime(dt_str: str) -> datetime:
    """Parse datetime from ISO string."""
    return datetime.fromisoformat(dt_str)
