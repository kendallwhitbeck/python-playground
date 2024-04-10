# data-groupings
import os
os.system('cls')

nums = [] # this is a list
print("nums =", nums)
print("len(nums) =", len(nums))
vals = nums[:]
print("len(vals) =", len(vals))

vals.append(457.0)

print("~~~ nums ~~~")
print("nums =", nums)
print("len(nums) =", len(nums))
print("type(nums) =", type(nums))
print("~~~ vals ~~~")
print("vals=", vals)
print("len(vals) =", len(vals))
print("type(vals) =", type(vals))

print("\n~~~ my_list ~~~")
my_list = [0 for i in range(1,5)]
print("my_list =", (my_list))
print("len(my_list) =", len(my_list))