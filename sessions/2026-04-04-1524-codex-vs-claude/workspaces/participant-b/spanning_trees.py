import numpy as np
from fractions import Fraction

def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n**0.5)+1):
        if n % i == 0:
            return False
    return True

n = 10
# Build adjacency matrix
adj = [[0]*n for _ in range(n)]
edges = []
for i in range(n):
    for j in range(i+1, n):
        xor_val = i ^ j
        if is_prime(xor_val):
            adj[i][j] = 1
            adj[j][i] = 1
            edges.append((i, j, xor_val))

print(f"Number of edges: {len(edges)}")
print("Edges:")
for e in edges:
    print(f"  {e[0]}-{e[1]} (xor={e[2]})")

# Build Laplacian matrix using exact rational arithmetic
L = [[Fraction(0)]*n for _ in range(n)]
for i in range(n):
    deg = sum(adj[i])
    L[i][i] = Fraction(deg)
    for j in range(n):
        if adj[i][j]:
            L[i][j] = Fraction(-1)

print("\nDegree sequence:", [sum(adj[i]) for i in range(n)])
print("\nLaplacian matrix:")
for row in L:
    print([int(x) for x in row])

# Compute determinant of (n-1)x(n-1) minor using Gaussian elimination with exact fractions
def det_fraction(matrix):
    n = len(matrix)
    M = [[Fraction(matrix[i][j]) for j in range(n)] for i in range(n)]
    sign = 1
    for col in range(n):
        # Find pivot
        pivot = None
        for row in range(col, n):
            if M[row][col] != 0:
                pivot = row
                break
        if pivot is None:
            return Fraction(0)
        if pivot != col:
            M[col], M[pivot] = M[pivot], M[col]
            sign *= -1
        for row in range(col+1, n):
            if M[row][col] != 0:
                factor = M[row][col] / M[col][col]
                for k in range(col, n):
                    M[row][k] -= factor * M[col][k]
    result = Fraction(sign)
    for i in range(n):
        result *= M[i][i]
    return result

# Remove last row and column
minor = [[L[i][j] for j in range(n-1)] for i in range(n-1)]
num_spanning_trees = det_fraction(minor)
print(f"\nNumber of spanning trees: {num_spanning_trees}")

# Verify with numpy
L_np = np.array([[float(L[i][j]) for j in range(n)] for i in range(n)])
minor_np = L_np[:n-1, :n-1]
det_np = np.linalg.det(minor_np)
print(f"Numpy verification: {det_np}")
print(f"Rounded: {round(det_np)}")
