# I need a question that's hard but fair, and that I can verify.
# Let me ask about counting linear extensions of a specific poset,
# leveraging the technique I just demonstrated.
#
# Or better: let me ask something that requires combining multiple 
# mathematical concepts.
#
# Idea: Consider the ring Z[x]/(x^4 + x^3 + x^2 + x + 1).
# This is the ring of integers in the cyclotomic field Q(zeta_5).
# How many ideals of norm at most 30 does this ring have?
#
# Hmm, this is too specialized.
#
# Let me try something about counting group actions or representations.
#
# Actually, let me ask about a specific combinatorial structure that
# requires careful reasoning.
#
# Q: How many labeled simple graphs on vertex set {1,...,8} have the
# property that every connected component has an even number of edges?
#
# This is a well-defined counting problem. Let me compute it.

from itertools import combinations

def count_graphs_with_even_edge_components(n):
    """Count labeled simple graphs on {1,...,n} where every connected 
    component has an even number of edges."""
    
    # Enumerate all possible edge sets
    all_edges = list(combinations(range(n), 2))
    total_edges = len(all_edges)
    count = 0
    
    for mask in range(1 << total_edges):
        # Get the edge set
        edges = []
        for i in range(total_edges):
            if mask & (1 << i):
                edges.append(all_edges[i])
        
        # Find connected components
        parent = list(range(n))
        def find(x):
            while parent[x] != x:
                parent[x] = parent[parent[x]]
                x = parent[x]
            return x
        def union(x, y):
            px, py = find(x), find(y)
            if px != py:
                parent[px] = py
        
        for u, v in edges:
            union(u, v)
        
        # Count edges per component
        comp_edges = {}
        for u, v in edges:
            root = find(u)
            comp_edges[root] = comp_edges.get(root, 0) + 1
        
        # Check if all components have even number of edges
        all_even = all(e % 2 == 0 for e in comp_edges.values())
        if all_even:
            count += 1
    
    return count

# This is too slow for n=8 (2^28 ≈ 268M subsets). Let me use a smarter approach.
# For n=6 (2^15 = 32768), it's feasible.

for n in range(2, 7):
    result = count_graphs_with_even_edge_components(n)
    total = 1 << (n*(n-1)//2)
    print(f"n={n}: {result} out of {total}")

