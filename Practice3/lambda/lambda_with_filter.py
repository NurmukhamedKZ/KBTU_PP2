"""Lambda with filter() for selection."""

numbers = [1, 2, 3, 4, 5, 6, 7, 8]
odd_only = list(filter(lambda x: x % 2 != 0, numbers))

if __name__ == "__main__":
    print(odd_only)
