"""
4. Write a Python program to find the sequences of one upper case letter followed by lower case letters.
"""
import re


def find_upper_lower_sequences(text: str) -> list:
    """Find sequences of one uppercase letter followed by lowercase letters."""
    pattern = r"[A-Z][a-z]+"
    return re.findall(pattern, text)


if __name__ == "__main__":
    text = "Hello World Python Programming"
    print(find_upper_lower_sequences(text))  # ['Hello', 'World', 'Python', 'Programming']
