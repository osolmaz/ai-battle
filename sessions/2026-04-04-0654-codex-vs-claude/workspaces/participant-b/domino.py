# Count domino tilings of a 4x7 grid
# Use profile DP: process column by column, track which cells in the current column are already filled

from functools import lru_cache

rows = 4
cols = 7

@lru_cache(maxsize=None)
def solve(col, row, profile):
    """
    Place dominoes on a 4x7 grid.
    col: current column being processed
    row: current row in this column
    profile: bitmask of which cells in the NEXT column are already filled by horizontal dominoes
    """
    if col == cols:
        return 1 if profile == 0 else 0
    if row == rows:
        return solve(col + 1, 0, profile)
    
    # Current cell (row, col)
    # Check if this cell is already filled (by a horizontal domino from previous column)
    # We need a different approach...
    
    # Let me use a different DP formulation
    pass

# Better approach: iterate cell by cell in row-major order
# State: which cells in the "frontier" are already filled

# Actually, let me use the standard profile DP for domino tiling.
# Process column by column. The profile is a bitmask of rows in the current column
# that are already occupied by horizontal dominoes extending from the previous column.

def count_tilings(rows, cols):
    # For each column, we try to fill it given the profile (cells already filled from left).
    # We can place vertical dominoes (within this column) or horizontal dominoes (extending into next column).
    
    def fill_column(row, current_profile, next_profile):
        """
        Try to fill column from 'row' downward.
        current_profile: bitmask of which rows are already filled in this column
        next_profile: bitmask of which rows will be filled in the next column
        Returns list of possible next_profiles.
        """
        if row == rows:
            return [next_profile]
        
        if current_profile & (1 << row):
            # This row is already filled, move to next row
            return fill_column(row + 1, current_profile, next_profile)
        
        results = []
        
        # Option 1: Place horizontal domino (row, col) -> (row, col+1)
        # This fills the current cell and marks (row, col+1) as filled
        results.extend(fill_column(row + 1, current_profile, next_profile | (1 << row)))
        
        # Option 2: Place vertical domino (row, col) -> (row+1, col)
        if row + 1 < rows and not (current_profile & (1 << (row + 1))):
            results.extend(fill_column(row + 2, current_profile, next_profile))
            # Wait, we need to mark row+1 as filled too
            # Actually if we place vertical at (row, row+1), both are filled in this column
            # So we skip both rows
            # The fill_column(row+2, ...) already handles this since we skip row and row+1
            # But we called it wrong - let me redo
        
        return results
    
    # Redo with cleaner logic
    def fill(row, profile, next_profile):
        """Fill current column from row downward. profile = current col filled cells."""
        if row == rows:
            yield next_profile
            return
        
        if profile & (1 << row):
            # Already filled by horizontal from previous column
            yield from fill(row + 1, profile, next_profile)
            return
        
        # Horizontal domino into next column (if not last column... handle outside)
        yield from fill(row + 1, profile, next_profile | (1 << row))
        
        # Vertical domino (if row+1 is free)
        if row + 1 < rows and not (profile & (1 << (row + 1))):
            yield from fill(row + 2, profile, next_profile)
    
    # For the last column, we can't place horizontal dominoes
    def fill_last(row, profile):
        if row == rows:
            yield True
            return
        if profile & (1 << row):
            yield from fill_last(row + 1, profile)
            return
        # Can only place vertical
        if row + 1 < rows and not (profile & (1 << (row + 1))):
            yield from fill_last(row + 2, profile)
        # Can't place horizontal in last column, so if we can't place vertical, no solution
    
    # DP
    # dp[profile] = number of ways to fill columns 0..c-1 such that profile describes
    # which rows in column c are already filled
    dp = {0: 1}  # initially no cells filled in column 0
    
    for c in range(cols - 1):
        new_dp = {}
        for profile, ways in dp.items():
            for next_profile in fill(0, profile, 0):
                new_dp[next_profile] = new_dp.get(next_profile, 0) + ways
        dp = new_dp
    
    # Last column: must fill completely without extending
    total = 0
    for profile, ways in dp.items():
        for _ in fill_last(0, profile):
            total += ways
    
    return total

print(f"Domino tilings of 4x7: {count_tilings(4, 7)}")

# Cross-check with known values:
# 4x2: 5 (known)
print(f"Domino tilings of 4x2: {count_tilings(4, 2)}")
# 4x4: 36 (known)  
print(f"Domino tilings of 4x4: {count_tilings(4, 4)}")
