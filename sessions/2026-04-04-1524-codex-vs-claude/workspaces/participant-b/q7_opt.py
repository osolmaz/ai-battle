# Optimized iterative DP for counting linear extensions of divisibility poset
# Process order ideals bottom-up (adding elements) instead of top-down

import sys
from collections import defaultdict

def solve(n, modulus=10**9+7):
    elements = list(range(2, n+1))
    num_elems = len(elements)
    elem_to_idx = {x: i for i, x in enumerate(elements)}
    
    # For each element, bitmask of its proper divisors in {2,...,n}
    divisors_mask = [0] * num_elems
    for i, x in enumerate(elements):
        for d in range(2, x):
            if x % d == 0 and d in elem_to_idx:
                divisors_mask[i] |= (1 << elem_to_idx[d])
    
    # For each element, bitmask of elements that have x as a divisor
    # (i.e., proper multiples of x in {2,...,n})
    multiples_mask = [0] * num_elems
    for i, x in enumerate(elements):
        for m in range(2*x, n+1, x):
            if m in elem_to_idx:
                multiples_mask[i] |= (1 << elem_to_idx[m])
    
    # DP: f[mask] = number of linear extensions of the order ideal represented by mask
    # f[0] = 1 (empty set)
    # f[mask] = sum over elements x in mask that are "available" to be added last
    #           (x is maximal in mask, i.e., no proper multiple of x is in mask)
    # f[mask] = sum_{x maximal in mask} f[mask ^ (1<<x)]
    
    # Process masks in order of increasing popcount (number of bits set)
    # This is equivalent to building up from smaller sets
    
    # Actually, we process by removing maximal elements (top-down):
    # Start with full_mask, remove maximal elements one by one.
    # But to build the DP table, we can process masks in decreasing order of popcount.
    
    # Alternative: "add from bottom" approach
    # g[mask] = number of valid orderings of elements in mask
    # g[0] = 1
    # g[mask] = sum over x in mask that are "eligible to be placed last"
    #           (x is maximal in mask)
    # g[mask] = sum_{x maximal in mask} g[mask ^ (1<<x)]
    
    # We only need to compute g for masks that are valid order ideals.
    # A mask is a valid order ideal if: for every x in mask, all proper divisors of x 
    # (in {2,...,n}) are also in mask.
    
    # BFS approach: enumerate all valid order ideals and compute g
    
    full_mask = (1 << num_elems) - 1
    
    # Use dictionary-based DP
    # Start from full_mask and work down
    g = {}
    g[0] = 1
    
    # BFS: generate order ideals by building up (adding available elements)
    # An element x is available to add to mask if all its divisors are in mask
    
    # Process level by level (by popcount)
    current_level = {0: 1}  # mask -> g value
    
    for level in range(num_elems):
        next_level = {}
        for mask, gval in current_level.items():
            # Find elements available to add
            for i in range(num_elems):
                if mask & (1 << i):
                    continue  # already in mask
                if (divisors_mask[i] & mask) == divisors_mask[i]:
                    # All divisors of element i are in mask; can add element i
                    new_mask = mask | (1 << i)
                    if new_mask not in next_level:
                        next_level[new_mask] = 0
                    next_level[new_mask] = (next_level[new_mask] + gval) % modulus
        
        current_level = next_level
        if level % 5 == 0 or level >= num_elems - 3:
            print(f"  Level {level+1}: {len(current_level)} states", flush=True)
    
    # The answer for {2,...,n} is in current_level[full_mask]
    result = current_level.get(full_mask, 0)
    return result

# Test small cases
for nn in [10, 12, 15, 20]:
    print(f"n={nn}:")
    result = solve(nn)
    print(f"  Result: {result}")
    print()

