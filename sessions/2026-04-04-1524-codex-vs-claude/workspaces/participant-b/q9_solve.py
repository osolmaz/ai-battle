# Count equivalence classes of valid sequences on a 120-cycle with 6 colors
# where every 4 consecutive elements are pairwise distinct,
# and the sum is divisible by 11.
# Equivalence under dihedral group D_120 (rotations and reflections).
#
# By Burnside's lemma:
# |classes| = (1/|G|) * sum_{g in G} |Fix(g)|
# where G = D_120 has order 240.
#
# G consists of:
# - 120 rotations: r^k for k=0,...,119
# - 120 reflections: s*r^k for k=0,...,119
#
# For each g in G, we need to count the number of valid sequences fixed by g
# that also satisfy the sum ≡ 0 mod 11 condition.
#
# This is a complex computation. Let me think about how to approach it.
#
# First, let's count the total number of valid sequences (without symmetry or sum constraint)
# using transfer matrices.
#
# The constraint is: every 4 consecutive elements c_i, c_{i+1}, c_{i+2}, c_{i+3} are pairwise distinct.
# With 6 colors, this means each window of 4 consecutive elements uses 4 distinct colors from {0,...,5}.
#
# This is equivalent to: c_{i+3} ∉ {c_i, c_{i+1}, c_{i+2}} for all i.
# AND c_{i+2} ∉ {c_i, c_{i+1}} (which is implied by the 4-window constraint applied at position i-1).
# AND c_{i+1} ≠ c_i (implied similarly).
#
# Wait, let me re-check. "c_i, c_{i+1}, c_{i+2}, c_{i+3} are pairwise distinct" means all 6 pairs are distinct.
# This is equivalent to: all four are different.
#
# So the constraint is: for all i, {c_i, c_{i+1}, c_{i+2}, c_{i+3}} has 4 distinct elements.
#
# This is a constraint on overlapping 4-tuples. We can model this with a transfer matrix
# where the state is (c_{i}, c_{i+1}, c_{i+2}) - the last 3 elements.
# The transition from (a, b, c) to (b, c, d) is allowed iff d ∉ {a, b, c}.
#
# With 6 colors, the number of states is 6*5*4 = 120 (ordered triples of distinct elements).
# The number of valid transitions: for each state (a,b,c), d can be any of {0,...,5}\{a,b,c},
# which has 3 choices.
#
# So the transfer matrix T is 120x120 with entries 0 or 1.
#
# The number of valid cyclic sequences of length 120 is Tr(T^120) (trace of T to the 120th power).
#
# But we also need the sum constraint (sum ≡ 0 mod 11) and the Burnside counting.
#
# For the sum constraint, we can augment the state to track the running sum mod 11.
# State: (a, b, c, s) where a,b,c are the last 3 colors and s is sum mod 11.
# Total states: 120 * 11 = 1320.
#
# For Burnside's lemma with the dihedral group, we need to count fixed points of each
# group element. A rotation by k fixes a sequence iff the sequence has period dividing k
# (i.e., c_i = c_{i+k mod 120} for all i). A reflection fixes a sequence iff the sequence
# is a palindrome with respect to the reflection axis.
#
# This is getting complex. Let me implement it step by step.
#
# Step 1: Build the transfer matrix
# Step 2: For each rotation r^k (k divides 120), count fixed valid sequences with sum ≡ 0 mod 11
# Step 3: For each reflection, count fixed valid sequences with sum ≡ 0 mod 11
# Step 4: Apply Burnside

