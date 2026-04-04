# Question idea: Count the number of distinct necklaces (up to rotation only)
# using beads of 3 colors, where the necklace has exactly 13 beads.
#
# By Burnside's lemma with cyclic group C_13:
# N = (1/13) * sum_{d|13} phi(13/d) * 3^d
# Since 13 is prime, divisors are 1 and 13.
# N = (1/13) * (phi(13)*3^1 + phi(1)*3^13)
# = (1/13) * (12*3 + 1*1594323)
# = (1/13) * (36 + 1594323)
# = (1/13) * 1594359
# = 122643

# That's too standard. Let me think of something better.

# How about a question involving the Tutte polynomial of a specific graph?
# Or counting specific substructures?

# Let me try: count the number of labeled forests on vertex set {1,...,8}
# A forest is an acyclic graph. The number of labeled forests on n vertices is
# (n+1)^(n-1) by a generalization of Cayley's formula? No, that's for trees.
# 
# Actually, the number of labeled forests on n vertices is sum over k of 
# C(n,k) * k * n^(n-k-1)... hmm, this is getting complicated.
#
# The exponential generating function for forests is e^{T(x)} where T(x) = x*e^{T(x)}
# (T is the EGF for labeled rooted trees).
# Actually, the EGF for labeled unrooted forests is e^{T(x)} where T(x) is the 
# EGF for labeled rooted trees. And T(x) = sum n^(n-1) x^n / n!.
# 
# The number of labeled forests on {1,...,n} is sum_{k=0}^{n} C(n,k) * (k+1)^{n-k-1}... 
# no wait, let me use the correct formula.
#
# By a result attributed to Cayley: the number of labeled forests on n vertices 
# with k connected components (i.e., k trees) is C(n,k) * n^(n-k-1)... hmm, I'm
# not confident about this.
#
# Let me try a different question.

# How about: compute the permanent of the 7x7 matrix M where M[i][j] = (i+j) mod 7
# for i,j in {0,...,6}?

import itertools

def permanent(matrix):
    n = len(matrix)
    result = 0
    for perm in itertools.permutations(range(n)):
        product = 1
        for i in range(n):
            product *= matrix[i][perm[i]]
        result += product
    return result

n = 7
M = [[(i+j) % n for j in range(n)] for i in range(n)]
print("Matrix:")
for row in M:
    print(row)
print(f"Permanent: {permanent(M)}")

# What about the permanent of a matrix defined by (i*j) mod 7?
M2 = [[(i*j) % n for j in range(n)] for i in range(n)]
print("\nMatrix (i*j mod 7):")
for row in M2:
    print(row)
print(f"Permanent: {permanent(M2)}")

# Hmm, let me think of a better question involving the chromatic polynomial
# of a specific graph.

# Actually, let me ask about counting something in a specific finite group.
# How many solutions does x^2 + y^2 + z^2 = 0 have in (Z/pZ)^3 for a specific prime p?

# For p=31:
p = 31
count = 0
for x in range(p):
    for y in range(p):
        for z in range(p):
            if (x*x + y*y + z*z) % p == 0:
                count += 1
print(f"\nSolutions to x^2+y^2+z^2=0 mod {p}: {count}")
# By theory: for odd prime p, the number is p^2 + (p-1)*(-1)^((p-1)/2) * p
# Hmm, actually the formula is more complex. Let me just use the computed value.
# For p ≡ 3 mod 4: count = p^2 (I think)
# For p=31: 31 ≡ 3 mod 4, so count should be p^2 = 961? But let's see.

