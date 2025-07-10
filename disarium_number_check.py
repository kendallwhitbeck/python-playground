def is_disarium_number(number):
    num_str =  str(number)
    digits = []
    
    # extract the digits from num_str
    for i in range(len(num_str)):
        digit = num_str[i]
        digit = int(digit)
        digits.append(digit)
    # digits_dbg = [1, 7, 5]  # TODO test line, remove when done

    # initialize variable
    n = 1
    sum = 0
    digit_to_the_n = 0

    # loop through digits calculating the power of n of digit
    for digit in digits: 
        digit_to_the_n= digit ** n
        sum = sum + digit_to_the_n
        n+=1

    # check if sum matches input number
    if sum == number:
        print(f"{number} is a Disarium number!")
    else:
        print(f"{number} is NOT a Disarium number :(")

def main():
    number = 33
    # number=175
    is_disarium_number(number)


if __name__ == "__main__":
    main()
