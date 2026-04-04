# Last question - I'm leading 10-9, so even if opponent gets this right I still win.
# But let me ask a good question anyway.
#
# Let me try: count the number of 5x5 Latin squares where the first row is (1,2,3,4,5).
# These are called "reduced" or "normalized" Latin squares with first row fixed.
# The number of reduced Latin squares of order 5 is 161280.
# But that's the number with BOTH first row and first column in natural order.
# With only first row fixed: 161280 * 5! / ... hmm.
#
# Actually, the number of Latin squares of order 5 is 161280.
# Number with first row = (1,2,3,4,5) is 161280 / 5! = ... wait no.
# Total Latin squares of order 5 = 161280.
# Fixing first row to (1,2,3,4,5): 161280 / 5! = ... 
# Actually no: 161280 is already the "reduced" count (first row fixed).
# Total = 161280 * 5! = 161280 * 120 = 19353600... that doesn't match known value.
# Known: total Latin squares of order 5 = 161280. And reduced (first row AND column fixed) = 56.
# So first-row-fixed = 56 * 4! = 56 * 24 = 1344... hmm that also seems off.
# 
# Let me just look at this: reduced LS of order 5 (first row and column normalized) = 56.
# First row only normalized: 56 * 4! = 1344? No: if first row is fixed, first column 
# can be any permutation starting with 1, so there are 4! choices for the rest of column 1.
# But these give non-isomorphic squares. So first-row-fixed = 56 * 4! = 1344.
# Total = 1344 * 5! = 161280. Yes, that matches.
#
# OK so the count with first row fixed is 1344, which is well-known.
# Let me try something harder.

# How about: count the number of ways to place 10 non-attacking rooks on a 10x10 board
# where certain squares are forbidden?
# This is the permanent of a 0-1 matrix.

# Let me design a specific 10x10 0-1 matrix and compute its permanent.
# Use a matrix with an interesting pattern.

# Matrix: M[i][j] = 1 if (i+j) mod 3 != 0 or |i-j| <= 3
# Let me just define it explicitly.

import random
random.seed(42)

# Actually let me just create a specific matrix
M = [
    [1,1,0,1,1,0,1,0,1,1],
    [1,0,1,1,0,1,0,1,1,0],
    [0,1,1,0,1,1,1,0,0,1],
    [1,1,0,1,0,1,1,1,0,1],
    [1,0,1,0,1,1,0,1,1,0],
    [0,1,1,1,1,0,1,0,1,1],
    [1,0,1,1,0,1,1,1,0,0],
    [0,1,0,1,1,0,1,1,1,1],
    [1,1,1,0,1,1,0,0,1,1],
    [1,0,1,1,0,1,1,1,0,1],
]

from itertools import permutations

n = 10
perm_count = 0
for sigma in permutations(range(n)):
    prod = 1
    for i in range(n):
        if M[i][sigma[i]] == 0:
            prod = 0
            break
    perm_count += prod

print(f"Permanent of matrix: {perm_count}")

# Also verify with Ryser's formula
def permanent_ryser(matrix):
    n = len(matrix)
    total = 0
    for mask in range(1, 1 << n):
        bits = bin(mask).count('1')
        prod = 1
        for i in range(n):
            s = 0
            for j in range(n):
                if mask & (1 << j):
                    s += matrix[i][j]
            prod *= s
        if (n - bits) % 2 == 0:
            total += prod
        else:
            total -= prod
    if n % 2 == 1:
        total = -total
    return total

ryser_result = permanent_ryser(M)
print(f"Ryser verification: {ryser_result}")
