# Q: How many labeled connected simple graphs on vertex set {1,...,8} have 
# exactly 12 edges and contain no triangle (3-clique)?

from itertools import combinations

def solve():
    n = 8
    all_edges = list(combinations(range(n), 2))
    total_edges = len(all_edges)  # C(8,2) = 28
    target_m = 12
    
    # Precompute edge index for triangle checking
    edge_set_lookup = {}
    for idx, (u, v) in enumerate(all_edges):
        edge_set_lookup[(u, v)] = idx
        edge_set_lookup[(v, u)] = idx
    
    # Precompute all triangles
    triangles = []
    for a, b, c in combinations(range(n), 3):
        triangles.append(((a,b), (b,c), (a,c)))
    
    count = 0
    total_checked = 0
    
    for edge_subset in combinations(range(total_edges), target_m):
        total_checked += 1
        
        # Get the actual edges
        edges = set(edge_subset)
        
        # Check triangle-free
        has_triangle = False
        for (e1, e2, e3) in triangles:
            idx1 = edge_set_lookup[e1]
            idx2 = edge_set_lookup[e2]
            idx3 = edge_set_lookup[e3]
            if idx1 in edges and idx2 in edges and idx3 in edges:
                has_triangle = True
                break
        
        if has_triangle:
            continue
        
        # Check connectivity using BFS
        adj = [set() for _ in range(n)]
        for idx in edge_subset:
            u, v = all_edges[idx]
            adj[u].add(v)
            adj[v].add(u)
        
        visited = {0}
        queue = [0]
        while queue:
            node = queue.pop()
            for nb in adj[node]:
                if nb not in visited:
                    visited.add(nb)
                    queue.append(nb)
        
        if len(visited) == n:
            count += 1
    
    print(f"Total subsets checked: {total_checked}")
    print(f"Connected triangle-free graphs with {target_m} edges on {n} vertices: {count}")
    return count

result = solve()

