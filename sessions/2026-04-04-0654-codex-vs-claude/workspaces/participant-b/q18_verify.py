# Verify resultant using the product formula:
# Res(f, g) = a_n^m * b_m^n * prod_{f(alpha)=0, g(beta)=0} (alpha - beta)
# But this needs roots. Let me verify differently.
#
# Res(f, g) = (-1)^(nm) * Res(g, f)
# Or: Res(f, g) = a_n^m * prod_{f(alpha)=0} g(alpha)
# 
# Let me just verify by computing the Sylvester matrix determinant differently.
# I'll use integer row reduction (bareiss algorithm).

def resultant_bareiss(f_coeffs, g_coeffs):
    n = len(f_coeffs) - 1
    m = len(g_coeffs) - 1
    size = n + m
    
    S = [[0] * size for _ in range(size)]
    for i in range(m):
        for j in range(n + 1):
            S[i][i + j] = f_coeffs[j]
    for i in range(n):
        for j in range(m + 1):
            S[m + i][i + j] = g_coeffs[j]
    
    # Bareiss algorithm for exact integer determinant
    mat = [row[:] for row in S]
    sign = 1
    prev_pivot = 1
    
    for col in range(size):
        # Find pivot
        pivot_row = None
        for row in range(col, size):
            if mat[row][col] != 0:
                pivot_row = row
                break
        if pivot_row is None:
            return 0
        if pivot_row != col:
            mat[col], mat[pivot_row] = mat[pivot_row], mat[col]
            sign *= -1
        
        for row in range(col + 1, size):
            for j in range(size - 1, col - 1, -1):
                mat[row][j] = (mat[col][col] * mat[row][j] - mat[row][col] * mat[col][j]) // prev_pivot
        
        prev_pivot = mat[col][col]
    
    return sign * mat[size-1][size-1]

f = [2, -3, 1, -7, 4, -5]
g = [3, 2, -1, 6, -8]

res = resultant_bareiss(f, g)
print(f"Resultant (Bareiss): {res}")
