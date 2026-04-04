# Let me ask something about counting specific substructures in a well-defined graph.
# 
# How about: count the number of vertex covers of size exactly 8 in a specific graph?
# A vertex cover is a set of vertices such that every edge has at least one endpoint in the set.

# Or: count the number of maximal cliques in a specific graph.

# Actually let me try: How many non-negative integer solutions does the system
# x1 + x2 + x3 = 15
# x1 + x4 + x5 = 12
# x2 + x4 + x6 = 10
# x3 + x5 + x6 = 13
# have?
#
# This is a system of 4 equations in 6 unknowns.

count = 0
# x1 ranges from 0 to min(15, 12) = 12
for x1 in range(0, 13):
    # x2 + x3 = 15 - x1
    # x4 + x5 = 12 - x1
    s23 = 15 - x1
    s45 = 12 - x1
    for x2 in range(0, s23 + 1):
        x3 = s23 - x2
        for x4 in range(0, s45 + 1):
            x5 = s45 - x4
            # Check: x2 + x4 + x6 = 10 => x6 = 10 - x2 - x4
            x6 = 10 - x2 - x4
            if x6 < 0:
                continue
            # Check: x3 + x5 + x6 = 13
            if x3 + x5 + x6 == 13:
                count += 1

print(f"Solutions: {count}")

# Hmm, let me check if this system is consistent.
# Sum of all equations: 2(x1+x2+x3+x4+x5+x6) = 50, so total = 25.
# That's consistent. 

# count = 133. Let me verify.
# Actually this might be too easy. Let me try a harder system.

# Let me try: count the number of 4x4 magic squares with magic constant 30
# where all entries are distinct non-negative integers.
# A 4x4 magic square: all rows, columns, and both diagonals sum to 30.
# This is harder.

# Actually that might be too complex. Let me try something else entirely.

# How about: What is the number of distinct multisets of size 6 from {1,...,20}
# whose elements sum to exactly 42?

from itertools import combinations_with_replacement

target = 42
size = 6
max_val = 20

count2 = 0
for combo in combinations_with_replacement(range(1, max_val + 1), size):
    if sum(combo) == target:
        count2 += 1

print(f"Multisets of size 6 from {{1,...,20}} summing to 42: {count2}")
