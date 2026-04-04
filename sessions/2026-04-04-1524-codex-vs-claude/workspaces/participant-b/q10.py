# I need to ask a question that Codex is less likely to get right.
# Codex has been solving everything, so I need something truly challenging.
#
# Let me try a question that combines multiple concepts and has a non-obvious twist.
#
# Idea: Count linear extensions of a specific poset (building on my demonstrated skill)
# but with a twist that makes it harder.
#
# Or: ask about a specific algebraic structure where the computation is tricky.
#
# Actually, let me try something involving a specific integral or sum that has
# a surprising closed form, but where getting the form wrong gives a wrong answer.
#
# Q: What is the number of ways to write 30 as an ordered sum of positive 
# integers where each term is at most 5?
#
# This is the coefficient of x^30 in 1/(1-x-x^2-x^3-x^4-x^5)... no, ordered sums
# (compositions) with parts in {1,2,3,4,5}.
#
# The number of such compositions is the coefficient of x^30 in:
# sum_{k>=0} (x + x^2 + x^3 + x^4 + x^5)^k = 1/(1 - x(1-x^5)/(1-x))
#
# This can be computed using the transfer matrix method or direct polynomial expansion.
# Let me compute it.

from functools import lru_cache

@lru_cache(maxsize=None)
def compositions(n, max_part=5):
    """Number of compositions of n with parts in {1,...,max_part}."""
    if n == 0:
        return 1
    if n < 0:
        return 0
    total = 0
    for k in range(1, min(n, max_part) + 1):
        total += compositions(n - k, max_part)
    return total

for n in range(1, 35):
    print(f"C({n}) = {compositions(n)}")

# This is a well-known sequence related to generalized Fibonacci numbers.
# Too easy to compute, not a good question.

# Let me think of something else.

# How about: What is the chromatic polynomial of the complement of the 
# Petersen graph evaluated at k=4?

# The complement of the Petersen graph has 10 vertices and C(10,2)-15 = 30 edges.
# Computing its chromatic polynomial requires knowing the graph structure.
# 
# Actually, the complement of the Petersen graph is known as the Kneser graph 
# complement... hmm, let me think.

# The Petersen graph is the Kneser graph KG(5,2). Its complement is the 
# Johnson graph J(5,2)? No, the complement of KG(5,2) is actually the 
# "Kneser complement" which is the graph where two 2-element subsets of {1,...,5}
# are adjacent iff they share an element. This is actually the line graph of K_5.

# L(K_5) has 10 vertices (edges of K_5) and each vertex has degree... 
# In K_5, each edge shares a vertex with 6 other edges. So L(K_5) is 6-regular.
# Edges: 10*6/2 = 30. ✓ (matches C(10,2) - 15 = 30).

# The chromatic polynomial of L(K_5) is a specific polynomial.
# P(k) for the line graph of K_5...

# This is getting too specialized. Let me think of a cleaner question.

# How about asking for the number of distinct proper 4-colorings of the 
# Petersen graph? This is P_Petersen(4).

# The chromatic polynomial of the Petersen graph:
# P(k) = k(k-1)(k-2)(k-3)(k^6 - 12k^5 + 58k^4 - 144k^3 + 193k^2 - 133k + 38)

# Wait, I'm not confident about this formula. Let me compute P(4) directly
# by trying all 4^10 colorings.

def petersen_chromatic_poly_at_k(k):
    """Count proper k-colorings of the Petersen graph."""
    # Petersen graph edges (0-indexed vertices 0-9)
    # Outer cycle: 0-1-2-3-4-0
    # Inner star: 5-7-9-6-8-5
    # Spokes: 0-5, 1-6, 2-7, 3-8, 4-9
    edges = [
        (0,1),(1,2),(2,3),(3,4),(4,0),  # outer
        (5,7),(7,9),(9,6),(6,8),(8,5),  # inner
        (0,5),(1,6),(2,7),(3,8),(4,9)   # spokes
    ]
    
    from itertools import product
    count = 0
    for coloring in product(range(k), repeat=10):
        valid = True
        for u, v in edges:
            if coloring[u] == coloring[v]:
                valid = False
                break
        if valid:
            count += 1
    return count

for k in range(1, 6):
    print(f"P_Petersen({k}) = {petersen_chromatic_poly_at_k(k)}")

