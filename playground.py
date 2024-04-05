import os
os.system('cls')

## ~~~~~~~~~~~~ Tuples ~~~~~~~~~~~~ ##
thistuple = ("apple", "banana", "cherry", "mango")
print(thistuple)
print(thistuple[1])
print(len(thistuple))
print(type(thistuple))
print("tuples are immutable, i.e., their elements cannot be changed")

#NOT a tuple
notatuple = ("apple")
print(type(notatuple)) # returns "<class 'str'>"

## ~~~~~~~~~~~~ Lists ~~~~~~~~~~~~ ##
# create list
mixed_list = [1,2,3,"hello",[4,5,6]]
print(mixed_list[0])
print(type(mixed_list[0]))

print(mixed_list[3])
print(type(mixed_list[3]))

print(mixed_list[4])
print(type(mixed_list[4]))

print(mixed_list)
print(type(mixed_list))

## ~~~~~~~~~~~~ Sets ~~~~~~~~~~~~ ##
my_set = {2,3,3,4,1}
# print(f"my_set print output is: {my_set}\n^^^Note: the duplicate value 3 is removed & the set is ordered by ascending")

## ~~~~~~~~~~~~ Dictionaries ~~~~~~~~~~~~ ##
my_dict = {"name":"Kendall", "age":27, "height":"5'11""", "job":"Software Engineer"}

print("Print output of my_dict:")
print(my_dict)
# print(f"Print output of my_dict but in the same print statement: '{my_dict}'");

print("Print output of my_dict[name]:");
print(my_dict["name"])
# print(f"Print output of \"my_dict[name]\" but in the same print statement w/ escaped quotes: \"{my_dict['name']}\" ");

## ~~~~~~~~~~~~ Fixtures ~~~~~~~~~~~~ ##
# import pytest

# test_example1()
# test_example2

# @pytest.fixture(autouse=True)
# def setup_and_teardown():
#     # This fixture will be automatically used by all tests
#     # It will run before and after each test
#     print("Setting up...")  # This will run before each test
#     yield
#     print("Tearing down...")  # This will run after each test

# def test_example1():
#     print("Test 1 running")

# def test_example2():
#     print("Test 2 running")

## ~~~~~~~~~~~~ Loops ~~~~~~~~~~~~ ##
print("## ~~~~~~~~~~~~ Loops ~~~~~~~~~~~~ ##")
for i in range(0,1):
    print('i=',i)
    
var =3
if var != 7:
    print(var)

menu = {"pizz": 2.39, "pasta": 1.99, "folpetti":3.99}
for value in menu:
    print(str(value)[0], end="")
    
    