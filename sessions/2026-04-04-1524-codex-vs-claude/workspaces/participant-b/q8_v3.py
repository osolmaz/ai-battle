from itertools import combinations
from functools import lru_cache

def count_binary_matrices(n, k):
    """Count n×n binary matrices with all row sums and column sums equal to k."""
    
    @lru_cache(maxsize=None)
    def dp(remaining_cols):
        total_remaining = sum(remaining_cols)
        if total_remaining == 0:
            return 1
        
        rows_remaining = total_remaining // k
        if rows_remaining == 0 or len([c for c in remaining_cols if c > 0]) < k:
            return 0
        
        # Find non-zero column indices
        non_zero_indices = [i for i, c in enumerate(remaining_cols) if c > 0]
        
        if len(non_zero_indices) < k:
            return 0
        
        total = 0
        for chosen in combinations(non_zero_indices, k):
            new_cols = list(remaining_cols)
            for j in chosen:
                new_cols[j] -= 1
            new_cols_sorted = tuple(sorted(new_cols, reverse=True))
            total += dp(new_cols_sorted)
        
        return total
    
    initial = tuple([k] * n)
    result = dp(initial)
    return result

# Test
for n in range(2, 10):
    for k in [1, 2, 3]:
        if k > n - 1:
            continue
        result = count_binary_matrices(n, k)
        print(f"n={n}, k={k}: {result}")