# Actually, for rotations by k, a sequence is fixed iff it has period k.
# But more precisely, a sequence fixed by rotation by k has period dividing gcd(120, k)... 
# no, rotation by k means c_i = c_{i+k} for all i. So the sequence has period dividing k.
# Wait, the sequence has period d where d | gcd(120, k)... hmm.
# If rotation by k fixes the sequence, then c_i = c_{i+k} for all i, meaning the period
# divides k AND 120 (since it's a cyclic sequence of length 120). So period divides gcd(k, 120).
#
# Actually, a cyclic sequence of length 120 is fixed by rotation by k iff its period divides k.
# And the period must also divide 120. So the period divides gcd(k, 120).
# Sequences with period dividing d (where d | 120) are determined by their first d elements,
# with the constraint that the cyclic extension satisfies the 4-distinct property.
#
# For rotation by k: the number of fixed sequences = number of valid cyclic sequences of 
# length d = gcd(k, 120) that extend periodically to length 120 and satisfy the constraints.
#
# Wait, I need to be more careful. If the sequence has period d dividing 120, then the
# cyclic sequence of length 120 has the 4-distinct property iff the cyclic sequence of 
# length d has the 4-distinct property (since the constraint is local, involving windows of 4).
# But this is only true if d ≥ 4 (otherwise the periodic extension might violate constraints).
# For d < 4, we need to check more carefully.
#
# Actually wait: if d = 1, then all elements are the same, and 4 consecutive would all be
# the same color - NOT pairwise distinct. So d=1 gives 0 valid sequences.
# d = 2: pattern ab ab ab... consecutive 4-window: a,b,a,b - need pairwise distinct,
# but a appears twice. So invalid.
# d = 3: pattern abc abc... 4-window: a,b,c,a - a appears twice. Invalid.
# d ≥ 4: The 4-window constraint for the periodic sequence is equivalent to the constraint
# on the cyclic sequence of length d. Need to verify: in the cyclic sequence of length d,
# every 4 consecutive elements (wrapping around) are pairwise distinct.
#
# So for d ≥ 4, the number of fixed valid sequences with sum ≡ 0 mod 11 under rotation by k
# (where d = gcd(k, 120)):
# = number of valid cyclic sequences of length d with sum ≡ 0 mod 11*d/gcd(11,120/d*something)
# Hmm, the sum constraint is: sum of 120 elements ≡ 0 mod 11.
# If the period is d, the sum = (120/d) * (sum of one period).
# So we need (120/d) * S ≡ 0 mod 11, where S is the sum of one period.
# Since gcd(120, 11) = 1 (11 is prime and doesn't divide 120), 120/d is coprime to 11
# unless 11 | 120/d... 120/d could be divisible by 11 only if d | 120 and 120/d is a
# multiple of 11, i.e., d | (120/11). But 120/11 is not an integer. So 11 ∤ 120/d for any d | 120.
# Therefore gcd(120/d, 11) = 1 (since 11 ∤ 120).
# So (120/d) * S ≡ 0 mod 11 iff S ≡ 0 mod 11.
#
# Great, so for rotation by k with d = gcd(k, 120):
# |Fix(r^k)| = (number of valid cyclic sequences of length d with period sum ≡ 0 mod 11)
# if d ≥ 4, else 0.
#
# But wait, I need sequences with period EXACTLY dividing d, not exactly d.
# A sequence fixed by r^k has c_i = c_{i+k}, which means period divides gcd(k, 120) = d.
# So the period could be any divisor of d. As long as ANY sequence with period dividing d
# is counted. But such a sequence is just a cyclic sequence of length d, and the valid 
# constraint is on the full 120-length sequence.
#
# For d ≥ 4: the sequence of length d repeated 120/d times. The 4-window constraint on
# the 120-length sequence IS the same as on the d-length cyclic sequence (since constraints
# are within windows of size 4, and d ≥ 4 means no "new" constraints arise from the repetition).
# This is because any 4 consecutive elements in the 120-length sequence correspond to 
# 4 consecutive elements in the d-length cyclic sequence (when indices are taken mod d).
#
# For d = 1, 2, 3: 0 fixed valid sequences (as argued above).
#
# So for each divisor d of 120 with d ≥ 4:
# |Fix(r^k)| where gcd(k,120) = d = Tr(T_d^d) restricted to sum ≡ 0 mod 11
#
# where T_d is the transfer matrix for the d-length cycle.
# Actually, T_d is the same transfer matrix T for any d ≥ 4. So |Fix| = Tr(T^d) with sum constraint.
#
# Wait, the sum constraint. I need to track the sum mod 11 within the transfer matrix.
# Let me augment the state to include sum mod 11.
#
# State: (a, b, c, s) where a,b,c are distinct colors and s is partial sum mod 11.
# States: 120 * 11 = 1320.
# Transition: (a,b,c,s) -> (b,c,d, (s+d) mod 11) for d ∉ {a,b,c}.
#
# For a cyclic sequence of length d with the sum constraint:
# We need to find the trace of T_aug^d restricted to states where the initial and final
# partial sums agree, AND the total sum is 0 mod 11.
#
# Hmm, actually, let me think about this differently.
# A cyclic sequence of length d with the transfer matrix T:
# Number of valid cyclic sequences = Tr(T^d) (without sum constraint).
# With sum constraint: use the augmented matrix T_aug (with sum mod 11 tracking).
# The trace of T_aug^d, restricted to states (a,b,c,0), gives the count of valid cyclic
# sequences of length d where the sum is 0 mod 11... but I need to be careful about
# how the sum is tracked.
#
# The state starts as (c_{d-2}, c_{d-1}, c_0, s) and after one step becomes
# (c_{d-1}, c_0, c_1, s + c_1 mod 11). Hmm, the sum tracking needs to account for
# all d elements, not just the ones added during transitions.
#
# Let me reconsider. In the cyclic sequence c_0, c_1, ..., c_{d-1}:
# State after processing c_0, c_1, c_2: (c_0, c_1, c_2, (c_0+c_1+c_2) mod 11)
# After transition to c_3: (c_1, c_2, c_3, (c_0+c_1+c_2+c_3) mod 11)
# ...
# After processing all d elements, back to state (c_{d-2}, c_{d-1}, c_0), 
# and sum = (c_0+c_1+...+c_{d-1}) mod 11.
# But we also need c_0 to be consistent (the cycle closes).
#
# Wait, I think the standard approach is:
# For a cyclic sequence of length d, the count is:
# sum over starting states (a,b,c,s) of T_aug^d [(a,b,c,s), (a,b,c,?)]
# where ? = s + (sum of all d elements - sum of first 3 elements)... this is getting complicated.
#
# Let me use a cleaner formulation. I'll build the augmented transfer matrix where:
# - State: (a, b, c, s) where s tracks sum of ALL elements placed so far, mod 11
# - Transition: (a,b,c,s) -> (b,c,d, (s+d) mod 11) if d ∉ {a,b,c}
#
# For a linear sequence of length d starting from some initial state (a,b,c,s_init):
# T_aug^{d-3} transforms (a,b,c, s_init) to states (x,y,z, s_final) where
# s_final = s_init + c_3 + c_4 + ... + c_{d-1} mod 11.
# But s_init = a + b + c mod 11 (if we start tracking from the first 3 elements).
# So s_final = a + b + c + c_3 + ... + c_{d-1} = sum of all d elements, mod 11.
#
# For a CYCLIC sequence: we need the last 3 elements to match the first 3.
# So starting from (c_0, c_1, c_2, (c_0+c_1+c_2) mod 11), after d-3 transitions,
# we need to end at (c_{d-2}, c_{d-1}, c_0, S mod 11) where S is the total sum.
# But we also need:
# - (c_{d-3}, c_{d-2}, c_{d-1}) -> c_0 valid: c_0 ∉ {c_{d-3}, c_{d-2}, c_{d-1}}
# - (c_{d-2}, c_{d-1}, c_0) -> c_1 valid: c_1 ∉ {c_{d-2}, c_{d-1}, c_0}
# - (c_{d-1}, c_0, c_1) -> c_2 valid: c_2 ∉ {c_{d-1}, c_0, c_1}
#
# This "wrap-around" constraint means we can't just use Tr(T^d).
#
# Actually, for the standard approach: Tr(T^d) works for counting cyclic sequences
# of length d with the constraint. Here's why:
#
# A cyclic sequence c_0, ..., c_{d-1} is valid iff for all i, c_i, c_{i+1}, c_{i+2}, c_{i+3}
# are pairwise distinct (indices mod d).
#
# This is a Markov chain condition. The state is the last 3 elements.
# State at position i: (c_i, c_{i+1}, c_{i+2}).
# Transition: (c_i, c_{i+1}, c_{i+2}) -> (c_{i+1}, c_{i+2}, c_{i+3}) iff c_{i+3} ∉ {c_i, c_{i+1}, c_{i+2}}.
#
# For a cyclic sequence of length d:
# Start at state (c_0, c_1, c_2).
# After d transitions (going through all positions), return to (c_0, c_1, c_2).
# Count = Tr(T^d).
#
# Wait, d transitions from (c_0,c_1,c_2):
# Step 1: -> (c_1,c_2,c_3) [adds c_3 with constraint c_3 ∉ {c_0,c_1,c_2}]
# Step 2: -> (c_2,c_3,c_4) [c_4 ∉ {c_1,c_2,c_3}]
# ...
# Step d-3: -> (c_{d-3}, c_{d-2}, c_{d-1}) [c_{d-1} ∉ {c_{d-4}, c_{d-3}, c_{d-2}}]
# 
# At this point, we've placed c_3 through c_{d-1} (that's d-3 elements).
# But for the cycle to close, we need:
# Step d-2: -> (c_{d-2}, c_{d-1}, c_0) [c_0 ∉ {c_{d-3}, c_{d-2}, c_{d-1}}]
# Step d-1: -> (c_{d-1}, c_0, c_1) [c_1 ∉ {c_{d-2}, c_{d-1}, c_0}]
# Step d:   -> (c_0, c_1, c_2) [c_2 ∉ {c_{d-1}, c_0, c_1}]
#
# After d steps, we return to (c_0, c_1, c_2). This requires all d "wrapping" constraints.
# So Tr(T^d) correctly counts the number of valid cyclic sequences of length d. ✓
#
# For the sum constraint: the augmented matrix T_aug has state (a,b,c,s).
# After d steps from (a,b,c,s_0), we arrive at (a,b,c,s_d).
# The sum added during d steps is: c_3 + c_4 + ... + c_{d-1} + c_0 + c_1 + c_2 = full sum.
# Wait: at each step, we add the NEW element.
# Step 1 (adding c_3): sum += c_3
# Step 2 (adding c_4): sum += c_4
# ...
# Step d-3 (adding c_{d-1}): sum += c_{d-1}
# Step d-2 (adding c_0, wrapping): sum += c_0
# Step d-1 (adding c_1): sum += c_1
# Step d (adding c_2): sum += c_2
#
# So total added = c_0 + c_1 + c_2 + c_3 + ... + c_{d-1} = sum of all elements.
# If we start with s_0 = 0, after d steps s_d = (sum of all elements) mod 11.
# For the cycle to close AND have sum ≡ 0 mod 11, we need to return to state (a,b,c,0).
#
# Hmm, but s_0 should be 0 (no elements summed yet). After step 1 (adding c_3), s = c_3.
# But wait, the initial state (c_0, c_1, c_2, s_0) has s_0 = 0 (before any elements are "added").
# But c_0, c_1, c_2 are the "initial" triple - their values ARE present but not counted in s_0.
# Then each step "adds" one element. After d steps, we've added c_3,...,c_{d-1},c_0,c_1,c_2.
# So s_d = c_0+c_1+c_2+c_3+...+c_{d-1} = full sum. ✓
#
# For the trace: Tr(T_aug^d) sums over all starting states (a,b,c,s_0) the number of
# d-step paths that return to (a,b,c,s_0). If we want sum = 0 mod 11, we need the 
# path to return with s = s_0. But s_0 is arbitrary (it's the "initial offset").
# For the actual sum to be 0 mod 11, we need the sum added = full sum ≡ 0 mod 11.
# This means s_d = s_0 + (full sum) should give full sum = s_d - s_0.
# If the path returns to (a,b,c,s_0), then s_d = s_0, so full sum = 0 mod 11. ✓
#
# Wait, that's not right. If the path returns to (a,b,c,s_0), that means s after d steps
# equals s_0. But s starts at s_0 and each step adds one element. So after d steps,
# s = s_0 + (sum of added elements) = s_0 + (full sum). For this to equal s_0, we need
# full sum ≡ 0 mod 11.
#
# So Tr(T_aug^d) over states with s=0 AND restricted to that specific s...
# Actually, Tr(T_aug^d) sums over ALL starting states (a,b,c,s) the diagonal entries.
# A diagonal entry at (a,b,c,s) counts paths returning to (a,b,c,s), which means
# full sum ≡ 0 mod 11 regardless of the value of s.
# So Tr(T_aug^d) counts valid cyclic sequences with sum ≡ 0 mod 11, but counted
# 11 times (once for each possible s value).
#
# Actually wait. The trace sums (a,b,c,s) for ALL s. But for a given cyclic sequence,
# the starting state is (c_0,c_1,c_2, s) for any s. The sequence is counted once for
# each s that allows it to return: since full sum ≡ 0 mod 11, ANY starting s works.
# So Tr(T_aug^d) = 11 * (number of valid cyclic sequences with sum ≡ 0 mod 11).
#
# Hmm, this doesn't seem right either. Let me reconsider.
#
# A valid cyclic sequence c_0,...,c_{d-1} with sum ≡ 0 mod 11 is represented by
# starting state (c_0, c_1, c_2, s) for EACH s ∈ {0,...,10}. The path is the same
# regardless of s (the color transitions don't depend on s), and the path returns to
# (c_0, c_1, c_2, s + full_sum mod 11). If full_sum ≡ 0, this is (c_0,c_1,c_2,s),
# so it's a diagonal entry for each s. So the sequence contributes 11 to the trace.
#
# Conversely, a sequence with full_sum ≢ 0 mod 11: the path from (c_0,c_1,c_2,s)
# returns to (c_0,c_1,c_2, s+full_sum), which is NOT the same state (since full_sum ≠ 0).
# So it contributes 0 to the trace.
#
# So: Tr(T_aug^d) = 11 * (number of valid cyclic sequences of length d with sum ≡ 0 mod 11). ✓
#
# Similarly, Tr(T^d) = number of valid cyclic sequences of length d (without sum constraint).
#
# For Burnside with the sum constraint:
# |Fix(r^k)| = number of valid cyclic sequences of length 120 that are fixed by rotation by k
#              AND have sum ≡ 0 mod 11.
# = (1/11) * Tr(T_aug^d) where d = gcd(k, 120), if d ≥ 4, else 0.
#
# Wait, actually I realize I need to be more careful. The sequences fixed by rotation by k
# have period dividing d = gcd(k, 120). Such a sequence is determined by its first d elements,
# which form a valid cyclic sequence of length d. And the sum of the 120-element sequence
# is (120/d) times the sum of the d-element period.
#
# So sum of 120-element sequence = (120/d) * sum_period.
# We need this ≡ 0 mod 11.
# Since gcd(120/d, 11) = 1 for all d | 120 (because 11 ∤ 120), this is equivalent to
# sum_period ≡ 0 mod 11.
#
# So |Fix(r^k)| = number of valid cyclic sequences of length d with sum ≡ 0 mod 11
#               = Tr(T_aug^d) / 11 (for d ≥ 4)
#               = 0 (for d < 4)
#
# Great. Now for reflections.
# A reflection of the 120-cycle maps position i to some 2a-i mod 120 (for some axis).
# There are 120 reflections. For the dihedral group D_120 acting on a cycle of 120 positions,
# the reflections are of two types:
# - Reflections through two vertices (opposite vertices): c_i <-> c_{2a-i} for some a
# - Reflections through two edges (midpoints of opposite edges): c_i <-> c_{2a+1-i} for some a
# But since 120 is even, we have 60 reflections through vertex pairs and 60 through edge pairs.
#
# Hmm, actually for a cycle of n=120 vertices:
# - If n is even: n/2 reflections through pairs of opposite vertices, n/2 through midpoints of opposite edges
#
# For a reflection σ, a sequence c is fixed by σ iff c_i = c_{σ(i)} for all i.
#
# This is more complex. For each reflection, the sequence is determined by its values
# on a fundamental domain (about half the positions), subject to the 4-distinct constraint
# being preserved by the reflection symmetry.
#
# This is getting very complex for a 30-minute time limit. Let me try to implement it.

