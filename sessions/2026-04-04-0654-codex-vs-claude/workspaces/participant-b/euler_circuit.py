# Count Eulerian circuits starting and ending at vertex 1 in a directed graph.
# Use the BEST (de Bruijn, van Aardenne-Ehrenfest, Smith, Tutte) theorem:
# ec(G) = t_w(G) * prod_{v in V} (out_deg(v) - 1)!
# where t_w(G) is the number of arborescences rooted at w (any vertex, say 1).
# An arborescence rooted at w is a directed spanning tree where all edges point toward w
# (i.e., every vertex has a directed path to w).
# Actually, it's arborescences rooted at w where edges point AWAY from w... 
# Let me be precise.
#
# BEST theorem: the number of Eulerian circuits starting with a specific edge from vertex w is:
# t_w * prod_{v != w} (out_deg(v) - 1)! ... no wait.
#
# The BEST theorem states:
# ec(G) = t_w(G) * prod_{v in V} (d_out(v) - 1)!
# where t_w(G) is the number of arborescences rooted at w (directed spanning trees 
# where every vertex can reach w, i.e., all edges point toward w... or away?)
#
# Let me just use brute force DFS to count Eulerian circuits.

edges = [
    (1,2), (1,5), (1,8), (2,4), (2,7), (2,10), (3,1), (3,8), (3,6),
    (4,3), (4,2), (4,7), (5,3), (5,4), (5,10), (6,5), (6,2), (6,9),
    (7,1), (7,6), (7,3), (8,7), (8,9), (8,4), (9,10), (9,6), (9,8),
    (10,9), (10,5), (10,1)
]

n = 10
m = len(edges)  # 30 edges

# Build adjacency: for each vertex, list of (target, edge_index)
adj = [[] for _ in range(n + 1)]
for idx, (u, v) in enumerate(edges):
    adj[u].append((v, idx))

# DFS-based Euler circuit enumeration
count = 0
used = [False] * m

def dfs(v, depth):
    global count
    if depth == m:
        if v == 1:
            count += 1
        return
    for (w, idx) in adj[v]:
        if not used[idx]:
            used[idx] = True
            dfs(w, depth + 1)
            used[idx] = False

dfs(1, 0)
print(f"Eulerian circuits from vertex 1: {count}")
