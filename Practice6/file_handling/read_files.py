from pathlib import Path

sample_file = Path("sample.txt")

sample_file.write_text(
    "Line 1: Hello, World!\n"
    "Line 2: Python file handling\n"
    "Line 3: Reading and writing files\n"
)

print("=== read() ===")
with open(sample_file, "r") as f:
    content = f.read()
    print(content)

print("=== readline() ===")
with open(sample_file, "r") as f:
    line = f.readline()
    while line:
        print(line, end="")
        line = f.readline()

print("\n\n=== readlines() ===")
with open(sample_file, "r") as f:
    lines = f.readlines()
    for i, line in enumerate(lines, start=1):
        print(f"  [{i}] {line}", end="")
