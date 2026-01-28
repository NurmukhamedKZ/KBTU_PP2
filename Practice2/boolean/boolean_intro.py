# Boolean Values in Python
# Booleans represent one of two values: True or False

# Example 1: Basic boolean values
print(True)   # Output: True
print(False)  # Output: False

# Example 2: Evaluating expressions to boolean
print(10 > 9)   # True - 10 is greater than 9
print(10 == 9)  # False - 10 is not equal to 9
print(10 < 9)   # False - 10 is not less than 9

# Example 3: Using boolean in if statement
a = 200
b = 33

if b > a:
    print("b is greater than a")
else:
    print("b is not greater than a")  # This will be printed

# Example 4: The bool() function
# The bool() function evaluates any value and returns True or False

# Most values are True
print(bool("Hello"))  # True - non-empty string
print(bool(15))       # True - non-zero number
print(bool(["apple", "cherry", "banana"]))  # True - non-empty list

# Example 5: Values that evaluate to False
print(bool(False))    # False
print(bool(None))     # False
print(bool(0))        # False
print(bool(""))       # False - empty string
print(bool(()))       # False - empty tuple
print(bool([]))       # False - empty list
print(bool({}))       # False - empty dictionary
