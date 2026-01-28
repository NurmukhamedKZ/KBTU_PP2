# Boolean Comparison Results in Python
# When you compare two values, the expression is evaluated and returns a Boolean

# Example 1: Comparison operators
print(10 > 9)    # True - greater than
print(10 < 9)    # False - less than
print(10 == 9)   # False - equal to
print(10 != 9)   # True - not equal to
print(10 >= 9)   # True - greater than or equal to
print(10 <= 9)   # False - less than or equal to

# Example 2: Comparing variables
x = 5
y = 3
print(x > y)     # True - 5 is greater than 3

# Example 3: Using comparison in conditional statements
a = 200
b = 33

if a > b:
    print("a is greater than b")

# Example 4: Comparing strings (alphabetically)
print("apple" < "banana")   # True - 'a' comes before 'b'
print("apple" == "apple")   # True - strings are identical
print("Apple" == "apple")   # False - case sensitive comparison

# Example 5: Comparing different types
print(10 == 10.0)  # True - int and float can be compared
print(10 == "10")  # False - int and string are different types

# Example 6: Chained comparisons
x = 10
print(5 < x < 15)   # True - x is between 5 and 15
print(1 < 2 < 3)    # True - all comparisons are true
print(1 < 2 > 3)    # False - 2 > 3 is false
