from math import comb
from itertools import combinations

# Count lattice paths from (0,0) to (12,12) using steps R=(1,0) and U=(0,1)
# that avoid all forbidden points.

forbidden = [(3,3), (6,6), (9,9), (4,8), (8,4)]

# Total paths without restriction
total = comb(24, 12)
print(f"Total unrestricted paths: {total}")

# Number of paths from (a,b) to (c,d) = C((c-a)+(d-b), c-a) if c>=a and d>=b, else 0
def paths(a, b, c, d):
    if c < a or d < b:
        return 0
    return comb((c-a)+(d-b), c-a)

# Inclusion-exclusion on subsets of forbidden points
# A path passes through a subset S of forbidden points if it passes through all of them.
# The points must be orderable (each coordinate non-decreasing) for a monotone path to visit all.

# For a subset of forbidden points, sort them and check if they form a chain
# (each point dominates the previous in both coordinates).
# If not a chain, no path can visit all of them, so contribution is 0.

# Actually, for lattice paths with only R and U steps, a path visits a set of points
# iff those points can be ordered as a chain where each is coordinate-wise ≤ the next.
# If the forbidden points form an antichain subset, no single path visits all of them.

# We need paths through ALL points in a subset S. For this, the points in S must form
# a chain. Sort them and check.

def count_paths_through_all(points, dest=(12,12)):
    """Count paths from (0,0) to dest passing through all given points (in some order on the path)."""
    # Sort points; they must form a chain
    pts = sorted(points)
    # Check chain property
    for i in range(len(pts)-1):
        if pts[i+1][0] < pts[i][0] or pts[i+1][1] < pts[i][1]:
            return 0
    # Count paths through all points in order
    prev = (0, 0)
    result = 1
    for p in pts:
        result *= paths(prev[0], prev[1], p[0], p[1])
        prev = p
    result *= paths(prev[0], prev[1], dest[0], dest[1])
    return result

# Inclusion-exclusion
answer = 0
for k in range(len(forbidden) + 1):
    for subset in combinations(forbidden, k):
        c = count_paths_through_all(list(subset))
        if k % 2 == 0:
            answer += c
        else:
            answer -= c

print(f"Paths avoiding all forbidden points: {answer}")

# Verify with a simpler case: no forbidden points
print(f"Verification (no forbidden): {comb(24,12)}")
