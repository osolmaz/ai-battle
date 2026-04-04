MOD = 10**9 + 7

# From previous computation:
rotation_sum = 969479437

# All 120 reflections contribute 0 to the Burnside sum.
# Reason: For vertex-pair reflections through v and v+60, the palindrome
# c_k = c_{2v-k mod 120} forces c_{v-1} = c_{v+1}. The 4-window at position
# v-2 contains c_{v-2}, c_{v-1}, c_v, c_{v+1} = c_{v-2}, c_{v-1}, c_v, c_{v-1}
# with c_{v-1} repeated, violating the pairwise distinct constraint.
# For edge-midpoint reflections, c_v = c_{v+1} is forced, directly violating distinctness.

reflection_sum = 0
total_sum = (rotation_sum + reflection_sum) % MOD

# |D_120| = 240
inv_240 = pow(240, MOD - 2, MOD)
answer = total_sum * inv_240 % MOD

print(f"Rotation sum: {rotation_sum}")
print(f"Reflection sum: {reflection_sum}")
print(f"Total Burnside sum: {total_sum}")
print(f"|D_120| = 240")
print(f"inv(240) mod MOD = {inv_240}")
print(f"Answer = {answer}")

# Let me also verify: rotation_sum should be divisible by 240 (or at least the 
# real number of classes should be an integer).
# Since we're working mod MOD, we can't directly check divisibility.
# But let's verify the answer makes sense.

# Double-check: also compute rotation_classes = rotation_sum / 120 (for cyclic group only)
inv_120 = pow(120, MOD - 2, MOD)
rotation_classes = rotation_sum * inv_120 % MOD
print(f"\nRotation-only classes (C_120): {rotation_classes}")

# The dihedral classes should be roughly half the cyclic classes 
# (since reflections halve the count, modulo contributions from fixed reflections).
# With 0 reflection fixed points, dihedral classes = cyclic classes / 2... 
# Hmm no, that's not how Burnside works. Let me reconsider.

# Burnside for D_120: (1/240) * (rotation_sum + reflection_sum)
# Burnside for C_120: (1/120) * rotation_sum

# If reflection_sum = 0:
# D_120 classes = rotation_sum / 240 = (rotation_sum / 120) / 2 = C_120 classes / 2

# This makes sense: each cyclic equivalence class either:
# 1. Is invariant under some reflection -> splits into 1 dihedral class
# 2. Is NOT invariant -> merges with its mirror image into 1 dihedral class

# Since no valid sequence is fixed by any reflection, ALL cyclic classes are type 2.
# So dihedral classes = cyclic classes / 2. ✓

print(f"\nD_120 classes = C_120 classes / 2 = {rotation_classes} / 2 = {rotation_classes * pow(2, MOD-2, MOD) % MOD}")
print(f"This should match: {answer}")
print(f"Match: {answer == rotation_classes * pow(2, MOD-2, MOD) % MOD}")

