"""
6. Write a Python program to replace all occurrences of space, comma, or dot with a colon.
"""
import re


def replace_with_colon(text: str) -> str:
    """Replace space, comma, and dot with colon."""
    pattern = r"[ ,.]"
    return re.sub(pattern, ":", text)


if __name__ == "__main__":
    text = "Hello, world. How are you?"
    print(replace_with_colon(text))  # Hello::world::How:are:you?
