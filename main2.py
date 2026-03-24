n = input()
keys = input().split()

def is_non_zero(x):
    return x != '0'

print(sum(map(is_non_zero, keys)))