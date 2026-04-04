# Question: Given a DFA, count strings of length n accepted.
# 
# DFA with states {0,1,2,3,4,5}, alphabet {a,b,c}, start state 0, 
# accepting states {3,5}.
# Transition function:
# State 0: a->1, b->2, c->0
# State 1: a->3, b->0, c->4
# State 2: a->4, b->5, c->1
# State 3: a->2, b->1, c->5
# State 4: a->5, b->3, c->2
# State 5: a->0, b->4, c->3

# Count strings of length 20 accepted.

transitions = {
    0: {'a': 1, 'b': 2, 'c': 0},
    1: {'a': 3, 'b': 0, 'c': 4},
    2: {'a': 4, 'b': 5, 'c': 1},
    3: {'a': 2, 'b': 1, 'c': 5},
    4: {'a': 5, 'b': 3, 'c': 2},
    5: {'a': 0, 'b': 4, 'c': 3},
}

accept = {3, 5}
n_states = 6
length = 20

# DP: dp[i][s] = number of strings of length i ending in state s
dp = [[0] * n_states for _ in range(length + 1)]
dp[0][0] = 1  # start state

for i in range(length):
    for s in range(n_states):
        if dp[i][s] == 0:
            continue
        for ch in 'abc':
            ns = transitions[s][ch]
            dp[i+1][ns] += dp[i][s]

total = sum(dp[length][s] for s in accept)
print(f"Strings of length {length} accepted: {total}")

# Verify with smaller lengths
for l in [1, 2, 3, 5, 10, 15, 20]:
    t = sum(dp[l][s] for s in accept)
    print(f"Length {l}: {t}")
