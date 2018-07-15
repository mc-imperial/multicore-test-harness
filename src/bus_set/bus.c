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
  * @file mem_thrashing.c
  * @author Dan Iorga, Tyler Sorenson, Alastair Donaldson
  * @date 31 Oct 2017
  * @brief Keep the bus and memory busy, mostly the bus
  *
  * Keep the bus and memory cotroller bussy.
  * This mostly focuses on the bus. Data is copied from one area of the memory
  * to the other. To be sure that data is transfered MEM<->CPU<->MEM
  */

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>

#include "../common/common.h"

/** Wrap the code in a loop consisting of ITERATIONS iterations */
#define ITERATIONS      1

/** Helper defines for memory allocation */
#define MB              ((1) << 10) << 10

/** The total memory the it will try to allocate and thrash */
#define MEM_SIZE        50 * (MB)

/**
 @brief this main func
 @ return 0 on success
 */
int main ()
{
    long begin = 0, end = 0;
    int32_t *mem1;
    int32_t *mem2;

    srand(time(NULL));


    begin = get_current_time_us();

#ifdef INFINITE
    while(1)
    {
#else
    for(int i = 0; i < ITERATIONS; i++)
    {
#endif
        mem1 = (int32_t*) malloc(MEM_SIZE);
        DIE ( mem1 == NULL, "Unable to allocate memory\n");
        memset((int32_t *)mem1, rand(), MEM_SIZE);
        mem2 = (int32_t*) malloc(MEM_SIZE);
        DIE ( mem2 == NULL, "Unable to allocate memory\n");
        memset((int32_t *)mem2, rand(), MEM_SIZE);
        for (int32_t i; i < MEM_SIZE/sizeof(int32_t); i++) mem2[i] = mem1[i] + rand();
        free(mem1);
        free(mem2);
    }

    end = get_current_time_us();
    printf("total time(us): %ld\n", end - begin);

	return 0;
}
