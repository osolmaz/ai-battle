# Count 3-colorings of K_7 edges with no monochromatic triangle
# Using backtracking with constraint checking

from itertools import combinations

def solve_k7():
    n = 7
    edges = list(combinations(range(n), 2))
    num_edges = len(edges)  # 21
    edge_idx = {e: i for i, e in enumerate(edges)}
    
    # Find all triangles and which edges they use
    triangles = []
    for a, b, c in combinations(range(n), 3):
        e1 = edge_idx[(a, b)]
        e2 = edge_idx[(a, c)]
        e3 = edge_idx[(b, c)]
        triangles.append((e1, e2, e3))
    
    print(f"K_7: {num_edges} edges, {len(triangles)} triangles")
    
    # For each edge, which triangles contain it
    edge_triangles = [[] for _ in range(num_edges)]
    for t_idx, (e1, e2, e3) in enumerate(triangles):
        edge_triangles[e1].append(t_idx)
        edge_triangles[e2].append(t_idx)
        edge_triangles[e3].append(t_idx)
    
    # Backtracking
    coloring = [-1] * num_edges
    count = [0]
    
    def backtrack(pos):
        if pos == num_edges:
            count[0] += 1
            return
        
        for color in range(3):
            coloring[pos] = color
            
            # Check all triangles containing this edge
            valid = True
            for t_idx in edge_triangles[pos]:
                e1, e2, e3 = triangles[t_idx]
                # Check if all 3 edges of this triangle are colored the same
                c1 = coloring[e1]
                c2 = coloring[e2]
                c3 = coloring[e3]
                if c1 >= 0 and c2 >= 0 and c3 >= 0 and c1 == c2 == c3:
                    valid = False
                    break
            
            if valid:
                backtrack(pos + 1)
        
        coloring[pos] = -1
    
    backtrack(0)
    print(f"3-colorings of K_7 without monochromatic triangle: {count[0]}")
    return count[0]

result = solve_k7()

