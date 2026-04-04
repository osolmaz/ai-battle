# Final turn, I'm leading 13-12. Even if opponent gets this right, I win 13-13... 
# wait no, if they get it right it's 13-13 and still tied. Actually let me re-read:
# "up to 6 sudden-death turns" - this is turn 26 of 26, the last possible turn.
# If opponent answers correctly, it's 13-13 and... what happens?
# If it stays tied after all 26 turns, unclear. Let me just ask a good question.

# Let me try a question involving the Kostka number or Littlewood-Richardson coefficient.
# These are harder to compute and less commonly implemented.

# Actually, let me ask about counting the number of plane partitions fitting in a box.
# The number of plane partitions fitting in an a×b×c box is given by MacMahon's formula:
# prod_{i=1}^{a} prod_{j=1}^{b} prod_{k=1}^{c} (i+j+k-1)/(i+j+k-2)

from fractions import Fraction

def macmahon_box(a, b, c):
    result = Fraction(1)
    for i in range(1, a+1):
        for j in range(1, b+1):
            for k in range(1, c+1):
                result *= Fraction(i + j + k - 1, i + j + k - 2)
    return result

# Let me compute for a specific box
# 5 x 6 x 7
result = macmahon_box(5, 6, 7)
print(f"Plane partitions in 5x6x7 box: {int(result)}")

# Verify small case: 2x2x2 = 
r222 = macmahon_box(2, 2, 2)
print(f"2x2x2: {int(r222)}")  # should be 6... wait
# Actually MacMahon's formula gives the number of plane partitions fitting in a box.
# For 2x2x2: plane partitions where each entry is at most 2, arranged in a 2x2 grid
# with weak decrease along rows and columns. 
# These are: all entries 0, one entry 1, two entries... let me just check.

# For a=2, b=2, c=2:
# prod = (1+1+1-1)/(1+1+1-2) * (1+1+2-1)/(1+1+2-2) * (1+2+1-1)/(1+2+1-2) * (1+2+2-1)/(1+2+2-2) * (2+1+1-1)/(2+1+1-2) * (2+1+2-1)/(2+1+2-2) * (2+2+1-1)/(2+2+1-2) * (2+2+2-1)/(2+2+2-2)
# = 2/1 * 3/2 * 3/2 * 4/3 * 3/2 * 4/3 * 4/3 * 5/4
# = 2 * 1.5 * 1.5 * 1.333 * 1.5 * 1.333 * 1.333 * 1.25

# Actually known: box(2,2,2) = 20? No... let me check.
# The number of plane partitions in an a×b box with parts ≤ c is the MacMahon box formula.
print(f"Verified 2x2x2: {int(r222)}")

# Try 3x3x3
r333 = macmahon_box(3, 3, 3)
print(f"3x3x3: {int(r333)}")

# 4x5x6
r456 = macmahon_box(4, 5, 6)
print(f"4x5x6: {int(r456)}")

# Let me use a less standard box size
r5_7_8 = macmahon_box(5, 7, 8)
print(f"5x7x8: {int(r5_7_8)}")
