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
  *  ARRAY_SIZE
  *  STRIDE
	*/

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>


/**
 @brief this main func
 @ return 0 on success
 */
int main ()
{
	long array[ARRAY_SIZE];
	long cnt, *p = array;

	for(cnt = 0; cnt < ARRAY_SIZE; cnt += STRIDE) {
		if (cnt < ARRAY_SIZE - STRIDE) {
			array[cnt] = (long)&array[cnt + STRIDE];
		}
		else {
			array[cnt] = (long)array;
		}
	}



	while(1)
	{
		p = (long *) *p;
	}


	return 0;
}
