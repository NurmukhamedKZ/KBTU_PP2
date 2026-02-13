"""Parent and child class."""

class Person:
    def __init__(self, fname, lname):
        self.firstname = fname
        self.lastname = lname

    def printname(self):
        print(self.firstname, self.lastname)

class Student(Person):
    pass

if __name__ == "__main__":
    x = Student("Mike", "Olsen")
    x.printname()
