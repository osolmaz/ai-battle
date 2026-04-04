# Count L-tromino tilings of a 7x9 grid with 6 cells removed.
# L-tromino: 2x2 square with one corner removed. 4 orientations.

rows = 7
cols = 9
removed = {(0,0), (3,0), (3,4), (5,8), (6,5), (6,8)}  # 0-indexed

# Board as set of cells
cells = set()
for r in range(rows):
    for c in range(cols):
        if (r,c) not in removed:
            cells.add((r,c))

print(f"Total cells: {len(cells)}")  # should be 57

# L-tromino shapes (relative to top-left of 2x2 bounding box)
# 4 orientations, each missing one corner of the 2x2 square
L_shapes = [
    [(0,0), (1,0), (1,1)],  # missing (0,1) - L shape
    [(0,0), (0,1), (1,0)],  # missing (1,1)
    [(0,0), (0,1), (1,1)],  # missing (1,0)
    [(0,1), (1,0), (1,1)],  # missing (0,0)
]

# For each cell, precompute which L-trominoes can cover it
# We'll use backtracking: find first uncovered cell, try all placements covering it

# Convert cells to sorted list for ordering
cell_list = sorted(cells)
cell_set = set(cells)

# For efficiency, represent board as a set of remaining cells
# and use the first (top-left) uncovered cell approach

def solve():
    # Find first uncovered cell (smallest in row-major order)
    board = set(cell_set)  # copy
    
    def backtrack():
        if not board:
            return 1
        
        # Find first uncovered cell
        target = min(board)  # This is slow; let's optimize
        
        r, c = target
        count = 0
        
        # Try all L-tromino placements that cover (r, c)
        # For each L-shape, try all positions where (r,c) could be one of the 3 cells
        for shape in L_shapes:
            for idx in range(3):
                # Place so that shape[idx] maps to (r, c)
                dr, dc = shape[idx]
                base_r, base_c = r - dr, c - dc
                # Compute all 3 cells of this placement
                placement = [(base_r + sr, base_c + sc) for sr, sc in shape]
                # Check all cells are on the board
                if all(p in board for p in placement):
                    # Place
                    for p in placement:
                        board.remove(p)
                    count += backtrack()
                    for p in placement:
                        board.add(p)
        
        return count
    
    return backtrack()

# Optimization: use a grid + find first cell via scanning
# Let me rewrite with better data structures

def solve_fast():
    grid = [[False]*cols for _ in range(rows)]
    for r, c in cell_set:
        grid[r][c] = True
    
    remaining = len(cell_set)
    
    def find_first():
        for r in range(rows):
            for c in range(cols):
                if grid[r][c]:
                    return (r, c)
        return None
    
    def backtrack(remaining):
        if remaining == 0:
            return 1
        
        target = find_first()
        if target is None:
            return 1
        
        r, c = target
        count = 0
        
        for shape in L_shapes:
            for idx in range(3):
                dr, dc = shape[idx]
                base_r, base_c = r - dr, c - dc
                placement = [(base_r + sr, base_c + sc) for sr, sc in shape]
                if all(0 <= pr < rows and 0 <= pc < cols and grid[pr][pc] for pr, pc in placement):
                    for pr, pc in placement:
                        grid[pr][pc] = False
                    count += backtrack(remaining - 3)
                    for pr, pc in placement:
                        grid[pr][pc] = True
        
        return count
    
    return backtrack(remaining)

result = solve_fast()
print(f"L-tromino tilings: {result}")
