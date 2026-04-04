# Let me try a harder question: count the number of accepting paths in an NFA
# Actually, let me try counting solutions to a constraint satisfaction problem.

# Question: How many 8-digit strings over {0,1,2,3,4,5,6,7,8,9} have the property that:
# - The sum of all digits is divisible by 7
# - No two adjacent digits are equal
# - The first digit is nonzero (so it's a valid 8-digit number)

# DP: state = (position, last_digit, sum_mod_7)

count = 0
# dp[pos][last_digit][sum_mod_7]
# pos ranges from 0 to 7 (8 digits)

from functools import lru_cache

@lru_cache(maxsize=None)
def dp(pos, last_digit, sum_mod):
    if pos == 8:
        return 1 if sum_mod == 0 else 0
    total = 0
    for d in range(10):
        if d == last_digit:
            continue
        total += dp(pos + 1, d, (sum_mod + d) % 7)
    return total

# First digit is nonzero and there's no "last digit" constraint
result = 0
for first in range(1, 10):
    result += dp(1, first, first % 7)

print(f"Count: {result}")

# Verify with smaller case (3-digit numbers)
@lru_cache(maxsize=None)
def dp3(pos, last_digit, sum_mod):
    if pos == 3:
        return 1 if sum_mod == 0 else 0
    total = 0
    for d in range(10):
        if d == last_digit:
            continue
        total += dp3(pos + 1, d, (sum_mod + d) % 7)
    return total

result3 = 0
for first in range(1, 10):
    result3 += dp3(1, first, first % 7)
print(f"3-digit verification: {result3}")

# Brute force 3-digit for checking
bf = 0
for n in range(100, 1000):
    digits = [int(c) for c in str(n)]
    if sum(digits) % 7 != 0:
        continue
    if any(digits[i] == digits[i+1] for i in range(len(digits)-1)):
        continue
    bf += 1
print(f"3-digit brute force: {bf}")
