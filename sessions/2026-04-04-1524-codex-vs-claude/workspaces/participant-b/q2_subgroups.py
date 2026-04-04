from itertools import permutations, combinations

# Verify: number of subgroups of A_5

# Represent A_5 as even permutations of {0,1,2,3,4}
def is_even_perm(p):
    """Check if permutation is even"""
    n = len(p)
    visited = [False] * n
    cycles = 0
    for i in range(n):
        if not visited[i]:
            cycles += 1
            j = i
            while not visited[j]:
                visited[j] = True
                j = p[j]
    return (n - cycles) % 2 == 0

def compose(p, q):
    """Compose permutations: first apply q, then p"""
    return tuple(p[q[i]] for i in range(len(p)))

def inverse(p):
    """Inverse permutation"""
    inv = [0] * len(p)
    for i, v in enumerate(p):
        inv[v] = i
    return tuple(inv)

# Generate A_5
identity = (0, 1, 2, 3, 4)
A5 = [p for p in permutations(range(5)) if is_even_perm(p)]
print(f"|A_5| = {len(A5)}")

# Convert to frozenset-friendly format
A5_set = set(A5)

def order_of(g):
    """Order of element g"""
    curr = g
    for i in range(1, 61):
        if curr == identity:
            return i
        curr = compose(curr, g)
    return -1

# Generate subgroup from a set of generators
def generate_subgroup(generators):
    subgroup = {identity}
    queue = list(generators)
    while queue:
        g = queue.pop()
        if g in subgroup:
            continue
        new_elements = set()
        for h in list(subgroup):
            for prod in [compose(g, h), compose(h, g), inverse(g)]:
                if prod not in subgroup and prod not in new_elements:
                    new_elements.add(prod)
                    queue.append(prod)
        subgroup.add(g)
        subgroup.update(new_elements)
    # Ensure closure
    changed = True
    while changed:
        changed = False
        elems = list(subgroup)
        for a in elems:
            for b in elems:
                p = compose(a, b)
                if p not in subgroup:
                    subgroup.add(p)
                    changed = True
    return frozenset(subgroup)

# Find all subgroups by trying all subsets of generators
# More efficient: try all pairs of elements
all_subgroups = set()

# Single-generated subgroups
for g in A5:
    sg = generate_subgroup([g])
    all_subgroups.add(sg)

print(f"After single generators: {len(all_subgroups)} subgroups")

# Two-generated subgroups
for g1, g2 in combinations(A5, 2):
    sg = generate_subgroup([g1, g2])
    all_subgroups.add(sg)

print(f"After pairs: {len(all_subgroups)} subgroups")

# Count by order
from collections import Counter
order_counts = Counter(len(sg) for sg in all_subgroups)
print(f"\nSubgroups by order: {dict(sorted(order_counts.items()))}")
print(f"\nTotal number of subgroups: {len(all_subgroups)}")

