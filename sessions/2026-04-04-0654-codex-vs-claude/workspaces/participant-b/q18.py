# Let me try a question about counting the number of ways to tile a specific
# region with specific polyominoes, or something involving a less standard computation.
#
# How about: compute the resultant of two specific polynomials?
# Res(f, g) = det(Sylvester matrix)

from fractions import Fraction

def resultant(f_coeffs, g_coeffs):
    """Compute resultant of f and g using Sylvester matrix.
    f_coeffs = [a_n, a_{n-1}, ..., a_0] (highest degree first)
    g_coeffs = [b_m, b_{m-1}, ..., b_0]
    """
    n = len(f_coeffs) - 1  # degree of f
    m = len(g_coeffs) - 1  # degree of g
    size = n + m
    
    # Build Sylvester matrix
    S = [[Fraction(0)] * size for _ in range(size)]
    
    # First m rows: coefficients of f shifted
    for i in range(m):
        for j in range(n + 1):
            S[i][i + j] = Fraction(f_coeffs[j])
    
    # Next n rows: coefficients of g shifted
    for i in range(n):
        for j in range(m + 1):
            S[m + i][i + j] = Fraction(g_coeffs[j])
    
    # Compute determinant
    mat = S
    size_mat = size
    det_val = Fraction(1)
    for col in range(size_mat):
        pivot = None
        for row in range(col, size_mat):
            if mat[row][col] != 0:
                pivot = row
                break
        if pivot is None:
            return Fraction(0)
        if pivot != col:
            mat[col], mat[pivot] = mat[pivot], mat[col]
            det_val *= -1
        det_val *= mat[col][col]
        pv = mat[col][col]
        for row in range(col + 1, size_mat):
            if mat[row][col] != 0:
                factor = mat[row][col] / pv
                for j in range(col, size_mat):
                    mat[row][j] -= factor * mat[col][j]
    return det_val

# f(x) = 2x^5 - 3x^4 + x^3 - 7x^2 + 4x - 5
# g(x) = 3x^4 + 2x^3 - x^2 + 6x - 8

f = [2, -3, 1, -7, 4, -5]  # degree 5
g = [3, 2, -1, 6, -8]       # degree 4

res = resultant(f, g)
print(f"Resultant of f and g: {res}")

# Let me also verify: the resultant should be an integer since all coefficients are integers
print(f"Is integer: {res.denominator == 1}")
