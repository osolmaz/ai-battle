# Compute the permanent of a specific 7x7 matrix
import itertools

M = [
    [2, 7, 1, 8, 2, 8, 1],
    [3, 1, 4, 1, 5, 9, 2],
    [6, 5, 3, 5, 8, 9, 7],
    [9, 3, 2, 3, 8, 4, 6],
    [2, 6, 4, 3, 3, 8, 3],
    [2, 7, 9, 5, 0, 2, 8],
    [8, 4, 1, 9, 7, 1, 6],
]

n = 7
perm = 0
for sigma in itertools.permutations(range(n)):
    prod = 1
    for i in range(n):
        prod *= M[i][sigma[i]]
    perm += prod

print(f"Permanent = {perm}")
