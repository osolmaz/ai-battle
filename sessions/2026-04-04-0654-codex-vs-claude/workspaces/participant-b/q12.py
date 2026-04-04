# Let me try a question about counting the number of distinct ways to 
# arrange non-attacking kings on a chessboard, or something similar.
#
# How about: Count the number of ways to place exactly 5 non-attacking kings
# on a 6x6 chessboard. (Kings attack all 8 adjacent squares.)

rows = 6
cols = 6
k = 5

# Generate all valid placements of k non-attacking kings
from itertools import combinations

cells = [(r, c) for r in range(rows) for c in range(cols)]

def attacks(r1, c1, r2, c2):
    return abs(r1-r2) <= 1 and abs(c1-c2) <= 1 and (r1, c1) != (r2, c2)

count = 0
for placement in combinations(cells, k):
    valid = True
    for i in range(k):
        for j in range(i+1, k):
            if attacks(placement[i][0], placement[i][1], placement[j][0], placement[j][1]):
                valid = False
                break
        if not valid:
            break
    if valid:
        count += 1

print(f"Ways to place {k} non-attacking kings on {rows}x{cols}: {count}")
