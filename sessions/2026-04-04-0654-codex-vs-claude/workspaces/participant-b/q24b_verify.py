# Verify n=13 by a different method: direct recursive enumeration for smaller cases
# and check the DP matches

from itertools import combinations

def enumerate_odd_partitions(elements):
    """Enumerate all set partitions of elements where every part has odd size."""
    if not elements:
        return 1
    
    elements = sorted(elements)
    first = elements[0]
    rest = elements[1:]
    
    total = 0
    # first goes in a part of odd size s
    for s in range(1, len(elements) + 1, 2):
        # Choose s-1 elements from rest to join first
        for others in combinations(rest, s - 1):
            remaining = [x for x in rest if x not in others]
            total += enumerate_odd_partitions(remaining)
    
    return total

# Verify for small cases
for nn in range(1, 10):
    bf = enumerate_odd_partitions(list(range(1, nn + 1)))
    print(f"n={nn}: brute force={bf}")
