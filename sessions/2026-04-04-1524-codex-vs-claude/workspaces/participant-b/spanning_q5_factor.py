from math import comb
from collections import Counter

n = 16
N = 1 << n  # 65536

# Compute Laplacian eigenvalues and multiplicities
eigenvalues = {}  # lam -> multiplicity
degree = comb(n, 1) + comb(n, 2)
print(f"Degree: {degree}")

for w in range(n + 1):
    t = n - 2 * w
    mu_num = t * t + 2 * t - n  # numerator of 2*mu
    assert mu_num % 2 == 0
    mu = mu_num // 2
    lam = degree - mu
    mult = comb(n, w)
    if lam == 0:
        print(f"  w={w}: eigenvalue 0, mult {mult} (skipped)")
        continue
    eigenvalues[lam] = eigenvalues.get(lam, 0) + mult
    print(f"  w={w}: t={t}, mu={mu}, lambda={lam}, mult={mult}")

print(f"\nDistinct non-zero eigenvalues:")
total_mult = 0
for lam in sorted(eigenvalues.keys()):
    print(f"  lambda={lam}, multiplicity={eigenvalues[lam]}")
    total_mult += eigenvalues[lam]
print(f"Total non-zero multiplicity: {total_mult} (should be {N-1})")

# Compute prime factorization of tau(G)
# tau = (1/N) * product of lam^mult
# First factorize each eigenvalue
def factorize(n):
    factors = Counter()
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors[d] += 1
            n //= d
        d += 1
    if n > 1:
        factors[n] += 1
    return factors

# Compute total prime factorization
total_factors = Counter()
for lam, mult in eigenvalues.items():
    lam_factors = factorize(lam)
    for p, e in lam_factors.items():
        total_factors[p] += e * mult

# Subtract the factor of N = 2^16
total_factors[2] -= 16

print(f"\nPrime factorization of tau(G):")
for p in sorted(total_factors.keys()):
    print(f"  {p}^{total_factors[p]}")

# Format as string
parts = []
for p in sorted(total_factors.keys()):
    e = total_factors[p]
    parts.append(f"{p}^{e}")
result = " * ".join(parts)
print(f"\ntau(G) = {result}")

# Verify: compute the actual number (it's huge, but Python can handle big ints)
tau = 1
for lam, mult in eigenvalues.items():
    tau *= lam ** mult
tau //= N
print(f"\nNumber of digits in tau(G): {len(str(tau))}")

# Verify prime factorization
remaining = tau
for p in sorted(total_factors.keys()):
    e = total_factors[p]
    for _ in range(e):
        assert remaining % p == 0, f"Failed for prime {p}"
        remaining //= p
print(f"After dividing out all prime factors, remaining = {remaining}")
assert remaining == 1, "Prime factorization is incomplete!"
print("Prime factorization verified!")

