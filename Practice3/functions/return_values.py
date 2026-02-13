"""Return values and multiple return."""


def add(a, b):
    return a + b


def min_max(numbers):
    """Return tuple of (min, max) or None if empty."""
    if not numbers:
        return None
    return min(numbers), max(numbers)


if __name__ == "__main__":
    print(add(10, 20))
    result = min_max([3, 1, 4, 1, 5])
    print(result)
    low, high = min_max([3, 1, 4])
    print(f"Low: {low}, High: {high}")
