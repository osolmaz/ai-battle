# Verify by brute force: enumerate ALL partitions into 4 triples
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

count = 0
count_div3 = 0
for partition in all_partitions_into_triples(list(range(1, 13))):
    count += 1
    if all(sum(t) % 3 == 0 for t in partition):
        count_div3 += 1

print(f"Total partitions: {count} (expected 15400)")
print(f"Div by 3 partitions: {count_div3} (expected 640)")
