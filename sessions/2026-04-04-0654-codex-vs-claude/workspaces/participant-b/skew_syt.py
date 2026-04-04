# Count SYT of skew shape lambda/mu
# lambda = (8,7,6,5,3,2), mu = (3,2,1)
# Total cells: (8+7+6+5+3+2) - (3+2+1) = 31 - 6 = 25

# The skew shape has cells:
# Row 1 (length 8, mu=3): columns 3,4,5,6,7 (0-indexed) -> 5 cells
# Row 2 (length 7, mu=2): columns 2,3,4,5,6 -> 5 cells  
# Row 3 (length 6, mu=1): columns 1,2,3,4,5 -> 5 cells
# Row 4 (length 5, mu=0): columns 0,1,2,3,4 -> 5 cells
# Row 5 (length 3, mu=0): columns 0,1,2 -> 3 cells
# Row 6 (length 2, mu=0): columns 0,1 -> 2 cells

lam = [8, 7, 6, 5, 3, 2]
mu = [3, 2, 1, 0, 0, 0]
nrows = len(lam)

# Enumerate cells of the skew shape
cells = []
for i in range(nrows):
    for j in range(mu[i], lam[i]):
        cells.append((i, j))

n = len(cells)
print(f"Number of cells: {n}")

# Use DP similar to regular SYT counting
# State: how many cells are filled in each row (offset by mu)
# filled[i] = number of cells filled in row i (ranges from 0 to lam[i]-mu[i])

from functools import lru_cache

row_sizes = [lam[i] - mu[i] for i in range(nrows)]
print(f"Row sizes: {row_sizes}")

@lru_cache(maxsize=None)
def count_syt(filled):
    total_filled = sum(filled)
    if total_filled == n:
        return 1
    
    result = 0
    for i in range(nrows):
        if filled[i] < row_sizes[i]:
            # Next cell in row i would be at column mu[i] + filled[i]
            col = mu[i] + filled[i]
            
            # Check column constraint: the cell above (row i-1, col) must already be filled
            # Cell (i-1, col) exists if i > 0 and mu[i-1] <= col < lam[i-1]
            if i > 0 and mu[i-1] <= col < lam[i-1]:
                # How many cells are filled in row i-1? filled[i-1]
                # Cells filled in row i-1 are columns mu[i-1] to mu[i-1]+filled[i-1]-1
                # Cell (i-1, col) is filled iff col < mu[i-1] + filled[i-1]
                if col >= mu[i-1] + filled[i-1]:
                    continue  # cell above not yet filled
            
            new_filled = list(filled)
            new_filled[i] += 1
            result += count_syt(tuple(new_filled))
    
    return result

initial = tuple([0] * nrows)
result = count_syt(initial)
print(f"SYT of skew shape: {result}")
