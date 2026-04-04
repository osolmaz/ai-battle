from itertools import product as cart_product

def aut_count_brute(group_orders):
    """Count automorphisms of Z/d_1 × ... × Z/d_k by brute force."""
    n = len(group_orders)
    G_size = 1
    for d in group_orders:
        G_size *= d
    
    elements = list(cart_product(*[range(d) for d in group_orders]))
    
    def add(x, y):
        return tuple((x[i] + y[i]) % group_orders[i] for i in range(n))
    
    def scale(c, x):
        return tuple((c * x[i]) % group_orders[i] for i in range(n))
    
    zero = tuple([0]*n)
    
    valid_images = []
    for i in range(n):
        d = group_orders[i]
        valid = [x for x in elements if scale(d, x) == zero]
        valid_images.append(valid)
    
    count = 0
    for imgs in cart_product(*valid_images):
        image_set = set()
        for elem in elements:
            result = zero
            for i in range(n):
                result = add(result, scale(elem[i], imgs[i]))
            image_set.add(result)
        if len(image_set) == G_size:
            count += 1
    
    return count

# Verify small cases
print("Z/8Z × Z/2Z:", aut_count_brute([8, 2]))
print("Z/8Z × Z/4Z:", aut_count_brute([8, 4]))
print("Z/8Z × Z/2Z × Z/2Z:", aut_count_brute([8, 2, 2]))

# Now compute the target: Z/4Z × Z/4Z × Z/2Z × Z/2Z × Z/2Z
# This has 128 elements, so brute force is too slow (endomorphism ring too large)
# But let me verify the formula: |Aut| = 64512 * 1024 = 66060288

# Let me verify against a formula from literature
# For Z/p^a × Z/p^b with a >= b:
# |Aut| = p^(a+b-2) * (p^2-1) * (p-1) if a > b
# |Aut| = p^(2a-2) * (p^2-1) * (p^2-p) if a = b

# Z/4 × Z/2 = Z/2^2 × Z/2^1, a=2, b=1 (a > b):
# |Aut| = 2^(2+1-2) * (4-1) * (2-1) = 2 * 3 * 1 = 6. But brute force gives 8!
# So this formula is wrong.

# Let me try another formula. From https://math.stackexchange.com/...
# |Aut(Z/p^a × Z/p^b)| for a >= b:
# = p^(2b-1) * (p-1) * (p^2-1) * p^(a-b)  ... no.

# Actually, for Z/4 × Z/2: |Aut| = 8 (verified by brute force).
# 8 = 2^3.
# For Z/4 × Z/4: |Aut| = 96 = 2^5 * 3.
# For Z/8 × Z/2: let me check.

print("\nFormula verification:")
# Z/4Z × Z/2Z: |Aut| = 8 ✓

