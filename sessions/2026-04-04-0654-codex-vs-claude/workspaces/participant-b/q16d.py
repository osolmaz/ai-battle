# Let me ask a graph coloring question on a specific moderately complex graph.
# Count the number of proper 3-colorings of a specific graph.
# If the graph has chromatic number 3, this is interesting.

# Build a graph that's 3-colorable but has a non-trivial count.
# How about: the 4-dimensional hypercube graph Q_4?
# Q_4 has 16 vertices and 32 edges. It's bipartite so chi=2.
# Not great for 3-colorings (trivially many).

# Let me try: count the number of proper 4-colorings of a specific planar graph.

# Actually, let me try a more creative question:
# Count the number of ways to fill a 4x4 grid with integers 1-4 such that:
# - Each row is a permutation of {1,2,3,4}
# - Each column is a permutation of {1,2,3,4}  
# - The two main diagonals each contain all 4 distinct values
# This is counting "diagonal Latin squares" of order 4.

from itertools import permutations

def check_diagonal_latin(grid):
    n = 4
    # Check rows
    for r in range(n):
        if len(set(grid[r])) != n:
            return False
    # Check columns
    for c in range(n):
        col = [grid[r][c] for r in range(n)]
        if len(set(col)) != n:
            return False
    # Check main diagonal
    diag1 = [grid[i][i] for i in range(n)]
    if len(set(diag1)) != n:
        return False
    # Check anti-diagonal
    diag2 = [grid[i][n-1-i] for i in range(n)]
    if len(set(diag2)) != n:
        return False
    return True

count = 0
perms = list(permutations([1,2,3,4]))
for r1 in perms:
    for r2 in perms:
        for r3 in perms:
            for r4 in perms:
                grid = [r1, r2, r3, r4]
                if check_diagonal_latin(grid):
                    count += 1

print(f"Diagonal Latin squares of order 4: {count}")

# Now try order 5 (this might be slow)
# Actually order 5 has 5!^4 = 24883200000 combinations... way too slow.

# Let me try order 4 but with an additional constraint.
# Count diagonal Latin squares of order 4 where the top-left 2x2 subgrid 
# contains {1,2,3,4}... nah.

# Let me try: how many "doubly diagonal" Latin squares of order 5 exist?
# Need smarter enumeration.

# For order 5, use constraint propagation
def count_diagonal_latin_5():
    n = 5
    vals = set(range(1, n+1))
    count = 0
    
    grid = [[0]*n for _ in range(n)]
    col_used = [set() for _ in range(n)]
    diag1_used = set()  # grid[i][i]
    diag2_used = set()  # grid[i][n-1-i]
    
    def solve(pos):
        nonlocal count
        r, c = divmod(pos, n)
        if r == n:
            count += 1
            return
        
        for v in range(1, n+1):
            # Check row
            if v in grid[r][:c]:
                continue
            # Check column
            if v in col_used[c]:
                continue
            # Check diagonals
            if r == c and v in diag1_used:
                continue
            if r + c == n - 1 and v in diag2_used:
                continue
            
            grid[r][c] = v
            col_used[c].add(v)
            if r == c:
                diag1_used.add(v)
            if r + c == n - 1:
                diag2_used.add(v)
            
            solve(pos + 1)
            
            grid[r][c] = 0
            col_used[c].remove(v)
            if r == c:
                diag1_used.remove(v)
            if r + c == n - 1:
                diag2_used.remove(v)
    
    solve(0)
    return count

print(f"Diagonal Latin squares of order 5: {count_diagonal_latin_5()}")
