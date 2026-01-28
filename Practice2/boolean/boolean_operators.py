# Boolean Operators in Python
# Python has three boolean operators: and, or, not

# ===== AND Operator =====
# Returns True if both statements are true
print("=== AND Operator ===")
x = 5
print(x > 3 and x < 10)   # True - both conditions are true
print(x > 3 and x < 4)    # False - second condition is false

# Example with variables
a = True
b = True
c = False
print(a and b)    # True
print(a and c)    # False
print(c and c)    # False

# ===== OR Operator =====
# Returns True if at least one statement is true
print("\n=== OR Operator ===")
print(x > 3 or x < 4)     # True - first condition is true
print(x < 3 or x > 10)    # False - both conditions are false

# Example with variables
print(a or c)     # True - at least one is true
print(c or c)     # False - both are false

# ===== NOT Operator =====
# Reverses the result, returns False if the result is true
print("\n=== NOT Operator ===")
print(not True)           # False
print(not False)          # True
print(not(x > 3 and x < 10))  # False - negates True

# Example: Check if value is NOT in a range
y = 15
print(not(5 < y < 10))    # True - y is NOT in range 5-10

# ===== Combining Operators =====
print("\n=== Combined Operators ===")
# Using multiple operators together
age = 25
has_license = True
has_car = False

# Check if person can drive
can_drive = age >= 18 and has_license
print(f"Can drive: {can_drive}")  # True

# Check if person can go on road trip
can_roadtrip = can_drive and has_car
print(f"Can go on road trip: {can_roadtrip}")  # False

# Check if person needs transportation
needs_transport = not has_car or age < 18
print(f"Needs transportation: {needs_transport}")  # True
