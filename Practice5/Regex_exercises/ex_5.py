"""
5. Write a Python program that matches a string that has an 'a' followed by anything, ending in 'b'.
"""
import re


def match_a_anything_b(text: str) -> list:
    """Match 'a' followed by anything, ending in 'b'."""
    pattern = r"a.*?b"
    return re.findall(pattern, text)


if __name__ == "__main__":
    text = "acb a123b axyb"
    print(match_a_anything_b(text))  # ['acb', 'a123b', 'axyb']
