# While Loop with Continue in Python
# 'continue' skips current iteration and continues with next

# Example 1: Basic continue
i = 0
while i < 6:
    i += 1
    if i == 3:
        continue
    print(i)

# Example 2: Skip even numbers
print("\nOdd numbers only:")
num = 0
while num < 10:
    num += 1
    if num % 2 == 0:
        continue
    print(num)

# Example 3: Skip negative numbers
print("\nSkip negatives:")
numbers = [1, -2, 3, -4, 5, -6, 7]
index = 0
while index < len(numbers):
    current = numbers[index]
    index += 1
    if current < 0:
        continue
    print(current)

# Example 4: Skip specific values
print("\nSkip number 5:")
i = 0
while i < 10:
    i += 1
    if i == 5:
        continue
    print(i, end=" ")
print()

# Example 5: Process only valid items
print("\nProcess valid items:")
items = ["apple", "", "banana", "", "cherry"]
idx = 0
while idx < len(items):
    item = items[idx]
    idx += 1
    if item == "":
        continue
    print(f"Processing: {item}")
