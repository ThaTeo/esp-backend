def as_hours(timestamp):
    return int(timestamp/3600) * 3600

def as_days(timestamp):
    return int(timestamp/(3600*24)) * (3600*24)
