# I'm leading 12-11. Let me ask a solid question.
# Let me try something involving counting with multiple constraints that's
# hard to get right but straightforward to verify.

# How about: Count the number of 6x6 binary matrices that are symmetric 
# (M = M^T) AND have all row sums equal to 3?
# This means: symmetric 0-1 matrix, 6x6, each row sums to 3.
# Since symmetric, column sums also = 3.
# This is counting 3-regular simple graphs on 6 labeled vertices.

from itertools import combinations

n = 6
target_degree = 3

# A symmetric binary matrix with zero diagonal and row sums = 3
# is a 3-regular graph on 6 vertices.
# Enumerate all possible edge sets.
all_edges = list(combinations(range(n), 2))  # 15 possible edges

count = 0
for mask in range(1 << len(all_edges)):
    degree = [0] * n
    for bit in range(len(all_edges)):
        if mask & (1 << bit):
            u, v = all_edges[bit]
            degree[u] += 1
            degree[v] += 1
    if all(d == target_degree for d in degree):
        count += 1

print(f"3-regular graphs on 6 labeled vertices: {count}")
# Known answer: should be 70

# That's too simple and well-known. Let me try something else.

# How about counting the number of ways to seat 10 people around a circular table
# such that no two of a specific set of pairs are adjacent?
# This is counting Hamiltonian cycles in the complement graph.

# Actually let me try something different: count the number of labeled 
# connected bipartite graphs on vertex set {1,...,4} ∪ {5,...,8}
# (i.e., bipartition {1,2,3,4} and {5,6,7,8}).

from collections import deque

A = [1, 2, 3, 4]
B = [5, 6, 7, 8]
# Possible edges: each a in A to each b in B: 4*4 = 16 edges
bipartite_edges = [(a, b) for a in A for b in B]
num_edges = len(bipartite_edges)

def is_connected(edge_mask):
    adj = {v: [] for v in A + B}
    for bit in range(num_edges):
        if edge_mask & (1 << bit):
            u, v = bipartite_edges[bit]
            adj[u].append(v)
            adj[v].append(u)
    
    visited = set()
    q = deque([1])
    visited.add(1)
    while q:
        v = q.popleft()
        for u in adj[v]:
            if u not in visited:
                visited.add(u)
                q.append(u)
    return len(visited) == 8

count_connected = 0
for mask in range(1, 1 << num_edges):
    if is_connected(mask):
        count_connected += 1

print(f"Connected labeled bipartite graphs on K_4,4: {count_connected}")
