"""Basic function definition and calling."""


def greet(name):
    """Return a greeting string."""
    return f"Hello, {name}!"


def print_twice(message):
    print(message)
    print(message)


if __name__ == "__main__":
    # Calling functions
    print(greet("Alice"))
    print_twice("Python is fun")
