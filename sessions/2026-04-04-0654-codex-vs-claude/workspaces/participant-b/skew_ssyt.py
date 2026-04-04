# Count SSYT of skew shape lambda/mu with entries in {1,...,k}
# Using the Jacobi-Trudi formula:
# s_{lambda/mu}(1^k) = det(h_{lambda_i - mu_j - i + j}(1^k))
# where h_r(1^k) = C(k+r-1, r) for r >= 0, h_r = 0 for r < 0

from math import comb
from fractions import Fraction

lam = [13, 12, 10, 8, 7, 5, 4, 2]
mu = [5, 3, 2, 1, 0, 0, 0, 0]
k = 10
n = len(lam)

def h(r, k):
    """Complete homogeneous symmetric function h_r evaluated at k ones."""
    if r < 0:
        return 0
    return comb(k + r - 1, r)

# Build the matrix
M = [[Fraction(0)] * n for _ in range(n)]
for i in range(n):
    for j in range(n):
        r = lam[i] - mu[j] - i + j
        M[i][j] = Fraction(h(r, k))

# Print matrix for debugging
print("Matrix:")
for row in M:
    print([int(x) for x in row])

# Compute determinant
def det(matrix):
    m = len(matrix)
    mat = [row[:] for row in matrix]
    d = Fraction(1)
    for col in range(m):
        pivot = None
        for row in range(col, m):
            if mat[row][col] != 0:
                pivot = row
                break
        if pivot is None:
            return Fraction(0)
        if pivot != col:
            mat[col], mat[pivot] = mat[pivot], mat[col]
            d *= -1
        d *= mat[col][col]
        pv = mat[col][col]
        for row in range(col + 1, m):
            if mat[row][col] != 0:
                factor = mat[row][col] / pv
                for j in range(col, m):
                    mat[row][j] -= factor * mat[col][j]
    return d

result = det(M)
print(f"\nSSYT count: {int(result)}")
print(f"Is integer: {result.denominator == 1}")
