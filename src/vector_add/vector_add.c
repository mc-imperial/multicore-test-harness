#include <stdio.h>
#include <stdlib.h>
#include <time.h>

static size_t MM = 90000000;

void add(double * restrict a, double * restrict b, double * restrict c, size_t n){
    size_t i;
    for(i = 0; i < n; ++i) {
        c[i] = a[i] + b[i];
    }
}

int main() {
    double * restrict a, * restrict b, * restrict c;
    size_t i;
    clock_t start,end;
    double diffs;

    a = (double *) malloc(MM*sizeof(double));
    b = (double *) malloc(MM*sizeof(double));
    c = (double *) malloc(MM*sizeof(double));


    for(i = 0; i < MM; ++i){
        a[i] = 1.0/(double)(i+1);
        b[i] = a[i];
    }

    start = clock();
    add(a,b,c,MM);
    end = clock();
    diffs = (end - start)/(double)CLOCKS_PER_SEC;

    printf("time(ns)=%lf\n",diffs*1000000);

    free(a);
    free(b);
    free(c);
    return 0;
}
