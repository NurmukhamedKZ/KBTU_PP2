# Boolean Introduction in Python
# Booleans represent one of two values: True or False

# Example 1: Basic boolean values
print(True)   # Output: True
print(False)  # Output: False

# Example 2: Boolean type
print(type(True))   # Output: <class 'bool'>
print(type(False))  # Output: <class 'bool'>

# Example 3: Evaluating expressions to boolean
print(10 > 9)   # Output: True
print(10 == 9)  # Output: False
print(10 < 9)   # Output: False

# Example 4: Using bool() function to evaluate values
# Most values are True
print(bool("Hello"))  # Output: True (non-empty string)
print(bool(15))       # Output: True (non-zero number)
print(bool(["apple", "cherry", "banana"]))  # Output: True (non-empty list)

# Example 5: Values that evaluate to False
print(bool(False))    # Output: False
print(bool(None))     # Output: False
print(bool(0))        # Output: False
print(bool(""))       # Output: False (empty string)
print(bool(()))       # Output: False (empty tuple)
print(bool([]))       # Output: False (empty list)
print(bool({}))       # Output: False (empty dictionary)
