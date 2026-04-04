# Let me try a question about counting the number of distinct ways to 
# partition a specific multiset, or something involving generating functions.
#
# How about: What is the number of integer solutions to
# x1 + x2 + x3 + x4 + x5 = 30
# where 1 <= x1 <= 10, 2 <= x2 <= 8, 3 <= x3 <= 12, 0 <= x4 <= 9, 4 <= x5 <= 15?
#
# This is a constrained integer composition problem.

# Brute force
count = 0
for x1 in range(1, 11):
    for x2 in range(2, 9):
        for x3 in range(3, 13):
            for x4 in range(0, 10):
                x5 = 30 - x1 - x2 - x3 - x4
                if 4 <= x5 <= 15:
                    count += 1

print(f"Number of solutions: {count}")

# Also verify with generating functions approach (polynomial multiplication)
# f(x) = x^1 + x^2 + ... + x^10
# g(x) = x^2 + x^3 + ... + x^8
# h(x) = x^3 + x^4 + ... + x^12
# p(x) = x^0 + x^1 + ... + x^9
# q(x) = x^4 + x^5 + ... + x^15
# Answer = coefficient of x^30 in f*g*h*p*q

def poly_mult(a, b):
    if not a or not b:
        return []
    result = [0] * (len(a) + len(b) - 1)
    for i, ai in enumerate(a):
        for j, bj in enumerate(b):
            result[i+j] += ai * bj
    return result

# Represent polynomials as lists where index = exponent
max_exp = 30

f = [0] * 31
for i in range(1, 11): f[i] = 1

g = [0] * 31
for i in range(2, 9): g[i] = 1

h = [0] * 31
for i in range(3, 13): h[i] = 1

p = [0] * 31
for i in range(0, 10): p[i] = 1

q = [0] * 31
for i in range(4, 16): q[i] = 1

result = poly_mult(f, g)
result = poly_mult(result, h)
result = poly_mult(result, p)
result = poly_mult(result, q)

print(f"Generating function verification: {result[30]}")
