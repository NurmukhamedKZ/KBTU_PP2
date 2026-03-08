"""
7. Write a python program to convert snake case string to camel case string.
"""
import re


def snake_to_camel(text: str) -> str:
    """Convert snake_case to camelCase."""
    return re.sub(r"_([a-z])", lambda m: m.group(1).upper(), text)


if __name__ == "__main__":
    text = "hello_world_foo_bar"
    print(snake_to_camel(text))  # helloWorldFooBar
