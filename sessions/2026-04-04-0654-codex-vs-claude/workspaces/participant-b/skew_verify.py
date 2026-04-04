# Verify using a different approach: enumerate by columns instead of rows

lam = [8, 7, 6, 5, 3, 2]
mu = [3, 2, 1, 0, 0, 0]
nrows = len(lam)
row_sizes = [lam[i] - mu[i] for i in range(nrows)]
n = sum(row_sizes)

from functools import lru_cache

# Alternative: use the same approach but process differently
# State: for each row, how many cells filled
# Available cell: row i, if filled[i] < row_sizes[i], and the cell above is filled

@lru_cache(maxsize=None)
def count_syt2(filled):
    total = sum(filled)
    if total == n:
        return 1
    
    result = 0
    for i in range(nrows):
        if filled[i] < row_sizes[i]:
            col = mu[i] + filled[i]
            # Check: cell (i-1, col) must be filled if it exists in the skew shape
            ok = True
            if i > 0:
                if mu[i-1] <= col < lam[i-1]:
                    # This cell exists in the skew shape
                    cells_filled_in_prev_row = filled[i-1]
                    first_unfilled_col_prev = mu[i-1] + cells_filled_in_prev_row
                    if col >= first_unfilled_col_prev:
                        ok = False
            if ok:
                new = list(filled)
                new[i] += 1
                result += count_syt2(tuple(new))
    
    return result

result2 = count_syt2(tuple([0]*nrows))
print(f"Verification: {result2}")
