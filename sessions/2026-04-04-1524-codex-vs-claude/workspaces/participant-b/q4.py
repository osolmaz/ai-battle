# Question: Count the number of units in the ring Z[i]/(7+11i)
# where Z[i] is the Gaussian integers.
#
# This requires:
# 1. Computing N(7+11i) = 49 + 121 = 170
# 2. Factoring (7+11i) in Z[i]
# 3. Using CRT and counting units in quotient rings
#
# Let me verify the answer computationally.

def hamming_weight(n):
    return bin(n).count('1')

# First, let me factor 7+11i in Z[i]
# N(7+11i) = 170 = 2 * 5 * 17
# 
# In Z[i]:
# 2 = -i(1+i)^2, so (2) = (1+i)^2
# 5 = (2+i)(2-i), so (5) = (2+i)(2-i)  
# 17 = (4+i)(4-i), so (17) = (4+i)(4-i)
#
# So we need to factor 7+11i into primes of Z[i]
# The primes dividing 7+11i must have norms dividing N(7+11i)=170

# Let me find the factorization by trial division
# Try dividing by 1+i: (7+11i)/(1+i) = (7+11i)(1-i)/2 = (7-7i+11i-11i^2)/2 = (7+4i+11)/2 = (18+4i)/2 = 9+2i
# So 7+11i = (1+i)(9+2i)
# N(9+2i) = 81+4 = 85 = 5*17

# Try dividing 9+2i by 2+i: (9+2i)/(2+i) = (9+2i)(2-i)/5 = (18-9i+4i-2i^2)/5 = (18-5i+2)/5 = (20-5i)/5 = 4-i
# So 9+2i = (2+i)(4-i)
# N(4-i) = 16+1 = 17. So 4-i is a prime in Z[i] (associated to 4-i, norm 17)

# So 7+11i = (1+i)(2+i)(4-i)
# Verify: (1+i)(2+i) = 2+i+2i+i^2 = 2+3i-1 = 1+3i
# (1+3i)(4-i) = 4-i+12i-3i^2 = 4+11i+3 = 7+11i ✓

# So (7+11i) = (1+i)(2+i)(4-i)
# These are three distinct primes (norms 2, 5, 17 respectively)

# By CRT: Z[i]/(7+11i) ≅ Z[i]/(1+i) × Z[i]/(2+i) × Z[i]/(4-i)
# Z[i]/(1+i) ≅ F_2 (2 elements, 1 unit)
# Z[i]/(2+i) ≅ F_5 (5 elements, 4 units)
# Z[i]/(4-i) ≅ F_17 (17 elements, 16 units)

# Total units = 1 * 4 * 16 = 64

# Let me verify computationally
def gauss_mod(a, b, alpha_re, alpha_im):
    """Reduce a+bi modulo alpha = alpha_re + alpha_im*i"""
    norm = alpha_re**2 + alpha_im**2
    q_re = round((a * alpha_re + b * alpha_im) / norm)
    q_im = round((b * alpha_re - a * alpha_im) / norm)
    r_re = a - q_re * alpha_re + q_im * alpha_im
    r_im = b - q_re * alpha_im - q_im * alpha_re
    return (r_re, r_im)

alpha_re, alpha_im = 7, 11
norm = alpha_re**2 + alpha_im**2
print(f"N(7+11i) = {norm}")

# Find all residues
residues = set()
for a in range(-30, 31):
    for b in range(-30, 31):
        r = gauss_mod(a, b, alpha_re, alpha_im)
        residues.add(r)

print(f"Number of residues: {len(residues)}")

# Count units
def gauss_mult_mod(a, b, c, d):
    re = a*c - b*d
    im = a*d + b*c
    return gauss_mod(re, im, alpha_re, alpha_im)

one = gauss_mod(1, 0, alpha_re, alpha_im)
units = 0
for r in residues:
    for s in residues:
        prod = gauss_mult_mod(r[0], r[1], s[0], s[1])
        if prod == one:
            units += 1
            break

print(f"Number of units: {units}")
print(f"Expected: 1 * 4 * 16 = {1*4*16}")

