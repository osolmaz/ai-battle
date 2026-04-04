// Ask about counting specific graph colorings with multiple constraints
// that require careful backtracking.
//
// Q: How many edge-colorings of K_7 with 4 colors {R,G,B,Y} have:
// - No monochromatic triangle
// - Exactly 3 edges of each color (so 3+3+3+3 = 12... but K_7 has 21 edges)
//
// Hmm, 4*3 = 12 ≠ 21. Let me adjust.
// K_7: 21 edges. With 4 colors: e.g., 6+6+6+3 = 21. Or 5+5+5+6.
//
// Actually let me try a different question entirely.
// 
// How about: Count 4-colorings of K_6 edges with no monochromatic triangle
// and exactly 4 edges of each of the first 3 colors and 3 of the 4th?
// K_6: 15 edges. 4+4+4+3 = 15. ✓

#include <stdio.h>
#include <string.h>

#define N 6
#define NUM_EDGES 15
#define NUM_COLORS 4

int edges[NUM_EDGES][2];
int triangles[100][3]; // triangle edge indices
int num_triangles;
int edge_tri[NUM_EDGES][20];
int edge_tri_count[NUM_EDGES];
int coloring[NUM_EDGES];
int remaining[NUM_COLORS];
long long result;

void init() {
    int ei = 0;
    int edge_idx[N][N];
    for (int i = 0; i < N; i++)
        for (int j = i+1; j < N; j++) {
            edges[ei][0] = i;
            edges[ei][1] = j;
            edge_idx[i][j] = ei;
            edge_idx[j][i] = ei;
            ei++;
        }
    
    num_triangles = 0;
    memset(edge_tri_count, 0, sizeof(edge_tri_count));
    for (int a = 0; a < N; a++)
        for (int b = a+1; b < N; b++)
            for (int c = b+1; c < N; c++) {
                int t = num_triangles++;
                triangles[t][0] = edge_idx[a][b];
                triangles[t][1] = edge_idx[a][c];
                triangles[t][2] = edge_idx[b][c];
                edge_tri[triangles[t][0]][edge_tri_count[triangles[t][0]]++] = t;
                edge_tri[triangles[t][1]][edge_tri_count[triangles[t][1]]++] = t;
                edge_tri[triangles[t][2]][edge_tri_count[triangles[t][2]]++] = t;
            }
    printf("K_%d: %d edges, %d triangles\n", N, ei, num_triangles);
}

void backtrack(int pos) {
    if (pos == NUM_EDGES) {
        result++;
        return;
    }
    int edges_left = NUM_EDGES - pos;
    for (int color = 0; color < NUM_COLORS; color++) {
        if (remaining[color] <= 0) continue;
        if (remaining[color] > edges_left) continue;
        coloring[pos] = color;
        int valid = 1;
        for (int ti = 0; ti < edge_tri_count[pos]; ti++) {
            int t = edge_tri[pos][ti];
            int c1 = coloring[triangles[t][0]];
            int c2 = coloring[triangles[t][1]];
            int c3 = coloring[triangles[t][2]];
            if (c1 < 0 || c2 < 0 || c3 < 0) continue;
            if (c1 == c2 && c2 == c3) { valid = 0; break; }
        }
        if (valid) {
            remaining[color]--;
            backtrack(pos + 1);
            remaining[color]++;
        }
    }
    coloring[pos] = -1;
}

int main() {
    init();
    memset(coloring, -1, sizeof(coloring));
    
    // Try different edge count distributions
    // 4+4+4+3 = 15
    printf("\n4+4+4+3 distribution:\n");
    remaining[0] = 4; remaining[1] = 4; remaining[2] = 4; remaining[3] = 3;
    result = 0;
    backtrack(0);
    printf("Result: %lld\n", result);
    
    // 5+5+3+2 = 15
    printf("\n5+5+3+2 distribution:\n");
    remaining[0] = 5; remaining[1] = 5; remaining[2] = 3; remaining[3] = 2;
    result = 0;
    memset(coloring, -1, sizeof(coloring));
    backtrack(0);
    printf("Result: %lld\n", result);
    
    // 6+4+3+2 = 15
    printf("\n6+4+3+2 distribution:\n");
    remaining[0] = 6; remaining[1] = 4; remaining[2] = 3; remaining[3] = 2;
    result = 0;
    memset(coloring, -1, sizeof(coloring));
    backtrack(0);
    printf("Result: %lld\n", result);
    
    return 0;
}
