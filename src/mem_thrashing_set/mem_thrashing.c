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
  * @brief Keep the bus and memory cotroller bussy
  *
  * Keep the bus and memory cotroller bussy
  * by writting random data to main memory.
  * The main advantage to this approach comapred to the
  * cache one is that you can not deactivate the main memory
  * like you would the cache.
  */

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>

#include "../common/common.h"

/** Wrap the code in a loop consisting of ITERATIONS iterations */
#define ITERATIONS      100000

/** Helper defines for memory allocation */
#define MB              ((1) << 10) << 10

/** The total memory the it will try to allocate and thrash */
#define MEM_SIZE        200 * (MB)

/**
 @brief this main func
 @ return 0 on success
 */
int main ()
{

    long begin = 0, end = 0;
    srand(time(NULL));

    int page_size = getpagesize();
    // total number of chunks you divide your memory in
    size_t chunks = MEM_SIZE / page_size;

    void *mem = malloc(MEM_SIZE);
    DIE ( mem == NULL, "Unable to allocate memory\n");

    begin = get_current_time_us();

#ifdef INFINITE
    while(1)
    {
#else
    for(int i = 0; i < ITERATIONS; i++)
    {
#endif
        // the chuck being threashed at the moment
        size_t chunk = rand() % chunks;
        size_t offset = chunk * page_size;
        void *location = (void *) mem + offset;

        /*
         * Write random data to a random memory location
         * We introduce randomness to avoid any compiler optimistation
         */
        void *check = memset(location, rand(), page_size);
        DIE ( check != location, "Failed to set memory ");

    }
    free(mem);

    end = get_current_time_us();
    printf("total time(us): %ld\n", end - begin);

	return 0;
}
