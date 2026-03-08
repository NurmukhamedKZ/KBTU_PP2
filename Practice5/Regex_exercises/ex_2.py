"""
2. Write a Python program that matches a string that has an 'a' followed by two to three 'b'.
"""
import re


def match_a_two_to_three_b(text: str) -> list:
    """Match 'a' followed by two to three 'b's."""
    pattern = r"ab{2,3}"
    return re.findall(pattern, text)


if __name__ == "__main__":
    text = "ab abb abbb abbbb a"
    print(match_a_two_to_three_b(text))  # ['abb', 'abbb', 'abbb']
