def is_usual(num: int) -> bool:
    # Usual numbers must be positive integers
    if num <= 0:
        return False
    
    # Repeatedly divide by the allowed prime factors
    for factor in [2, 3, 5]:
        while num % factor == 0:
            num //= factor
            
    # If the remaining number is 1, it only had 2, 3, and 5 as factors
    return num == 1

def main():
    try:
        # Read input n
        line = input().strip()
        if not line:
            return
        n = int(line)
        
        # Check if it is usual and print result
        if is_usual(n):
            print("Yes")
        else:
            print("No")
    except EOFError:
        pass
    except ValueError:
        pass

if __name__ == "__main__":
    main()