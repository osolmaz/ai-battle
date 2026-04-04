# Verify: number of distinct simple graphs on 5 labeled vertices that are both
# connected and have an Eulerian circuit (every vertex has even degree).

from itertools import combinations

def has_eulerian_circuit(adj, n):
    """Check all vertices have even degree and graph is connected (among vertices with edges)."""
    # Check even degree
    degree = [0]*n
    edges_exist = False
    for i in range(n):
        for j in range(i+1, n):
            if adj[i][j]:
                degree[i] += 1
                degree[j] += 1
                edges_exist = True
    
    if not edges_exist:
        return False  # no edges = no circuit
    
    for i in range(n):
        if degree[i] % 2 != 0:
            return False
    return True

def is_connected(adj, n):
    """Check if the graph is connected."""
    # Find a vertex with at least one edge
    start = -1
    for i in range(n):
        for j in range(n):
            if adj[i][j]:
                start = i
                break
        if start >= 0:
            break
    if start < 0:
        return False  # no edges
    
    visited = set()
    stack = [start]
    while stack:
        v = stack.pop()
        if v in visited:
            continue
        visited.add(v)
        for u in range(n):
            if adj[v][u] and u not in visited:
                stack.append(u)
    
    # All vertices must be reachable (for connected on all 5 vertices)
    return len(visited) == n

n = 5
all_possible_edges = list(combinations(range(n), 2))
num_edges = len(all_possible_edges)  # 10

count = 0
for mask in range(1, 1 << num_edges):
    adj = [[0]*n for _ in range(n)]
    for bit in range(num_edges):
        if mask & (1 << bit):
            u, v = all_possible_edges[bit]
            adj[u][v] = 1
            adj[v][u] = 1
    
    if is_connected(adj, n) and has_eulerian_circuit(adj, n):
        count += 1

print(f"Count of connected Eulerian graphs on 5 labeled vertices: {count}")
