/*******************************************************************************
 * Copyright (c) 2017 Dan Iorga, Tyler Sorenson, Alastair Donaldson

 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:

 * The above copyright notice and this permission notice shall be included in all
 * copies or substantial portions of the Software.

 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 *******************************************************************************/

 /**
  * @file cache_stress.c
  * @author Dan Iorga, Tyler Sorenson, Alastair Donaldson
  * @date 1 Nov 2017
  * @brief Run through the cache
  *
  * This test runs through a region of memory the size of the
  * L3 cache, striding at the size of a cache line (64 bytes)
  * Makes lots of accesses to the l3. Hopefully sensative to stress
  * on that cache
  */

#include <stdio.h>
#include <stdlib.h>

#include "../common/common.h"

/** Helper defines for cache allocation */
#define KB              ((1) << 10)

/** The size of the cache */
#define CACHE_SIZE      10 * SIZE * KB

/** Wrap the code in a loop consisting of ITERATIONS iterations */
#define ITERATIONS      500

/**
 @brief this main func
 @ return 0 on success
 */
int main() {

    register volatile int * my_array_1;
    register unsigned int sum = 0;
    long begin = 0;
    long end = 0;

    my_array_1 = (int *) malloc(CACHE_SIZE);
    DIE(my_array_1 == NULL, "Unable to allocate memory");

    for (int i = 0; i < CACHE_SIZE/sizeof(int); i++) my_array_1[i] = i;

    begin = get_current_time_us();

#ifdef INFINITE
    while(1) {
#else
    for (int it = 0; it < ITERATIONS; it++) {
#endif
        for (int i = 0; i < CACHE_SIZE/sizeof(int); i+=CACHE_LINE/4) {
                sum += my_array_1[i];
            }
    }
    

    end = get_current_time_us();

    printf("Sum: %u\n", sum);
    printf("total time(us): %ld\n", end - begin);

    free( (void *) my_array_1);
    return 0;
}
