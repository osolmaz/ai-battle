# Verify by subset enumeration approach
from itertools import combinations

edges = [
    (1,2), (1,3), (1,5), (2,3), (2,4), (2,6), (3,5), (3,7),
    (4,5), (4,6), (4,8), (5,7), (5,9), (6,8), (6,10),
    (7,9), (7,10), (8,9), (8,10), (9,10)
]

n = 10
edge_set = set()
for u,v in edges:
    edge_set.add((u,v))
    edge_set.add((v,u))

# A simple cycle on a subset S of vertices exists iff we can find a Hamiltonian cycle
# in the induced subgraph on S. But that's not right either - the cycle uses specific
# edges from the original graph but must form a single cycle on the subset.
# 
# Actually: a simple cycle corresponds to a subset S of vertices (|S| >= 3) and 
# a set of |S| edges forming a cycle on those vertices. 
# 
# Alternative: enumerate subsets, for each check how many Hamiltonian cycles exist
# in the induced subgraph.

def count_ham_cycles_in_subset(subset):
    """Count Hamiltonian cycles in the induced subgraph on subset, divided by 2 for direction."""
    if len(subset) < 3:
        return 0
    verts = sorted(subset)
    k = len(verts)
    idx = {v: i for i, v in enumerate(verts)}
    
    # Build adjacency for subset
    sub_adj = [[] for _ in range(k)]
    for i, u in enumerate(verts):
        for j, v in enumerate(verts):
            if i < j and (u, v) in edge_set:
                sub_adj[i].append(j)
                sub_adj[j].append(i)
    
    # Count Hamiltonian cycles starting from vertex 0 (smallest)
    count = 0
    def dfs(current, visited_mask, depth):
        nonlocal count
        if depth == k:
            if 0 in [x for x in sub_adj[current] if x == 0]:
                count += 1
            return
        for nb in sub_adj[current]:
            if not (visited_mask & (1 << nb)):
                dfs(nb, visited_mask | (1 << nb), depth + 1)
    
    dfs(0, 1, 1)
    return count // 2  # each cycle counted twice (two directions)

total = 0
vertices = list(range(1, n+1))
for size in range(3, n+1):
    for subset in combinations(vertices, size):
        total += count_ham_cycles_in_subset(subset)

print(f"Total simple cycles (subset method): {total}")
