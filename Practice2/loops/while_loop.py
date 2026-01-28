# While Loop in Python
# Executes code while a condition is true

# Example 1: Basic while loop
i = 1
while i < 6:
    print(i)
    i += 1

# Example 2: Countdown
print("\nCountdown:")
count = 5
while count > 0:
    print(count)
    count -= 1
print("Liftoff!")

# Example 3: Sum of numbers
print("\nSum calculation:")
total = 0
num = 1
while num <= 10:
    total += num
    num += 1
print(f"Sum of 1-10: {total}")

# Example 4: While with user condition
print("\nDoubling:")
value = 1
while value < 100:
    print(value)
    value *= 2

# Example 5: While with else
print("\nWhile with else:")
i = 1
while i < 4:
    print(i)
    i += 1
else:
    print("Loop finished!")
