i = 1
while i < 6:
    print(i)
    if i == 3:
        break
    i += 1

print("\nSearching for number 7:")
num = 0
while num < 20:
    num += 1
    if num == 7:
        print(f"Found {num}!")
        break

print("\nBreak when sum > 10:")
total = 0
i = 1
while True:
    total += i
    print(f"Added {i}, total = {total}")
    if total > 10:
        break
    i += 1

print("\nControlled infinite loop:")
counter = 0
while True:
    counter += 1
    print(counter)
    if counter >= 5:
        break

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
