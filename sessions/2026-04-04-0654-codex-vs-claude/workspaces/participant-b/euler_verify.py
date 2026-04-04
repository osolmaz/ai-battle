# Verify using BEST theorem:
# ec(G, start=w) = t_w(G) * prod_{v in V} (out_deg(v) - 1)!
# where t_w(G) = number of arborescences rooted at w
# An arborescence rooted at w: directed spanning tree where for every vertex v,
# there's a directed path from v to w. Equivalently, in-arborescence rooted at w.
# 
# t_w = det of the (n-1)x(n-1) matrix obtained from the Kirchhoff/Laplacian matrix
# by deleting row w and column w.
# The Laplacian L for directed graphs: L[i][j] = -#edges from i to j (i!=j), 
# L[i][i] = out_degree(i).
# For arborescences rooted at w, we use: t_w = det of matrix obtained by 
# deleting row w and column w from the Laplacian.
# Actually for directed graphs, the matrix-tree theorem uses the Laplacian where
# L[i][i] = out_degree(i) and L[i][j] = -(number of edges from i to j) for i!=j.
# Deleting row and column of root w gives the count of out-arborescences rooted at w
# (trees directed away from w).
# 
# For BEST theorem, we need in-arborescences rooted at w (trees directed toward w).
# For in-arborescences, use the in-degree Laplacian:
# L_in[i][i] = in_degree(i), L_in[i][j] = -(number of edges from j to i) for i!=j
# and delete row w and column w.

from math import factorial
from fractions import Fraction

edges = [
    (1,2), (1,5), (1,8), (2,4), (2,7), (2,10), (3,1), (3,8), (3,6),
    (4,3), (4,2), (4,7), (5,3), (5,4), (5,10), (6,5), (6,2), (6,9),
    (7,1), (7,6), (7,3), (8,7), (8,9), (8,4), (9,10), (9,6), (9,8),
    (10,9), (10,5), (10,1)
]

n = 10

# Compute out-degrees
out_deg = [0] * (n + 1)
in_deg = [0] * (n + 1)
for u, v in edges:
    out_deg[u] += 1
    in_deg[v] += 1

print("Out-degrees:", [out_deg[i] for i in range(1, n+1)])
print("In-degrees:", [in_deg[i] for i in range(1, n+1)])

# Build Laplacian for in-arborescences (using out-degree Laplacian)
# For counting in-arborescences rooted at w:
# Use L where L[i][i] = out_deg(i), L[i][j] = -a(i,j) where a(i,j) = #edges from i to j
# Then delete row w and column w, compute determinant.

# Actually, I need to be more careful. Let me use both approaches.

# Standard directed Laplacian (out-degree version):
# L[i][j] = out_deg(i) if i==j, -a(i,j) otherwise
# det of L with row w, col w deleted = number of in-arborescences rooted at w

# Build adjacency count matrix
a = [[0]*(n+1) for _ in range(n+1)]
for u, v in edges:
    a[u][v] += 1

# Build Laplacian (1-indexed, use indices 1..10)
L = [[Fraction(0)]*(n) for _ in range(n)]
for i in range(1, n+1):
    for j in range(1, n+1):
        if i == j:
            L[i-1][j-1] = Fraction(out_deg[i])
        else:
            L[i-1][j-1] = Fraction(-a[i][j])

# Delete row 0 (vertex 1) and column 0 (vertex 1) -> indices 1..9
w = 0  # vertex 1 is index 0
M = [[L[i][j] for j in range(n) if j != w] for i in range(n) if i != w]

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
        for row in range(col+1, m):
            if mat[row][col] != 0:
                factor = mat[row][col] / pv
                for j in range(col, m):
                    mat[row][j] -= factor * mat[col][j]
    return d

t_w = det(M)
print(f"In-arborescences rooted at vertex 1: {t_w}")

# BEST theorem: ec = t_w * prod_{v} (out_deg(v) - 1)!
prod_fact = 1
for v in range(1, n+1):
    prod_fact *= factorial(out_deg[v] - 1)

print(f"Product of (out_deg-1)!: {prod_fact}")

ec = int(t_w) * prod_fact
print(f"BEST theorem result: {ec}")
