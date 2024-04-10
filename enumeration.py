import os
os.system('cls')

# enumeration
print("~~~ double index for loop ~~~")
arr = ['a', 'b', 'c']
print(arr)
enum_arr = enumerate(arr)
print(enum_arr)
# for i in enum_arr:
#     print(i)
for i,j in enum_arr:
    print(i, j)
    # print(i, j)

print("next")

for x in enum_arr:
    print(x)
print("done")