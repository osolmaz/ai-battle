# Count elements of order 13 in GL(3, F_3)
from collections import Counter

def mat_mul_3(A, B, p):
    """3x3 matrix multiplication mod p."""
    C = [[0]*3 for _ in range(3)]
    for i in range(3):
        for j in range(3):
            s = 0
            for k in range(3):
                s += A[i][k] * B[k][j]
            C[i][j] = s % p
    return C

def mat_eq(A, B):
    return all(A[i][j] == B[i][j] for i in range(3) for j in range(3))

def solve():
    p = 3
    I = [[1,0,0],[0,1,0],[0,0,1]]
    
    order_counts = Counter()
    total = 0
    
    for m in range(p**9):
        # Decode matrix
        M = [[0]*3 for _ in range(3)]
        val = m
        for i in range(3):
            for j in range(3):
                M[i][j] = val % p
                val //= p
        
        # Check determinant
        det = (M[0][0]*(M[1][1]*M[2][2]-M[1][2]*M[2][1])
             - M[0][1]*(M[1][0]*M[2][2]-M[1][2]*M[2][0])
             + M[0][2]*(M[1][0]*M[2][1]-M[1][1]*M[2][0])) % p
        if det == 0:
            continue
        total += 1
        
        # Compute order
        curr = [row[:] for row in I]
        for k in range(1, 400):  # max order in GL(3,F_3) divides lcm(26, 8, 3, ...) 
            curr = mat_mul_3(curr, M, p)
            if mat_eq(curr, I):
                order_counts[k] += 1
                break
    
    print(f"|GL(3, F_3)| = {total}")
    print(f"Elements of order 13: {order_counts.get(13, 0)}")
    
    # Show all orders
    for order in sorted(order_counts.keys()):
        if order_counts[order] > 0:
            print(f"  Order {order}: {order_counts[order]}")

solve()

