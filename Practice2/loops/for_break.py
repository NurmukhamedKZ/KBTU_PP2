# For Loop with Break in Python
# 'break' stops the loop before it finishes

# Example 1: Basic break
fruits = ["apple", "banana", "cherry"]
for x in fruits:
    print(x)
    if x == "banana":
        break

# Example 2: Break before print
print("\nBreak before print:")
fruits = ["apple", "banana", "cherry"]
for x in fruits:
    if x == "banana":
        break
    print(x)

# Example 3: Search in list
print("\nSearch for 'cherry':")
fruits = ["apple", "banana", "cherry", "date"]
for fruit in fruits:
    if fruit == "cherry":
        print(f"Found: {fruit}")
        break
    print(f"Checking: {fruit}")

# Example 4: Break with range
print("\nBreak at 5:")
for i in range(10):
    if i == 5:
        break
    print(i)

# Example 5: Find first even number
print("\nFirst even number:")
numbers = [1, 3, 5, 8, 9, 10]
for num in numbers:
    if num % 2 == 0:
        print(f"First even: {num}")
        break
