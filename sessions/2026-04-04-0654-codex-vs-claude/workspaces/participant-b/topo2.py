edges = [
    ('A','D'), ('A','F'), ('A','G'), ('A','J'), ('A','P'),
    ('B','J'), ('B','N'), ('B','Q'),
    ('C','I'),
    ('D','F'), ('D','J'), ('D','K'),
    ('E','N'), ('E','Q'),
    ('F','M'), ('F','O'), ('F','R'),
    ('G','N'), ('G','P'),
    ('H','I'), ('H','M'),
    ('I','N'),
    ('J','R'),
    ('K','M'),
    ('L','R'),
    ('M','Q'),
    ('O','P'), ('O','R'),
    ('P','Q')
]

vertices = list('ABCDEFGHIJKLMNOPQR')
n = len(vertices)
idx = {v: i for i, v in enumerate(vertices)}

preds = {v: set() for v in vertices}
for u, v in edges:
    preds[v].add(u)

pred_mask = [0] * n
for v in vertices:
    for p in preds[v]:
        pred_mask[idx[v]] |= (1 << idx[p])

full = (1 << n) - 1
dp = [0] * (1 << n)
dp[0] = 1

for mask in range(full):
    if dp[mask] == 0:
        continue
    for i in range(n):
        if mask & (1 << i):
            continue
        if (pred_mask[i] & mask) == pred_mask[i]:
            dp[mask | (1 << i)] += dp[mask]

print(dp[full])
