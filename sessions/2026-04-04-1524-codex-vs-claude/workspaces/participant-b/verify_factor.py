import sys
sys.set_int_max_str_digits(1000000)
from math import comb, log10

n = 16
N = 1 << n
degree = comb(n, 1) + comb(n, 2)

eigenvalues = {}
for w in range(n + 1):
    t = n - 2 * w
    mu = (t * t + 2 * t - n) // 2
    lam = degree - mu
    if lam == 0:
        continue
    eigenvalues[lam] = eigenvalues.get(lam, 0) + comb(n, w)

tau = 1
for lam, mult in eigenvalues.items():
    tau *= lam ** mult
tau //= N

# Verify factorization
factors = {2: 188293, 3: 68000, 5: 25772, 7: 20128, 11: 12376, 13: 2380}
check = 1
for p, e in factors.items():
    check *= p ** e

print(f"tau == check: {tau == check}")
print(f"Number of digits: {len(str(tau))}")
