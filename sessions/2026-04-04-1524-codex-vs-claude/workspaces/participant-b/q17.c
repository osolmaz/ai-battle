// K_{5,5}: 25 edges. 3 colors with 15 red, 5 blue, 5 green.
// No monochromatic C_4 (= no monochromatic K_{2,2}).
// K_{5,5} has C(5,2)^2 = 100 copies of K_{2,2}.
//
// Approach: backtracking with pruning.
// Edges: (a, b) for a in {0..4}, b in {0..4}. Edge index = a*5 + b.

#include <stdio.h>
#include <string.h>
#include <stdlib.h>

#define NA 5
#define NB 5
#define NUM_EDGES 25

// K_{2,2} subgraphs: choose 2 from A and 2 from B
// C(5,2)^2 = 100

int quads[100][4]; // 4 edge indices per quad
int num_quads;
int edge_quads[NUM_EDGES][40]; // which quads each edge belongs to
int edge_quad_count[NUM_EDGES];

int coloring[NUM_EDGES];
int remaining[3]; // 0=red(15), 1=blue(5), 2=green(5)
long long result;

void init() {
    num_quads = 0;
    memset(edge_quad_count, 0, sizeof(edge_quad_count));
    
    for (int a1 = 0; a1 < NA; a1++)
        for (int a2 = a1+1; a2 < NA; a2++)
            for (int b1 = 0; b1 < NB; b1++)
                for (int b2 = b1+1; b2 < NB; b2++) {
                    int q = num_quads++;
                    // Edges: (a1,b1), (a1,b2), (a2,b1), (a2,b2)
                    quads[q][0] = a1*NB + b1;
                    quads[q][1] = a1*NB + b2;
                    quads[q][2] = a2*NB + b1;
                    quads[q][3] = a2*NB + b2;
                    for (int k = 0; k < 4; k++)
                        edge_quads[quads[q][k]][edge_quad_count[quads[q][k]]++] = q;
                }
    
    printf("K_{5,5}: %d edges, %d K_{2,2} subgraphs\n", NUM_EDGES, num_quads);
}

void backtrack(int pos) {
    if (pos == NUM_EDGES) {
        result++;
        return;
    }
    
    int edges_left = NUM_EDGES - pos;
    
    for (int c = 0; c < 3; c++) {
        if (remaining[c] <= 0) continue;
        if (remaining[c] > edges_left) continue;
        
        coloring[pos] = c;
        
        // Check quads
        int valid = 1;
        for (int qi = 0; qi < edge_quad_count[pos]; qi++) {
            int q = edge_quads[pos][qi];
            int c0 = coloring[quads[q][0]];
            int c1 = coloring[quads[q][1]];
            int c2 = coloring[quads[q][2]];
            int c3 = coloring[quads[q][3]];
            if (c0 < 0 || c1 < 0 || c2 < 0 || c3 < 0) continue;
            if (c0 == c1 && c1 == c2 && c2 == c3) {
                valid = 0;
                break;
            }
        }
        
        if (valid) {
            remaining[c]--;
            backtrack(pos + 1);
            remaining[c]++;
        }
    }
    
    coloring[pos] = -1;
}

int main() {
    init();
    memset(coloring, -1, sizeof(coloring));
    remaining[0] = 15; // red
    remaining[1] = 5;  // blue
    remaining[2] = 5;  // green
    result = 0;
    
    backtrack(0);
    
    printf("C4-free 3-colorings (15R, 5B, 5G): %lld\n", result);
    return 0;
}
