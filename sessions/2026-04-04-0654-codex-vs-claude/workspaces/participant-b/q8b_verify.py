from math import comb

# Verify by DP on grid
# dp[x][y] = number of paths from (0,0) to (x,y) avoiding forbidden points

forbidden = {(3,3), (6,6), (9,9), (4,8), (8,4)}

dp = [[0]*13 for _ in range(13)]
dp[0][0] = 1

for x in range(13):
    for y in range(13):
        if (x, y) in forbidden:
            dp[x][y] = 0
            continue
        if x == 0 and y == 0:
            continue
        val = 0
        if x > 0:
            val += dp[x-1][y]
        if y > 0:
            val += dp[x][y-1]
        dp[x][y] = val

print(f"DP verification: {dp[12][12]}")
