"""Positional and default arguments."""


def power(base, exponent=2):
    """Raise base to exponent; default exponent is 2."""
    return base ** exponent


def describe_pet(animal, name="Unknown"):
    return f"{name} is a {animal}."


if __name__ == "__main__":
    print(power(3))        # 9, uses default exponent
    print(power(3, 4))     # 81
    print(describe_pet("dog", "Rex"))
    print(describe_pet("cat"))  # name defaults to "Unknown"
