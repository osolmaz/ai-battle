# Verify: partitions of 100 into exactly 7 distinct positive parts
# Using generating functions approach

def count_partitions_distinct(n, k):
    """Count partitions of n into exactly k distinct positive parts using DP table."""
    # dp[j][s] = number of ways to pick j distinct parts from {1,...,n} summing to s
    # Process values 1, 2, ..., n-1 and decide include/exclude (like 0-1 knapsack)
    
    # dp[j][s] after considering values {1,...,v}
    # But n can be up to 100 and k up to 7, so this is manageable
    
    # Initialize: dp[0][0] = 1
    dp = [[0] * (n + 1) for _ in range(k + 1)]
    dp[0][0] = 1
    
    for v in range(1, n):  # consider adding value v
        # Process in reverse to avoid using v twice
        for j in range(min(k, v), 0, -1):
            for s in range(v, n + 1):
                dp[j][s] += dp[j-1][s-v]
    
    return dp[k][n]

result = count_partitions_distinct(100, 7)
print(f"Partitions of 100 into 7 distinct parts: {result}")

# Cross-check smaller cases
print(f"Partitions of 10 into 3 distinct parts: {count_partitions_distinct(10, 3)}")
print(f"Partitions of 15 into 4 distinct parts: {count_partitions_distinct(15, 4)}")
# 15 into 4 distinct: 1+2+3+9, 1+2+4+8, 1+2+5+7, 1+3+4+7, 1+3+5+6, 2+3+4+6 = 6
