# Verify: number of units in Z[i]/(6+8i)
# Z[i]/(alpha) where alpha = 6+8i, N(alpha) = 100

# Elements of Z[i]/(alpha) can be represented by their residues
# We need to find a system of representatives for Z[i] mod (6+8i)

# Method: enumerate all a+bi with 0 <= a,b < some bound,
# and identify equivalence classes mod (6+8i)

def gauss_mod(a, b, alpha_re, alpha_im):
    """Reduce a+bi modulo alpha = alpha_re + alpha_im*i using nearest integer division"""
    # To divide (a+bi) by (alpha_re + alpha_im*i):
    # (a+bi)/(alpha_re + alpha_im*i) = (a+bi)(alpha_re - alpha_im*i) / N(alpha)
    norm = alpha_re**2 + alpha_im**2
    # Real part of quotient: (a*alpha_re + b*alpha_im) / norm
    # Imag part: (b*alpha_re - a*alpha_im) / norm
    q_re = round((a * alpha_re + b * alpha_im) / norm)
    q_im = round((b * alpha_re - a * alpha_im) / norm)
    # Remainder: (a+bi) - (q_re + q_im*i)(alpha_re + alpha_im*i)
    # = (a - q_re*alpha_re + q_im*alpha_im) + (b - q_re*alpha_im - q_im*alpha_re)*i
    r_re = a - q_re * alpha_re + q_im * alpha_im
    r_im = b - q_re * alpha_im - q_im * alpha_re
    return (r_re, r_im)

# Find all residues mod 6+8i
alpha_re, alpha_im = 6, 8
norm = alpha_re**2 + alpha_im**2  # 100

# Generate representatives
residues = set()
for a in range(-20, 21):
    for b in range(-20, 21):
        r = gauss_mod(a, b, alpha_re, alpha_im)
        residues.add(r)

print(f"Number of residues: {len(residues)}")  # Should be 100

# Now check which elements are units
# An element r = (r_re, r_im) is a unit if there exists s = (s_re, s_im) such that
# r * s ≡ 1 (mod alpha)

def gauss_mult(a, b, c, d):
    """Multiply (a+bi)(c+di) = (ac-bd) + (ad+bc)i"""
    return (a*c - b*d, a*d + b*c)

def gauss_reduce(a, b):
    return gauss_mod(a, b, alpha_re, alpha_im)

units = set()
residue_list = sorted(residues)

# For each residue, check if it has a multiplicative inverse
for r in residue_list:
    for s in residue_list:
        prod = gauss_mult(r[0], r[1], s[0], s[1])
        prod_red = gauss_reduce(prod[0], prod[1])
        if prod_red == (1, 0) or prod_red == gauss_reduce(1, 0):
            units.add(r)
            break

one_red = gauss_reduce(1, 0)
print(f"1 mod alpha = {one_red}")
print(f"Number of units: {len(units)}")

# Also compute using the formula: phi for Gaussian integers
# 6+8i = 2(3+4i) = -i(1+i)^2 * (2+i)^2
# Units = N(alpha) * prod over prime ideals p|alpha of (1 - 1/N(p))
# Primes dividing (6+8i): (1+i) with N=2, (2+i) with N=5
# But (1+i) appears to power 2 and (2+i) to power 2
# For (p^k): units in Z[i]/(p^k) = N(p)^k - N(p)^(k-1) = N(p)^(k-1)(N(p)-1)
# Z[i]/(1+i)^2: |units| = N(1+i)^1 * (N(1+i) - 1) = 2 * 1 = 2
# Z[i]/(2+i)^2: |units| = N(2+i)^1 * (N(2+i) - 1) = 5 * 4 = 20
# Total = 2 * 20 = 40
print(f"Expected by formula: 2 * 20 = {2*20}")

