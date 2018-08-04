#include <stdio.h>
#include <stdlib.h>
#include <time.h>

static size_t MM = 32000;

void add(float * restrict a, float * restrict b, float * restrict c, size_t n){
    size_t i;
    for(i = 0; i < n; ++i) {
        c[i] = a[i] + b[i];
    }
}

int main() {
    float * restrict a, * restrict b, * restrict c;
    size_t i;
    clock_t start,end;
    float diffs;

    a = (float *) malloc(MM*sizeof(float));
    b = (float *) malloc(MM*sizeof(float));
    c = (float *) malloc(MM*sizeof(float));


    for(i = 0; i < MM; ++i){
        a[i] = 1.0/(float)(i+1);
        b[i] = a[i];
    }

    start = clock();
    add(a,b,c,MM);
    end = clock();
    diffs = (end - start)/(float)CLOCKS_PER_SEC;

    printf("time(ns)=%lf\n",diffs*1000000);

    free(a);
    free(b);
    free(c);
    return 0;
}
