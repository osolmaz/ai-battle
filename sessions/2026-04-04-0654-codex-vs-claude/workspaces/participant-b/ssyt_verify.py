# Verify with a small case first, then re-derive
# For shape (2,1) with entries in {1,2,3}:
# SSYT: 
# 1 1 / 2, 1 1 / 3, 1 2 / 2, 1 2 / 3, 1 3 / 2, 1 3 / 3, 2 2 / 3, 2 3 / 3
# Wait let me enumerate: rows weakly increasing, columns strictly increasing
# Row 1: a b with a<=b, Row 2: c with c > a (strict column increase)
# (1,1,2), (1,1,3), (1,2,2), (1,2,3), (1,3,2)? No: b>=a in row 1, c>a in col 1
# Wait: shape (2,1) means row 1 has 2 cells, row 2 has 1 cell.
# Cell (0,0)=a, (0,1)=b, (1,0)=c
# Constraints: a<=b (row 1), a<c (column 0 strict increase)
# Entries in {1,2,3}

count_small = 0
for a in range(1,4):
    for b in range(a,4):  # a<=b
        for c in range(a+1,4):  # c>a
            count_small += 1
print(f"SSYT of shape (2,1) with entries in {{1,2,3}}: {count_small}")

# Hook-content formula:
from fractions import Fraction
shape_small = [2, 1]
k_small = 3
num = Fraction(1)
den = Fraction(1)
for i in range(len(shape_small)):
    for j in range(shape_small[i]):
        content = j - i
        arm = shape_small[i] - j - 1
        leg = sum(1 for r in range(i+1, len(shape_small)) if shape_small[r] > j)
        hook = arm + leg + 1
        num *= (k_small + content)
        den *= hook
print(f"Hook-content formula: {int(num/den)}")

# Now verify the main computation independently
shape = [13, 10, 9, 7, 4, 3, 1, 1]
k = 11

# Compute as a single large fraction
from functools import reduce
from math import gcd

num_factors = []
den_factors = []

for i in range(len(shape)):
    for j in range(shape[i]):
        content = j - i
        arm = shape[i] - j - 1
        leg = sum(1 for r in range(i+1, len(shape)) if shape[r] > j)
        hook = arm + leg + 1
        num_factors.append(k + content)
        den_factors.append(hook)

# Multiply all numerator factors and denominator factors
num_prod = 1
for f in num_factors:
    num_prod *= f
den_prod = 1
for f in den_factors:
    den_prod *= f

print(f"Numerator product: {num_prod}")
print(f"Denominator product: {den_prod}")
print(f"Result: {num_prod // den_prod}")
print(f"Exact division: {num_prod % den_prod == 0}")
