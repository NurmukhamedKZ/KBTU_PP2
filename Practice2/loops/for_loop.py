fruits = ["apple", "banana", "cherry"]
for x in fruits:
    print(x)

print("\nLooping through string:")
for char in "banana":
    print(char)

print("\nUsing range():")
for x in range(6):
    print(x)

print("\nRange 2 to 5:")
for x in range(2, 6):
    print(x)

print("\nRange with step 2:")
for x in range(0, 10, 2):
    print(x)

print("\nFor with else:")
for x in range(3):
    print(x)
else:
    print("Loop completed!")

print("\nNested loops:")
adj = ["red", "big"]
fruits = ["apple", "banana"]
for a in adj:
    for f in fruits:
        print(a, f)
