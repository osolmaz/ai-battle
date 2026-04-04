# Let me think of a question that's tricky but verifiable.
# I'll ask about a specific computation in group theory / number theory.

# Question: What is the multiplicative order of 2 modulo 257?
# 257 is prime (Fermat prime F_3 = 2^8 + 1)
# The order of 2 mod 257 divides phi(257) = 256 = 2^8
# 2^8 = 256 ≡ -1 (mod 257), so 2^8 != 1
# 2^16 = (2^8)^2 = (-1)^2 = 1 (mod 257)
# So order is 16.

# Hmm, that might be too easy for a strong model. Let me think of something harder.

# How about: What is the number of integers n with 1 ≤ n ≤ 10000 such that 
# n^2 + 1 is divisible by exactly one prime ≡ 1 (mod 4)?

# Actually let me try a different angle - a question about formal languages / automata.

# Let me try: Consider strings over {0,1} of length 12. How many such strings 
# have the property that every contiguous substring of length 4 contains at least two 1s?

count = 0
for mask in range(1 << 12):
    s = format(mask, '012b')
    valid = True
    for i in range(9):  # positions 0..8 for substrings of length 4
        substr = s[i:i+4]
        if substr.count('1') < 2:
            valid = False
            break
    if valid:
        count += 1

print(f"Strings of length 12 where every 4-substring has ≥2 ones: {count}")

# Let me also verify with DP
# State: last 3 bits
from functools import lru_cache

@lru_cache(maxsize=None)
def dp(pos, last3):
    """pos = current position (0-indexed), last3 = tuple of last 3 bits placed"""
    if pos == 12:
        return 1
    total = 0
    for bit in [0, 1]:
        if pos >= 3:
            window = last3 + (bit,)  # last 3 + current = window of 4
            if sum(window) < 2:
                continue
        total += dp(pos + 1, (last3[1], last3[2], bit) if pos >= 2 else last3 + (bit,) if len(last3) < 3 else last3)
    return total

# Hmm, the DP is getting messy with initialization. The brute force is correct.
print("Brute force count:", count)