# OK let me just build the transfer matrix and compute everything numerically.

import numpy as np
from collections import defaultdict
import sys

MOD = 10**9 + 7

# Generate all valid states: triples (a,b,c) with a,b,c distinct, from {0,...,5}
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

num_states = len(states)
print(f"Number of states: {num_states}")  # Should be 120

# Build transition matrix T (without sum tracking)
# T[i][j] = 1 if state i can transition to state j
# State i = (a,b,c), state j = (b,c,d) with d ∉ {a,b,c}
T = [[0] * num_states for _ in range(num_states)]
for i, (a, b, c) in enumerate(states):
    for d in range(6):
        if d != a and d != b and d != c:
            j = state_idx[(b, c, d)]
            T[i][j] = 1

# Matrix multiplication mod MOD
def mat_mul(A, B, mod):
    n = len(A)
    m = len(B[0])
    k = len(B)
    C = [[0] * m for _ in range(n)]
    for i in range(n):
        for j in range(m):
            s = 0
            for l in range(k):
                s += A[i][l] * B[l][j]
            C[i][j] = s % mod
    return C

def mat_pow(M, p, mod):
    n = len(M)
    result = [[1 if i == j else 0 for j in range(n)] for i in range(n)]
    base = [row[:] for row in M]
    while p > 0:
        if p % 2 == 1:
            result = mat_mul(result, base, mod)
        base = mat_mul(base, base, mod)
        p //= 2
    return result

