# Sudden death - I'm leading 11-10. If opponent gets this right, we continue.
# If they get it wrong, I win. Let me ask something tricky but fair.
#
# Let me try: count the number of closed knight's tours on a 6x6 board.
# A closed knight's tour visits all 36 squares exactly once and returns to start.
# The number of directed closed knight's tours on 6x6 is 9862 (known).
# Undirected: 9862 / 2 = 4931... but this might be looked up.
#
# Let me try something less standard.
# Count the number of ways to partition the set {1,...,12} into 4 triples
# such that in each triple, the sum of the three elements is divisible by 3.
#
# Sum of 1..12 = 78. 78/3 = 26. Each triple must sum to a multiple of 3.
# Since 4 triples sum to 78, and each triple sum is ≡ 0 (mod 3), total is 0 mod 3. 78 mod 3 = 0. ✓

from itertools import combinations

elements = list(range(1, 13))

def count_partitions():
    # Partition {1,...,12} into 4 unordered triples, each summing to 0 mod 3
    # To avoid counting permutations of triples, fix element 1 in the first triple.
    
    count = 0
    remaining = set(range(2, 13))
    
    def solve(triples, rem, min_first):
        nonlocal count
        if len(triples) == 4:
            count += 1
            return
        
        # Choose a triple from remaining elements
        # To avoid overcounting, the first element of each triple is the smallest
        # remaining, and triples are ordered by their smallest element.
        rem_list = sorted(rem)
        first = rem_list[0]
        rest = rem_list[1:]
        
        for pair in combinations(rest, 2):
            triple = (first, pair[0], pair[1])
            if sum(triple) % 3 == 0:
                new_rem = rem - {first, pair[0], pair[1]}
                solve(triples + [triple], new_rem, 0)
    
    # Element 1 is always in the first triple (it's the smallest)
    solve([], set(range(1, 13)), 0)
    return count

result = count_partitions()
print(f"Partitions of {{1,...,12}} into 4 triples with each triple sum div by 3: {result}")

# Hmm, this might be too easy. Let me compute it and see.
# Also compute without the divisibility constraint for sanity check.
# Total partitions of 12 into 4 triples: 12!/(3!^4 * 4!) = 15400

from math import factorial
total = factorial(12) // (factorial(3)**4 * factorial(4))
print(f"Total partitions into 4 triples: {total}")
