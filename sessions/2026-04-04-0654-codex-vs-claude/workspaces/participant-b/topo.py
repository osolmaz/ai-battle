from itertools import permutations

# Define edges
edges = [
    ('A','H'), ('B','G'), ('B','H'), ('B','I'), ('B','L'),
    ('C','D'), ('C','F'), ('C','G'), ('C','J'),
    ('D','L'), ('E','G'), ('E','J'), ('E','L'),
    ('F','I'), ('H','K'), ('H','L'), ('J','K'), ('K','L')
]

vertices = list('ABCDEFGHIJKL')

# Build adjacency for topological check
# For each edge u->v, u must come before v
prereqs = {v: set() for v in vertices}
for u, v in edges:
    prereqs[v].add(u)

# Use recursive counting with memoization
# State: set of remaining vertices
# Available: vertices whose all prerequisites are already placed

from functools import lru_cache

edge_set = set(edges)

# Build successor and predecessor lists
preds = {v: set() for v in vertices}
for u, v in edges:
    preds[v].add(u)

def count_topo():
    # Use bitmask approach
    n = len(vertices)
    idx = {v: i for i, v in enumerate(vertices)}
    
    # Precompute predecessor masks
    pred_mask = [0] * n
    for v in vertices:
        for p in preds[v]:
            pred_mask[idx[v]] |= (1 << idx[p])
    
    # DP with bitmask: dp[mask] = number of topological orderings using exactly the vertices in mask
    full = (1 << n) - 1
    dp = [0] * (1 << n)
    dp[0] = 1
    
    for mask in range(full):
        if dp[mask] == 0:
            continue
        # Find available vertices not in mask whose preds are all in mask
        for i in range(n):
            if mask & (1 << i):
                continue  # already placed
            if (pred_mask[i] & mask) == pred_mask[i]:
                # All predecessors of i are in mask
                new_mask = mask | (1 << i)
                dp[new_mask] += dp[mask]
    
    return dp[full]

print(count_topo())
