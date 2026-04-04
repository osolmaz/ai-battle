# Let me try a different question: CRT + modular arithmetic

# Compute: Find the unique integer x with 0 <= x < 2*3*5*7*11*13 = 30030 such that
# x ≡ 1 (mod 2), x ≡ 2 (mod 3), x ≡ 3 (mod 5), x ≡ 4 (mod 7), x ≡ 5 (mod 11), x ≡ 6 (mod 13)
# Then compute x^3 mod 1000000007

from sympy.ntheory.modular import crt

moduli = [2, 3, 5, 7, 11, 13]
remainders = [1, 2, 3, 4, 5, 6]

r, m = crt(moduli, remainders)
print(f"x = {r}, modulus product = {m}")
print(f"x^3 mod 10^9+7 = {pow(r, 3, 1000000007)}")
