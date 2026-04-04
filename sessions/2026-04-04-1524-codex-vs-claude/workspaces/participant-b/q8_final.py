# Q: f(n) = |{(a,b) in (Z/nZ)^2 : a^2 + b^2 = 0 mod n}|. What is f(2025)?
# 2025 = 3^4 * 5^2

# Verify with brute force for small values
def f_brute(n):
    count = 0
    for a in range(n):
        for b in range(n):
            if (a*a + b*b) % n == 0:
                count += 1
    return count

# Test
for n in [1,2,3,4,5,9,25,27,45,81]:
    print(f"f({n}) = {f_brute(n)}")

# Now for n=2025
print(f"\nf(2025) = {f_brute(2025)}")

# Verify multiplicativity: f(2025) should equal f(81) * f(25)
print(f"f(81) * f(25) = {f_brute(81) * f_brute(25)}")

