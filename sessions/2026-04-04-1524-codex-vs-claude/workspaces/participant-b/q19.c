// K_{5,5}: 25 edges, vertices A={0..4}, B={0..4}
// Edge (a,b) = index a*5+b
// 
// Constraint 1: No monochromatic C_4 (= no monochromatic K_{2,2})
// Constraint 2: Every vertex has degree pattern (3,1,1) in some color order
//   i.e., one color appears 3 times, the other two each appear once
//
// Approach: backtracking with both constraints checked incrementally.

#include <stdio.h>
#include <string.h>

#define NA 5
#define NB 5
#define NUM_EDGES 25

int quads[100][4];
int num_quads;
int edge_quads[NUM_EDGES][40];
int edge_quad_count[NUM_EDGES];

// For each vertex in A (row), track color counts
// A vertex a has edges a*5+0, a*5+1, ..., a*5+4
// For each vertex in B (col), track color counts  
// B vertex b has edges 0*5+b, 1*5+b, ..., 4*5+b

int coloring[NUM_EDGES];
int row_color_count[NA][3]; // row_color_count[a][c] = # edges of color c from vertex a
int col_color_count[NB][3]; // col_color_count[b][c] = # edges of color c to vertex b
int row_colored[NA]; // how many edges of row a are colored
int col_colored[NB]; // how many edges of col b are colored
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

// Check if the degree pattern (3,1,1) is still achievable for a vertex
// given current color counts and number of edges remaining
int check_vertex_feasible(int counts[3], int colored, int total) {
    int remaining = total - colored;
    if (remaining == 0) {
        // Must be exactly (3,1,1) pattern
        int has3 = 0, has1 = 0, has0 = 0;
        for (int c = 0; c < 3; c++) {
            if (counts[c] == 3) has3++;
            else if (counts[c] == 1) has1++;
            else if (counts[c] == 0) has0++;
            else return 0; // count is 2, 4, or 5 - invalid
        }
        return (has3 == 1 && has1 == 2);
    }
    
    // Check if (3,1,1) is still achievable
    // Total edges = 5. Pattern must be (3,1,1).
    // Current counts must be achievable: no color can exceed 3,
    // at most one color can reach 3, etc.
    for (int c = 0; c < 3; c++) {
        if (counts[c] > 3) return 0;
    }
    
    // More detailed check: can we distribute 'remaining' edges among 3 colors
    // to reach a (3,1,1) pattern?
    // We need exactly one color with count 3, two with count 1.
    // For each color c that could be the "3" color:
    for (int major = 0; major < 3; major++) {
        int needed_major = 3 - counts[major];
        if (needed_major < 0) continue;
        // The other two colors each need count 1
        int other_needed = 0;
        int feasible = 1;
        for (int c = 0; c < 3; c++) {
            if (c == major) continue;
            int need = 1 - counts[c];
            if (need < 0) { feasible = 0; break; }
            other_needed += need;
        }
        if (!feasible) continue;
        if (needed_major + other_needed == remaining) return 1;
    }
    return 0;
}

void backtrack(int pos) {
    if (pos == NUM_EDGES) {
        result++;
        return;
    }
    
    int a = pos / NB;
    int b = pos % NB;
    
    for (int c = 0; c < 3; c++) {
        coloring[pos] = c;
        row_color_count[a][c]++;
        col_color_count[b][c]++;
        row_colored[a]++;
        col_colored[b]++;
        
        // Check C_4 constraint
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
        
        // Check vertex degree pattern feasibility
        if (valid) {
            if (!check_vertex_feasible(row_color_count[a], row_colored[a], NB))
                valid = 0;
        }
        if (valid) {
            if (!check_vertex_feasible(col_color_count[b], col_colored[b], NA))
                valid = 0;
        }
        
        if (valid) {
            backtrack(pos + 1);
        }
        
        row_color_count[a][c]--;
        col_color_count[b][c]--;
        row_colored[a]--;
        col_colored[b]--;
    }
    
    coloring[pos] = -1;
}

int main() {
    init();
    memset(coloring, -1, sizeof(coloring));
    memset(row_color_count, 0, sizeof(row_color_count));
    memset(col_color_count, 0, sizeof(col_color_count));
    memset(row_colored, 0, sizeof(row_colored));
    memset(col_colored, 0, sizeof(col_colored));
    result = 0;
    
    printf("K_{5,5}: %d edges, %d K_{2,2} subgraphs\n", NUM_EDGES, num_quads);
    backtrack(0);
    printf("Result: %lld\n", result);
    
    return 0;
}
