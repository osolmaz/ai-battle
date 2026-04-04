# That question works but computing it for n=8 requires a smarter method.
# Let me think of a different question that's cleaner.
#
# How about: Count the number of ways to tile a 6x6 grid with 
# L-trominoes and straight trominoes?
# Hmm, that might not work perfectly (6x6 = 36 squares, 36/3 = 12 trominoes).
# But the tileability depends on coloring arguments.
#
# Actually let me just ask a question involving a specific computation 
# that's hard to get right without careful work.
#
# Q: What is the number of 8x8 binary matrices (entries 0 or 1) with 
# all row sums and all column sums equal to 3?
#
# This is R(3,3,...,3; 3,3,...,3) for an 8x8 matrix, which counts
# 3-regular bipartite graphs.
#
# This is equivalent to counting perfect matchings in a specific 
# hypergraph, or equivalently, the permanent of a specific matrix.
#
# Actually, this equals the number of ways to place 24 ones in an 8x8
# grid such that each row and column has exactly 3 ones.
# 
# This is related to Latin rectangles and can be computed using
# inclusion-exclusion or the permanent.
#
# The number of such matrices is:
# 8! * perm(J_8 restricted) / (3!)^8 ... no, that's not right.
#
# Let me think. The number of 0-1 matrices with row sums r and column sums c
# is a well-studied combinatorial quantity. For the case where all row sums 
# = all column sums = k (a k-regular bipartite graph), this is:
#
# D(n, k) = n! * permanent of [C(k, ...)] ... no, let me just compute it directly.
#
# For an n×n 0-1 matrix with all row sums and column sums = k:
# This equals the number of k-regular bipartite graphs on n+n vertices.
# For n=8, k=3: ?
#
# I can compute this as the permanent of the matrix where each entry is
# C(n-?, ?) ... no, that's not right either.
#
# Let me just compute it directly using a DP or recursive approach.

from functools import lru_cache
from math import comb

def count_binary_matrices(n, k):
    """Count n×n binary matrices with all row sums and column sums equal to k."""
    # Row by row approach: for each row, choose k columns to be 1.
    # State: tuple of remaining column sums.
    # 
    # Initially all column sums are k.
    # For each row, we choose k columns (from those with remaining sum > 0)
    # and decrement their remaining sums.
    
    @lru_cache(maxsize=None)
    def dp(remaining_cols):
        # remaining_cols is a tuple of remaining column sums, sorted
        # (to enable memoization with fewer states)
        if sum(remaining_cols) == 0:
            return 1
        
        total_remaining = sum(remaining_cols)
        rows_remaining = total_remaining // k
        
        if rows_remaining == 0:
            return 0
        
        # Choose k columns for the current row
        # remaining_cols is sorted in non-increasing order
        non_zero = [(i, c) for i, c in enumerate(remaining_cols) if c > 0]
        
        if len(non_zero) < k:
            return 0
        
        # Generate all ways to choose k columns from non_zero
        total = 0
        for chosen in combinations(range(len(non_zero)), k):
            new_cols = list(remaining_cols)
            valid = True
            for j in chosen:
                idx = non_zero[j][0]
                new_cols[idx] -= 1
                if new_cols[idx] < 0:
                    valid = False
                    break
            if not valid:
                continue
            new_cols_sorted = tuple(sorted(new_cols, reverse=True))
            total += dp(new_cols_sorted)
        
        return total
    
    initial = tuple([k] * n)
    return dp(initial)

# Test small cases
for n in range(2, 9):
    for k in [1, 2, 3]:
        if k > n:
            continue
        result = count_binary_matrices(n, k)
        print(f"n={n}, k={k}: {result}")

