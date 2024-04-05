print('Exercise 1')
for i in range(0, 11):
    if (i%2 == 1):
        print(i)

print('\nExercise 2')
x = 0
while x < 11:
    if x % 2 != 0: # Line of code.
        print(x) # Line of code.
    x += 1 # Line of code.

print('\nExercise 3')
for ch in "john.smith@pythoninstitute.org":
    if ch == "@":
        break # Line of code.
    print(ch, end="") # Line of code.

print('\n\nExercise 4')
for digit in "0165031806510":
    if digit == "0":
        print("x", end="") # Line of code.
        continue # Line of code.
    print(digit, end="") # Line of code.

print('\n\nExercise 6')
n = range(4);
print(n)
for num in n:
    print(num)

print('\n\n~~~ ord(0:9) loop ~~~')
n = ('0','1','2','3','4','5','6','7','8','9')
print(n)
for num in n:
    print("ord(",num,") =",ord(num))

