# Count elements of order 24 in GL(2, F_11)
from collections import Counter

def gl2_order_count(p):
    order_counts = Counter()
    total = 0
    
    for a in range(p):
        for b in range(p):
            for c in range(p):
                for d in range(p):
                    det = (a*d - b*c) % p
                    if det == 0:
                        continue
                    total += 1
                    
                    M = (a, b, c, d)
                    # Compute M^k mod p until we get identity
                    ca, cb, cc, cd = 1, 0, 0, 1  # identity
                    
                    for k in range(1, p*p*p + 1):
                        # multiply (ca,cb,cc,cd) by (a,b,c,d) mod p
                        na = (ca*a + cb*c) % p
                        nb = (ca*b + cb*d) % p
                        nc = (cc*a + cd*c) % p
                        nd = (cc*b + cd*d) % p
                        ca, cb, cc, cd = na, nb, nc, nd
                        
                        if (ca, cb, cc, cd) == (1, 0, 0, 1):
                            order_counts[k] += 1
                            break
    
    return order_counts, total

print("Computing GL(2, F_11)...")
counts, total = gl2_order_count(11)
print(f"|GL(2, F_11)| = {total} (expected 13200)")
print(f"Elements of order 24: {counts.get(24, 0)}")
print(f"\nAll orders:")
for order in sorted(counts.keys()):
    print(f"  Order {order}: {counts[order]}")

