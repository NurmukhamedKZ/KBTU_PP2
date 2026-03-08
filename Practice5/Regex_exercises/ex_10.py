"""
10. Write a Python program to convert a given camel case string to snake case.
"""
import re


def camel_to_snake(text: str) -> str:
    """Convert camelCase to snake_case."""
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", text)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


if __name__ == "__main__":
    text = "helloWorldFooBar"
    print(camel_to_snake(text))  # hello_world_foo_bar