# This is 120x120 matrix multiplication, which is feasible but slow in pure Python.
# Let me use numpy for speed, but be careful about overflow.

# Actually, for mod arithmetic, I should use numpy with careful modding.
# Or I can use a sparse representation since each row has exactly 3 nonzero entries.

# Let me use numpy with int64 and periodic modding.

# For the augmented matrix (with sum mod 11), the size is 120 * 11 = 1320.
# Matrix multiplication of 1320x1320 matrices: 1320^3 ≈ 2.3 * 10^9 per multiplication.
# With about 7 squarings (for power 120), this is ~1.6 * 10^10 operations.
# Too slow in pure Python but feasible with numpy.

# Let me use numpy.
import numpy as np

# Build augmented matrix: state (triple_idx, sum_mod_11)
# Transition: from (i, s) to (j, (s + d) % 11) where d is the new color
aug_size = num_states * 11
T_aug = np.zeros((aug_size, aug_size), dtype=np.int64)

for i, (a, b, c) in enumerate(states):
    for d in range(6):
        if d != a and d != b and d != c:
            j = state_idx[(b, c, d)]
            for s in range(11):
                s_new = (s + d) % 11
                T_aug[i * 11 + s][j * 11 + s_new] = 1

print(f"Augmented matrix size: {aug_size}x{aug_size}")
print(f"Non-zero entries: {np.count_nonzero(T_aug)}")

