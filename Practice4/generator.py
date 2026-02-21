# Task 1
def generator(n):
    for i in range(1,n+1):
        yield i**2

# Task 2
def even_generator(n):
    for i in range(0,n+1,2):
        yield i
    
# user = int(input("Input n: "))
# for i in even_generator(user):
#     print(i, end=", ")


# Task 3
def divisible_by_3_and_4(n):
    for i in range(0,n+1):
        if i % 3 == 0 and i % 4 == 0:
            yield i

# user = int(input("Input n: "))
# for i in divisible_by_3_and_4(user):
#     print(i, end=", ")


# Task 4
def squares(a,b):
    for i in range(a,b+1):
        yield i**2

# user1 = int(input("Input a: "))
# user2 = int(input("Input b: "))
# for i in squares(user1,user2):
#     print(i, end=", ")

# Task 5
def generator2(n):
    for i in range(n,-1,-1):
        yield i

user = int(input("Input n: "))
for i in generator2(user):
    print(i, end=", ")