# Count Standard Young Tableaux of shape (7, 5, 4, 3, 1) 
# which has 7+5+4+3+1 = 20 cells.
# Use hook length formula: f^lambda = n! / prod(hook lengths)

from math import factorial

shape = [7, 5, 4, 3, 1]
n = sum(shape)

# Compute hook lengths
# For cell (i, j) (0-indexed), hook length = arm + leg + 1
# arm = number of cells to the right in the same row = shape[i] - j - 1
# leg = number of cells below in the same column = number of rows r > i with shape[r] > j

hooks = []
for i, row_len in enumerate(shape):
    for j in range(row_len):
        arm = row_len - j - 1
        leg = sum(1 for r in range(i + 1, len(shape)) if shape[r] > j)
        hook = arm + leg + 1
        hooks.append(hook)

print(f"Shape: {shape}")
print(f"n = {n}")
print(f"Hooks: {sorted(hooks, reverse=True)}")
print(f"Product of hooks: {1}")

product = 1
for h in hooks:
    product *= h

syt_count = factorial(n) // product
print(f"Product of hooks = {product}")
print(f"SYT count = {n}! / {product} = {syt_count}")

# Verify it's an integer
assert factorial(n) % product == 0
print(f"Verified: {syt_count} is an integer")
