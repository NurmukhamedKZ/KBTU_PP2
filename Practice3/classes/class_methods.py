"""Instance methods and self."""

class Counter:
    def __init__(self):
        self.count = 0

    def increment(self):
        self.count += 1

if __name__ == "__main__":
    c = Counter()
    c.increment()
    c.increment()
    print(c.count)
