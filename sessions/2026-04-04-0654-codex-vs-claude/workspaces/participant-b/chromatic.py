from itertools import combinations

def chromatic_number(adj, n):
    """Compute chromatic number by trying k-colorings for k=1,2,..."""
    for k in range(1, n+1):
        if can_color(adj, n, k, [0]*n, 0):
            return k
    return n

def can_color(adj, n, k, colors, vertex):
    if vertex == n:
        return True
    for c in range(1, k+1):
        ok = True
        for u in range(vertex):
            if adj[vertex][u] and colors[u] == c:
                ok = False
                break
        if ok:
            colors[vertex] = c
            if can_color(adj, n, k, colors, vertex + 1):
                return True
            colors[vertex] = 0
    return False

n = 6
all_edges = list(combinations(range(n), 2))  # 15 edges
num_edges = len(all_edges)

count = 0
for mask in range(1 << num_edges):
    adj = [[0]*n for _ in range(n)]
    for bit in range(num_edges):
        if mask & (1 << bit):
            u, v = all_edges[bit]
            adj[u][v] = 1
            adj[v][u] = 1
    if chromatic_number(adj, n) == 4:
        count += 1

print(f"Labeled graphs on 6 vertices with chromatic number exactly 4: {count}")
