import matplotlib.pyplot as plt
import math
import os

os.system('cls')  # clear the terminal window text

# Sample data
x = range(1,100)
# y = [1]*len(x)  # Initialize y list w/ value of 1 for as many x data points as there are

# Time-complexity formulas
complexity_labels = ['O(1)', 'O(log n)', 'O(n)', 'O(n log n)', 'O(n^2)', 'O(n^3)', 'O(2^n)', 'O(n!)']
formulas = [
    lambda n: 1,
    lambda n: math.log(n),
    lambda n: n,
    lambda n: n * math.log(n),
    lambda n: n ** 2,
    lambda n: n ** 3,
    lambda n: 2 ** n,
    lambda n: math.factorial(n)
]

# Calculate y-values based on time-complexity formulas
for i, complexity_label in enumerate(complexity_labels[:-1]):
    formula = formulas[i]
    y_values = [formula(xi) for xi in x]

    # Plot the graph
    plt.plot(x, y_values, label=complexity_label)

# Add labels
plt.xlabel('input size (n)')
plt.ylabel('Operations (O)')
plt.title('Big-O Complexity')

# Format graph
plt.grid()
plt.legend()
plt.ylim(0, 100)

# Display the graph
plt.show()