# Compute Ramsey-type colorings of K_n edges
from itertools import combinations, product

def count_rainbow_colorings(n, num_colors):
    """Count edge colorings of K_n with num_colors colors 
    that contain no monochromatic triangle."""
    
    edges = list(combinations(range(n), 2))
    num_edges = len(edges)
    edge_idx = {e: i for i, e in enumerate(edges)}
    
    # Find all triangles
    triangles = []
    for a, b, c in combinations(range(n), 3):
        e1 = edge_idx[(a, b)]
        e2 = edge_idx[(a, c)]
        e3 = edge_idx[(b, c)]
        triangles.append((e1, e2, e3))
    
    print(f"K_{n}: {num_edges} edges, {len(triangles)} triangles")
    
    count = 0
    for coloring in product(range(num_colors), repeat=num_edges):
        valid = True
        for e1, e2, e3 in triangles:
            if coloring[e1] == coloring[e2] == coloring[e3]:
                valid = False
                break
        if valid:
            count += 1
    
    total = num_colors ** num_edges
    print(f"Colorings without monochromatic triangle: {count} / {total}")
    return count

# K_5 with 3 colors
count_rainbow_colorings(5, 3)

# K_6 with 3 colors (14M iterations - might be slow but let's try)
print("\nK_6 with 3 colors:")
count_rainbow_colorings(6, 3)

