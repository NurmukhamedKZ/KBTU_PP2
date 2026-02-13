"""Lambda with map() for transformation."""

numbers = [1, 2, 3, 4, 5]
doubled = list(map(lambda x: x * 2, numbers))

if __name__ == "__main__":
    print(doubled)
