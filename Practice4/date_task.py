import datetime

# Task 1
x = datetime.datetime.now()
z = x - datetime.timedelta(days=5)
print("5 days ago: ", z)


# Task 2
x = datetime.datetime.now()
print("Yesterday: ", datetime.date(x.year, x.month, x.day-1))
print("Today: ", datetime.date(x.year, x.month, x.day))
print("Tomorrow: ", datetime.date(x.year, x.month, x.day+1))


# Task 3
x = datetime.datetime.now()
x = x.replace(microsecond=0)
print("Current microsecond: ", x.microsecond)


# Task 4
x = datetime.datetime(2026, 7, 2, 12, 30, 5)
z = datetime.datetime(2010, 9, 1, 12, 0, 0)
time_difference = x - z
print("Time difference: ", time_difference)
print("Time difference in days: ", time_difference.days)
print("Time difference in seconds: ", time_difference.seconds)
print("Full time difference: ", time_difference.total_seconds())