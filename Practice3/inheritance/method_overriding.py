"""Method overriding in child class."""

class Animal:
    def speak(self):
        return "Some sound"

class Dog(Animal):
    def speak(self):
        return "Woof"

if __name__ == "__main__":
    d = Dog()
    print(d.speak())
