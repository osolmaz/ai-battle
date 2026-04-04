from math import gcd, factorial
from itertools import permutations
from collections import Counter

# Count necklaces with exactly 3 red, 4 blue, 5 green beads (12 beads total)
# Using Burnside's lemma: (1/n) * sum_{d|n} phi(n/d) * f(d)
# where f(d) = number of arrangements with the given composition that are fixed by rotation by d positions

# A rotation by d positions fixes an arrangement iff the arrangement has period d
# (i.e., the string is made of n/d copies of a substring of length d)
# This means d must divide n=12, and the composition of one period of length d 
# must be: 3/(12/d) red, 4/(12/d) blue, 5/(12/d) green
# These must all be integers.

def euler_phi(n):
    result = n
    p = 2
    temp = n
    while p * p <= temp:
        if temp % p == 0:
            while temp % p == 0:
                temp //= p
            result -= result // p
        p += 1
    if temp > 1:
        result -= result // temp
    return result

n = 12
red, blue, green = 3, 4, 5

total = 0
for d in range(1, n+1):
    if n % d != 0:
        continue
    k = n // d  # number of copies
    # Each period of length d must have red/k red, blue/k blue, green/k green
    if red % k != 0 or blue % k != 0 or green % k != 0:
        continue
    r, b, g = red // k, blue // k, green // k
    # Number of arrangements of d beads with r red, b blue, g green
    arrangements = factorial(d) // (factorial(r) * factorial(b) * factorial(g))
    total += euler_phi(k) * arrangements

necklaces = total // n
print(f"Necklaces with 3R, 4B, 5G: {necklaces}")

# Let me also verify by brute force
from itertools import permutations

def canonical(s):
    """Return lexicographically smallest rotation"""
    n = len(s)
    best = s
    for i in range(1, n):
        rotated = s[i:] + s[:i]
        if rotated < best:
            best = rotated
    return best

beads = 'R'*3 + 'B'*4 + 'G'*5
seen = set()
for p in set(permutations(beads)):
    s = ''.join(p)
    seen.add(canonical(s))

print(f"Brute force verification: {len(seen)}")
