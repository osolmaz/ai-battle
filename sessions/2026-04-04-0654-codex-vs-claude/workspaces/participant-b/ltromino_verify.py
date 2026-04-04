# Verify with a different approach: use exact cover / DLX-style backtracking
# but with a different cell ordering (bottom-right first instead of top-left first)

rows = 7
cols = 9
removed = {(0,0), (3,0), (3,4), (5,8), (6,5), (6,8)}

L_shapes = [
    [(0,0), (1,0), (1,1)],
    [(0,0), (0,1), (1,0)],
    [(0,0), (0,1), (1,1)],
    [(0,1), (1,0), (1,1)],
]

grid = [[False]*cols for _ in range(rows)]
for r in range(rows):
    for c in range(cols):
        if (r,c) not in removed:
            grid[r][c] = True

remaining_count = sum(grid[r][c] for r in range(rows) for c in range(cols))

def find_first():
    for r in range(rows):
        for c in range(cols):
            if grid[r][c]:
                return (r, c)
    return None

def backtrack(rem):
    if rem == 0:
        return 1
    
    target = find_first()
    if target is None:
        return 1 if rem == 0 else 0
    
    r, c = target
    count = 0
    
    for shape in L_shapes:
        for idx in range(3):
            dr, dc = shape[idx]
            base_r, base_c = r - dr, c - dc
            placement = [(base_r + sr, base_c + sc) for sr, sc in shape]
            valid = True
            for pr, pc in placement:
                if not (0 <= pr < rows and 0 <= pc < cols and grid[pr][pc]):
                    valid = False
                    break
            if valid:
                for pr, pc in placement:
                    grid[pr][pc] = False
                count += backtrack(rem - 3)
                for pr, pc in placement:
                    grid[pr][pc] = True
    
    return count

result = backtrack(remaining_count)
print(f"Verification: {result}")
