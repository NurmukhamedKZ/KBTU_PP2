# Short Hand If Else (Ternary Operator) in Python
# Write if-else in one line

# Example 1: Short hand if
a = 200
b = 33
if a > b: print("a is greater than b")

# Example 2: Short hand if else (ternary)
a = 2
b = 330
print("A") if a > b else print("B")

# Example 3: Ternary with variable assignment
x = 10
y = 20
max_value = x if x > y else y
print(f"Max value: {max_value}")

# Example 4: Multiple conditions in one line
a = 330
b = 330
print("A") if a > b else print("=") if a == b else print("B")

# Example 5: Ternary in string formatting
age = 20
status = "adult" if age >= 18 else "minor"
print(f"You are an {status}")
