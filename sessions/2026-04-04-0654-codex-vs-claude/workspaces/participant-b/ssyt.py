# Count SSYT of shape (13,10,9,7,4,3,1,1) with entries in {1,...,11}
# Using the hook-content formula:
# s_λ(1,1,...,1) = prod_{(i,j) in λ} (k + c(i,j)) / h(i,j)
# where c(i,j) = j - i (content) and h(i,j) = hook length
# k = 11

from fractions import Fraction

shape = [13, 10, 9, 7, 4, 3, 1, 1]
k = 11
nrows = len(shape)

# Compute hook lengths and content for each cell
# Cell (i, j) is 0-indexed: row i, column j
# hook(i,j) = arm + leg + 1
# arm = shape[i] - j - 1
# leg = number of rows r > i with shape[r] > j
# content(i,j) = j - i

numerator = Fraction(1)
denominator = Fraction(1)

for i in range(nrows):
    for j in range(shape[i]):
        # Content
        content = j - i
        
        # Hook length
        arm = shape[i] - j - 1
        leg = sum(1 for r in range(i + 1, nrows) if shape[r] > j)
        hook = arm + leg + 1
        
        numerator *= (k + content)
        denominator *= hook

result = numerator / denominator
print(f"SSYT count: {result}")
print(f"Is integer: {result.denominator == 1}")
print(f"Integer value: {int(result)}")
