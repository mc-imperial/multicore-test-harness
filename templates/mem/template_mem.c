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

		memset((void *)mem + offset, rand(), page_size);

	}


	return 0;
}
