# Let me ask about counting the number of distinct ways to express a number
# as an ordered sum (composition) with specific constraints.
# 
# Or better: ask about a less common combinatorial object.
#
# How about: Count the number of labeled forests on n vertices with exactly k trees?
# That's n^(k-1) * C(n,k) * ... actually it uses Cayley-like formulas.
#
# Let me try something different: count the number of abelian groups of a given order.
# The number of abelian groups of order n depends on the prime factorization of n.
# For n = p1^a1 * p2^a2 * ..., it's product of p(ai) where p is the partition function.
#
# Too easy if you know the formula.
#
# Let me try: What is the number of non-isomorphic simple graphs on 8 vertices?
# This is a well-known sequence value. Answer: 12346. Too easy to look up.
#
# How about computing the Tutte polynomial of a specific graph at a specific point?
# 
# Actually, let me try a question about counting the number of maximal independent sets
# in a specific graph, or the number of maximum matchings.
#
# Let me ask: How many perfect matchings does the following bipartite graph have?
# With a specific biadjacency matrix.

# Actually, the permanent of the biadjacency matrix gives the number of perfect matchings.
# I already asked a permanent question. Let me try something else.

# How about: What is the Wiener index of a specific graph?
# The Wiener index is the sum of all pairwise shortest path distances.

# Let me create a graph and compute it.
from collections import deque

# Graph on 15 vertices with specific edges
edges = [
    (0,1),(0,4),(0,7),(1,2),(1,5),(2,3),(2,6),(3,7),(3,10),
    (4,5),(4,8),(5,6),(5,9),(6,7),(6,11),(7,12),(8,9),(8,13),
    (9,10),(9,14),(10,11),(10,13),(11,12),(11,14),(12,13),(13,14)
]

n = 15
adj = [[] for _ in range(n)]
for u,v in edges:
    adj[u].append(v)
    adj[v].append(u)

# BFS from each vertex to compute all pairwise distances
def bfs(start):
    dist = [-1]*n
    dist[start] = 0
    q = deque([start])
    while q:
        v = q.popleft()
        for u in adj[v]:
            if dist[u] == -1:
                dist[u] = dist[v] + 1
                q.append(u)
    return dist

wiener = 0
for v in range(n):
    dists = bfs(v)
    wiener += sum(dists)
wiener //= 2  # each pair counted twice

print(f"Wiener index: {wiener}")

# Hmm, this is probably too easy. Let me think of something harder.

# Let me count independent sets in a graph.
# An independent set is a set of vertices with no edges between them.
# Count ALL independent sets (including empty set).

edges2 = [
    (0,1),(0,3),(0,5),(1,2),(1,4),(2,3),(2,5),(2,7),
    (3,4),(3,6),(4,5),(4,7),(4,9),(5,6),(5,8),
    (6,7),(6,9),(6,11),(7,8),(7,10),(8,9),(8,11),
    (9,10),(10,11)
]

n2 = 12
adj2_set = set()
for u,v in edges2:
    adj2_set.add((u,v))
    adj2_set.add((v,u))

# Brute force: check all 2^12 subsets
count_ind = 0
for mask in range(1 << n2):
    independent = True
    verts = [i for i in range(n2) if mask & (1 << i)]
    for i in range(len(verts)):
        for j in range(i+1, len(verts)):
            if (verts[i], verts[j]) in adj2_set:
                independent = False
                break
        if not independent:
            break
    if independent:
        count_ind += 1

print(f"Independent sets (including empty): {count_ind}")

# The independence polynomial evaluated at 1 gives this count.
# Let's exclude the empty set
print(f"Non-empty independent sets: {count_ind - 1}")
