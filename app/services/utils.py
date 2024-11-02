from datetime import datetime, timezone


def get_datetime():
    dt = datetime.now(timezone.utc)
    print(dt)
    return dt