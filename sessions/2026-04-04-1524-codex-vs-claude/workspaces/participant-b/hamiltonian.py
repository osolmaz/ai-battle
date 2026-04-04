# Count Hamiltonian cycles in graph G on {0,...,15}
# where i,j adjacent iff hamming_weight(i XOR j) in {1, 2}
# We want ordered 16-tuples starting at v0=0, visiting all vertices,
# with v15 adjacent to v0. This counts directed Hamiltonian cycles starting at 0.

def hamming_weight(n):
    return bin(n).count('1')

# Build adjacency list
n = 16
adj = [[] for _ in range(n)]
for i in range(n):
    for j in range(i+1, n):
        hw = hamming_weight(i ^ j)
        if hw in (1, 2):
            adj[i].append(j)
            adj[j].append(i)

print(f"Degree sequence: {[len(adj[i]) for i in range(n)]}")
print(f"Total edges: {sum(len(adj[i]) for i in range(n)) // 2}")

# Count Hamiltonian cycles starting at vertex 0
# Use dynamic programming with bitmask
# dp[mask][v] = number of Hamiltonian paths from 0 to v visiting exactly the vertices in mask
# mask includes vertex 0 and vertex v

from collections import defaultdict

dp = defaultdict(int)
dp[(1 << 0, 0)] = 1  # Start at vertex 0, mask = {0}

for step in range(15):  # 15 more vertices to visit
    new_dp = defaultdict(int)
    for (mask, v), count in dp.items():
        if count == 0:
            continue
        for u in adj[v]:
            if not (mask & (1 << u)):  # u not yet visited
                new_mask = mask | (1 << u)
                new_dp[(new_mask, u)] += count
    dp = new_dp
    print(f"Step {step+1}: {len(dp)} states, {sum(dp.values())} paths")

# Now count Hamiltonian cycles: paths that end at a vertex adjacent to 0
full_mask = (1 << n) - 1
total = 0
for v in adj[0]:
    total += dp.get((full_mask, v), 0)

print(f"\nNumber of directed Hamiltonian cycles starting at 0: {total}")

