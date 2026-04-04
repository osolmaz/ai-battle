# Question: Count the number of simple cycles in a specific undirected graph.
# This is a well-defined problem but trickier than paths - easy to over/under count.

# Let me design a graph and compute the answer.
# Graph on vertices {1..10} with specific edges.

edges = [
    (1,2), (1,3), (1,5), (2,3), (2,4), (2,6), (3,5), (3,7),
    (4,5), (4,6), (4,8), (5,7), (5,9), (6,8), (6,10),
    (7,9), (7,10), (8,9), (8,10), (9,10)
]

n = 10
adj = [[] for _ in range(n+1)]
adj_set = set()
for u, v in edges:
    adj[u].append(v)
    adj[v].append(u)
    adj_set.add((u,v))
    adj_set.add((v,u))

# Count simple cycles. A simple cycle is a closed path visiting each vertex at most once,
# with length >= 3. Two cycles are the same if they traverse the same set of edges
# (regardless of starting vertex or direction).
# 
# Standard approach: for each subset of vertices of size >= 3, check if the induced
# subgraph has a Hamiltonian cycle. But that counts cycles in subsets, not simple cycles
# in the original graph... Actually no - a simple cycle in the graph corresponds to
# a subset of vertices that form a cycle (each vertex has degree exactly 2 in the cycle).
#
# Better: enumerate all simple cycles. Use DFS from each vertex, only consider cycles
# where the smallest vertex is the "root" to avoid counting duplicates.

def count_simple_cycles():
    count = 0
    
    def dfs(start, current, visited, length):
        nonlocal count
        for neighbor in adj[current]:
            if neighbor == start and length >= 3:
                # Found a cycle - count it (divide by 2 for direction)
                count += 1
            elif neighbor > start and neighbor not in visited:
                visited.add(neighbor)
                dfs(start, neighbor, visited, length + 1)
                visited.remove(neighbor)
    
    for start in range(1, n+1):
        visited = {start}
        dfs(start, start, visited, 1)
    
    # Each cycle is found twice (once for each direction)
    return count // 2

result = count_simple_cycles()
print(f"Number of simple cycles: {result}")

# Let me verify with a small example: triangle (1,2,3) should give 1
edges_test = [(1,2),(2,3),(1,3)]
adj_test = [[] for _ in range(4)]
for u,v in edges_test:
    adj_test[u].append(v)
    adj_test[v].append(u)

# Quick manual test
old_adj = adj
adj = adj_test
old_n = n
n = 3
test_result = count_simple_cycles()
print(f"Triangle test: {test_result} (expected 1)")
adj = old_adj
n = old_n

# Also test K4 (should have 7 simple cycles: 4 triangles + 3 four-cycles)
edges_k4 = [(1,2),(1,3),(1,4),(2,3),(2,4),(3,4)]
adj_k4 = [[] for _ in range(5)]
for u,v in edges_k4:
    adj_k4[u].append(v)
    adj_k4[v].append(u)
adj = adj_k4
n = 4
test_k4 = count_simple_cycles()
print(f"K4 test: {test_k4} (expected 7)")
