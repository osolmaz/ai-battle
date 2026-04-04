# Let me try a question about counting the number of distinct ways to partition
# a set, or something involving Stirling numbers or Bell numbers with a twist.

# How about: Count the number of surjective functions from a 10-element set to a 6-element set.
# This is 6! * S(10,6) where S(10,6) is a Stirling number of the second kind.
# S(10,6) = 22827, so answer = 720 * 22827 = ... let me compute

# Actually that might be too standard. Let me try something else.

# Question: Consider a 6x6 grid graph (36 vertices). How many spanning trees does it have?
# This requires computing the determinant of a 35x35 Laplacian minor - Kirchhoff's theorem.
# This is hard to get right and the answer is a large number.

import numpy as np

def grid_spanning_trees(rows, cols):
    n = rows * cols
    # Build Laplacian matrix
    L = np.zeros((n, n), dtype=np.int64)
    
    for r in range(rows):
        for c in range(cols):
            v = r * cols + c
            # Right neighbor
            if c + 1 < cols:
                w = r * cols + (c + 1)
                L[v][v] += 1
                L[w][w] += 1
                L[v][w] -= 1
                L[w][v] -= 1
            # Down neighbor
            if r + 1 < rows:
                w = (r + 1) * cols + c
                L[v][v] += 1
                L[w][w] += 1
                L[v][w] -= 1
                L[w][v] -= 1
    
    # Remove last row and column
    L_reduced = L[:-1, :-1]
    
    # Compute determinant - need exact arithmetic
    # Use fraction-free approach or sympy... but sympy not available
    # Let me use Python's built-in for exact integer arithmetic
    
    # Gaussian elimination with fractions
    from fractions import Fraction
    
    m = n - 1
    M = [[Fraction(L_reduced[i][j]) for j in range(m)] for i in range(m)]
    
    det = Fraction(1)
    for col in range(m):
        # Find pivot
        pivot = None
        for row in range(col, m):
            if M[row][col] != 0:
                pivot = row
                break
        if pivot is None:
            return 0
        if pivot != col:
            M[col], M[pivot] = M[pivot], M[col]
            det *= -1
        
        det *= M[col][col]
        pivot_val = M[col][col]
        
        for row in range(col + 1, m):
            if M[row][col] != 0:
                factor = M[row][col] / pivot_val
                for j in range(col, m):
                    M[row][j] -= factor * M[col][j]
    
    return int(det)

# Known: 2x2 grid has 4 spanning trees
print(f"2x2: {grid_spanning_trees(2, 2)}")
# Known: 3x3 grid has 192 spanning trees  
print(f"3x3: {grid_spanning_trees(3, 3)}")
# Known: 4x4 grid has 100352 spanning trees
print(f"4x4: {grid_spanning_trees(4, 4)}")

# Now compute 5x5
print(f"5x5: {grid_spanning_trees(5, 5)}")

# And 6x6
print(f"6x6: {grid_spanning_trees(6, 6)}")
