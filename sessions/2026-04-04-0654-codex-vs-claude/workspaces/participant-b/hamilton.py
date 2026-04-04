from itertools import permutations

edges = [(1,2),(2,3),(2,4),(4,5),(2,6),(5,7),(4,8),(7,9),(1,10),(9,11),(5,12),(3,13),(12,14),(10,13),(6,10),(3,11),(12,13),(4,10),(6,8),(2,9),(9,13),(3,7),(5,11),(8,9),(4,7)]

adj = set()
for u, v in edges:
    adj.add((u, v))
    adj.add((v, u))

n = 14

# Use DFS with bitmask for efficiency
def count_hamiltonian_paths():
    count = 0
    full_mask = (1 << n) - 1
    
    def dfs(node, visited_mask, depth):
        nonlocal count
        if depth == n:
            if node == 14:
                count += 1
            return
        for neighbor in range(1, n + 1):
            if not (visited_mask & (1 << (neighbor - 1))) and (node, neighbor) in adj:
                dfs(neighbor, visited_mask | (1 << (neighbor - 1)), depth + 1)
    
    dfs(1, 1 << 0, 1)  # Start at vertex 1, mark it visited
    return count

result = count_hamiltonian_paths()
print(f"Hamiltonian paths from 1 to 14: {result}")
