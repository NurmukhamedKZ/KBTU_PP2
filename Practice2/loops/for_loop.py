# For Loop in Python
# Used to iterate over a sequence (list, tuple, string, etc.)

# Example 1: Loop through a list
fruits = ["apple", "banana", "cherry"]
for x in fruits:
    print(x)

# Example 2: Loop through a string
print("\nLooping through string:")
for char in "banana":
    print(char)

# Example 3: Using range()
print("\nUsing range():")
for x in range(6):
    print(x)

# Example 4: Range with start and end
print("\nRange 2 to 5:")
for x in range(2, 6):
    print(x)

# Example 5: Range with step
print("\nRange with step 2:")
for x in range(0, 10, 2):
    print(x)

# Example 6: For with else
print("\nFor with else:")
for x in range(3):
    print(x)
else:
    print("Loop completed!")

# Example 7: Nested for loops
print("\nNested loops:")
adj = ["red", "big"]
fruits = ["apple", "banana"]
for a in adj:
    for f in fruits:
        print(a, f)
