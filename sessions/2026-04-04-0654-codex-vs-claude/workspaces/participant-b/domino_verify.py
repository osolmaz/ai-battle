# Verify with a different approach: exact cover / backtracking

rows = 8
cols = 8
removed = {(0,6), (1,4), (1,6), (3,1), (5,4), (5,5), (7,3), (7,4)}  # 0-indexed

cells = []
cell_idx = {}
for r in range(rows):
    for c in range(cols):
        if (r, c) not in removed:
            cell_idx[(r, c)] = len(cells)
            cells.append((r, c))

n = len(cells)  # should be 56

# Generate all possible dominoes
dominoes = []
for i, (r, c) in enumerate(cells):
    # Horizontal
    if (r, c+1) in cell_idx:
        dominoes.append((i, cell_idx[(r, c+1)]))
    # Vertical
    if (r+1, c) in cell_idx:
        dominoes.append((i, cell_idx[(r+1, c)]))

# Backtracking: find first uncovered cell, try all dominoes covering it
def count_tilings():
    covered = [False] * n
    
    def solve():
        # Find first uncovered cell
        first = -1
        for i in range(n):
            if not covered[i]:
                first = i
                break
        if first == -1:
            return 1  # All covered
        
        total = 0
        r, c = cells[first]
        # Try horizontal domino
        if (r, c+1) in cell_idx:
            j = cell_idx[(r, c+1)]
            if not covered[j]:
                covered[first] = True
                covered[j] = True
                total += solve()
                covered[first] = False
                covered[j] = False
        # Try vertical domino
        if (r+1, c) in cell_idx:
            j = cell_idx[(r+1, c)]
            if not covered[j]:
                covered[first] = True
                covered[j] = True
                total += solve()
                covered[first] = False
                covered[j] = False
        return total
    
    return solve()

result = count_tilings()
print(f"Verification: {result}")
