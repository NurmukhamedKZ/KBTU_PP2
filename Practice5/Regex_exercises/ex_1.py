"""
1. Write a Python program that matches a string that has an 'a' followed by zero or more 'b's.
"""
import re


def match_a_zero_or_more_b(text: str) -> list:
    """Match 'a' followed by zero or more 'b's."""
    pattern = r"ab*"
    return re.findall(pattern, text)


if __name__ == "__main__":
    text = "ab abb abbb a ab"
    print(match_a_zero_or_more_b(text))  # ['ab', 'abb', 'abbb', 'a', 'ab']
