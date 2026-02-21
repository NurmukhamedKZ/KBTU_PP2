import math

# Task 1
def radians_conversion(degree):
    return math.radians(degree)

def custom_radians_conversion(degree):
    return degree * math.pi / 180

def radian():
    user = float(input("Input degree: "))
    print(f"Output radians: {radians_conversion(user):.6f}")
    print(f"Output custom radians: {custom_radians_conversion(user):.6f}")


# Task 2
def area_trapezoid():
    height = float(input("Input height: "))
    base1 = float(input("Input base1: "))
    base2 = float(input("Input base2: "))
    print(f"Output area: {(base1 + base2) * height / 2:.2f}")
    

# Task 3
def area_polygon():
    sides = int(input("Input number of sides: "))
    side_length = float(input("Input side length: "))
    print(f"Output area: {sides * side_length ** 2 / (4 * math.tan(math.pi / sides)):.2f}")

# Task 4
def area_parallelogram():
    base = float(input("Input base: "))
    height = float(input("Input height: "))
    print(f"Output area: {base * height:.2f}")
