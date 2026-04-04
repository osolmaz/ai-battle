# Count elements of each order in GL(2, F_7) and GL(3, F_3)
import numpy as np

def gl2_order_count(p):
    """Count elements by order in GL(2, F_p)."""
    from collections import Counter
    
    order_counts = Counter()
    
    # Enumerate all 2x2 matrices over F_p with nonzero determinant
    for a in range(p):
        for b in range(p):
            for c in range(p):
                for d in range(p):
                    det = (a*d - b*c) % p
                    if det == 0:
                        continue
                    
                    # Compute order: find smallest k > 0 with M^k = I
                    M = [[a, b], [c, d]]
                    curr = [[1, 0], [0, 1]]  # identity
                    
                    for k in range(1, p*p*p):  # max order bound
                        # curr = curr * M mod p
                        new = [[0, 0], [0, 0]]
                        for i in range(2):
                            for j in range(2):
                                s = 0
                                for l in range(2):
                                    s += curr[i][l] * M[l][j]
                                new[i][j] = s % p
                        curr = new
                        
                        if curr == [[1, 0], [0, 1]]:
                            order_counts[k] += 1
                            break
    
    return order_counts

# GL(2, F_7)
print("Computing GL(2, F_7) order distribution...")
counts_7 = gl2_order_count(7)
total = sum(counts_7.values())
print(f"|GL(2, F_7)| = {total} (expected 2016)")
print("Orders and counts:")
for order in sorted(counts_7.keys()):
    print(f"  Order {order}: {counts_7[order]}")

print(f"\nElements of order 12: {counts_7.get(12, 0)}")

