# I need a question that's hard for Codex. Let me try something that requires
# combining multiple mathematical techniques in a non-standard way.
#
# Idea: Count the number of labeled graphs on {1,...,7} that are both 
# planar AND have a Hamiltonian cycle.
#
# This is well-defined but requires checking both planarity and Hamiltonicity
# for each graph. C(21, m) for various m is feasible to enumerate if we're
# smart about it.
#
# Actually, total simple graphs on 7 vertices: 2^21 = 2097152. 
# For each, check planarity and Hamiltonicity. Both are polynomial-time checks.
# But 2M graphs to check might be slow in Python.
#
# Let me try it with optimizations.

# Actually, let me think of a cleaner question.
# 
# How about: compute the number of linear extensions of a specific poset?
# I showed strong ability with this in turn 7.
# But Codex might also handle it.
#
# How about: What is the largest k such that the complete bipartite graph K_{k,k}
# has a proper edge coloring with k colors where every pair of color classes 
# forms a Hamiltonian cycle? (This is related to 1-factorizations.)
# Hmm, this is more of a research question.
#
# Let me try: count labeled graphs on 8 vertices with exactly 12 edges 
# that have chromatic number exactly 4.
# This requires computing chromatic numbers, which is NP-hard in general
# but feasible for small graphs.

# Actually, let me think about what's truly hard for Codex but feasible for me.
# Both of us can run code. Both can implement backtracking. Both know math.
#
# Maybe I should ask a question where the MATHEMATICAL FORMULATION is the 
# hard part - where you need to translate between mathematical concepts.
#
# Q: What is the permanent of the character table of S_5?
#
# The character table of S_5 is a 7×7 matrix (7 conjugacy classes).
# The permanent is the sum over all permutations of products of entries.
# 7! = 5040 terms, very feasible.
#
# Character table of S_5:
# Partitions of 5: (5), (4,1), (3,2), (3,1,1), (2,2,1), (2,1,1,1), (1,1,1,1,1)
# Conjugacy classes: same partitions
# 
# The character table is well-known. Let me look it up / compute it.

# Character table of S_5:
# Columns: cycle types (1^5), (2,1^3), (2^2,1), (3,1^2), (3,2), (4,1), (5)
# Sizes:    1       10       15       20       20      30     24
#
# Irreps:        (1^5) (2,1^3) (2^2,1) (3,1^2) (3,2) (4,1) (5)
# triv (5):       1      1       1       1       1     1     1
# std (4,1):      4      2       0       1      -1     0    -1
# (3,2):          5      1       1      -1       1    -1     0
# (3,1,1):        6      0      -2       0       0     0     1
# (2,2,1):        5     -1       1      -1      -1     1     0
# (2,1,1,1):      4     -2       0       1       1     0    -1
# sign (1^5):     1     -1       1       1      -1    -1     1

# Let me verify: the character table of S_5.
# Row sums should give irrep evaluated at identity (dimension).
# Actually, different sources may order rows/columns differently.
# Let me use a specific, verified source.

# The standard character table of S_5:
# I'll define it explicitly and compute the permanent.

import numpy as np
from itertools import permutations

# Character table of S_5 (7 x 7)
# Rows: irreducible representations (indexed by partitions)
# Columns: conjugacy classes (indexed by cycle types)
# Order of columns: (1^5), (2,1^3), (2^2,1), (3,1^2), (3,2), (4,1), (5)

char_table = [
    [1,  1,  1,  1,  1,  1,  1],   # trivial (5)
    [4,  2,  0,  1, -1,  0, -1],   # standard (4,1)
    [5,  1,  1, -1,  1, -1,  0],   # (3,2)
    [6,  0, -2,  0,  0,  0,  1],   # (3,1,1)
    [5, -1,  1, -1, -1,  1,  0],   # (2,2,1)
    [4, -2,  0,  1,  1,  0, -1],   # (2,1,1,1)
    [1, -1,  1,  1, -1, -1,  1],   # sign (1,1,1,1,1)
]

n = len(char_table)
print(f"Character table is {n}x{n}")

# Verify: dimensions squared should sum to 120 = |S_5|
dim_sq_sum = sum(row[0]**2 for row in char_table)
print(f"Sum of dimension^2: {dim_sq_sum} (should be 120)")

# Verify orthogonality: sum over classes of chi_i(g) * chi_j(g) * |class(g)| / |G|
# should give delta_{ij}
class_sizes = [1, 10, 15, 20, 20, 30, 24]  # |S_5| = 120
for i in range(n):
    for j in range(i, min(i+2, n)):
        s = sum(char_table[i][k] * char_table[j][k] * class_sizes[k] for k in range(n))
        expected = 120 if i == j else 0
        if s != expected:
            print(f"  Orthogonality check ({i},{j}): {s} (expected {expected})")

print("Orthogonality checks passed" if all(
    sum(char_table[i][k] * char_table[j][k] * class_sizes[k] for k in range(n)) == (120 if i == j else 0)
    for i in range(n) for j in range(n)
) else "Orthogonality FAILED")

# Compute permanent
def permanent(matrix):
    n = len(matrix)
    total = 0
    for perm in permutations(range(n)):
        prod = 1
        for i in range(n):
            prod *= matrix[i][perm[i]]
        total += prod
    return total

perm_val = permanent(char_table)
print(f"\nPermanent of character table of S_5: {perm_val}")

