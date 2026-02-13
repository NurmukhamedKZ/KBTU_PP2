"""Class vs instance variables."""

class Dog:
    species = "Canis"  # class variable

    def __init__(self, name):
        self.name = name  # instance variable

if __name__ == "__main__":
    a = Dog("Rex")
    b = Dog("Max")
    print(a.name, b.name, Dog.species)
