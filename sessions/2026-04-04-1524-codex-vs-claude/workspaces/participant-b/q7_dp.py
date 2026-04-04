# The number of order ideals grows but might be manageable for n=40.
# Let me try to compute the number of order ideals for larger n.
# Also, let me compute the linear extensions using DP on order ideals.

# DP approach:
# For each order ideal I, compute f(I) = number of linear extensions of elements in I.
# f(empty) = 1
# f(I) = sum over maximal elements m of I: f(I \ {m})
# (where m is maximal means no element of I is a proper multiple of m that's also in I)
#
# Alternatively (building up):
# f(I) = sum over elements x that are maximal in I: f(I \ {x})
#
# Or equivalently (building up from bottom):
# g(I) = number of valid orderings of elements in I
# g(empty) = 1
# g(I) = sum over x ∈ I that are "available" (all divisors of x in {2,...,n} are in I\{x}... 
# wait, "available" means all proper divisors of x (in {2,...,40}) are in the already-placed set.
# If I is the set of elements placed so far, then x is the last element placed.
# For x to be the last one placed, x must be maximal in I (no proper multiple of x is in I).
#
# So: g(I) = sum over x maximal in I: g(I \ {x})
#
# This is the "top-down removal" approach.
# Let me implement this.

import sys
from collections import defaultdict

def solve(n, modulus=None):
    elements = list(range(2, n+1))
    num_elements = len(elements)
    
    # For each element, find its proper divisors in {2,...,n}
    divisors_in_set = {}
    for x in elements:
        divs = []
        for d in range(2, x):
            if x % d == 0:
                divs.append(d)
        divisors_in_set[x] = divs
    
    # For each element, find its proper multiples in {2,...,n}
    multiples_in_set = {}
    for x in elements:
        mults = []
        for m in range(2*x, n+1, x):
            mults.append(m)
        multiples_in_set[x] = mults
    
    # DP: g(I) = number of linear extensions of elements in I
    # g(empty) = 1
    # g(I) = sum over x maximal in I: g(I \ {x})
    #
    # I'll represent I as a frozenset and use memoization.
    
    memo = {}
    
    def g(I_frozen):
        if I_frozen in memo:
            return memo[I_frozen]
        if len(I_frozen) == 0:
            return 1
        
        I = set(I_frozen)
        total = 0
        # Find maximal elements in I
        for x in I:
            # x is maximal if no multiple of x is in I
            is_maximal = True
            for m in multiples_in_set[x]:
                if m in I:
                    is_maximal = False
                    break
            if is_maximal:
                new_I = I_frozen - {x}
                total += g(new_I)
        
        if modulus:
            total %= modulus
        memo[I_frozen] = total
        return total
    
    full_set = frozenset(elements)
    result = g(full_set)
    return result

# Test small cases
for n in range(1, 16):
    result = solve(n)
    print(f"n={n}: {result}")

