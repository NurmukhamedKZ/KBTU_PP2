
i = 0
while i < 6:
    i += 1
    if i == 3:
        continue
    print(i)

print("\nOdd numbers only:")
num = 0
while num < 10:
    num += 1
    if num % 2 == 0:
        continue
    print(num)

print("\nSkip negatives:")
numbers = [1, -2, 3, -4, 5, -6, 7]
index = 0
while index < len(numbers):
    current = numbers[index]
    index += 1
    if current < 0:
        continue
    print(current)

print("\nSkip number 5:")
i = 0
while i < 10:
    i += 1
    if i == 5:
        continue
    print(i, end=" ")
print()

print("\nProcess valid items:")
items = ["apple", "", "banana", "", "cherry"]
idx = 0
while idx < len(items):
    item = items[idx]
    idx += 1
    if item == "":
        continue
    print(f"Processing: {item}")
