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
  * @file system_calls.c
  * @author Dan Iorga, Tyler Sorenson, Alastair Donaldson
  * @date 31 Oct 2017
  * @brief Generate software interrupts
  *
  * The main idea is to generate software interupts, which are
  * needed by system calls. By writting to random regions of the file
  * we avoid optiomisations
  * The following system calls are gnerated:
  * open, close, write, fstat, lseek
  */


#include <stdio.h>
#include <time.h>
#include <stdlib.h>
#include <math.h>

#include "../common/common.h"

/** Wrap the code in a loop consisting of ITERATIONS iterations */
#define ITERATIONS	10000


/**
 @brief this main func
 @ return 0 on success
 */
int main ()
{
    char file_name[25]="dummy.txt";
    FILE *fp;

    long begin = 0, end = 0;
    int ret;

    begin = get_current_time_us();

    srand(time(NULL));

#ifdef INFINITE
    while(1)
    {
#else
    for(int i=0; i < ITERATIONS; i++)
    {
#endif
        // Randomly generate position and char
		int offset = (int) sqrt(rand());
		char ch = (char) (rand() % 128);

        // Create and open the file
        fp = fopen(file_name,"w");
        DIE( fp == NULL, "Error while opening the file.\n");

        // Go to a random position
        ret = fseek(fp, offset, 0);
        DIE( ret != 0, "Unable to go to position");

        // Write a random char
        ret = fputc(ch, fp);
        DIE( ret != (int) ch, "Unable to write char");

        // Finally close
        ret = fclose(fp);
        DIE( ret !=0 , "Unable to close file");

        // Delete the file
        ret = remove(file_name);
        DIE( ret == 1, "Error while deleting file.\n");
	}

	end = get_current_time_us();
	printf("total time(us): %ld\n", end - begin);


	return 0;
}
