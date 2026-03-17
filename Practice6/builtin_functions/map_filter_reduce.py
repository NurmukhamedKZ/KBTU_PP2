from functools import reduce

numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
words = ["hello", "world", "python", "programming", "file"]

# map() - apply a function to each element
squares = list(map(lambda x: x ** 2, numbers))
print("map() - squares:", squares)

upper_words = list(map(str.upper, words))
print("map() - uppercase words:", upper_words)

# filter() - keep elements where condition is True
evens = list(filter(lambda x: x % 2 == 0, numbers))
print("\nfilter() - even numbers:", evens)

long_words = list(filter(lambda w: len(w) > 5, words))
print("filter() - words longer than 5 chars:", long_words)

# reduce() - fold list into a single value
total = reduce(lambda acc, x: acc + x, numbers)
print("\nreduce() - sum:", total)

product = reduce(lambda acc, x: acc * x, numbers)
print("reduce() - product:", product)

max_val = reduce(lambda a, b: a if a > b else b, numbers)
print("reduce() - max:", max_val)

# Combining map and filter
even_squares = list(map(lambda x: x ** 2, filter(lambda x: x % 2 == 0, numbers)))
print("\nmap + filter - squares of even numbers:", even_squares)

# Aggregation built-ins
print("\nsum():", sum(numbers))
print("min():", min(numbers))
print("max():", max(numbers))
print("len():", len(numbers))
