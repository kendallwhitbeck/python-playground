# verify_bounds_playground
from decimal import Decimal
import os
os.system('cls')

def verify_bounds(value):
    print("entered function 'verify_bounds'")
    def string_to_numeric(value):
        print("entered function 'string_to_numeric'")
        bools = {'true': True, 'false': False}
        if value in bools:
            print("temp debug KPW1") # TODO remove this debug line KPW
            return bools[value]
        if value.startswith("'") and value.endswith("'"):
            print("temp debug KPW2, value =", value) # TODO remove this debug line KPW
            print("temp debug KPW2.1, value[1:-1] =", value[1:-1]) # TODO remove this debug line KPW
            print("temp debug KPW2.2, ord(value[1:-1]) =", ord(value[1:-1])) # TODO remove this debug line KPW
            return ord(value[1:-1])
        if value.endswith('U'):
            print("temp debug KPW3") # TODO remove this debug line KPW
            value = value[:-1]
        if value.startswith('0x'):
            print("temp debug KPW4") # TODO remove this debug line KPW
            return int(value, 16)
        print("temp debug KPW5, value =", value) # TODO remove this debug line KPW
        print("temp debug KPW6, Decimal(value) =",Decimal(value)) # TODO remove this debug line KPW
        return Decimal(value)
    numeric_value = string_to_numeric(value)
    print("numeric_value =",numeric_value)
    return numeric_value

value = "'8'"
# value = '1'
# value = '7'
# value = 'true'
# value = '0xf'; print(value)
newValue = verify_bounds(value)
print("newValue =",newValue)
