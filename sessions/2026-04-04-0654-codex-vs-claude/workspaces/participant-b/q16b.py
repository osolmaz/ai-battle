# Count: how many integer-sided triangles have perimeter exactly 100?
# Triangle inequality: a + b > c, a + c > b, b + c > a
# where a, b, c >= 1 and a + b + c = 100
# Count unordered triples (a <= b <= c).

count = 0
for a in range(1, 34):  # a <= 100/3
    for b in range(a, (100 - a) // 2 + 1):  # b >= a, b <= c means b <= (100-a)/2
        c = 100 - a - b
        if c >= b and a + b > c:  # triangle inequality (others auto-satisfied since a<=b<=c means a+c>b and b+c>a)
            count += 1

print(f"Integer-sided triangles with perimeter 100: {count}")

# Known formula: if n is even, p(n) = round(n^2/12)
# p(100) = round(10000/12) = round(833.33) = 833
print(f"Formula check: {round(100*100/12)}")

# Actually the exact formula for even n: n^2/12 if n ≡ 0 (mod 12)
# For n=100: 100 ≡ 4 (mod 12). 
# The exact count for even n is: round(n^2/12) = different based on mod 12
# Let me just trust the computation.

# This is too well-known. Let me try something harder.

# Question: What is the number of ways to express 50 as an ordered sum of 
# positive odd integers? (I.e., compositions of 50 into odd parts.)

# A composition of n into odd parts: use generating function
# Each part is 1, 3, 5, 7, ...
# GF for one part: x + x^3 + x^5 + ... = x/(1-x^2)
# GF for compositions: 1/(1 - x/(1-x^2)) = (1-x^2)/(1-x^2-x) = (1-x^2)/(1-x-x^2)

# Wait, that's compositions (ordered sums). Let me use DP.

def compositions_odd_parts(n):
    # dp[i] = number of compositions of i into positive odd parts
    dp = [0] * (n + 1)
    dp[0] = 1
    for i in range(1, n + 1):
        for odd in range(1, i + 1, 2):
            dp[i] += dp[i - odd]
    return dp[n]

result = compositions_odd_parts(50)
print(f"Compositions of 50 into odd parts: {result}")

# The GF is 1/(1 - (x + x^3 + x^5 + ...)) = 1/(1 - x/(1-x^2))
# = (1-x^2)/(1-x^2-x)
# Denominator: 1-x-x^2 (Fibonacci-related!)
# So dp[n] = dp[n-1] + dp[n-2] with dp[0]=1, dp[1]=1
# That means compositions into odd parts follow Fibonacci!
# F(n+1) where F is the standard Fibonacci sequence.

# Let's verify: dp[0]=1, dp[1]=1, dp[2]=dp[1]+dp[0]=2, dp[3]=dp[2]+dp[1]=3
# Compositions of 2: just "1+1" = 1 way? No wait: 
# Compositions of 2 into odd parts: 1+1 = 1 way. But dp says 2?
# Hmm, let me recheck. dp[2] = dp[2-1] = dp[1] = 1 (only odd=1 works)
# Oh wait, my recurrence dp[i] += dp[i-odd] for odd=1,3,5,...
# dp[2] = dp[2-1] = dp[1] = 1. OK so it is 1. The Fibonacci claim is wrong.
# Actually the GF simplification: 
# sum_{odd>=1} x^odd = x + x^3 + x^5 + ... = x(1+x^2+x^4+...) = x/(1-x^2)
# GF = 1/(1-x/(1-x^2)) = (1-x^2)/(1-x^2-x)
# 1-x^2-x = -(x^2+x-1), roots at x = (-1±√5)/2
# So the coefficients satisfy c[n] = c[n-1] + c[n-2] with appropriate initial conditions.
# But the GF is (1-x^2)/(1-x-x^2), not 1/(1-x-x^2).
# Let p[n] be the coefficient of x^n in GF.
# (1-x-x^2) * P(x) = 1-x^2
# p[n] - p[n-1] - p[n-2] = [n=0] - [n=2]
# p[0] = 1 (from constant term)
# p[1] - p[0] = 0 => p[1] = 1
# p[2] - p[1] - p[0] = -1 => p[2] = 1+1-1 = 1
# p[n] = p[n-1] + p[n-2] for n >= 3
# So: 1, 1, 1, 2, 3, 5, 8, 13, 21, 34, ...
# This is Fibonacci shifted!
# p[n] = F(n-1) for n >= 1 where F(1)=F(2)=1.
# p[50] = F(49) in standard Fibonacci.

# Let me verify
fib = [0] * 51
fib[0] = 1
fib[1] = 1
fib[2] = 1
for i in range(3, 51):
    fib[i] = fib[i-1] + fib[i-2]
print(f"Fibonacci-based: p[50] = {fib[50]}")
print(f"DP result: {result}")

# Hmm, since this follows Fibonacci, it's probably too easy to compute.
# Let me try something else.
