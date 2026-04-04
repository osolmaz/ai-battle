# Optimized: track rainbow triangle count incrementally during backtracking
from itertools import combinations

def solve():
    n = 8
    edges = list(combinations(range(n), 2))
    num_edges = len(edges)
    edge_idx = {e: i for i, e in enumerate(edges)}
    
    triangles = []
    for a, b, c in combinations(range(n), 3):
        e1 = edge_idx[(a, b)]
        e2 = edge_idx[(a, c)]
        e3 = edge_idx[(b, c)]
        triangles.append((e1, e2, e3))
    
    num_triangles = len(triangles)
    
    edge_triangles = [[] for _ in range(num_edges)]
    for t_idx, (e1, e2, e3) in enumerate(triangles):
        edge_triangles[e1].append(t_idx)
        edge_triangles[e2].append(t_idx)
        edge_triangles[e3].append(t_idx)
    
    target = [6, 9, 13]
    target_rainbow = 8
    
    coloring = [-1] * num_edges
    remaining = list(target)
    rainbow_count = [0]  # current count of rainbow triangles
    # Track how many edges of each triangle are colored
    tri_colored = [0] * num_triangles
    count = [0]
    
    def backtrack(pos):
        if pos == num_edges:
            if rainbow_count[0] == target_rainbow:
                count[0] += 1
            return
        
        edges_left = num_edges - pos
        
        # Pruning: if rainbow count already exceeds target, prune
        if rainbow_count[0] > target_rainbow:
            return
        
        for color in range(3):
            if remaining[color] <= 0:
                continue
            if remaining[color] > edges_left:
                continue
            
            coloring[pos] = color
            
            # Check triangles and update rainbow count
            valid = True
            rainbow_delta = 0
            completed_triangles = []
            
            for t_idx in edge_triangles[pos]:
                e1, e2, e3 = triangles[t_idx]
                tri_colored[t_idx] += 1
                
                if tri_colored[t_idx] == 3:
                    completed_triangles.append(t_idx)
                    c1 = coloring[e1]
                    c2 = coloring[e2]
                    c3 = coloring[e3]
                    if c1 == c2 == c3:
                        valid = False
                        # Undo tri_colored updates
                        for t2 in edge_triangles[pos]:
                            tri_colored[t2] -= 1
                            if t2 == t_idx:
                                break
                        # need to undo up to and including t_idx
                        break
                    if c1 != c2 and c2 != c3 and c1 != c3:
                        rainbow_delta += 1
            
            if not valid:
                # Undo remaining tri_colored updates (already partially undone above)
                # Actually, let me restructure to make undo cleaner
                coloring[pos] = -1
                continue
            
            if rainbow_count[0] + rainbow_delta > target_rainbow:
                # Too many rainbow triangles already
                for t_idx in edge_triangles[pos]:
                    tri_colored[t_idx] -= 1
                coloring[pos] = -1
                continue
            
            remaining[color] -= 1
            rainbow_count[0] += rainbow_delta
            backtrack(pos + 1)
            remaining[color] += 1
            rainbow_count[0] -= rainbow_delta
            
            for t_idx in edge_triangles[pos]:
                tri_colored[t_idx] -= 1
        
        coloring[pos] = -1
    
    # Hmm, the undo logic above is buggy. Let me rewrite more carefully.
    pass

# Let me write a cleaner version
def solve_clean():
    n = 8
    edges = list(combinations(range(n), 2))
    num_edges = len(edges)
    edge_idx = {e: i for i, e in enumerate(edges)}
    
    triangles = []
    for a, b, c in combinations(range(n), 3):
        e1 = edge_idx[(a, b)]
        e2 = edge_idx[(a, c)]
        e3 = edge_idx[(b, c)]
        triangles.append((e1, e2, e3))
    
    num_triangles = len(triangles)
    
    edge_triangles = [[] for _ in range(num_edges)]
    for t_idx, (e1, e2, e3) in enumerate(triangles):
        edge_triangles[e1].append(t_idx)
        edge_triangles[e2].append(t_idx)
        edge_triangles[e3].append(t_idx)
    
    target = [6, 9, 13]
    target_rainbow = 8
    
    coloring = [-1] * num_edges
    remaining = list(target)
    rainbow_count = [0]
    count = [0]
    
    def backtrack(pos):
        if pos == num_edges:
            if rainbow_count[0] == target_rainbow:
                count[0] += 1
            return
        
        edges_left = num_edges - pos
        if rainbow_count[0] > target_rainbow:
            return
        
        for color in range(3):
            if remaining[color] <= 0:
                continue
            if remaining[color] > edges_left:
                continue
            
            coloring[pos] = color
            
            # Check all triangles containing this edge
            valid = True
            delta = 0
            for t_idx in edge_triangles[pos]:
                e1, e2, e3 = triangles[t_idx]
                c1 = coloring[e1]
                c2 = coloring[e2]
                c3 = coloring[e3]
                if c1 < 0 or c2 < 0 or c3 < 0:
                    continue  # triangle not fully colored
                if c1 == c2 == c3:
                    valid = False
                    break
                if c1 != c2 and c2 != c3 and c1 != c3:
                    delta += 1
            
            if valid and rainbow_count[0] + delta <= target_rainbow:
                remaining[color] -= 1
                rainbow_count[0] += delta
                backtrack(pos + 1)
                remaining[color] += 1
                rainbow_count[0] -= delta
        
        coloring[pos] = -1
    
    import sys
    sys.setrecursionlimit(100000)
    backtrack(0)
    print(f"Valid colorings: {count[0]}")
    return count[0]

solve_clean()

