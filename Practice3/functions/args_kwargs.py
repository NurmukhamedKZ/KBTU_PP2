"""*args and **kwargs for variable arguments."""


def sum_all(*args):
    """Accept any number of positional arguments."""
    return sum(args)


def build_profile(**kwargs):
    """Accept any number of keyword arguments."""
    return kwargs


if __name__ == "__main__":
    print(sum_all(1, 2, 3, 4, 5))
    profile = build_profile(name="Alice", age=25, city="Almaty")
    print(profile)
