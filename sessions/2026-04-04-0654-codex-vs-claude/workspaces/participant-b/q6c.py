# Count proper 4-colorings of a specific graph
# Use inclusion-exclusion / deletion-contraction or brute force

from itertools import product

# Let me create an interesting graph - a graph on 9 vertices
edges = [
    (0,1), (0,2), (0,3), (1,2), (1,4), (1,5), (2,3), (2,5), (2,6),
    (3,6), (3,7), (4,5), (4,8), (5,6), (5,8), (6,7), (6,8), (7,8)
]

n = 9
k = 4  # number of colors

adj_set = set()
for u,v in edges:
    adj_set.add((u,v))
    adj_set.add((v,u))

# Brute force count proper k-colorings
count = 0
for coloring in product(range(k), repeat=n):
    proper = True
    for u, v in edges:
        if coloring[u] == coloring[v]:
            proper = False
            break
    if proper:
        count += 1

print(f"Number of proper {k}-colorings: {count}")

# Also compute the full chromatic polynomial for verification
for kk in range(1, 6):
    c = 0
    for coloring in product(range(kk), repeat=n):
        proper = True
        for u, v in edges:
            if coloring[u] == coloring[v]:
                proper = False
                break
        if proper:
            c += 1
    print(f"P({kk}) = {c}")
