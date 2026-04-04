# Verify n=14, d=3 with a different DP formulation
# Use permanent of the 0-1 biadjacency matrix via Ryser's formula

def permanent_ryser(matrix):
    n = len(matrix)
    # Ryser's formula: perm(A) = (-1)^n * sum_{S subset of [n]} (-1)^|S| * prod_{i=1}^{n} sum_{j in S} a_{ij}
    total = 0
    for mask in range(1, 1 << n):
        # S = set of columns in mask
        bits = bin(mask).count('1')
        prod = 1
        for i in range(n):
            s = 0
            for j in range(n):
                if mask & (1 << j):
                    s += matrix[i][j]
            prod *= s
        if (n - bits) % 2 == 0:
            total += prod
        else:
            total -= prod
    
    if n % 2 == 1:
        total = -total
    return total

# Build biadjacency matrix for n=14, d=3
n = 14
d = 3
matrix = [[0]*n for _ in range(n)]
for i in range(n):
    for j in range(n):
        if abs(i - j) <= d:
            matrix[i][j] = 1

# Ryser's formula for n=14 requires 2^14 = 16384 subsets - very fast
result = permanent_ryser(matrix)
print(f"Permanent (Ryser) for n={n}, d={d}: {result}")
