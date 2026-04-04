# Count directed Hamiltonian cycles starting and ending at vertex 1
# 20 vertices, use DFS with bitmask

edges = [
    (1,7),(1,10),(2,10),(3,8),(3,10),(3,19),(3,20),(4,1),(4,2),(4,10),
    (4,11),(4,12),(4,14),(5,1),(5,7),(5,8),(5,10),(5,15),(6,4),(6,13),
    (6,14),(7,5),(7,10),(7,12),(7,18),(8,4),(8,13),(9,8),(9,15),(9,18),
    (9,20),(10,3),(10,4),(10,15),(10,18),(10,19),(11,1),(11,3),(11,4),
    (11,6),(11,8),(11,10),(11,12),(11,13),(12,1),(12,2),(12,8),(12,9),
    (13,2),(13,4),(13,6),(13,11),(13,12),(13,17),(13,18),(14,1),(14,3),
    (14,7),(14,19),(14,20),(15,10),(15,11),(15,13),(15,17),(16,17),
    (17,5),(17,10),(17,11),(17,14),(17,15),(18,1),(18,3),(18,4),(18,16),
    (18,17),(18,19),(18,20),(19,7),(19,8),(19,14),(19,16),(19,18),
    (20,2),(20,6),(20,19)
]

n = 20
adj = [[] for _ in range(n + 1)]
for u, v in edges:
    adj[u].append(v)

# Check which vertices can reach vertex 1 (to prune)
can_reach_1 = set()
for u, v in edges:
    if v == 1:
        can_reach_1.add(u)

# DFS with bitmask
count = 0
full_mask = (1 << n) - 1

def dfs(node, visited_mask, depth):
    global count
    if depth == n:
        # Check if there's an edge back to 1
        if 1 in adj[node]:
            count += 1
        return
    for nb in adj[node]:
        bit = 1 << (nb - 1)
        if not (visited_mask & bit):
            dfs(nb, visited_mask | bit, depth + 1)

# Start at vertex 1
dfs(1, 1 << 0, 1)
print(f"Directed Hamiltonian cycles from 1: {count}")
