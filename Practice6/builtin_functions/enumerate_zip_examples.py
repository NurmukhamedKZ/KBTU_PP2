names = ["Alice", "Bob", "Charlie", "Diana"]
scores = [85, 92, 78, 96]
grades = ["B", "A", "C", "A+"]

# enumerate() - iterate with index
print("=== enumerate() ===")
for i, name in enumerate(names):
    print(f"  [{i}] {name}")

print("\nenumerate() with start=1:")
for rank, name in enumerate(names, start=1):
    print(f"  Rank {rank}: {name}")

# zip() - pair up multiple iterables
print("\n=== zip() ===")
for name, score in zip(names, scores):
    print(f"  {name}: {score}")

print("\nzip() with three lists:")
for name, score, grade in zip(names, scores, grades):
    print(f"  {name} -> {score} ({grade})")

# zip to create dict
score_dict = dict(zip(names, scores))
print("\ndict from zip:", score_dict)

# sorted()
print("\n=== sorted() ===")
print("sorted numbers:", sorted([3, 1, 4, 1, 5, 9, 2, 6]))
print("sorted descending:", sorted([3, 1, 4, 1, 5, 9, 2, 6], reverse=True))
print("sorted by score:", sorted(zip(names, scores), key=lambda x: x[1], reverse=True))

# Type checking and conversions
print("\n=== Type conversions ===")
print(f"int('42')   = {int('42')}")
print(f"float('3.14') = {float('3.14')}")
print(f"str(100)    = {str(100)!r}")
print(f"bool(0)     = {bool(0)}, bool(1) = {bool(1)}")
print(f"list((1,2,3)) = {list((1, 2, 3))}")
print(f"tuple([1,2,3]) = {tuple([1, 2, 3])}")
print(f"set([1,1,2,3]) = {set([1, 1, 2, 3])}")

# Type checking
values = [42, 3.14, "hello", True, [1, 2], None]
print("\ntype() checking:")
for v in values:
    print(f"  type({v!r}) = {type(v).__name__}")

print("\nisinstance() checking:")
print(f"  isinstance(42, int)   = {isinstance(42, int)}")
print(f"  isinstance(42, float) = {isinstance(42, float)}")
print(f"  isinstance('hi', str) = {isinstance('hi', str)}")
