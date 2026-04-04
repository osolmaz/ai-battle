# 8x8 grid with 8 squares removed. 64-8=56 cells remain, so 28 dominoes needed.
# Removed: (1,7), (2,5), (2,7), (4,2), (6,5), (6,6), (8,4), (8,5)
# Using (row, col) 1-indexed.

# Profile DP approach: process column by column (or row by row)
# Actually, let me use a general domino tiling counter for arbitrary boards.

# Represent the board as a grid, process cell by cell in row-major order.
# State: bitmask of which cells in the "frontier" are already covered.

# Better approach: use the standard profile DP scanning row by row.

rows = 8
cols = 8
removed = {(1,7), (2,5), (2,7), (4,2), (6,5), (6,6), (8,4), (8,5)}

# Convert to 0-indexed
removed_0 = {(r-1, c-1) for r, c in removed}

# Board: board[r][c] = True if cell exists
board = [[True]*cols for _ in range(rows)]
for r, c in removed_0:
    board[r][c] = False

# Profile DP: scan cells in row-major order.
# For each cell, we decide how to cover it (or skip if removed/already covered).
# The "profile" tracks which upcoming cells are already covered by a domino placed earlier.
# 
# We process cells left-to-right, top-to-bottom.
# At each cell, the relevant "future" cells that might be pre-covered are:
# - the cell to the right (horizontal domino)
# - the cell below (vertical domino)
#
# State: set of cells that are pre-covered. But this is exponential.
#
# Better: use column profile DP.
# Process column by column. The profile is a bitmask of rows in the current column
# that are already covered by horizontal dominoes from the previous column.

# Actually for a board with holes, let me just do a recursive backtracking approach
# with memoization on which cells remain uncovered, using bitmask.

# 56 cells is too many for a full bitmask. Let me use profile DP properly.

# Profile DP: process cells in row-major order.
# At each step, we need to know which of the next `cols` cells are pre-filled.
# The profile is a bitmask of length `cols` representing the current row's remaining cells.

# Let me think more carefully. Standard approach for domino tiling with holes:
# Process row by row. Profile = bitmask of which cells in the current row are
# already filled by vertical dominoes from the previous row.

def count_tilings():
    # For each row, given which cells are pre-filled from above (profile_in),
    # fill the row using horizontal and vertical dominoes.
    # Vertical dominoes extend into the next row.
    # profile_in: bitmask, bit j set means cell (row, j) is already filled from above
    # profile_out: bitmask, bit j set means cell (row+1, j) will be filled from this row
    
    def fill_row(row, col, profile_in, profile_out):
        """Generator yielding all possible profile_out values."""
        if col == cols:
            yield profile_out
            return
        
        cell_exists = board[row][col]
        cell_filled = (profile_in >> col) & 1
        
        if not cell_exists or cell_filled:
            # Cell doesn't exist or is already filled - skip
            yield from fill_row(row, col + 1, profile_in, profile_out)
            return
        
        # Cell exists and is not filled. We must cover it.
        
        # Option 1: Vertical domino (extends to row below)
        if row + 1 < rows and board[row + 1][col]:
            yield from fill_row(row, col + 1, profile_in, profile_out | (1 << col))
        
        # Option 2: Horizontal domino (extends to the right)
        if col + 1 < cols and board[row][col + 1] and not ((profile_in >> (col + 1)) & 1):
            yield from fill_row(row, col + 2, profile_in, profile_out)
        
        # Option 3: Leave uncovered? No - every cell must be covered.
        # But wait, we can't leave it uncovered. If neither option works, this branch fails.
    
    # DP over rows
    # dp[profile] = number of ways
    dp = {0: 1}  # Initially, no cells in row 0 are pre-filled
    
    for row in range(rows):
        new_dp = {}
        for profile_in, ways in dp.items():
            for profile_out in fill_row(row, 0, profile_in, 0):
                new_dp[profile_out] = new_dp.get(profile_out, 0) + ways
        dp = new_dp
    
    # After processing all rows, profile_out should be 0 (no cells extend beyond last row)
    return dp.get(0, 0)

result = count_tilings()
print(f"Number of domino tilings: {result}")