# Matrix power mod p using numpy
def np_mat_pow_mod(M, power, mod):
    n = M.shape[0]
    result = np.eye(n, dtype=np.int64)
    base = M.copy()
    while power > 0:
        if power % 2 == 1:
            # result = result @ base % mod
            # Do in chunks to avoid overflow
            result = np_mat_mul_mod(result, base, mod)
        base = np_mat_mul_mod(base, base, mod)
        power //= 2
    return result

def np_mat_mul_mod(A, B, mod):
    # For 1320x1320 int64 matrices, direct multiplication might overflow
    # Max entry in product: 1320 * (mod-1)^2 which overflows int64
    # Need to be careful. Let me split into chunks.
    n = A.shape[0]
    C = np.zeros((n, n), dtype=np.int64)
    # Process in blocks to avoid overflow
    # Each entry: sum of A[i,k]*B[k,j] for k. Max A[i,k] < mod, B[k,j] < mod.
    # A[i,k]*B[k,j] < mod^2 ≈ 10^18 < 9.2*10^18 (int64 max). OK for single product.
    # Sum of n such products: n * mod^2 ≈ 1320 * 10^18 > int64 max. Overflow!
    # Need to mod periodically.
    
    # Split columns of A / rows of B into chunks
    chunk = max(1, (9 * 10**18) // (int(mod) * int(mod)))
    chunk = min(chunk, n)
    for start in range(0, n, chunk):
        end = min(start + chunk, n)
        C = (C + A[:, start:end] @ B[start:end, :]) % mod
    return C

# Compute for each divisor d of 120 with d >= 4
# The divisors of 120: 
import math
divisors_120 = sorted([d for d in range(1, 121) if 120 % d == 0])
print(f"Divisors of 120: {divisors_120}")

# For each divisor d >= 4, compute Tr(T_aug^d) / 11
# Also need to count how many k in {0,...,119} have gcd(k, 120) = d
# Answer: φ(120/d) for each d | 120

# For Burnside rotation part:
# sum_{k=0}^{119} |Fix(r^k)| = sum_{d | 120, d >= 4} φ(120/d) * Tr(T_aug^d) / 11

# Euler's totient function
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

print("\nDivisors and phi values:")
for d in divisors_120:
    print(f"  d={d}: 120/d={120//d}, phi(120/d)={euler_phi(120//d)}")

# Now I need to compute Tr(T_aug^d) for each relevant d.
# The divisors of 120 that are >= 4: 4, 5, 6, 8, 10, 12, 15, 20, 24, 30, 40, 60, 120

relevant_divisors = [d for d in divisors_120 if d >= 4]
print(f"\nRelevant divisors: {relevant_divisors}")

# For efficiency, I should compute T_aug^d for each d using the factorization of d.
# But matrix powers can be computed directly for each d.

# Actually, the matrices are 1320x1320. Each matrix multiplication costs O(1320^3) ≈ 2.3*10^9.
# Even with numpy, this might take a few seconds per multiplication.
# For each d, computing T_aug^d takes about 7 multiplications (squarings for d up to 120).
# With 13 divisors, that's about 100 multiplications total, or about 100 * a few seconds ≈ minutes.
# This might be feasible but tight.

# Let me try a smarter approach: compute T_aug^{2^k} for k = 0,...,6 (powers of 2 up to 64),
# then combine for each d.

# Actually, let me just compute T_aug^d for each d using repeated squaring from scratch.
# But I can reuse partial results.

# The fastest approach: compute T_aug, T_aug^2, T_aug^4, T_aug^8, T_aug^16, T_aug^32, T_aug^64
# Then for d=120: T_aug^64 * T_aug^32 * T_aug^16 * T_aug^8 = T_aug^120

# Let me compute all needed powers.
print("\nComputing matrix powers...")
sys.stdout.flush()

# Start computation
# First, let me verify with a small test: Tr(T^4) should count valid 4-cycles.
# A valid 4-cycle c_0,c_1,c_2,c_3 has all 4 pairwise distinct AND
# c_1,c_2,c_3,c_0 pairwise distinct AND c_2,c_3,c_0,c_1 ... etc.
# Since all windows wrap around and it's a 4-cycle, the constraint is just that
# all 4 are distinct. Number of such cycles: 6*5*4*3 = 360.
# But as CYCLES (up to starting point), each is counted 4 times. Wait no, Tr(T^4)
# counts each cyclic sequence once per starting state, so the trace counts ordered
# cyclic sequences (fixing the start). Actually, Tr(T^d) counts the number of 
# valid cyclic sequences where the state returns to itself after d steps.
# Each cyclic sequence c_0,...,c_{d-1} contributes 1 to the trace for EACH starting
# position i where (c_i, c_{i+1}, c_{i+2}) is used as the starting state.
# So Tr(T^d) counts sequences with multiplicity d? No...
# 
# Actually, Tr(T^d) = sum_i (T^d)_{ii} = sum over states s of [T^d]_{ss}.
# [T^d]_{ss} counts the number of d-step paths from s to s. Each such path
# corresponds to a cyclic sequence where c_0,c_1,c_2 is determined by s, and
# the subsequent elements complete a cycle back to s.
# Different starting states s correspond to different starting positions in the same
# cyclic sequence. So each cyclic sequence of length d is counted d times in Tr(T^d).
#
# Wait, that's not right either. Let me think again.
# A cyclic sequence c_0,...,c_{d-1} can be "entered" at any starting triple
# (c_i, c_{i+1}, c_{i+2}) for i = 0, ..., d-1. Each gives a different starting state.
# So the cyclic sequence is counted d times in Tr(T^d).
# Therefore, number of distinct cyclic sequences = Tr(T^d) / d.
# For d=4: Tr(T^4) / 4 = number of distinct valid 4-cycles = 6*5*4*3 / 4 = 90? 
# Hmm, the number of distinct NECKLACES is 6*5*4*3/4 = 90, but Tr(T^d)/d counts
# distinct CYCLIC sequences (not necklaces). Actually, Tr(T^d) = Tr(T^d), which
# double-counts sequences that have symmetry. Hmm.
# 
# Actually, Tr(T^d) counts the number of LABELED cyclic sequences: sequences
# c_0,...,c_{d-1} on a labeled cycle where the labeling distinguishes the starting point.
# For a labeled cycle with a distinguished starting vertex (vertex 0), a valid sequence
# is any valid coloring. The trace exactly counts these.
# But for our application (Burnside's lemma), we need to count fixed points of group
# elements acting on LABELED cyclic sequences of length 120 (where labels are positions 0-119).
# So Tr(T^d) directly gives |Fix(r^0)| (the identity) when d=120.
# And for rotation by k with gcd(k,120) = d: |Fix(r^k)| = Tr(T^d)... 
# wait, no. If the labeled sequence has period d, it repeats every d positions.
# But the labeled sequence of length 120 is determined by its first d elements.
# So |Fix(r^k)| = number of valid labeled cyclic sequences of length d, which is Tr(T^d).
# Hmm, but the cyclic sequence of length d might not account for the wrap-around at 
# position 120 correctly. Actually it does, since the sequence repeats with period d.
#
# Let me re-derive: Rotation by k fixes c iff c_i = c_{i+k} for all i.
# This means the sequence has period dividing d = gcd(k, 120).
# The sequence is determined by c_0, ..., c_{d-1}, which must satisfy:
# - The 4-distinct constraint at every position (checking windows of 4 mod d)
# This is exactly the constraint for a valid cyclic sequence of length d on a d-cycle.
# The number of such sequences = Tr(T^d) (for the labeled d-cycle with starting point).
# But wait, the labeled d-cycle with starting point: each vertex of the d-cycle has a 
# label from {0,...,d-1}. The number of valid colorings of this cycle IS Tr(T^d).
# And each such coloring gives exactly one labeled 120-sequence (by repeating with period d).
# So |Fix(r^k)| = Tr(T^d). ✓
#
# Wait, but there's a subtlety: Tr(T^d) counts the labeled d-cycle colorings.
# Each starting triple determines the rest. But I argued earlier that each cyclic sequence
# is counted d times. So Tr(T^d) = d * (number of distinct cyclic sequences of length d).
# For the Burnside application, I want the number of LABELED 120-sequences with period d.
# A labeled 120-sequence with period d: determined by its first d elements.
# The first d elements form a LABELED cyclic sequence on positions 0,...,d-1.
# The number of such labeled sequences is Tr(T^d) (counting each labeled sequence once?
# or d times?).
#
# OK I think I'm overcomplicating this. Let me just carefully verify with a small example.
#
# For d=4, 6 colors, the constraint is all 4 pairwise distinct:
# Tr(T^4) = number of 4-step closed walks in the state graph.
# Each state (a,b,c): transition to (b,c,d) with d ∉ {a,b,c}.
# 4-step closed walk from (a,b,c) back to (a,b,c):
# Step 1: (a,b,c) -> (b,c,d) with d ∉ {a,b,c}
# Step 2: (b,c,d) -> (c,d,a') with a' = a (need to return), and a ∉ {b,c,d}
#   - Is a ∉ {b,c,d}? a ≠ b and a ≠ c (given, since starting state is valid), a ≠ d (since d ∉ {a,b,c}).
#   - So yes, we can go to (c,d,a).
# Step 3: (c,d,a) -> (d,a,b') with b' = b, and b ∉ {c,d,a}
#   - b ≠ c (given), b ≠ d (since d was chosen ∉ {a,b,c}), b ≠ a (given). ✓
# Step 4: (d,a,b) -> (a,b,c') with c' = c, and c ∉ {d,a,b}
#   - c ≠ d (since d ∉ {a,b,c}), c ≠ a (given), c ≠ b (given). ✓
#
# So from each starting state (a,b,c), for each choice of d, the 4-step walk is forced.
# d has 3 choices (any of the 3 colors not in {a,b,c}).
# Starting states: 120.
# Tr(T^4) = 120 * 3 = 360.
#
# This represents 360 labeled cyclic sequences of length 4 (on labeled vertices 0,1,2,3)
# where all 4 are distinct. The number of such sequences: 6*5*4*3 = 360. ✓
# (Choose c_0: 6, c_1: 5, c_2: 4, c_3: 3. Each labeling is distinct.)
#
# So Tr(T^d) counts the number of LABELED cyclic sequences of length d (on a labeled d-cycle).
# This is exactly what we need for |Fix(r^k)| where gcd(k,120)=d.
#
# OK great, now let me compute. I'll use a more efficient approach.

# For the sum constraint: Tr(T_aug^d) = 11 * (number of labeled d-cycle colorings with sum ≡ 0 mod 11)
# So |Fix(r^k)| with sum constraint = Tr(T_aug^d) / 11 for d = gcd(k, 120).

# Let me verify: Tr(T_aug^4) should be 11 * |{labeled 4-cycle colorings with sum ≡ 0 mod 11}|.
# Sum of 4 distinct colors from {0,...,5}: e.g., {0,1,2,3} has sum 6, {0,1,2,4} has sum 7, etc.
# The 4-subsets of {0,1,2,3,4,5}: C(6,4) = 15.
# Each 4-subset can be arranged in 4! = 24 ways on a labeled 4-cycle.
# So total labeled colorings: 15 * 24 = 360. ✓
# Among these, those with sum ≡ 0 mod 11:
# The 4-subsets of {0,...,5} with their sums:
sums = {}
from itertools import combinations, permutations
for combo in combinations(range(6), 4):
    s = sum(combo)
    sums[s] = sums.get(s, 0) + 1
print(f"\n4-subsets by sum: {sums}")
# Sums range from 0+1+2+3=6 to 2+3+4+5=14.
# Sum ≡ 0 mod 11: sum = 11. 
# Which 4-subsets have sum 11? {0,2,4,5}:11, {0,3,4,5}:12... 
# {1,2,3,5}:11. {0,2,4,5}:11.
count_sum_0_mod_11 = 0
for combo in combinations(range(6), 4):
    if sum(combo) % 11 == 0:
        count_sum_0_mod_11 += 1
        print(f"  {combo}: sum={sum(combo)}")
print(f"4-subsets with sum ≡ 0 mod 11: {count_sum_0_mod_11}")
print(f"Labeled 4-cycle colorings with sum ≡ 0: {count_sum_0_mod_11 * 24}")
print(f"Expected Tr(T_aug^4) = 11 * {count_sum_0_mod_11 * 24} = {11 * count_sum_0_mod_11 * 24}")

