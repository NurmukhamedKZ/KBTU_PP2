# For Loop with Continue in Python
# 'continue' skips the current iteration

# Example 1: Basic continue
fruits = ["apple", "banana", "cherry"]
for x in fruits:
    if x == "banana":
        continue
    print(x)

# Example 2: Skip specific number
print("\nSkip number 3:")
for x in range(6):
    if x == 3:
        continue
    print(x)

# Example 3: Print only odd numbers
print("\nOdd numbers only:")
for i in range(10):
    if i % 2 == 0:
        continue
    print(i)

# Example 4: Skip empty strings
print("\nSkip empty strings:")
items = ["hello", "", "world", "", "python"]
for item in items:
    if item == "":
        continue
    print(item)

# Example 5: Process only positive numbers
print("\nPositive numbers only:")
numbers = [1, -2, 3, -4, 5, -6]
for num in numbers:
    if num < 0:
        continue
    print(f"Processing: {num}")
