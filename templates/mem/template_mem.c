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
	* @file template_mem_thrashing.c
	* @author Dan Iorga, Tyler Sorenson, Alastair Donaldson
	* @date 1 Nov 2017
	* @brief A configurable template based on mem_thrashing
	* (found in src/mem_thrashing)
	*
	* Parameters to randomise:
  *  SIZE_MB
  *  PAGE_SIZE_BYTES
	*/

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <time.h>

/** Helper defines for memory allocation */
#define MB              (((1) << 10) << 10)

/** The total memory the it will try to allocate and thrash */
#define MEM_SIZE        SIZE_MB * (MB)

/** memset standard */
#define MEMSET_NORMAL memset((void *)mem + offset, rand(), page_size)
/** memset half page */
#define MEMSET_HALF_PAGE memset((void *)mem + offset, rand(), page_size/2)
/** memset half offset */
#define MEMSET_HALF_OFFSET memset((void *)mem + offset/2, rand(), page_size/2)
/** memset half */
#define MEMSET_HALF memset((void *)mem + offset/2, rand(), page_size/2)

/** 1st tunnable parameter */
#if INSTR1 == 1
#define INSTR1_V MEMSET_NORMAL 
#elif INSTR1 == 2
#define INSTR1_V MEMSET_HALF_PAGE
#elif INSTR1 == 3
#define INSTR1_V MEMSET_HALF_OFFSET
#elif INSTR1 == 4
#define INSTR1_V MEMSET_HALF
#else
#define INSTR1_V
#endif


/** 2st tunnable parameter */
#if INSTR2 == 1
#define INSTR2_V MEMSET_NORMAL 
#elif INSTR2 == 2
#define INSTR2_V MEMSET_HALF_PAGE
#elif INSTR2 == 3
#define INSTR2_V MEMSET_HALF_OFFSET
#elif INSTR2 == 4
#define INSTR2_V MEMSET_HALF
#else
#define INSTR2_V
#endif

/** 3st tunnable parameter */
#if INSTR3 == 1
#define INSTR3_V MEMSET_NORMAL 
#elif INSTR3 == 2
#define INSTR3_V MEMSET_HALF_PAGE
#elif INSTR3 == 3
#define INSTR3_V MEMSET_HALF_OFFSET
#elif INSTR3 == 4
#define INSTR3_V MEMSET_HALF
#else
#define INSTR3_V
#endif


/** 4st tunnable parameter */
#if INSTR4 == 1
#define INSTR4_V MEMSET_NORMAL 
#elif INSTR4 == 2
#define INSTR4_V MEMSET_HALF_PAGE
#elif INSTR4 == 3
#define INSTR4_V MEMSET_HALF_OFFSET
#elif INSTR4 == 4
#define INSTR4_V MEMSET_HALF
#else
#define INSTR4_V
#endif

/** 5st tunnable parameter */
#if INSTR5 == 1
#define INSTR5_V MEMSET_NORMAL 
#elif INSTR5 == 2
#define INSTR5_V MEMSET_HALF_PAGE
#elif INSTR5 == 3
#define INSTR5_V MEMSET_HALF_OFFSET
#elif INSTR5 == 4
#define INSTR5_V MEMSET_HALF
#else
#define INSTR5_V
#endif

/**
 @brief this main func
 @ return 0 on success
 */
int main ()
{
	int page_size = PAGE_SIZE_BYTES;
	void *mem = malloc(MEM_SIZE);


	if (mem == NULL) {
		perror("Unable to allocate memory\n");
		exit(EXIT_FAILURE);
	}


	srand(time(NULL));

	while(1)
	{
		size_t chunks = MEM_SIZE / page_size;

		size_t chunk = rand() % chunks;
		size_t offset = chunk * page_size;

        INSTR1_V;
        INSTR2_V;
        INSTR3_V;
        INSTR4_V;
        INSTR5_V;


	}


	return 0;
}
