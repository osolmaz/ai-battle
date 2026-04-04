#include <stdio.h>
#include <string.h>

#define N 8
#define MAX_EDGES 28
#define TARGET 11

int edges[MAX_EDGES][2];
int num_edges;

int main() {
    num_edges = 0;
    for (int i = 0; i < N; i++)
        for (int j = i+1; j < N; j++) {
            edges[num_edges][0] = i;
            edges[num_edges][1] = j;
            num_edges++;
        }
    
    long long count = 0;
    int chosen[TARGET];
    for (int i = 0; i < TARGET; i++) chosen[i] = i;
    
    while (1) {
        int degree[N] = {0};
        for (int i = 0; i < TARGET; i++) {
            degree[edges[chosen[i]][0]]++;
            degree[edges[chosen[i]][1]]++;
        }
        
        int all_odd = 1;
        for (int v = 0; v < N; v++)
            if (degree[v] % 2 == 0) { all_odd = 0; break; }
        
        if (all_odd) {
            int adj[N]; memset(adj, 0, sizeof(adj));
            for (int i = 0; i < TARGET; i++) {
                adj[edges[chosen[i]][0]] |= (1 << edges[chosen[i]][1]);
                adj[edges[chosen[i]][1]] |= (1 << edges[chosen[i]][0]);
            }
            int visited = 1, queue = 1;
            while (queue) {
                int v = __builtin_ctz(queue);
                queue &= ~(1 << v);
                int nb = adj[v] & ~visited;
                visited |= nb; queue |= nb;
            }
            if (visited == (1 << N) - 1) count++;
        }
        
        int i = TARGET - 1;
        while (i >= 0 && chosen[i] == num_edges - TARGET + i) i--;
        if (i < 0) break;
        chosen[i]++;
        for (int j = i+1; j < TARGET; j++) chosen[j] = chosen[j-1] + 1;
    }
    
    printf("Connected graphs with %d edges, all odd degrees: %lld\n", TARGET, count);
    return 0;
}
