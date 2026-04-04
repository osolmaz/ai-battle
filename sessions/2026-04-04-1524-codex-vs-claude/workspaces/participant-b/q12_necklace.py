# Count necklaces (up to D_12) of 12 beads with 4 red, 4 blue, 4 green
from math import factorial, gcd
from itertools import permutations

def multinomial(n, groups):
    result = factorial(n)
    for g in groups:
        result //= factorial(g)
    return result

n = 12
colors = [4, 4, 4]  # 4 red, 4 blue, 4 green
num_colors = len(colors)

# Burnside's lemma with D_12

# ROTATIONS
rotation_sum = 0
for k in range(n):
    d = gcd(k, n) if k > 0 else n  # period
    # Each color needs colors[c] * d / n beads per period, must be integer
    per_period = []
    valid = True
    for c in range(num_colors):
        if (colors[c] * d) % n != 0:
            valid = False
            break
        per_period.append(colors[c] * d // n)
    
    if valid:
        fix = multinomial(d, per_period)
    else:
        fix = 0
    rotation_sum += fix

print(f"Rotation sum: {rotation_sum}")
print(f"Cyclic necklaces: {rotation_sum // n}")

# REFLECTIONS
# For n=12 (even): 6 vertex-pair reflections, 6 edge-pair reflections
reflection_sum = 0

# Vertex-pair: 2 fixed beads + 5 pairs
# For each vertex-pair reflection:
# Need: for each color c, f_c + 2*p_c = colors[c], where f_c = #fixed beads of color c, p_c = #pairs of color c
# Sum f_c = 2, sum p_c = 5
# f_c must have same parity as colors[c] (since colors[c] - f_c = 2*p_c must be even)

def count_vertex_fixed(fixed_count, pair_count, num_pairs):
    """Count arrangements of fixed beads and pairs."""
    # Fixed beads: 2 beads, each assigned a color
    # But the fixed beads are distinguishable (they're at specific positions)
    # So the number of ways to assign colors to 2 fixed beads with f_c of each color:
    fixed_arrangements = multinomial(2, fixed_count)
    # Pairs: num_pairs pairs, assigned colors with p_c pairs of each color:
    pair_arrangements = multinomial(num_pairs, pair_count)
    return fixed_arrangements * pair_arrangements

# Enumerate all valid (f_R, f_B, f_G) with f_c + 2*p_c = 4, sum f_c = 2
from itertools import product as cart_product
vertex_fix_per_reflection = 0
for f in cart_product(range(3), repeat=num_colors):  # f_c in {0, 1, 2}
    if sum(f) != 2:
        continue
    valid = True
    p = []
    for c in range(num_colors):
        remainder = colors[c] - f[c]
        if remainder < 0 or remainder % 2 != 0:
            valid = False
            break
        p.append(remainder // 2)
    if valid and sum(p) == 5:
        count = count_vertex_fixed(list(f), p, 5)
        vertex_fix_per_reflection += count

print(f"Vertex-pair fix per reflection: {vertex_fix_per_reflection}")
reflection_sum += 6 * vertex_fix_per_reflection

# Edge-pair: 6 pairs, no fixed beads
# f_c = 0 for all, 2*p_c = colors[c], p_c = colors[c]/2
edge_fix_per_reflection = 0
p_edge = []
valid_edge = True
for c in range(num_colors):
    if colors[c] % 2 != 0:
        valid_edge = False
        break
    p_edge.append(colors[c] // 2)
if valid_edge:
    edge_fix_per_reflection = multinomial(6, p_edge)

print(f"Edge-pair fix per reflection: {edge_fix_per_reflection}")
reflection_sum += 6 * edge_fix_per_reflection

print(f"Reflection sum: {reflection_sum}")

total = rotation_sum + reflection_sum
print(f"Total Burnside sum: {total}")
print(f"|D_12| = {2*n}")
print(f"Dihedral necklaces: {total // (2*n)}")
assert total % (2*n) == 0

# Verify with brute force
from itertools import combinations

def brute_force_necklaces():
    """Generate all colorings and group by dihedral equivalence."""
    # Generate all multiset permutations of [0]*4 + [1]*4 + [2]*4
    from itertools import permutations
    seen = set()
    classes = set()
    
    # Generate all distinct permutations
    base = [0]*4 + [1]*4 + [2]*4
    all_perms = set(permutations(base))
    
    for perm in all_perms:
        # Compute canonical form under D_12
        min_form = perm
        for k in range(n):
            rotated = perm[k:] + perm[:k]
            if rotated < min_form:
                min_form = rotated
            reflected = perm[k::-1] + perm[-1:k:-1]  # wrong
            # Proper reflection: reverse, then rotate
        
        # Actually, let me compute all D_12 images
        best = perm
        for k in range(n):
            rotated = tuple(perm[(i+k)%n] for i in range(n))
            if rotated < best:
                best = rotated
            reflected = tuple(perm[(k-i)%n] for i in range(n))
            if reflected < best:
                best = reflected
        classes.add(best)
    
    return len(classes)

bf = brute_force_necklaces()
print(f"\nBrute force: {bf} dihedral necklaces")

