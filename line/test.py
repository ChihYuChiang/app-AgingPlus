from datetime import datetime, timezone, timedelta

#Expect timestamp in seconds instead of milliseconds
timestamp = round(1571575495842 / 1000)

#Convert to GMT+8 time
datetimeStr = datetime.fromtimestamp(timestamp, tz=timezone(timedelta(hours=8)))

print(datetimeStr)