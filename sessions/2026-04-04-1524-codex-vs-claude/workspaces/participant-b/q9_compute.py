import numpy as np
import sys
from itertools import combinations, permutations

MOD = 10**9 + 7

# Build states: triples (a,b,c) of distinct colors from {0,...,5}
states = []
state_idx = {}
for a in range(6):
    for b in range(6):
        if b == a: continue
        for c in range(6):
            if c == a or c == b: continue
            idx = len(states)
            states.append((a, b, c))
            state_idx[(a, b, c)] = idx

num_states = len(states)  # 120

# Build augmented transfer matrix (1320 x 1320)
# State index: triple_idx * 11 + sum_mod_11
aug_size = num_states * 11

# Use sparse representation for matrix multiplication
# For each state, store list of (target_state, count) transitions
# Actually, let me just use dense numpy arrays and compute matrix powers.

# Build T_aug as numpy array
T_aug = np.zeros((aug_size, aug_size), dtype=np.int64)
for i, (a, b, c) in enumerate(states):
    for d in range(6):
        if d != a and d != b and d != c:
            j = state_idx[(b, c, d)]
            for s in range(11):
                s_new = (s + d) % 11
                T_aug[i * 11 + s][j * 11 + s_new] = 1

# Matrix multiplication mod p, handling potential overflow
def mat_mul_mod(A, B, mod):
    """Multiply two matrices mod p using numpy, avoiding overflow."""
    n = A.shape[0]
    # Split into chunks to avoid int64 overflow
    # A[i,k] * B[k,j] < mod^2 ≈ 10^18, sum over k entries < k * mod^2
    # int64 max ≈ 9.2 * 10^18, so can sum about 9 entries safely
    chunk_size = max(1, 9 * 10**18 // (mod * mod))
    chunk_size = min(chunk_size, n)
    
    C = np.zeros((n, n), dtype=np.int64)
    for start in range(0, n, chunk_size):
        end = min(start + chunk_size, n)
        C = (C + np.mod(A[:, start:end] @ B[start:end, :], mod * 10)) % mod
    return C

def mat_pow_mod(M, power, mod):
    """Compute M^power mod p."""
    n = M.shape[0]
    result = np.eye(n, dtype=np.int64)
    base = M.copy() % mod
    while power > 0:
        if power & 1:
            result = mat_mul_mod(result, base, mod)
        base = mat_mul_mod(base, base, mod)
        power >>= 1
    return result

# First verify: Tr(T_aug^4) should be 528
print("Computing T_aug^4 for verification...")
sys.stdout.flush()
T4 = mat_pow_mod(T_aug, 4, MOD)
tr4 = sum(T4[i][i] for i in range(aug_size)) % MOD
print(f"Tr(T_aug^4) = {tr4} (expected 528)")

# Now compute for all relevant divisors
divisors_120 = [1, 2, 3, 4, 5, 6, 8, 10, 12, 15, 20, 24, 30, 40, 60, 120]

def euler_phi(n):
    result = n
    temp = n
    p = 2
    while p * p <= temp:
        if temp % p == 0:
            while temp % p == 0:
                temp //= p
            result -= result // p
        p += 1
    if temp > 1:
        result -= result // temp
    return result

print("\nComputing traces for each divisor...")
sys.stdout.flush()

traces = {}
for d in divisors_120:
    if d < 4:
        traces[d] = 0
        print(f"  d={d}: trace=0 (d < 4)")
    else:
        Td = mat_pow_mod(T_aug, d, MOD)
        tr = 0
        for i in range(aug_size):
            tr = (tr + Td[i][i]) % MOD
        traces[d] = tr
        print(f"  d={d}: Tr(T_aug^{d}) = {tr}")
    sys.stdout.flush()

# Rotation contribution to Burnside sum:
# sum_{k=0}^{119} |Fix(r^k)| = sum_{d | 120} phi(120/d) * |Fix_d|
# where |Fix_d| = Tr(T_aug^d) / 11 for d >= 4, else 0
# But we need mod arithmetic: /11 means * modular_inverse(11, MOD)

inv_11 = pow(11, MOD - 2, MOD)

rotation_sum = 0
for d in divisors_120:
    phi_val = euler_phi(120 // d)
    fix_d = traces[d] * inv_11 % MOD
    contribution = phi_val * fix_d % MOD
    rotation_sum = (rotation_sum + contribution) % MOD
    if d >= 4:
        print(f"  d={d}: phi={phi_val}, Tr/11={fix_d}, contribution={contribution}")

print(f"\nRotation sum = {rotation_sum}")
print("(This is the sum over all 120 rotations of |Fix(g)|)")

# Now I need the reflection contributions.
# This is more complex. I'll handle reflections separately.

# For now, let me at least compute the rotation-only answer (for cyclic group C_120):
# |classes under rotation| = rotation_sum * inv(120) mod MOD
inv_120 = pow(120, MOD - 2, MOD)
rotation_classes = rotation_sum * inv_120 % MOD
print(f"\nClasses under rotation only (C_120): {rotation_classes}")

