# Optimized DP using bitmask representation
# Elements {2,...,40} mapped to bits 0..38

import sys

def solve(n, modulus=10**9+7):
    elements = list(range(2, n+1))
    num_elems = len(elements)
    elem_to_idx = {x: i for i, x in enumerate(elements)}
    
    # For each element, bitmask of its proper multiples in {2,...,n}
    multiples_mask = [0] * num_elems
    for i, x in enumerate(elements):
        for m in range(2*x, n+1, x):
            if m in elem_to_idx:
                multiples_mask[i] |= (1 << elem_to_idx[m])
    
    # DP: for each bitmask (set of remaining elements), count linear extensions
    # by removing maximal elements from the top
    # 
    # State: bitmask of remaining elements
    # g(mask) = sum over maximal elements i in mask: g(mask ^ (1<<i))
    # g(0) = 1
    #
    # For n=40, we have 39 bits, so 2^39 states. Way too many.
    # We need a smarter approach.
    
    # Let me check: how many distinct states actually appear?
    # We can use BFS/DFS with memoization (dictionary).
    
    if num_elems > 25:
        print(f"n={n}: too large for direct bitmask DP ({num_elems} elements)")
        return None
    
    # For num_elems <= 25, we can try dictionary-based memoization
    full_mask = (1 << num_elems) - 1
    
    memo = {}
    
    def g(mask):
        if mask in memo:
            return memo[mask]
        if mask == 0:
            return 1
        
        total = 0
        temp = mask
        while temp:
            i = (temp & -temp).bit_length() - 1  # lowest set bit
            temp &= temp - 1
            # Check if i is maximal in mask: no multiple of elements[i] is in mask
            if (multiples_mask[i] & mask) == 0:
                total += g(mask ^ (1 << i))
        
        total %= modulus
        memo[mask] = total
        return total
    
    sys.setrecursionlimit(10**6)
    result = g(full_mask)
    print(f"n={n}: {result} (memo size: {len(memo)})")
    return result

# Count order ideals (states) for increasing n
for n in range(2, 26):
    solve(n)

