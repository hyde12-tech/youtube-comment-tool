from datetime import datetime, timezone, timedelta

JST = timezone(timedelta(hours=9))


def utc_to_jst(utc_str: str) -> str:
    dt = datetime.fromisoformat(utc_str.replace('Z', '+00:00'))
    return dt.astimezone(JST).strftime('%Y-%m-%d %H:%M:%S')
