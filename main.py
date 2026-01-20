def main():
    a = input()
    # try:
    #     int(a)
    #     print("int")
    # except Exception as e:
    #     print("str")

    if a.isdigit():
        print(
            "int"
        )
    else:
        print("str")


if __name__ == "__main__":
    main()
