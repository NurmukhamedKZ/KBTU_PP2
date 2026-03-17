from pathlib import Path

data_file = Path("data.txt")

# Write mode - creates or overwrites
with open(data_file, "w") as f:
    f.write("Initial line 1\n")
    f.write("Initial line 2\n")

print("After write:")
print(data_file.read_text())

# Append mode - adds to existing content
with open(data_file, "a") as f:
    f.write("Appended line 3\n")
    f.write("Appended line 4\n")

print("After append:")
print(data_file.read_text())

# 'x' mode - exclusive creation (fails if file exists)
new_file = Path("new_exclusive.txt")
if new_file.exists():
    new_file.unlink()

with open(new_file, "x") as f:
    f.write("Created exclusively with 'x' mode\n")

print("Exclusive file content:")
print(new_file.read_text())

# Cleanup
data_file.unlink(missing_ok=True)
new_file.unlink(missing_ok=True)
