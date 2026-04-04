# Let me try a question involving counting something in a specific algebraic structure,
# or a number theory computation that's tricky.
#
# How about: What is the number of solutions to x^2 + y^2 + z^2 = 2025 
# in non-negative integers (x, y, z)?
# Note: 2025 = 45^2. Order matters (x,y,z are ordered).

n = 2025
count = 0
import math

for x in range(int(math.isqrt(n)) + 1):
    for y in range(int(math.isqrt(n - x*x)) + 1):
        rem = n - x*x - y*y
        if rem >= 0:
            z = int(math.isqrt(rem))
            if z * z == rem:
                count += 1

print(f"Solutions to x^2+y^2+z^2=2025 in non-negative integers: {count}")

# Let me also try: how many representations as sum of 4 squares?
# That might be too large.

# Actually, let me try a different question: compute the Möbius function sum
# M(n) = sum_{k=1}^{n} mu(k) for a specific n.

def compute_mertens(N):
    """Compute M(N) = sum_{k=1}^{N} mu(k)"""
    # Sieve mu
    mu = [0] * (N + 1)
    mu[1] = 1
    is_prime = [True] * (N + 1)
    primes = []
    
    for i in range(2, N + 1):
        if is_prime[i]:
            primes.append(i)
            mu[i] = -1
        for p in primes:
            if i * p > N:
                break
            is_prime[i * p] = False
            if i % p == 0:
                mu[i * p] = 0
                break
            else:
                mu[i * p] = -mu[i]
    
    return sum(mu[1:N+1])

# Mertens function at specific values
for N in [1000, 5000, 10000, 50000]:
    print(f"M({N}) = {compute_mertens(N)}")

# M(10000) is a well-known value. Let me try M(100000).
print(f"M(100000) = {compute_mertens(100000)}")
