"""Multiple inheritance."""

class Flyer:
    def fly(self):
        return "Flying"

class Swimmer:
    def swim(self):
        return "Swimming"

class Duck(Flyer, Swimmer):
    pass

if __name__ == "__main__":
    d = Duck()
    print(d.fly(), d.swim())
