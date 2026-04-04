# Verify f(p^k) formula for p ≡ 1 mod 4
# Formula: f(p^k) = p^{k-1} * (k*(p-1) + p)

def f_brute(n):
    count = 0
    for a in range(n):
        a2 = (a*a) % n
        for b in range(n):
            if (a2 + b*b) % n == 0:
                count += 1
    return count

def f_formula(p, k):
    """f(p^k) using the derived formulas"""
    if p == 2:
        return 2**k  # empirical
    elif p % 4 == 3:
        return p ** (2 * (k // 2))
    else:  # p % 4 == 1
        return p**(k-1) * (k*(p-1) + p)

# Verify for various primes and powers
print("Verification of formula:")
for p in [2, 3, 5, 7, 11, 13, 17]:
    for k in range(1, 5):
        n = p**k
        if n <= 500:  # brute force limit
            bf = f_brute(n)
            fm = f_formula(p, k)
            match = "✓" if bf == fm else "✗"
            print(f"  f({p}^{k}) = f({n}): brute={bf}, formula={fm} {match}")

# Compute f(4100625) = f(3^8 * 5^4) = f(3^8) * f(5^4)
f_3_8 = f_formula(3, 8)
f_5_4 = f_formula(5, 4)
result = f_3_8 * f_5_4
print(f"\nf(3^8) = {f_3_8}")
print(f"f(5^4) = {f_5_4}")
print(f"f(4100625) = f(3^8) * f(5^4) = {result}")

# Also verify f(3^8) by checking against smaller values
# f(3^k) = 3^{2*floor(k/2)} for k=1,...,8
for k in range(1, 9):
    fm = f_formula(3, k)
    n = 3**k
    if n <= 500:
        bf = f_brute(n)
        match = "✓" if bf == fm else "✗"
        print(f"  f(3^{k}) = f({n}): brute={bf}, formula={fm} {match}")
    else:
        print(f"  f(3^{k}) = f({n}): formula={fm}")

