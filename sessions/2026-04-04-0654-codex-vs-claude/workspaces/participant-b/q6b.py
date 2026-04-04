from fractions import Fraction

def grid_spanning_trees(rows, cols):
    n = rows * cols
    L = [[0]*n for _ in range(n)]
    
    for r in range(rows):
        for c in range(cols):
            v = r * cols + c
            if c + 1 < cols:
                w = r * cols + (c + 1)
                L[v][v] += 1; L[w][w] += 1; L[v][w] -= 1; L[w][v] -= 1
            if r + 1 < rows:
                w = (r + 1) * cols + c
                L[v][v] += 1; L[w][w] += 1; L[v][w] -= 1; L[w][v] -= 1
    
    m = n - 1
    M = [[Fraction(L[i][j]) for j in range(m)] for i in range(m)]
    
    det = Fraction(1)
    for col in range(m):
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

print(f"2x2: {grid_spanning_trees(2, 2)}")
print(f"3x3: {grid_spanning_trees(3, 3)}")
print(f"4x4: {grid_spanning_trees(4, 4)}")
print(f"5x5: {grid_spanning_trees(5, 5)}")

print(f"4x6: {grid_spanning_trees(4, 6)}")
print(f"3x7: {grid_spanning_trees(3, 7)}")
