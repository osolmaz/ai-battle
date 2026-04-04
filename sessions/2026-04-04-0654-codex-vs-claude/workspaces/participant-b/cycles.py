# Count distinct simple directed cycles of length >= 3
# Two cycles are the same if one is a cyclic rotation of the other.
# So we count each cycle once, canonicalized by smallest vertex first.

edges_list = [
    (1,10), (11,1), (13,1), (16,1),
    (2,7), (2,10), (12,2),
    (3,6), (11,3), (16,3),
    (4,7), (4,12), (4,15), (4,18), (4,19),
    (8,5), (5,12), (5,16), (5,17),
    (6,7), (10,6), (13,6),
    (9,7), (11,7), (17,7), (19,7),
    (7,13), (7,14),
    (8,10), (14,8), (17,8),
    (10,9), (9,11), (12,9), (13,9), (9,16), (9,19),
    (10,15), (16,10), (10,19),
    (11,14), (11,15), (11,16),
    (12,14), (15,12), (12,16),
    (16,13), (17,13),
    (15,16), (16,17), (16,19),
    (17,18), (19,17), (19,18)
]

n = 19
adj = [[] for _ in range(n + 1)]
edge_set = set()
for u, v in edges_list:
    adj[u].append(v)
    edge_set.add((u, v))

# DFS: enumerate all simple cycles where the smallest vertex in the cycle is the starting vertex.
# Start from each vertex v, only visit vertices >= v (except when returning to v).

count = 0

def dfs(start, current, visited, length):
    global count
    for nb in adj[current]:
        if nb == start and length >= 3:
            count += 1
        elif nb > start and nb not in visited:
            visited.add(nb)
            dfs(start, nb, visited, length + 1)
            visited.remove(nb)

for start in range(1, n + 1):
    visited = {start}
    dfs(start, start, visited, 1)

print(f"Number of simple directed cycles (length >= 3): {count}")
