# Verify SYT count by a different method: recursive enumeration
# A Standard Young Tableau fills cells 1..n such that rows and columns are increasing.
# Build the tableau cell by cell, placing values 1, 2, ..., n in order.
# At each step, a cell (i,j) is "available" if:
#   - (i, j-1) is filled (or j=0)
#   - (i-1, j) is filled (or i=0)

shape = [7, 5, 4, 3, 1]
n = sum(shape)

# Represent state as tuple of how many cells filled in each row
# filled[i] = number of cells filled in row i (0 to shape[i])

from functools import lru_cache

@lru_cache(maxsize=None)
def count_syt(filled):
    total_filled = sum(filled)
    if total_filled == n:
        return 1
    
    result = 0
    for i in range(len(shape)):
        if filled[i] < shape[i]:
            # Can we place in row i at position filled[i]?
            j = filled[i]
            # Check: row above must have filled more
            if i == 0 or filled[i-1] > j:
                new_filled = list(filled)
                new_filled[i] += 1
                result += count_syt(tuple(new_filled))
    
    return result

initial = tuple([0] * len(shape))
result = count_syt(initial)
print(f"SYT count (recursive): {result}")
