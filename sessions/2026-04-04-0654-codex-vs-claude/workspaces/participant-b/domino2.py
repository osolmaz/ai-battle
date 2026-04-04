def count_tilings(rows, cols):
    # Ensure rows <= cols for efficiency (use rows as the profile dimension)
    if rows > cols:
        rows, cols = cols, rows
    
    def fill(row, profile, next_profile):
        if row == rows:
            yield next_profile
            return
        if profile & (1 << row):
            yield from fill(row + 1, profile, next_profile)
            return
        # Horizontal domino into next column
        yield from fill(row + 1, profile, next_profile | (1 << row))
        # Vertical domino
        if row + 1 < rows and not (profile & (1 << (row + 1))):
            yield from fill(row + 2, profile, next_profile)
    
    def fill_last(row, profile):
        if row == rows:
            yield True
            return
        if profile & (1 << row):
            yield from fill_last(row + 1, profile)
            return
        if row + 1 < rows and not (profile & (1 << (row + 1))):
            yield from fill_last(row + 2, profile)
    
    dp = {0: 1}
    for c in range(cols - 1):
        new_dp = {}
        for profile, ways in dp.items():
            for next_profile in fill(0, profile, 0):
                new_dp[next_profile] = new_dp.get(next_profile, 0) + ways
        dp = new_dp
    
    total = 0
    for profile, ways in dp.items():
        for _ in fill_last(0, profile):
            total += ways
    return total

print(f"Domino tilings of 5x8: {count_tilings(5, 8)}")
print(f"Domino tilings of 4x7: {count_tilings(4, 7)}")
# Known: 2x6 = 13
print(f"Domino tilings of 2x6: {count_tilings(2, 6)}")
