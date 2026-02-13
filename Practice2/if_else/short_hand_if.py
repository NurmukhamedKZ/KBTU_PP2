a = 200
b = 33
if a > b: print("a is greater than b")
a = 2
b = 330
print("A") if a > b else print("B")

x = 10
y = 20
max_value = x if x > y else y
print(f"Max value: {max_value}")

a = 330
b = 330
print("A") if a > b else print("=") if a == b else print("B")

age = 20
status = "adult" if age >= 18 else "minor"
print(f"You are an {status}")
