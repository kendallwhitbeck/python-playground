import os
os.system('cls')

z = 10
y = 0
x = y < z and z > y or y > z and z < y

print(y < z , z > y , y > z , z < y)

print("x=", x)
print("print test")

my_list = [1,2,3,4]
my_list2 = []
for i in my_list:
    my_list2.insert(len(my_list), i)
    print("in for loop i=",i,"with my_list2 =", my_list2)
print("my_list2 =", my_list2)
print("my_list2[-3:0] =", my_list2[-3:-1])

var = 0
while var < 6:
    var += 1
    if var % 2 == 0:
        continue
    print("#",var)

my_list = [[0,1,2,3] for i in range(2)]
print(my_list)
print(my_list[1][0])

vals = [1,2,3]
vals[0],vals[2] = vals[2],vals[0]
print(vals)

print("exercise 20")
for i in range(1):
    print("#", i)
else:
    print("# else")

print("~~~ PE1 Summary Test Question 29 ~~~")
# in = 4
# for = 6
# print = 7; print(print)
In = 8; print(In)

print("~~~ PE1 Summary Test Question 35 ~~~")
x = 1
y = 2
z = 3
x, y, z = 3, x, y
print(x,y,z)


print("\n~~~ Sample array of strings ~~~")
# Sample array of strings
array_of_strings = ['3 love\n', '6 computers\n', '2 dogs\n', '4 cats\n', '1 I\n', '5 you']

# Print each string with newline character
for string in array_of_strings:
    print(string)
    # print(string, end='')
    # print(string, end='\n')

# Alternatively, you can use the join() method to concatenate the strings and then print them
# print(''.join(array_of_strings), end='')


print("\n~~~ pyramid scheme incrementing ~~~")
current_row_end = 1
for i in range(1, 11):
    print(f"i={i}")
    print(f"current_row_end={current_row_end}")
    current_row_end = i + 2 * current_row_end

# Define the total number of rows in the pyramid
total_rows = 10

# Initialize the starting value for the current row
current_row_start = 1

# Loop to print only the end of each pyramid row
for row_length in range(1, total_rows + 1):  # Start from the first row
    # Determine the end of the current row
    current_row_end = current_row_start + row_length - 1

    # Print the end of the current row
    print(current_row_end)

    # Update the starting value for the next row
    current_row_start = current_row_end + 1

