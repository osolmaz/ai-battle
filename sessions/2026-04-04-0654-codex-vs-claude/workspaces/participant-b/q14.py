# Let me try a question about counting the number of ways to tile a region
# with a mix of tile types, or something requiring careful constraint handling.
#
# How about: Count the number of labeled directed acyclic graphs on 7 vertices
# (i.e., DAGs on {1,...,7}).
#
# This is a well-known sequence but the values get large and require careful computation.
# The formula uses inclusion-exclusion: a(n) = sum_{k=1}^{n} (-1)^{k+1} * C(n,k) * 2^{k*(n-k)} * a(n-k)
# with a(0) = 1.

from math import comb

def count_dags(n):
    a = [0] * (n + 1)
    a[0] = 1
    for m in range(1, n + 1):
        s = 0
        for k in range(1, m + 1):
            s += ((-1) ** (k + 1)) * comb(m, k) * (2 ** (k * (m - k))) * a[m - k]
        a[m] = s
    return a[n]

# Known values:
# a(1) = 1
# a(2) = 3
# a(3) = 25
# a(4) = 543
# a(5) = 29281

for i in range(1, 9):
    print(f"DAGs on {i} vertices: {count_dags(i)}")

# These might be looked up. Let me try something less standard.
# How about counting DAGs with a specific number of edges?
# Or counting DAGs on 6 vertices with exactly 8 edges?

# Actually, let me try: count the number of labeled DAGs on 6 vertices 
# that have exactly one source (vertex with in-degree 0) and exactly one sink (vertex with out-degree 0).

# For 6 vertices, total possible directed graphs = 2^30, but DAGs are much fewer.
# Let me enumerate.

n = 6
from itertools import combinations

# A DAG on n vertices can be represented by a topological ordering + edges
# But easier: enumerate all possible edge sets and check acyclicity.
# 2^(6*5/2) for undirected = 2^15, but for directed 2^(6*5) = 2^30... too many.
# Wait, for a DAG edges go from lower to higher in some topological order.
# There are n! topological orders, and for each, 2^(n*(n-1)/2) possible edge sets.
# But this overcounts since different orders can give same DAG.

# Better: use the fact that a DAG on {1,...,n} has a topological ordering.
# Enumerate by choosing which edges exist among all n*(n-1)/2 = 15 possible
# "forward" edges for each permutation... this is getting complicated.

# Let me just enumerate all 2^(n*(n-1)) possible directed graphs on 6 vertices
# and check which are DAGs. n*(n-1) = 30... 2^30 ≈ 10^9, too slow.

# Better approach: enumerate DAGs using the topological ordering.
# A DAG is uniquely determined by its edge set, and there exists at least one
# topological ordering. We can enumerate by layers.

# Actually, for n=6, the total number of DAGs is 3781503 (from the formula above).
# Let me filter for sources and sinks.

# For small n, I can use a different approach: enumerate all DAGs on 6 vertices
# by considering the partial order structure.

# Actually, let me change the question entirely. Let me ask something about
# counting specific types of functions or mappings.

# How about: count the number of labeled posets on 5 elements?
# This is T0 topologies, or equivalently, partial orders.
# Known: the number of partial orders on 5 elements is 4231.
# Too well-known.

# Let me try: how many non-isomorphic groups of order 720?
# 720 = 16 * 45 = 2^4 * 3^2 * 5. Hmm, this is hard to compute.

# Let me go back to something computational but less standard.
# 
# Question: Consider the group S_7 (symmetric group on 7 elements).
# How many elements of S_7 have order exactly 12?

from math import gcd
from itertools import permutations

def lcm(a, b):
    return a * b // gcd(a, b)

def perm_order(p):
    """Compute the order of permutation p (given as a tuple, 0-indexed)."""
    n = len(p)
    visited = [False] * n
    order = 1
    for i in range(n):
        if not visited[i]:
            cycle_len = 0
            j = i
            while not visited[j]:
                visited[j] = True
                j = p[j]
                cycle_len += 1
            order = lcm(order, cycle_len)
    return order

n = 7
target_order = 12
count = 0
for p in permutations(range(n)):
    if perm_order(p) == target_order:
        count += 1

print(f"Elements of S_7 with order 12: {count}")

# Also try order 10 and 6 for cross-checking
for target in [6, 10, 12, 15]:
    c = sum(1 for p in permutations(range(n)) if perm_order(p) == target)
    print(f"  Order {target}: {c}")
