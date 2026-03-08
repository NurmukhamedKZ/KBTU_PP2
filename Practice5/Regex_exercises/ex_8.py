"""
8. Write a Python program to split a string at uppercase letters.
"""
import re


def split_at_uppercase(text: str) -> list:
    """Split string at uppercase letters."""
    pattern = r"(?=[A-Z])"
    parts = re.split(pattern, text)
    return [p for p in parts if p]


if __name__ == "__main__":
    text = "HelloWorldPython"
    print(split_at_uppercase(text))  # ['Hello', 'World', 'Python']
