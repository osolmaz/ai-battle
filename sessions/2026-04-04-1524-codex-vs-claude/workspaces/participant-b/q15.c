#include <stdio.h>
#include <string.h>

#define N 8
#define NUM_EDGES 28
#define NUM_TRIANGLES 56

int edges[NUM_EDGES][2];
int triangles[NUM_TRIANGLES][3]; // edge indices
int edge_tri[NUM_EDGES][10]; // triangle indices for each edge
int edge_tri_count[NUM_EDGES];

int coloring[NUM_EDGES];
int remaining[3]; // remaining edges of each color
int rainbow_count;
long long result;

int target[3] = {6, 9, 13};
int target_rainbow = 8;

void init() {
    int ei = 0;
    for (int i = 0; i < N; i++)
        for (int j = i+1; j < N; j++) {
            edges[ei][0] = i;
            edges[ei][1] = j;
            ei++;
        }
    
    // Build edge lookup
    int edge_idx[N][N];
    for (int i = 0; i < NUM_EDGES; i++) {
        edge_idx[edges[i][0]][edges[i][1]] = i;
        edge_idx[edges[i][1]][edges[i][0]] = i;
    }
    
    int ti = 0;
    memset(edge_tri_count, 0, sizeof(edge_tri_count));
    for (int a = 0; a < N; a++)
        for (int b = a+1; b < N; b++)
            for (int c = b+1; c < N; c++) {
                int e1 = edge_idx[a][b];
                int e2 = edge_idx[a][c];
                int e3 = edge_idx[b][c];
                triangles[ti][0] = e1;
                triangles[ti][1] = e2;
                triangles[ti][2] = e3;
                edge_tri[e1][edge_tri_count[e1]++] = ti;
                edge_tri[e2][edge_tri_count[e2]++] = ti;
                edge_tri[e3][edge_tri_count[e3]++] = ti;
                ti++;
            }
}

void backtrack(int pos) {
    if (pos == NUM_EDGES) {
        if (rainbow_count == target_rainbow)
            result++;
        return;
    }
    
    int edges_left = NUM_EDGES - pos;
    if (rainbow_count > target_rainbow) return;
    
    for (int color = 0; color < 3; color++) {
        if (remaining[color] <= 0) continue;
        if (remaining[color] > edges_left) continue;
        
        coloring[pos] = color;
        
        int valid = 1;
        int delta = 0;
        
        for (int ti = 0; ti < edge_tri_count[pos]; ti++) {
            int t = edge_tri[pos][ti];
            int e1 = triangles[t][0], e2 = triangles[t][1], e3 = triangles[t][2];
            int c1 = coloring[e1], c2 = coloring[e2], c3 = coloring[e3];
            if (c1 < 0 || c2 < 0 || c3 < 0) continue;
            if (c1 == c2 && c2 == c3) { valid = 0; break; }
            if (c1 != c2 && c2 != c3 && c1 != c3) delta++;
        }
        
        if (valid && rainbow_count + delta <= target_rainbow) {
            remaining[color]--;
            rainbow_count += delta;
            backtrack(pos + 1);
            remaining[color]++;
            rainbow_count -= delta;
        }
    }
    
    coloring[pos] = -1;
}

int main() {
    init();
    memset(coloring, -1, sizeof(coloring));
    remaining[0] = target[0];
    remaining[1] = target[1];
    remaining[2] = target[2];
    rainbow_count = 0;
    result = 0;
    
    backtrack(0);
    
    printf("Result: %lld\n", result);
    return 0;
}
