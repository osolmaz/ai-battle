# Let me try a harder variant: partition {1,...,15} into 5 triples where each
# triple has sum divisible by 5.
# Sum of 1..15 = 120. 120/5 = 24. Each triple sums to multiple of 5.

from itertools import combinations

def all_partitions_into_triples(elems):
    if len(elems) == 0:
        yield []
        return
    elems = sorted(elems)
    first = elems[0]
    rest = elems[1:]
    for pair in combinations(rest, 2):
        triple = (first, pair[0], pair[1])
        remaining = [x for x in rest if x not in pair]
        for partition in all_partitions_into_triples(remaining):
            yield [triple] + partition

count_div5 = 0
for partition in all_partitions_into_triples(list(range(1, 16))):
    if all(sum(t) % 5 == 0 for t in partition):
        count_div5 += 1

print(f"Partitions of {{1,...,15}} into 5 triples, each sum div 5: {count_div5}")

# Also: partition {1,...,18} into 6 triples, each with sum divisible by 4
count_div4 = 0
for partition in all_partitions_into_triples(list(range(1, 19))):
    if all(sum(t) % 4 == 0 for t in partition):
        count_div4 += 1

print(f"Partitions of {{1,...,18}} into 6 triples, each sum div 4: {count_div4}")
