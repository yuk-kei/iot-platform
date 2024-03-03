from dateutil.parser import parse
from datetime import datetime, timedelta, timezone


def parse_time_input(time_str):
    """
    Parses a time string which could be in relative format (e.g., "-5h", "-10s")
    or an absolute ISO format. Returns a naive datetime object in UTC.
    """
    if time_str.startswith("-"):
        # It's a relative time format
        unit = time_str[-1]  # 'h' for hours or 's' for seconds
        value = int(time_str[1:-1])  # Extract the numeric part

        if unit == 'h':
            delta = timedelta(hours=value)
        elif unit == 's':
            delta = timedelta(seconds=value)
        else:
            raise ValueError("Unsupported time unit. Only 'h' (hours) and 's' (seconds) are supported.")

        # Subtract the delta from the current UTC time
        return datetime.utcnow() - delta
    else:
        # It's an absolute ISO format time
        result_time = datetime.fromisoformat(time_str)
        # If the datetime object is timezone-aware, convert it to UTC and make it naive
        if result_time.tzinfo is not None:
            result_time = result_time.astimezone(timezone.utc).replace(tzinfo=None)
        return result_time


def time_or_time_delta(curr_time_str):
    """
    The time_or_time_delta function takes in a string and returns either the time delta or the time.
        If it is a timedelta, then it will return that value.
        If it is not, then we assume that this is an absolute timestamp and convert to seconds since epoch.

    :param curr_time_str: Pass in the current time string
    :return: A datetime object
    :doc-author: Yukkei
    """
    if len(curr_time_str) == 1:
        return "Invalid time format"
    if curr_time_str[-1] == 'd':
        return curr_time_str
    elif curr_time_str[-1] == 'h':
        return curr_time_str
    elif curr_time_str[-1] == 'm':
        return curr_time_str
    elif curr_time_str[-1] == 's':
        return curr_time_str

    try:
        target_time = parse(curr_time_str)

        target_time_seconds = int(target_time.timestamp())
        return target_time_seconds

    except ValueError:
        print(f"Error: unable to parse time string {curr_time_str}")