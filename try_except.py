# try-except

try:
    value = int(3)
    # value = int(input("Enter a value: "))
    print(value/value)
except ValueError:
    print("Bad input...")
except ZeroDivisionError:
    print("Very bad input...")
except:
    print("Booo!")
    
print("~~~ PE1 Summary Test Question 2 ~~~")
try:
    print(Hello, World)
except NameError:
    print("NameError")
except SyntaxError:
    print("SyntaxError")
except SystemError:
    print("SystemError")

print("~~~ PE1 Summary Test Question 5 ~~~")
try:
    var = int(10.5)
    print(5/0)
    # break
except(ZeroDivisionError):
    print("ZeroDivisionError...")
except(ValueError):
    print("ValueError...")
# except:
#    print("Sorry, something went wrong...")


