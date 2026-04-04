# Kneser graph KG(11,4): vertices are 4-element subsets of {1,...,11}
# Two vertices adjacent iff disjoint.
# Number of vertices: C(11,4) = 330
# 
# This is a 330-vertex graph. Computing spanning trees requires the 
# Laplacian eigenvalues via Kirchhoff's theorem.
#
# KG(11,4) is a vertex-transitive graph. Its eigenvalues can be computed
# using the theory of association schemes (Johnson scheme).
#
# For the Kneser graph KG(n,k), the eigenvalues of the adjacency matrix are:
# lambda_j = (-1)^j * C(n-k-j, k-j) for j = 0, 1, ..., k
# with multiplicity C(n,j) - C(n,j-1) for j >= 1, and multiplicity 1 for j=0.
#
# Wait, let me recall the correct formula.
# For KG(n,k), the eigenvalues are:
# lambda_j = (-1)^j * C(n-k-j, k-j) for j = 0, 1, ..., k
# with multiplicity m_j = C(n,j) - C(n,j-1)
# where C(n,-1) = 0.
#
# For KG(11,4):
# n=11, k=4
# j=0: lambda_0 = (-1)^0 * C(11-4-0, 4-0) = C(7,4) = 35
#       m_0 = C(11,0) - C(11,-1) = 1 - 0 = 1
# j=1: lambda_1 = (-1)^1 * C(11-4-1, 4-1) = -C(6,3) = -20
#       m_1 = C(11,1) - C(11,0) = 11 - 1 = 10
# j=2: lambda_2 = (-1)^2 * C(11-4-2, 4-2) = C(5,2) = 10
#       m_2 = C(11,2) - C(11,1) = 55 - 11 = 44
# j=3: lambda_3 = (-1)^3 * C(11-4-3, 4-3) = -C(4,1) = -4
#       m_3 = C(11,3) - C(11,2) = 165 - 55 = 110
# j=4: lambda_4 = (-1)^4 * C(11-4-4, 4-4) = C(3,0) = 1
#       m_4 = C(11,4) - C(11,3) = 330 - 165 = 165

# Check: sum of multiplicities = 1 + 10 + 44 + 110 + 165 = 330 ✓ (= C(11,4))

# Degree of KG(11,4) = C(11-4, 4) = C(7,4) = 35 (number of 4-subsets of {1,...,11}\S for any 4-subset S)
# This matches lambda_0 = 35. ✓

# Laplacian eigenvalues: mu_j = degree - lambda_j = 35 - lambda_j
# mu_0 = 35 - 35 = 0 (multiplicity 1) ✓
# mu_1 = 35 - (-20) = 55 (multiplicity 10)
# mu_2 = 35 - 10 = 25 (multiplicity 44)
# mu_3 = 35 - (-4) = 39 (multiplicity 110)
# mu_4 = 35 - 1 = 34 (multiplicity 165)

# Number of spanning trees by Kirchhoff:
# tau = (1/330) * prod of non-zero Laplacian eigenvalues
# = (1/330) * 55^10 * 25^44 * 39^110 * 34^165

from math import comb
import sys

n, k = 11, 4
num_vertices = comb(n, k)
print(f"KG({n},{k}): {num_vertices} vertices")

eigenvalues = []
for j in range(k+1):
    lam = ((-1)**j) * comb(n-k-j, k-j)
    mult = comb(n, j) - (comb(n, j-1) if j > 0 else 0)
    eigenvalues.append((j, lam, mult))
    print(f"  j={j}: lambda={lam}, multiplicity={mult}")

degree = eigenvalues[0][1]
print(f"Degree: {degree}")

laplacian_eigs = []
for j, lam, mult in eigenvalues:
    mu = degree - lam
    laplacian_eigs.append((mu, mult))
    print(f"  Laplacian eigenvalue: {mu}, multiplicity: {mult}")

# Spanning trees = (1/n_vertices) * product of non-zero Laplacian eigenvalues
print(f"\nSpanning trees = (1/{num_vertices}) * ", end="")
terms = []
for mu, mult in laplacian_eigs:
    if mu != 0:
        terms.append(f"{mu}^{mult}")
print(" * ".join(terms))

# Compute the prime factorization
# tau = 55^10 * 25^44 * 39^110 * 34^165 / 330

# Factor each:
# 55 = 5 * 11
# 25 = 5^2
# 39 = 3 * 13
# 34 = 2 * 17
# 330 = 2 * 3 * 5 * 11

# Numerator prime factorization:
# 55^10 = 5^10 * 11^10
# 25^44 = 5^88
# 39^110 = 3^110 * 13^110
# 34^165 = 2^165 * 17^165

# Total numerator: 2^165 * 3^110 * 5^(10+88) * 11^10 * 13^110 * 17^165
# = 2^165 * 3^110 * 5^98 * 11^10 * 13^110 * 17^165

# Denominator: 330 = 2 * 3 * 5 * 11

# tau = 2^(165-1) * 3^(110-1) * 5^(98-1) * 11^(10-1) * 13^110 * 17^165
# = 2^164 * 3^109 * 5^97 * 11^9 * 13^110 * 17^165

print(f"\nPrime factorization:")
print(f"tau = 2^164 * 3^109 * 5^97 * 11^9 * 13^110 * 17^165")

# Verify by computing the actual number
tau_num = 55**10 * 25**44 * 39**110 * 34**165
tau = tau_num // 330
assert tau_num % 330 == 0, "Not divisible!"
print(f"\nVerification: tau_num divisible by 330: True")

# Verify prime factorization
remaining = tau
for p, e in [(2, 164), (3, 109), (5, 97), (11, 9), (13, 110), (17, 165)]:
    for _ in range(e):
        assert remaining % p == 0, f"Not divisible by {p}"
        remaining //= p
print(f"After removing all prime factors: {remaining}")
assert remaining == 1, "Factorization incomplete!"
print("Prime factorization verified!")

