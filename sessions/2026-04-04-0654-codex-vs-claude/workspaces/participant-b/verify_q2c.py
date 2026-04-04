# Let me ask about a specific combinatorial/algorithmic problem

# Question: How many ways can you place 8 non-attacking rooks on an 8x8 chessboard
# such that no rook is on the main diagonal (cells where row == column)?
# This is D_8 * 8! / 8! = D_8... no wait.
# 
# Actually: place 8 non-attacking rooks = one per row, one per column = a permutation.
# No rook on the main diagonal = a derangement.
# D_8 = 8! * sum_{k=0}^{8} (-1)^k / k!
# D_8 = 40320 * (1 - 1 + 1/2 - 1/6 + 1/24 - 1/120 + 1/720 - 1/5040 + 1/40320)
# = 40320 * (1/2 - 1/6 + 1/24 - 1/120 + 1/720 - 1/5040 + 1/40320)

import math

n = 8
D_n = 0
for k in range(n+1):
    D_n += ((-1)**k) * math.factorial(n) // math.factorial(k)

print(f"D_8 = {D_n}")

# That's 14833 - too well known. Let me think of something harder.

# Better question: combinatorics with constraints
# How many labeled simple graphs on vertices {1,...,7} have exactly 3 connected components?

from itertools import combinations

def count_components(adj, n):
    visited = [False]*n
    components = 0
    for start in range(n):
        if not visited[start]:
            components += 1
            stack = [start]
            while stack:
                v = stack.pop()
                if visited[v]:
                    continue
                visited[v] = True
                for u in range(n):
                    if adj[v][u] and not visited[u]:
                        stack.append(u)
    return components

n = 7
all_edges = list(combinations(range(n), 2))  # 21 edges
num_edges = len(all_edges)

count = 0
for mask in range(1 << num_edges):
    adj = [[0]*n for _ in range(n)]
    for bit in range(num_edges):
        if mask & (1 << bit):
            u, v = all_edges[bit]
            adj[u][v] = 1
            adj[v][u] = 1
    if count_components(adj, n) == 3:
        count += 1

print(f"Labeled graphs on 7 vertices with exactly 3 components: {count}")
