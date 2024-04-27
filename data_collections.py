# data-collections

my_tuple = tuple((1, 2, "string"))
print(my_tuple)
tup = 1 , 2 , 3
print(tup)
print(type(tup))

tup = 1, 2, 3
a, b, c = tup
print(tup)
print(a,b,c)
print(a * b * c)

tup = 1, 2, 3, 2, 4, 5, 6, 2, 7, 2, 8, 9
duplicates = tup.count(2) # Write your code here.
print(duplicates)    # outputs: 4

d1 = {'Adam Smith': 'A', 'Judy Paxton': 'B+'}
d2 = {'Mary Louis': 'A', 'Patrick White': 'C'}
d3 = {}
for item in (d1, d2):
    # Write your code here:
    d3.update(item)
print(f"d3={d3}")
print(len(d3))

my_list = ["car", "Ford", "flower", "Tulip"]
t = tuple(my_list) # Write your code here.
print(t)
print(type(t))

colors_tuple = (("green", "#008000"), ("blue", "#0000FF"))
colors_dictionary = dict(colors_tuple) # Write your code here.
print(type(colors_tuple))
print(colors_dictionary)
colors_list = [["green", "#008000"], ["blue", "#0000FF"]]
colors_dictionary = dict(colors_list) # Write your code here.
print(type(colors_list))
print(colors_dictionary)

value = "5"
# value = input("enter value: ")
print(type(value))

print("~~~ PE1 -- Module 4 Test Question 20 ~~~")
dictionary = {'one': 'two', 'three': 'one', 'two': 'three'}
print(dictionary)
w = dictionary.values() # AttributeError, use .values() instead
print("w =",w)
print(len(dictionary)) # outputs '3'
v = dictionary['one']
print(v) # outputs 'two'
for k in range (len(dictionary)):
    v = dictionary[v]
    print("v =",v)
print (v)

print("~~~ PE1 -- Module 4 Test Question 22 ~~~")
tup = (1, 2, 4, 8)  ; print(tup)
tup = tup[-2:-1]     ; print(tup)
tup = tup[-1]        ; print(tup, end=' w/ type = ')
print(type(tup))

print("~~~ PE1 Summary Test Question 22 ~~~")
dct = {}
dct['1'] = (1, 2); print(dct)
dct['2'] = (2, 1); print(dct)
print("dct.keys =", dct.keys())
# print(dct['1'][1])
for x in dct.keys():
    print("dct.keys =",x)
    print(dct[x][1]) #, end="")

print("~~~ PE1 Summary Test Question 32 ~~~")
foo = (1,2,3)
x = 2
print("foo.index(x) =", foo.index(x))

print("~~~ PE1 Summary Test Question 26 ~~~")
dataVar = [3,1,2]
print("dataVar =", dataVar)
dataVar[1] = dataVar[1] + dataVar[0] # Note: if dataVar were a tuple (using parentheses instead of brackets), then this line would raise a TypeError
print("dataVar =", dataVar)

print("dct")
print(dct.get('1'))