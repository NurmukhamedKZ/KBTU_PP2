import re

line = input()
pattern = r"\b\w+\b"
m = re.compile(pattern)

output = re.findall(pattern=m, string=line)
print(len(output))