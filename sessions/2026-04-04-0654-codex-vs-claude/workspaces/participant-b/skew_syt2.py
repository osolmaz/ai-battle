# Count SYT of skew shape lambda/mu
# lambda = (14,13,12,11,9,7,6,5,3,1)
# mu = (6,4,2,1,0,0,0,0,0,0)
# Total cells: (14+13+12+11+9+7+6+5+3+1) - (6+4+2+1) = 81 - 13 = 68

lam = [14, 13, 12, 11, 9, 7, 6, 5, 3, 1]
mu =  [6,  4,  2,  1,  0, 0, 0, 0, 0, 0]
nrows = len(lam)

row_sizes = [lam[i] - mu[i] for i in range(nrows)]
n = sum(row_sizes)
print(f"Number of cells: {n}")
print(f"Row sizes: {row_sizes}")

from functools import lru_cache

@lru_cache(maxsize=None)
def count_syt(filled):
    total_filled = sum(filled)
    if total_filled == n:
        return 1
    
    result = 0
    for i in range(nrows):
        if filled[i] < row_sizes[i]:
            col = mu[i] + filled[i]
            # Check: cell (i-1, col) must be filled if it exists in the skew shape
            ok = True
            if i > 0:
                if mu[i-1] <= col < lam[i-1]:
                    cells_filled_in_prev_row = filled[i-1]
                    first_unfilled_col_prev = mu[i-1] + cells_filled_in_prev_row
                    if col >= first_unfilled_col_prev:
                        ok = False
            if ok:
                new = list(filled)
                new[i] += 1
                result += count_syt(tuple(new))
    
    return result

initial = tuple([0] * nrows)
result = count_syt(initial)
print(f"SYT of skew shape: {result}")
