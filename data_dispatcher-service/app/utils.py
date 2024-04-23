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
        elif unit == 'm':
            delta = timedelta(minutes=value)
        elif unit == 's':
            delta = timedelta(seconds=value)
        elif unit == 'd':
            delta = timedelta(days=value)
        else:
            raise ValueError("Unsupported time unit. Only 'd', 'h', 'm', and 's' are supported.")

        # Subtract the delta from the current UTC time
        return datetime.now(timezone.utc) - delta
    else:
        # It's an absolute ISO format time
        result_time = parse(time_str)
        # result_time = datetime.fromisoformat(time_str)
        # # If the datetime object is timezone-aware, convert it to UTC and make it naive
        # if result_time.tzinfo is None:
        #     result_time = result_time.replace(tzinfo=timezone.utc)
        return result_time.astimezone(timezone.utc)


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

if __name__ == "__main__":

    print(datetime.utcnow())
    print(datetime.now())
    print(parse_time_input("-10h"))
    print(parse_time_input("2024-03-04T22:24:41.010Z"))