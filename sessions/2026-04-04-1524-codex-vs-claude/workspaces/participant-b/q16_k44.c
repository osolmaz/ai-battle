#include <stdio.h>
#include <string.h>

// K_{4,4}: vertices A={0,1,2,3} and B={4,5,6,7}
// Edges: (a,b) for a in A, b in B. 16 edges total.
// Index: edge(a,b) = a*4 + (b-4), for a in {0..3}, b in {4..7}
// So edge indices 0..15.
//
// C_4 subgraphs: choose 2 from A and 2 from B.
// C(4,2)^2 = 36 such subgraphs.
// Each has 4 edges forming a K_{2,2}.
// 
// Constraint: no monochromatic C_4, i.e., for each K_{2,2}, not all 4 edges same color.

#define NUM_EDGES 16
#define NUM_COLORS 3

// Precompute all 36 K_{2,2} subgraphs
int quads[36][4]; // each quad has 4 edge indices
int num_quads;

void init() {
    num_quads = 0;
    for (int a1 = 0; a1 < 4; a1++)
        for (int a2 = a1+1; a2 < 4; a2++)
            for (int b1 = 0; b1 < 4; b1++)
                for (int b2 = b1+1; b2 < 4; b2++) {
                    // Edges: (a1,b1+4), (a1,b2+4), (a2,b1+4), (a2,b2+4)
                    quads[num_quads][0] = a1*4 + b1;
                    quads[num_quads][1] = a1*4 + b2;
                    quads[num_quads][2] = a2*4 + b1;
                    quads[num_quads][3] = a2*4 + b2;
                    num_quads++;
                }
    printf("K_{4,4}: %d edges, %d C_4 subgraphs\n", NUM_EDGES, num_quads);
}

int main() {
    init();
    
    long long count = 0;
    int coloring[NUM_EDGES];
    
    // Enumerate all 3^16 colorings
    for (long long mask = 0; mask < 43046721LL; mask++) {
        // Decode coloring
        long long m = mask;
        for (int i = 0; i < NUM_EDGES; i++) {
            coloring[i] = m % 3;
            m /= 3;
        }
        
        // Check all quads
        int valid = 1;
        for (int q = 0; q < num_quads; q++) {
            int c0 = coloring[quads[q][0]];
            int c1 = coloring[quads[q][1]];
            int c2 = coloring[quads[q][2]];
            int c3 = coloring[quads[q][3]];
            if (c0 == c1 && c1 == c2 && c2 == c3) {
                valid = 0;
                break;
            }
        }
        
        if (valid) count++;
    }
    
    printf("Colorings without monochromatic C_4: %lld\n", count);
    printf("Total colorings: %lld\n", 43046721LL);
    return 0;
}
