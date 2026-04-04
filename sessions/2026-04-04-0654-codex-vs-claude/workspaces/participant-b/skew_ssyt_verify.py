# Verify with Bareiss integer determinant algorithm
from math import comb

lam = [13, 12, 10, 8, 7, 5, 4, 2]
mu = [5, 3, 2, 1, 0, 0, 0, 0]
k = 10
n = len(lam)

def h(r, k):
    if r < 0:
        return 0
    return comb(k + r - 1, r)

M = [[0] * n for _ in range(n)]
for i in range(n):
    for j in range(n):
        r = lam[i] - mu[j] - i + j
        M[i][j] = h(r, k)

# Bareiss algorithm
mat = [row[:] for row in M]
sign = 1
prev_pivot = 1

for col in range(n):
    pivot_row = None
    for row in range(col, n):
        if mat[row][col] != 0:
            pivot_row = row
            break
    if pivot_row is None:
        print("Determinant is 0")
        exit()
    if pivot_row != col:
        mat[col], mat[pivot_row] = mat[pivot_row], mat[col]
        sign *= -1
    
    for row in range(col + 1, n):
        for j in range(n - 1, col - 1, -1):
            mat[row][j] = (mat[col][col] * mat[row][j] - mat[row][col] * mat[col][j]) // prev_pivot
    
    prev_pivot = mat[col][col]

result = sign * mat[n-1][n-1]
print(f"Bareiss verification: {result}")
