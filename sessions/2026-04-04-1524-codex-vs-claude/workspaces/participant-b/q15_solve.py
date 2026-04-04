# K_8: 28 edges, 56 triangles
# Constraints: no monochromatic triangle, 6 red, 9 blue, 13 green, exactly 8 rainbow triangles
# 
# Reuse the backtracking approach from the previous K_8 question,
# but also count rainbow triangles.

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
    
    num_triangles = len(triangles)
    print(f"K_8: {num_edges} edges, {num_triangles} triangles")
    
    # For each edge, which triangles contain it
    edge_triangles = [[] for _ in range(num_edges)]
    for t_idx, (e1, e2, e3) in enumerate(triangles):
        edge_triangles[e1].append(t_idx)
        edge_triangles[e2].append(t_idx)
        edge_triangles[e3].append(t_idx)
    
    # Target: 6 red (0), 9 blue (1), 13 green (2), 8 rainbow triangles
    target = [6, 9, 13]
    target_rainbow = 8
    
    coloring = [-1] * num_edges
    remaining = list(target)
    count = [0]
    
    def count_rainbow():
        """Count rainbow triangles in current coloring."""
        r = 0
        for e1, e2, e3 in triangles:
            c1, c2, c3 = coloring[e1], coloring[e2], coloring[e3]
            if c1 >= 0 and c2 >= 0 and c3 >= 0:
                if c1 != c2 and c2 != c3 and c1 != c3:
                    r += 1
        return r
    
    def backtrack(pos):
        if pos == num_edges:
            if count_rainbow() == target_rainbow:
                count[0] += 1
            return
        
        edges_left = num_edges - pos
        
        for color in range(3):
            if remaining[color] <= 0:
                continue
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
    print(f"Valid colorings with exactly {target_rainbow} rainbow triangles: {count[0]}")
    return count[0]

result = solve()

