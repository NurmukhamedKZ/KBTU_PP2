
# import math
# from datetime import datetime, timezone, timedelta
# import calendar

# def parse_dt(line):
#     line = line.strip()
#     parts = line.split(" ")
#     date_part, time_part, tz_part = parts[:2] + [parts[2].replace("UTC", "")]
#     sign = 1 if tz_part[0] == '+' else -1
#     hh, mm = map(int, tz_part[1:].split(':'))
#     offset = timezone(timedelta(hours=sign*hh, minutes=sign*mm))
#     dt = datetime.strptime(date_part + " " + time_part, '%Y-%m-%d %H:%M:%S').replace(tzinfo=offset)
#     return dt

# start_date = parse_dt(input())
# end_date = parse_dt(input())

# difference = (end_date - start_date).total_seconds()

# print(int(difference))



import math

def solve():
    x1, y1 = map(float, input().split())
    x2, y2 = map(float, input().split())

    A = y2**2-y1**2
    B = 2 * x2 * y1**2 - 2 * x1 * y2**2
    C = x1**2*y2**2 - x2**2*y1**2

    discriminant = B**2 - 4*A*C

    if A == 0:
        x = -C / B
        return x
    else:
        new_x1 = (-B + math.sqrt(discriminant)) / (2*A)
        new_x2 = (-B - math.sqrt(discriminant)) / (2*A)

        if x1 <= new_x1 <= x2:
            return new_x1
        elif x1 <= new_x2 <= x2:
            return new_x2
        if x2 <= new_x1 <= x1:
            return new_x1
        elif x2 <= new_x2 <= x1:
            return new_x2

# Print the result formatted to 10 decimal places as requested
x = solve()
# Avoid -0.0 so output matches expected "0.0000000000" (size 26)
if x == 0:
    x = 0.0
print(f"{x:.10f} {0:.10f}")