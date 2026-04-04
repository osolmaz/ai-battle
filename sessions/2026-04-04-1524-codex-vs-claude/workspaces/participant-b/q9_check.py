# Final verification of the reflection argument and answer

MOD = 10**9 + 7

# Verify reflection argument with a small example
# On a cycle of length 8 with 6 colors, same constraints (every 4 consecutive pairwise distinct)
# Check if any valid sequence is fixed by a vertex-pair reflection.

def check_reflections(n, num_colors=6):
    """Check if any valid n-cycle is fixed by any reflection."""
    from itertools import product
    
    # Generate all valid cyclic sequences
    valid = []
    for seq in product(range(num_colors), repeat=n):
        ok = True
        for i in range(n):
            w = [seq[(i+j)%n] for j in range(4)]
            if len(set(w)) < 4:
                ok = False
                break
        if ok:
            valid.append(seq)
    
    print(f"n={n}: {len(valid)} valid sequences")
    
    # Check vertex-pair reflections
    fixed_by_reflection = 0
    for seq in valid:
        for v in range(n):
            # Reflection through vertex v: sigma(k) = 2v - k mod n
            is_fixed = True
            for k in range(n):
                if seq[k] != seq[(2*v - k) % n]:
                    is_fixed = False
                    break
            if is_fixed:
                fixed_by_reflection += 1
                print(f"  Fixed by vertex reflection through {v}: {seq}")
                break
    
    # Check edge-midpoint reflections
    for seq in valid:
        for v in range(n):
            # Reflection through midpoint of edge (v, v+1): sigma(k) = 2v+1-k mod n
            is_fixed = True
            for k in range(n):
                if seq[k] != seq[(2*v + 1 - k) % n]:
                    is_fixed = False
                    break
            if is_fixed:
                fixed_by_reflection += 1
                print(f"  Fixed by edge reflection through ({v},{v+1}): {seq}")
                break
    
    print(f"  Total fixed by any reflection: {fixed_by_reflection}")
    return fixed_by_reflection

# Test with small even cycles
for n in [4, 6, 8, 10]:
    if n <= 10:  # feasible
        check_reflections(n)
    print()

