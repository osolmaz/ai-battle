# Count 9x9 binary matrices with given row and column sums
# Row sums: (5,4,3,3,3,4,4,2,4)
# Col sums: (5,2,3,5,5,3,3,1,5)
# Sum of row sums = 5+4+3+3+3+4+4+2+4 = 32
# Sum of col sums = 5+2+3+5+5+3+3+1+5 = 32 ✓

# Use DP: fill row by row. State = tuple of remaining column sums.
# After placing row i with row_sum r[i], the remaining column sums decrease.

row_sums = [5,4,3,3,3,4,4,2,4]
col_sums = [5,2,3,5,5,3,3,1,5]
n = 9

from itertools import combinations
from functools import lru_cache

# For each row with sum k, we choose k columns to place 1s.
# The state is the remaining column capacities.

# DP: process rows one at a time
# State: tuple of remaining column sums (sorted would lose column identity... no, we need exact columns)

def solve():
    # dp[state] = number of ways, where state = tuple of remaining col sums
    dp = {tuple(col_sums): 1}
    
    for row_idx in range(n):
        rs = row_sums[row_idx]
        new_dp = {}
        
        for state, ways in dp.items():
            # Choose rs columns from the 9 columns to place 1s
            # Each chosen column j must have state[j] > 0
            available = [j for j in range(n) if state[j] > 0]
            
            for chosen in combinations(available, rs):
                new_state = list(state)
                for j in chosen:
                    new_state[j] -= 1
                new_state = tuple(new_state)
                new_dp[new_state] = new_dp.get(new_state, 0) + ways
        
        dp = new_dp
        print(f"Row {row_idx}: {len(dp)} states")
    
    # The answer is dp[(0,0,...,0)]
    target = tuple([0]*n)
    return dp.get(target, 0)

result = solve()
print(f"Number of binary matrices: {result}")
