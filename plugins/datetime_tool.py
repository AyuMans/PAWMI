from datetime import datetime
from zoneinfo import ZoneInfo
def get_datetime():
    now = datetime.now(ZoneInfo("Asia/Kolkata"))
    return {
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M:%S"),
        "day": now.strftime("%A"),
        "timezone": "IST" 
        }