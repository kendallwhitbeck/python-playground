# functions

# defining hello() function
def hello(name):    # defining a function
    print("Hello,", name)    # body of the function
# main code invoking hello() function
name2 = 'kendall'
# name2 = input("Enter your name: ")
hello(name2)    # calling the function

# Following does not work:
# def add_numbers(a, b=2, c): #SyntaxError: non-default argument follows default argument
#     print(a + b + c)

def hi():
    print("Hi!")
    return
hi()

# Recursive implementation of the factorial function.
def factorial(n):
    print("n =",n)
    if n == 1:    # The base case (termination condition.)
        return 1
    else:
        return n * factorial(n - 1)
print(factorial(4)) # 4 * 3 * 2 * 1 = 24

def del2ndElem(my_list):
    del my_list[1]
    return my_list
my_list = [1,'delete 2nd element',2,3,4,5]
print(my_list)
print(del2ndElem(my_list))


def fun(In=2, out=3):
    return In * out
print(fun(3))

x = z = None
y = 2
print(x,y,z)
print(x == y)
print(x == z)

print("~~~ Mary Had a Little Lamb ~~~")
my_list = ['Mary', 'had', 'a', 'little', 'lamb']
def my_list_fun(my_list_arg):
    del my_list_arg[3]
    my_list_arg[3] = 'ram'
    return my_list # this line is required to produce the expected string, otherwise the print would return 'None'
print(my_list_fun(my_list)) # Note: the function name cannot be the same as the variable name passed into the function

print("~~~ PE1 Summary Test Question 21 ~~~")
def fun(inp, out=3, third=4):
    return inp * out * third
print(fun(2))

