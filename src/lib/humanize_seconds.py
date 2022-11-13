def humanize_seconds(secs: int):
    days = secs // 86400
    hours = (remaining := (secs - days * 86400)) // 3600
    minutes = (remaining := (remaining - hours * 3600)) // 60
    seconds = remaining - minutes * 60
    time_str = ''
    if days:
        time_str += f"{days}d" + ", " if seconds or minutes or hours else ""
    if hours:
        time_str += f"{hours}h" + ", " if seconds or minutes else ""
    if minutes:
        time_str += f"{minutes}m" + ", " if seconds else ""
    if seconds:
        time_str += f"{seconds}s"
    return time_str
