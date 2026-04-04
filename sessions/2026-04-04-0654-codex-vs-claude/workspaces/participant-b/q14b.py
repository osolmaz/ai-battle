# Compute the number of proper 5-colorings of the Petersen graph.
# The Petersen graph has 10 vertices and 15 edges.

# Petersen graph edges (0-indexed):
# Outer cycle: 0-1-2-3-4-0
# Inner star: 5-7-9-6-8-5
# Connections: 0-5, 1-6, 2-7, 3-8, 4-9

petersen_edges = [
    (0,1),(1,2),(2,3),(3,4),(4,0),  # outer cycle
    (5,7),(7,9),(9,6),(6,8),(8,5),  # inner star
    (0,5),(1,6),(2,7),(3,8),(4,9),  # connections
]

from itertools import product

n = 10
k = 5
adj_set = set()
for u,v in petersen_edges:
    adj_set.add((u,v))
    adj_set.add((v,u))

# Count proper k-colorings
count = 0
for coloring in product(range(k), repeat=n):
    proper = True
    for u, v in petersen_edges:
        if coloring[u] == coloring[v]:
            proper = False
            break
    if proper:
        count += 1

print(f"Proper 5-colorings of Petersen graph: {count}")

# This might be easy to look up. Let me try k=6 too for a less standard value.
# Actually, let me try a different question.

# How about: What is the number of Hamiltonian cycles in the complete bipartite graph K_{5,5}?
# A Hamiltonian cycle in K_{5,5} visits all 10 vertices.
# The number is (5!)^2 * 2 / (2 * 10) ... no wait.
# Actually: arrange the vertices as a1,...,a5, b1,...,b5.
# A Hamiltonian cycle alternates between A and B partitions.
# Start at a1 (fix to avoid rotation), choose which b to visit: 5 choices,
# then which a: 4 choices, then b: 4, a: 3, b: 3, a: 2, b: 2, a: 1, b: 1, back to a1.
# So: 5 * 4 * 4 * 3 * 3 * 2 * 2 * 1 * 1 = 5 * (4!)^2... hmm
# Actually it's (5-1)! * 5! / 2 = 4! * 120 / 2 = 24 * 60 = 1440... not sure.
# Known formula: number of Hamiltonian cycles in K_{n,n} = n! * (n-1)! / 2
# For n=5: 120 * 24 / 2 = 1440.
# Too well known and easy.

# Let me try something completely different. 
# Count the number of integer partitions of 100 into exactly 7 distinct parts.

def count_partitions_distinct_parts(n, k):
    """Count partitions of n into exactly k distinct positive parts."""
    # DP: dp[i][j][last] = ways to partition using j parts so far, sum = i, last part used = last
    # Better: dp[parts_used][current_sum] with the constraint that parts are increasing
    
    # Use: dp[j][s] = number of ways to choose j distinct parts from {1,...,n} summing to s
    # Parts must be distinct and positive. Order doesn't matter (it's a partition).
    # Use parts in increasing order.
    
    from functools import lru_cache
    
    @lru_cache(maxsize=None)
    def dp(parts_left, remaining_sum, min_val):
        if parts_left == 0:
            return 1 if remaining_sum == 0 else 0
        if remaining_sum <= 0:
            return 0
        # Minimum possible sum with parts_left parts starting from min_val
        min_sum = sum(range(min_val, min_val + parts_left))
        if min_sum > remaining_sum:
            return 0
        
        total = 0
        # Choose the next (smallest remaining) part
        max_val = remaining_sum - sum(range(min_val + 1, min_val + parts_left))  # rough upper bound
        for v in range(min_val, remaining_sum + 1):
            # Remaining parts_left-1 parts must be > v and sum to remaining_sum - v
            min_remaining = sum(range(v + 1, v + parts_left))
            if min_remaining > remaining_sum - v:
                break
            total += dp(parts_left - 1, remaining_sum - v, v + 1)
        
        return total
    
    return dp(k, n, 1)

result = count_partitions_distinct_parts(100, 7)
print(f"Partitions of 100 into 7 distinct parts: {result}")

# Verify with a smaller case: partitions of 10 into 3 distinct parts
# Should be: 1+2+7, 1+3+6, 1+4+5, 2+3+5 = 4... wait
# 1+2+7=10, 1+3+6=10, 1+4+5=10, 2+3+5=10, 2+4+4=10 (not distinct) = 4
r2 = count_partitions_distinct_parts(10, 3)
print(f"Partitions of 10 into 3 distinct parts: {r2} (expected 4)")
