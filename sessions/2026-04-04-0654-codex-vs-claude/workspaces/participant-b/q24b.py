# Let me try a question about counting the number of surjective functions
# with specific constraints, or counting specific types of set partitions.
#
# How about: Count the number of set partitions of {1,...,13} into non-empty 
# parts where every part has odd size.
# This is related to the exponential generating function for odd-size parts.

# EGF: exp(sinh(x)) = exp((e^x - e^(-x))/2)
# We want [x^13/13!] * exp(sinh(x)) * 13!

# Let me compute by DP.
# Bell-like number but restricted to odd part sizes.

from math import comb

def count_odd_partitions(n):
    # dp[k] = number of set partitions of {1,...,k} into parts of odd size
    dp = [0] * (n + 1)
    dp[0] = 1
    
    for k in range(1, n + 1):
        # Element k joins a new part of odd size s (1, 3, 5, ...)
        # Choose s-1 other elements from {1,...,k-1} to join this part
        for s in range(1, k + 1, 2):
            dp[k] += comb(k - 1, s - 1) * dp[k - s]
    
    return dp[n]

for i in range(1, 14):
    print(f"Odd-part partitions of {{{1},...,{i}}}: {count_odd_partitions(i)}")

result = count_odd_partitions(13)
print(f"\nAnswer: {result}")

# Verify small case: n=3
# Partitions of {1,2,3}: {1},{2},{3} (all odd sizes ✓); {1,2},{3} (even size part ✗); 
# {1,3},{2} (✗); {2,3},{1} (✗); {1,2,3} (odd size ✓)
# So 2 partitions. Check:
print(f"Verification n=3: {count_odd_partitions(3)} (expected 2)")
