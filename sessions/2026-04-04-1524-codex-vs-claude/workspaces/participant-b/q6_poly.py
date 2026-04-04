# Compute x^100 mod (x^5 - x - 1) over Z[x]
# Then find the coefficients and their sum

def poly_mod(a, mod):
    """Reduce polynomial a modulo mod. Polynomials are lists [a0, a1, ..., an] representing a0 + a1*x + ... + an*x^n"""
    a = list(a)
    while len(a) >= len(mod):
        if a[-1] != 0:
            coeff = a[-1]  # leading coefficient of a divided by leading of mod
            # Since mod is monic (leading coeff 1), this is just a[-1]
            shift = len(a) - len(mod)
            for i in range(len(mod)):
                a[shift + i] -= coeff * mod[i]
        a.pop()
    # Remove trailing zeros
    while len(a) > 1 and a[-1] == 0:
        a.pop()
    return a

def poly_mul(a, b):
    """Multiply two polynomials"""
    result = [0] * (len(a) + len(b) - 1)
    for i in range(len(a)):
        for j in range(len(b)):
            result[i + j] += a[i] * b[j]
    return result

def poly_mul_mod(a, b, mod):
    """Multiply a and b, then reduce mod"""
    return poly_mod(poly_mul(a, b), mod)

def poly_pow_mod(base, exp, mod):
    """Compute base^exp mod mod using repeated squaring"""
    result = [1]  # polynomial "1"
    base = poly_mod(base, mod)
    while exp > 0:
        if exp % 2 == 1:
            result = poly_mul_mod(result, base, mod)
        base = poly_mul_mod(base, base, mod)
        exp //= 2
    return result

# p(x) = x^5 - x - 1, represented as [-1, -1, 0, 0, 0, 1]
mod = [-1, -1, 0, 0, 0, 1]

# x represented as [0, 1]
x = [0, 1]

# Compute x^100 mod p(x)
result = poly_pow_mod(x, 100, mod)

# Pad to length 5
while len(result) < 5:
    result.append(0)

print(f"x^100 mod (x^5 - x - 1) = {result[0]} + {result[1]}*x + {result[2]}*x^2 + {result[3]}*x^3 + {result[4]}*x^4")
print(f"Coefficients: a={result[0]}, b={result[1]}, c={result[2]}, d={result[3]}, e={result[4]}")
print(f"Sum a+b+c+d+e = {sum(result[:5])}")

# Verify by checking in floating point with actual root
import cmath
# Find roots of x^5 - x - 1
# Use Newton's method for real root
x0 = 1.2
for _ in range(100):
    fx = x0**5 - x0 - 1
    fpx = 5*x0**4 - 1
    x0 -= fx / fpx

alpha = x0
print(f"\nReal root alpha ≈ {alpha}")
print(f"alpha^5 - alpha - 1 = {alpha**5 - alpha - 1}")
print(f"alpha^100 ≈ {alpha**100}")
reconstructed = result[0] + result[1]*alpha + result[2]*alpha**2 + result[3]*alpha**3 + result[4]*alpha**4
print(f"Reconstructed = {reconstructed}")
print(f"Match: {abs(alpha**100 - reconstructed) < 1e-5}")

