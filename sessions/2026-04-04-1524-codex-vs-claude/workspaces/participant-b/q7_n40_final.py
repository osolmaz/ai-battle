# n=30 peak was ~102K states - very manageable!
# Let me run n=40 now.

import sys

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
    
    full_mask = (1 << num_elems) - 1
    
    # BFS level by level
    current_level = {0: 1}
    
    for level in range(num_elems):
        next_level = {}
        for mask, gval in current_level.items():
            for i in range(num_elems):
                if mask & (1 << i):
                    continue
                if (divisors_mask[i] & mask) == divisors_mask[i]:
                    new_mask = mask | (1 << i)
                    if new_mask in next_level:
                        next_level[new_mask] = (next_level[new_mask] + gval) % modulus
                    else:
                        next_level[new_mask] = gval
        
        current_level = next_level
        print(f"  Level {level+1}/{num_elems}: {len(current_level)} states", flush=True)
    
    result = current_level.get(full_mask, 0)
    return result

print("n=40:")
result = solve(40)
print(f"\nResult for n=40: {result}")

