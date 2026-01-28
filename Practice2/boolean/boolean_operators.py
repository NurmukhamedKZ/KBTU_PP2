# Boolean Operators in Python
# Python has three logical operators: and, or, not

# Example 1: 'and' operator
# Returns True if both statements are true
x = 5
print(x > 3 and x < 10)  # Output: True (both conditions are true)
print(x > 3 and x > 10)  # Output: False (second condition is false)

# Example 2: 'or' operator
# Returns True if at least one statement is true
print(x > 3 or x < 4)   # Output: True (first condition is true)
print(x < 3 or x > 10)  # Output: False (both conditions are false)

# Example 3: 'not' operator
# Reverses the result, returns False if the result is true
print(not(x > 3 and x < 10))  # Output: False (negates True)
print(not(x > 10))            # Output: True (negates False)

# Example 4: Combining operators
a = True
b = False
c = True

print(a and b)          # Output: False
print(a or b)           # Output: True
print(not a)            # Output: False
print(a and b or c)     # Output: True (and has higher precedence than or)
print(a and (b or c))   # Output: True

# Example 5: Practical example with boolean operators
age = 25
has_license = True
is_sober = True

# Check if person can drive
can_drive = age >= 18 and has_license and is_sober
print(f"Can drive: {can_drive}")  # Output: Can drive: True

# Check if person is eligible for discount (either senior or student)
is_senior = False
is_student = True
gets_discount = is_senior or is_student
print(f"Gets discount: {gets_discount}")  # Output: Gets discount: True
