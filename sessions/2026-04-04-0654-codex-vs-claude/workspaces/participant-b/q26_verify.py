# Verify 5x6x7 box with brute force for smaller case, and re-derive the formula

from fractions import Fraction

# Double-check MacMahon formula for 2x2x2 by enumeration
# A plane partition fitting in a 2x2 box with entries at most 2:
# pi[1][1] >= pi[1][2], pi[1][1] >= pi[2][1], etc.
# 0 <= pi[i][j] <= 2, weakly decreasing along rows and columns

count = 0
for a in range(3):
    for b in range(min(a,2)+1):  # b <= a
        for c in range(min(a,2)+1):  # c <= a
            for d in range(min(b,c,2)+1):  # d <= b, d <= c
                count += 1

print(f"Brute force 2x2 box, parts ≤ 2: {count}")

# Now verify the main answer using an alternative computation
# MacMahon box formula: prod_{i=0}^{a-1} prod_{j=0}^{b-1} (i+j+c+1)!/((i+j+1)!) * ... 
# Actually let me just recompute with a slightly different indexing

def macmahon_box_v2(a, b, c):
    """Alternative form: prod_{1<=i<=a, 1<=j<=b} (c + i + j - 1) / (i + j - 1)"""
    # Wait, that's for something else. Let me use the standard formula.
    # prod_{i=1}^{a} prod_{j=1}^{b} prod_{k=1}^{c} (i+j+k-1)/(i+j+k-2)
    result = Fraction(1)
    for i in range(1, a+1):
        for j in range(1, b+1):
            for k in range(1, c+1):
                result *= Fraction(i + j + k - 1, i + j + k - 2)
    return int(result)

print(f"5x6x7 recomputed: {macmahon_box_v2(5, 6, 7)}")

# Also try yet another form: prod_{1<=i<=a, 1<=j<=b} C(c + i + j - 2, i + j - 1) ... 
# no that's not standard. Let me just verify by permuting dimensions.
# MacMahon's formula should be symmetric in a, b, c
print(f"6x5x7: {macmahon_box_v2(6, 5, 7)}")
print(f"7x5x6: {macmahon_box_v2(7, 5, 6)}")
print(f"7x6x5: {macmahon_box_v2(7, 6, 5)}")
