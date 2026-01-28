# While Loop with Break in Python
# 'break' stops the loop even if condition is still true

# Example 1: Basic break
i = 1
while i < 6:
    print(i)
    if i == 3:
        break
    i += 1

# Example 2: Search and break
print("\nSearching for number 7:")
num = 0
while num < 20:
    num += 1
    if num == 7:
        print(f"Found {num}!")
        break

# Example 3: Break on condition
print("\nBreak when sum > 10:")
total = 0
i = 1
while True:
    total += i
    print(f"Added {i}, total = {total}")
    if total > 10:
        break
    i += 1

# Example 4: Break in infinite loop
print("\nControlled infinite loop:")
counter = 0
while True:
    counter += 1
    print(counter)
    if counter >= 5:
        break

# Example 5: Break with user simulation
print("\nSimulated password check:")
attempts = 0
password = "secret"
while attempts < 3:
    attempts += 1
    guess = "wrong" if attempts < 3 else "secret"
    if guess == password:
        print("Access granted!")
        break
    print(f"Attempt {attempts}: Wrong password")
