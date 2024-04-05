# Bitwise Operations
import os
os.system('cls')

x = 4
print(x)
print(bin(x))

x = ~x
print(bin(x))
print(x)

the_list = ['list', False, 3e8]
print(the_list[1] in the_list)
print(the_list.index(False) == 1)
print(300 in the_list and the_list[1])

tup = (0,1,2)
tup2 = (3,4,5)
# del tup[0]
print (tup+tup2)

def func(param):
    param = [variable]
    return param