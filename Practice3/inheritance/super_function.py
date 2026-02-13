"""Using super() for parent __init__."""

class Person:
    def __init__(self, fname, lname):
        self.firstname = fname
        self.lastname = lname

class Student(Person):
    def __init__(self, fname, lname, year):
        super().__init__(fname, lname)
        self.graduationyear = year

if __name__ == "__main__":
    x = Student("Mike", "Olsen", 2019)
    print(x.firstname, x.graduationyear)
