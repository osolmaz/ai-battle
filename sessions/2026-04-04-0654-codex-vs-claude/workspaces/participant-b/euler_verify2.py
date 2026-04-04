from math import factorial
from fractions import Fraction

edges = [
    (1,2), (1,5), (1,8), (2,4), (2,7), (2,10), (3,1), (3,8), (3,6),
    (4,3), (4,2), (4,7), (5,3), (5,4), (5,10), (6,5), (6,2), (6,9),
    (7,1), (7,6), (7,3), (8,7), (8,9), (8,4), (9,10), (9,6), (9,8),
    (10,9), (10,5), (10,1)
]

n = 10
out_deg = [0] * (n + 1)
in_deg = [0] * (n + 1)
a = [[0]*(n+1) for _ in range(n+1)]
for u, v in edges:
    out_deg[u] += 1
    in_deg[v] += 1
    a[u][v] += 1

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

# Try in-degree Laplacian
L_in = [[Fraction(0)]*n for _ in range(n)]
for i in range(1, n+1):
    for j in range(1, n+1):
        if i == j:
            L_in[i-1][j-1] = Fraction(in_deg[i])
        else:
            L_in[i-1][j-1] = Fraction(-a[j][i])  # edges FROM j TO i

w = 0  # vertex 1
M_in = [[L_in[i][j] for j in range(n) if j != w] for i in range(n) if i != w]
t_in = det(M_in)
print(f"In-degree Laplacian arborescences: {t_in}")

# Out-degree Laplacian (what I computed before)
L_out = [[Fraction(0)]*n for _ in range(n)]
for i in range(1, n+1):
    for j in range(1, n+1):
        if i == j:
            L_out[i-1][j-1] = Fraction(out_deg[i])
        else:
            L_out[i-1][j-1] = Fraction(-a[i][j])

M_out = [[L_out[i][j] for j in range(n) if j != w] for i in range(n) if i != w]
t_out = det(M_out)
print(f"Out-degree Laplacian arborescences: {t_out}")

prod_fact = 1
for v in range(1, n+1):
    prod_fact *= factorial(out_deg[v] - 1)
print(f"Product of (out_deg-1)!: {prod_fact}")

print(f"BEST with t_in: {int(t_in) * prod_fact}")
print(f"BEST with t_out: {int(t_out) * prod_fact}")

# The brute force gave 15083520
# 15083520 / 1024 = 14730
# 15083520 / 3 = 5027840 (matches t_out version)
print(f"15083520 / 3 = {15083520 // 3}")
print(f"15083520 / 1024 = {15083520 / 1024}")

# Hmm, let me reconsider. The BEST theorem:
# The number of Eulerian circuits in a directed graph is:
# ec = t_w * prod_{v in V} (d_out(v) - 1)!
# This counts directed closed walks starting at w that use each edge exactly once.
# 
# But actually, I think the standard statement might be that this counts circuits
# modulo choice of starting vertex. For a fixed starting vertex, multiply by... no.
# 
# Actually the key subtlety: BEST theorem counts Eulerian circuits, and any 
# Eulerian circuit can start at any vertex. If we want to count those starting at
# a specific vertex w, we get ec(G) as above.
# But our brute force counts sequences starting at 1, and there are out_deg(1)=3
# choices for the first edge. Maybe the BEST theorem fixes the first edge?

# Let me check: BEST theorem states ec = t_w * prod (d_out(v)-1)!
# This is said to count the number of Eulerian circuits from w.
# If our answer is 3x this, maybe our brute force is counting something different.

# Actually, I think the BEST theorem might count Eulerian circuits as equivalence 
# classes under cyclic rotation. The number of distinct edge sequences starting at w
# would then be ec * d_out(w) / d_out(w)... no that doesn't help.

# Let me just trust the brute force since it directly implements what the question asks.
print(f"\nBrute force answer: 15083520")
