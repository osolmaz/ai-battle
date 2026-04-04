# K_8 has C(8,2) = 28 edges.
# We need: 5 red + 9 blue + 14 green = 28 edges. ✓
# No monochromatic triangle.
#
# Approach: enumerate all ways to choose 5 red edges, 9 blue edges, 14 green edges
# from the 28 edges of K_8, checking no monochromatic triangle.
#
# C(28,5) * C(23,9) = too large for brute force? Let me check.
# C(28,5) = 98280. C(23,9) = 817190. Product ≈ 8 * 10^10. Way too many.
#
# Better approach: use backtracking. Assign colors to edges one by one,
# pruning when a monochromatic triangle is formed or when the remaining
# edge counts are impossible.
#
# K_8 has 28 edges and C(8,3) = 56 triangles.
#
# Let me use a constraint-based approach: iterate over all possible assignments
# of colors to the 28 edges, with the constraint of exactly 5 red, 9 blue, 14 green,
# and no monochromatic triangle.

from itertools import combinations

def solve():
    n = 8
    edges = list(combinations(range(n), 2))
    num_edges = len(edges)  # 28
    edge_idx = {e: i for i, e in enumerate(edges)}
    
    # Find all triangles
    triangles = []
    for a, b, c in combinations(range(n), 3):
        e1 = edge_idx[(a, b)]
        e2 = edge_idx[(a, c)]
        e3 = edge_idx[(b, c)]
        triangles.append((e1, e2, e3))
    
    print(f"K_8: {num_edges} edges, {len(triangles)} triangles")
    
    # For each edge, which triangles contain it
    edge_triangles = [[] for _ in range(num_edges)]
    for t_idx, (e1, e2, e3) in enumerate(triangles):
        edge_triangles[e1].append(t_idx)
        edge_triangles[e2].append(t_idx)
        edge_triangles[e3].append(t_idx)
    
    # Target: 5 red (0), 9 blue (1), 14 green (2)
    target = [5, 9, 14]
    
    # Backtracking
    coloring = [-1] * num_edges
    remaining = list(target)  # remaining edges of each color to assign
    count = [0]
    
    def backtrack(pos):
        if pos == num_edges:
            count[0] += 1
            return
        
        edges_left = num_edges - pos
        
        for color in range(3):
            if remaining[color] <= 0:
                continue
            
            # Check if enough edges remain
            if remaining[color] > edges_left:
                continue
            
            coloring[pos] = color
            
            # Check all triangles containing this edge for monochromatic
            valid = True
            for t_idx in edge_triangles[pos]:
                e1, e2, e3 = triangles[t_idx]
                c1 = coloring[e1]
                c2 = coloring[e2]
                c3 = coloring[e3]
                if c1 >= 0 and c2 >= 0 and c3 >= 0 and c1 == c2 == c3:
                    valid = False
                    break
            
            if valid:
                remaining[color] -= 1
                backtrack(pos + 1)
                remaining[color] += 1
        
        coloring[pos] = -1
    
    backtrack(0)
    print(f"Valid colorings: {count[0]}")
    return count[0]

result = solve()

