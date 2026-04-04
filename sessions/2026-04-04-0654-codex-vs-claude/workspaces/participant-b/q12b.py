# Eulerian numbers are well-known, so let me try something less standard.
# 
# How about: count permutations of {1,...,10} that avoid both 2143 and 1324?
# Pattern avoidance with two patterns simultaneously is less standard.

# Actually, let me try: count the number of permutations of {1,...,9} 
# where no element is more than 2 positions away from its original position.
# I.e., |sigma(i) - i| <= 2 for all i.

from itertools import permutations

n = 9
max_displacement = 2

count = 0
for perm in permutations(range(1, n+1)):
    valid = True
    for i in range(n):
        if abs(perm[i] - (i+1)) > max_displacement:
            valid = False
            break
    if valid:
        count += 1

print(f"Permutations of {{1,...,{n}}} with max displacement {max_displacement}: {count}")

# Let me try n=11, displacement 3
n2 = 11
max_d2 = 3
# This might be too slow with brute force for n=11... let me check timing
import time

# Actually n=11 has 11! = 39916800 permutations, too slow for brute force.
# Let me use DP instead.

# DP approach: place elements one by one
# State: which elements have been placed (bitmask) and current position
# Actually, the constraint is |sigma(i) - i| <= d, i.e., position i can hold values in [i-d, i+d]

# Better: this is counting perfect matchings in a bipartite graph
# where position i is connected to value j iff |i-j| <= d.
# This is equivalent to the permanent of a 0-1 matrix.

def count_bounded_perms(n, d):
    # DP with bitmask: which values have been used
    # Process positions 0, 1, ..., n-1 (0-indexed, representing 1,...,n)
    dp = {0: 1}  # mask -> count
    for pos in range(n):
        new_dp = {}
        for mask, ways in dp.items():
            # Position pos+1 (1-indexed) can hold values in [pos+1-d, pos+1+d]
            for val in range(max(1, pos+1-d), min(n, pos+1+d) + 1):
                bit = 1 << (val - 1)
                if not (mask & bit):
                    new_mask = mask | bit
                    new_dp[new_mask] = new_dp.get(new_mask, 0) + ways
        dp = new_dp
    
    full = (1 << n) - 1
    return dp.get(full, 0)

# Verify with brute force result
print(f"DP verification for n={n}, d={max_displacement}: {count_bounded_perms(n, max_displacement)}")

# Now compute harder cases
for nn, dd in [(12, 3), (14, 3), (13, 3)]:
    result = count_bounded_perms(nn, dd)
    print(f"n={nn}, d={dd}: {result}")
