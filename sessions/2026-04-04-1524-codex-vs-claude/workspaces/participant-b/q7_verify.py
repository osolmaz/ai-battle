# Verify n=40 result with a second run and cross-check smaller values

import sys

def solve(n, modulus=10**9+7):
    elements = list(range(2, n+1))
    num_elems = len(elements)
    elem_to_idx = {x: i for i, x in enumerate(elements)}
    
    divisors_mask = [0] * num_elems
    for i, x in enumerate(elements):
        for d in range(2, x):
            if x % d == 0 and d in elem_to_idx:
                divisors_mask[i] |= (1 << elem_to_idx[d])
    
    full_mask = (1 << num_elems) - 1
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
    
    return current_level.get(full_mask, 0)

# Cross-check: compute without modulus for small n
def solve_exact(n):
    elements = list(range(2, n+1))
    num_elems = len(elements)
    elem_to_idx = {x: i for i, x in enumerate(elements)}
    divisors_mask = [0] * num_elems
    for i, x in enumerate(elements):
        for d in range(2, x):
            if x % d == 0 and d in elem_to_idx:
                divisors_mask[i] |= (1 << elem_to_idx[d])
    full_mask = (1 << num_elems) - 1
    current_level = {0: 1}
    for level in range(num_elems):
        next_level = {}
        for mask, gval in current_level.items():
            for i in range(num_elems):
                if mask & (1 << i):
                    continue
                if (divisors_mask[i] & mask) == divisors_mask[i]:
                    new_mask = mask | (1 << i)
                    next_level[new_mask] = next_level.get(new_mask, 0) + gval
        current_level = next_level
    return current_level.get(full_mask, 0)

# Verify small cases
MOD = 10**9 + 7
for n in [10, 12, 15, 20]:
    exact = solve_exact(n)
    modded = solve(n)
    print(f"n={n}: exact={exact}, mod={modded}, check={exact % MOD == modded}")

# Run n=40 again
print("\nRunning n=40...")
result = solve(40)
print(f"n=40 result: {result}")
