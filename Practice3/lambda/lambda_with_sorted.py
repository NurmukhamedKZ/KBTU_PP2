"""Lambda with sorted() for custom sort key."""

students = [("Emil", 25), ("Tobias", 22), ("Linus", 28)]
by_age = sorted(students, key=lambda x: x[1])

if __name__ == "__main__":
    print(by_age)
