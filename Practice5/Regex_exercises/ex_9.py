import re


def insert_spaces_before_capitals(text: str) -> str:
    """Insert spaces between words starting with capital letters."""
    return re.sub(r"([a-z])([A-Z])", r"\1 \2", text)


if __name__ == "__main__":
    text = "HelloWorldPython"
    print(insert_spaces_before_capitals(text))  # Hello World Python
