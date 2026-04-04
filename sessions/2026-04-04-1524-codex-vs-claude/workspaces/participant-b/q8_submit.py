MOD = 10**9 + 7

# f(p^k) for p ≡ 1 mod 4: p^{k-1} * (k*(p-1) + p)
# f(5^80) = 5^79 * (80*4 + 5) = 5^79 * 325
# f(13^60) = 13^59 * (60*12 + 13) = 13^59 * 733

# f(5^80 * 13^60) = f(5^80) * f(13^60) = 5^79 * 325 * 13^59 * 733

# 325 = 13 * 25 = 13 * 5^2
# So f = 13 * 5^81 * 13^59 * 733 = 733 * 5^81 * 13^60

val = (733 * pow(5, 81, MOD) % MOD * pow(13, 60, MOD) % MOD) % MOD
print(f"f(5^80 * 13^60) mod 10^9+7 = {val}")

# Double-check
f_5_80 = pow(5, 79, MOD) * 325 % MOD
f_13_60 = pow(13, 59, MOD) * 733 % MOD
val2 = f_5_80 * f_13_60 % MOD
print(f"Cross-check: {val2}")
assert val == val2

# Also verify f(5^k) formula for k up to 5
def f_brute(n):
    count = 0
    for a in range(n):
        a2 = (a*a) % n
        for b in range(n):
            if (a2 + b*b) % n == 0:
                count += 1
    return count

for k in range(1, 6):
    n = 5**k
    bf = f_brute(n)
    fm = 5**(k-1) * (k*4 + 5)
    print(f"f(5^{k}) = {n}: brute={bf}, formula={fm}, match={bf==fm}")

for k in range(1, 4):
    n = 13**k
    bf = f_brute(n)
    fm = 13**(k-1) * (k*12 + 13)
    print(f"f(13^{k}) = {n}: brute={bf}, formula={fm}, match={bf==fm}")

