#include <stdio.h>
#include <string.h>

#define N 8
#define NUM_EDGES 28
#define NUM_TRIANGLES 56

int edges[NUM_EDGES][2];
int triangles[NUM_TRIANGLES][3];
int edge_tri[NUM_EDGES][10];
int edge_tri_count[NUM_EDGES];
int coloring[NUM_EDGES];
int remaining[3];
int rainbow_count;
long long result_by_rainbow[60]; // count by number of rainbow triangles

int target[3] = {6, 9, 13};

void init() {
    int ei = 0;
    for (int i = 0; i < N; i++)
        for (int j = i+1; j < N; j++) {
            edges[ei][0] = i;
            edges[ei][1] = j;
            ei++;
        }
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
                int e1 = edge_idx[a][b], e2 = edge_idx[a][c], e3 = edge_idx[b][c];
                triangles[ti][0] = e1; triangles[ti][1] = e2; triangles[ti][2] = e3;
                edge_tri[e1][edge_tri_count[e1]++] = ti;
                edge_tri[e2][edge_tri_count[e2]++] = ti;
                edge_tri[e3][edge_tri_count[e3]++] = ti;
                ti++;
            }
}

void backtrack(int pos) {
    if (pos == NUM_EDGES) {
        result_by_rainbow[rainbow_count]++;
        return;
    }
    int edges_left = NUM_EDGES - pos;
    for (int color = 0; color < 3; color++) {
        if (remaining[color] <= 0) continue;
        if (remaining[color] > edges_left) continue;
        coloring[pos] = color;
        int valid = 1, delta = 0;
        for (int ti = 0; ti < edge_tri_count[pos]; ti++) {
            int t = edge_tri[pos][ti];
            int c1 = coloring[triangles[t][0]], c2 = coloring[triangles[t][1]], c3 = coloring[triangles[t][2]];
            if (c1 < 0 || c2 < 0 || c3 < 0) continue;
            if (c1 == c2 && c2 == c3) { valid = 0; break; }
            if (c1 != c2 && c2 != c3 && c1 != c3) delta++;
        }
        if (valid) {
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
    remaining[0] = 6; remaining[1] = 9; remaining[2] = 13;
    rainbow_count = 0;
    memset(result_by_rainbow, 0, sizeof(result_by_rainbow));
    backtrack(0);
    
    long long total = 0;
    for (int i = 0; i < 57; i++) {
        if (result_by_rainbow[i] > 0) {
            printf("Rainbow=%d: %lld\n", i, result_by_rainbow[i]);
            total += result_by_rainbow[i];
        }
    }
    printf("Total (no mono tri, 6R 9B 13G): %lld\n", total);
    printf("Rainbow=8: %lld\n", result_by_rainbow[8]);
    return 0;
}
