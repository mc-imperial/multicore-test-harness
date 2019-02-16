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
	* @file template_mem_bus.c
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
#include "../../src/common/common.h"

/** Helper defines for memory allocation */
#define MB              (((1) << 10) << 10)

/** The total memory the it will try to allocate and thrash */
#define MEM_SIZE        SIZE_MB * (MB)

/** 1st tunnable parameter */
#if SIZE == 1
#define SIZE_A uint8_t
#elif SIZE == 2
#define SIZE_A int8_t
#elif SIZE == 3
#define SIZE_A uint16_t
#elif SIZE == 4
#define SIZE_A int16_t
#elif SIZE == 5
#define SIZE_A uint32_t
#elif SIZE == 6
#define SIZE_A int32_t
#elif SIZE == 7
#define SIZE_A uint64_t
#elif SIZE == 8
#define SIZE_A int64_t
#endif

/** location 1 to location 2 */
#define MEM1_2_MEM2 for (SIZE_A i; i < MEM_SIZE/sizeof(SIZE_A); i++) mem2[i] = mem1[i]
/** location 2 to location 1 */
#define MEM2_2_MEM1 for (SIZE_A i; i < MEM_SIZE/sizeof(SIZE_A); i++) mem1[i] = mem2[i]
/** location 1 to CPU to location 1 */
#define MEM1_2_CPU_2_MEM1 for (SIZE_A i; i < MEM_SIZE/sizeof(SIZE_A); i++) mem1[i] = mem1[i] + rand()
/** location 1 to CPU to location 2 */
#define MEM1_2_CPU_2_MEM2 for (SIZE_A i; i < MEM_SIZE/sizeof(SIZE_A); i++) mem2[i] = mem1[i] + rand()
/** location 2 to CPU to location 1 */
#define MEM2_2_CPU_2_MEM1 for (SIZE_A i; i < MEM_SIZE/sizeof(SIZE_A); i++) mem1[i] = mem2[i] + rand()

/** 1st tunnable parameter */
#if INSTR1 == 1
#define INSTR1_V MEM1_2_MEM2
#elif INSTR1 == 2
#define INSTR1_V MEM2_2_MEM1
#elif INSTR1 == 3
#define INSTR1_V MEM1_2_CPU_2_MEM1
#elif INSTR1 == 4
#define INSTR1_V MEM1_2_CPU_2_MEM2
#elif INSTR1 == 5
#define INSTR1_V MEM2_2_CPU_2_MEM1
#else
#define INSTR1_V
#endif

/** 2nd tunnable parameter */
#if INSTR2 == 1
#define INSTR2_V MEM1_2_MEM2
#elif INSTR2 == 2
#define INSTR2_V MEM2_2_MEM1
#elif INSTR2 == 3
#define INSTR2_V MEM1_2_CPU_2_MEM1
#elif INSTR2 == 4
#define INSTR2_V MEM1_2_CPU_2_MEM2
#elif INSTR2 == 5
#define INSTR2_V MEM2_2_CPU_2_MEM1
#else
#define INSTR2_V
#endif

/** 3rd tunnable parameter */
#if INSTR3 == 1
#define INSTR3_V MEM1_2_MEM2
#elif INSTR3 == 2
#define INSTR3_V MEM2_2_MEM1
#elif INSTR3 == 3
#define INSTR3_V MEM1_2_CPU_2_MEM1
#elif INSTR3 == 4
#define INSTR3_V MEM1_2_CPU_2_MEM2
#elif INSTR3 == 5
#define INSTR3_V MEM2_2_CPU_2_MEM1
#else
#define INSTR3_V
#endif

/** 4th tunnable parameter */
#if INSTR4 == 1
#define INSTR4_V MEM1_2_MEM2
#elif INSTR4 == 2
#define INSTR4_V MEM2_2_MEM1
#elif INSTR4 == 3
#define INSTR4_V MEM1_2_CPU_2_MEM1
#elif INSTR4 == 4
#define INSTR4_V MEM1_2_CPU_2_MEM2
#elif INSTR4 == 5
#define INSTR4_V MEM2_2_CPU_2_MEM1
#else
#define INSTR4_V
#endif

/** 5th tunnable parameter */
#if INSTR5 == 1
#define INSTR5_V MEM1_2_MEM2
#elif INSTR5 == 2
#define INSTR5_V MEM2_2_MEM1
#elif INSTR5 == 3
#define INSTR5_V MEM1_2_CPU_2_MEM1
#elif INSTR5 == 4
#define INSTR1_V MEM1_2_CPU_2_MEM2
#elif INSTR5 == 5
#define INSTR5_V MEM2_2_CPU_2_MEM1
#else
#define INSTR5_V
#endif

/**
 @brief this main func
 @ return 0 on success
 */
int main ()
{
    volatile SIZE_A *mem1;
    volatile SIZE_A *mem2;

    srand(time(NULL));


	while(1)
	{
        mem1 = (SIZE_A*) malloc(MEM_SIZE);
        DIE ( mem1 == NULL, "Unable to allocate memory\n");
        memset((SIZE_A *)mem1, rand(), MEM_SIZE);
        mem2 = (SIZE_A*) malloc(MEM_SIZE);
        DIE ( mem2 == NULL, "Unable to allocate memory\n");
        memset((SIZE_A *)mem2, rand(), MEM_SIZE);
        INSTR1_V;
        INSTR2_V;
        INSTR3_V;
        INSTR4_V;
        INSTR5_V;
        free(mem1);
        free(mem2);
	}

	return 0;
}
