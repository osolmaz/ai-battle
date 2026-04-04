// Verify using backtracking with a different edge ordering
#include <stdio.h>
#include <string.h>

#define NUM_EDGES 16
int quads[36][4];
int num_quads;
int edge_quads[16][20];
int edge_quad_count[16];
int coloring[NUM_EDGES];
long long result;

void init() {
    num_quads = 0;
    memset(edge_quad_count, 0, sizeof(edge_quad_count));
    for (int a1 = 0; a1 < 4; a1++)
        for (int a2 = a1+1; a2 < 4; a2++)
            for (int b1 = 0; b1 < 4; b1++)
                for (int b2 = b1+1; b2 < 4; b2++) {
                    int q = num_quads;
                    quads[q][0] = a1*4 + b1;
                    quads[q][1] = a1*4 + b2;
                    quads[q][2] = a2*4 + b1;
                    quads[q][3] = a2*4 + b2;
                    for (int k = 0; k < 4; k++)
                        edge_quads[quads[q][k]][edge_quad_count[quads[q][k]]++] = q;
                    num_quads++;
                }
}

void backtrack(int pos) {
    if (pos == NUM_EDGES) { result++; return; }
    for (int c = 0; c < 3; c++) {
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
        if (valid) backtrack(pos + 1);
    }
    coloring[pos] = -1;
}

int main() {
    init();
    memset(coloring, -1, sizeof(coloring));
    result = 0;
    backtrack(0);
    printf("Backtracking result: %lld\n", result);
    return 0;
}
