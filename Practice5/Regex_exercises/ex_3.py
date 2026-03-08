"""
3. Write a Python program to find sequences of lowercase letters joined with a underscore.
"""
import re


def find_lowercase_underscore_sequences(text: str) -> list:
    """Find sequences of lowercase letters joined with underscore."""
    pattern = r"[a-z]+_[a-z]+"
    return re.findall(pattern, text)


if __name__ == "__main__":
    text = "hello_world foo_bar test_case"
    print(find_lowercase_underscore_sequences(text))  # ['hello_world', 'foo_bar', 'test_case']
