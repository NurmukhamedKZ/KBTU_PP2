"""The __init__() constructor and self."""

class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age

if __name__ == "__main__":
    p = Person("Alice", 25)
    print(p.name, p.age)
