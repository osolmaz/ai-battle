#include <stdio.h>
#include <string.h>

#define NA 4
#define NB 5
#define NUM_EDGES 20

int quads[100][4];
int num_quads;
int edge_quads[NUM_EDGES][40];
int edge_quad_count[NUM_EDGES];
int coloring[NUM_EDGES];
int remaining[3];
long long result;

void init() {
    num_quads = 0;
    memset(edge_quad_count, 0, sizeof(edge_quad_count));
    for (int a1 = 0; a1 < NA; a1++)
        for (int a2 = a1+1; a2 < NA; a2++)
            for (int b1 = 0; b1 < NB; b1++)
                for (int b2 = b1+1; b2 < NB; b2++) {
                    int q = num_quads++;
                    quads[q][0] = a1*NB + b1;
                    quads[q][1] = a1*NB + b2;
                    quads[q][2] = a2*NB + b1;
                    quads[q][3] = a2*NB + b2;
                    for (int k = 0; k < 4; k++)
                        edge_quads[quads[q][k]][edge_quad_count[quads[q][k]]++] = q;
                }
}

void backtrack(int pos) {
    if (pos == NUM_EDGES) { result++; return; }
    int edges_left = NUM_EDGES - pos;
    for (int c = 0; c < 3; c++) {
        if (remaining[c] <= 0) continue;
        if (remaining[c] > edges_left) continue;
        coloring[pos] = c;
        int valid = 1;
        for (int qi = 0; qi < edge_quad_count[pos]; qi++) {
            int q = edge_quads[pos][qi];
            int c0 = coloring[quads[q][0]];
            int c1 = coloring[quads[q][1]];
            int c2 = coloring[quads[q][2]];
            int c3 = coloring[quads[q][3]];
            if (c0 < 0 || c1 < 0 || c2 < 0 || c3 < 0) continue;
            if (c0 == c1 && c1 == c2 && c2 == c3) { valid = 0; break; }
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
    printf("K_{4,5}: %d edges, %d K_{2,2} subgraphs\n", NUM_EDGES, num_quads);
    
    // Try 8+6+6 = 20
    memset(coloring, -1, sizeof(coloring));
    remaining[0] = 8; remaining[1] = 6; remaining[2] = 6;
    result = 0;
    backtrack(0);
    printf("(8,6,6): %lld\n", result);
    
    // Try 7+7+6 = 20
    memset(coloring, -1, sizeof(coloring));
    remaining[0] = 7; remaining[1] = 7; remaining[2] = 6;
    result = 0;
    backtrack(0);
    printf("(7,7,6): %lld\n", result);
    
    // Try 9+6+5 = 20
    memset(coloring, -1, sizeof(coloring));
    remaining[0] = 9; remaining[1] = 6; remaining[2] = 5;
    result = 0;
    backtrack(0);
    printf("(9,6,5): %lld\n", result);
    
    // Try 10+5+5 = 20
    memset(coloring, -1, sizeof(coloring));
    remaining[0] = 10; remaining[1] = 5; remaining[2] = 5;
    result = 0;
    backtrack(0);
    printf("(10,5,5): %lld\n", result);
    
    return 0;
}
