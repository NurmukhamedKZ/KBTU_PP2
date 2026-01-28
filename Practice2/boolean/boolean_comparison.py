# Boolean as Comparison Results
# Comparisons return boolean values

# Example 1: Comparing numbers
a = 10
b = 20

print(a > b)   # Output: False (10 is not greater than 20)
print(a < b)   # Output: True (10 is less than 20)
print(a == b)  # Output: False (10 is not equal to 20)
print(a != b)  # Output: True (10 is not equal to 20)

# Example 2: Comparing strings
x = "apple"
y = "banana"

print(x == y)  # Output: False
print(x != y)  # Output: True
print(x < y)   # Output: True (alphabetically, 'apple' comes before 'banana')

# Example 3: Using comparison in conditions
age = 18
print(age >= 18)  # Output: True (age is greater than or equal to 18)

# Example 4: Comparing with variables
num1 = 100
num2 = 100

print(num1 == num2)  # Output: True
print(num1 is num2)  # Output: True (same object in memory for small integers)

# Example 5: Chained comparisons
x = 5
print(1 < x < 10)  # Output: True (x is between 1 and 10)
print(1 < x and x < 10)  # Same as above, explicit version
