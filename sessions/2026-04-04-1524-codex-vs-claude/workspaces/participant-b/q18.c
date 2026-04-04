// I need to ask a question I can verify but that's hard for Codex.
// Let me ask about counting specific structures that require careful computation.
//
// Q: How many 3-colorings of K_{5,5} edges have no monochromatic C_4
// and exactly 10 red, 8 blue, 7 green edges?
// 
// This requires careful backtracking on K_{5,5} with 25 edges.
// The edge counts are feasible (all ≤ z(5,5;2,2) for each color).

#include <stdio.h>
#include <string.h>

#define NA 5
#define NB 5
#define NUM_EDGES 25

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
    
    // Try several distributions
    int dists[][3] = {
        {10, 8, 7},
        {9, 9, 7},
        {9, 8, 8},
        {11, 7, 7},
        {12, 7, 6},
        {10, 10, 5},
    };
    
    for (int d = 0; d < 6; d++) {
        memset(coloring, -1, sizeof(coloring));
        remaining[0] = dists[d][0];
        remaining[1] = dists[d][1];
        remaining[2] = dists[d][2];
        result = 0;
        backtrack(0);
        printf("(%d,%d,%d): %lld\n", dists[d][0], dists[d][1], dists[d][2], result);
        fflush(stdout);
    }
    
    return 0;
}
