from fractions import Fraction
from math import comb
from collections import Counter

def hamming_weight(n):
    return bin(n).count('1')

# Verify eigenvalue formula for small n using direct Laplacian computation
def verify_small(n_bits):
    N = 1 << n_bits
    # Build adjacency
    adj = [[0]*N for _ in range(N)]
    for i in range(N):
        for j in range(i+1, N):
            hw = hamming_weight(i ^ j)
            if hw in (1, 2):
                adj[i][j] = 1
                adj[j][i] = 1
    
    # Build Laplacian
    L = [[Fraction(0)]*N for _ in range(N)]
    for i in range(N):
        deg = sum(adj[i])
        L[i][i] = Fraction(deg)
        for j in range(N):
            if adj[i][j]:
                L[i][j] = Fraction(-1)
    
    # Compute det of (N-1)x(N-1) minor
    minor = [[L[i][j] for j in range(N-1)] for i in range(N-1)]
    
    def det_fraction(matrix):
        n = len(matrix)
        M = [[Fraction(matrix[i][j]) for j in range(n)] for i in range(n)]
        sign = 1
        for col in range(n):
            pivot = None
            for row in range(col, n):
                if M[row][col] != 0:
                    pivot = row
                    break
            if pivot is None:
                return Fraction(0)
            if pivot != col:
                M[col], M[pivot] = M[pivot], M[col]
                sign *= -1
            for row in range(col+1, n):
                if M[row][col] != 0:
                    factor = M[row][col] / M[col][col]
                    for k in range(col, n):
                        M[row][k] -= factor * M[col][k]
        result = Fraction(sign)
        for i in range(n):
            result *= M[i][i]
        return result
    
    direct = det_fraction(minor)
    
    # Now compute via eigenvalue formula
    product = Fraction(1)
    for w in range(n_bits + 1):
        t = n_bits - 2 * w
        mu = Fraction(t * t + 2 * t - n_bits, 2)
        lam = Fraction(comb(n_bits, 1) + comb(n_bits, 2)) - mu  # degree - mu
        mult = comb(n_bits, w)
        if w == 0:
            assert lam == 0  # zero eigenvalue
            continue
        product *= lam ** mult
    
    formula = product / N
    
    print(f"n_bits={n_bits}: direct={direct}, formula={formula}, match={direct==formula}")
    return direct == formula

# Test for small cases
for nb in range(2, 6):
    verify_small(nb)

