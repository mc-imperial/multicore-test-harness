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
	* @file template_system_calls.c
	* @author Dan Iorga, Tyler Sorenson, Alastair Donaldson
	* @date 1 Nov 2017
	* @brief A configurable template based on system_calls
	* (found in src/syste_calls_set)
	*
	* Parameters to randomise:
  * INSTR1
  * INSTR2
  * INSTR3
	* INSTR4
	* INSTR5
	*/


#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#include <math.h>


/** SEEK */
#define MY_INSTR_SEEK(fp, value, filename) fseek(fp, (int) value, 0); value = sqrt(value)
/** READ */
#define MY_INSTR_READ(fp, value, filename) value = fgetc( fp ); value = sqrt(value)
/** WRITE */
#define MY_INSTR_WRITE(fp, value, filename) fputc( (char) value, fp); value = sqrt(value)
/** REOPEN */
#define MY_INSTR_REOPEN(fp, value, filename) fclose(fp); fp = fopen(filename, "w")

/** 1st tunnable parameter */
#if INSTR1 == 1
#define INSTR1_V(fp, value, filename) MY_INSTR_SEEK(fp, value, filename)
#elif INSTR1 == 2
#define INSTR1_V(fp, value, filename) MY_INSTR_READ(fp, value, filename)
#elif INSTR1 == 3
#define INSTR1_V(fp, value, filename) MY_INSTR_WRITE(fp, value, filename)
#elif INSTR1 == 4
#define INSTR1_V(fp, value, filename) MY_INSTR_REOPEN(fp, value, filename)
#else
#define INSTR1_V(fp, value, filename)
#endif

/** 2nd tunnable parameter */
#if INSTR2 == 1
#define INSTR2_V(fp, value, filename) MY_INSTR_SEEK(fp, value, filename)
#elif INSTR2 == 2
#define INSTR2_V(fp, value, filename) MY_INSTR_READ(fp, value, filename)
#elif INSTR2 == 3
#define INSTR2_V(fp, value, filename) MY_INSTR_WRITE(fp, value, filename)
#elif INSTR2 == 4
#define INSTR2_V(fp, value, filename) MY_INSTR_REOPEN(fp, value, filename)
#else
#define INSTR2_V(fp, value, filename)
#endif

/** 3rd tunnable parameter */
#if INSTR3 == 1
#define INSTR3_V(fp, value, filename) MY_INSTR_SEEK(fp, value, filename)
#elif INSTR3 == 2
#define INSTR3_V(fp, value, filename) MY_INSTR_READ(fp, value, filename)
#elif INSTR3 == 3
#define INSTR3_V(fp, value, filename) MY_INSTR_WRITE(fp, value, filename)
#elif INSTR3 == 4
#define INSTR3_V(fp, value, filename) MY_INSTR_REOPEN(fp, value, filename)
#else
#define INSTR3_V(fp, value, filename)
#endif

/** 4th tunnable parameter */
#if INSTR4 == 1
#define INSTR4_V(fp, value, filename) MY_INSTR_SEEK(fp, value, filename)
#elif INSTR4 == 2
#define INSTR4_V(fp, value, filename) MY_INSTR_READ(fp, value, filename)
#elif INSTR4 == 3
#define INSTR4_V(fp, value, filename) MY_INSTR_WRITE(fp, value, filename)
#elif INSTR4 == 4
#define INSTR4_V(fp, value, filename) MY_INSTR_REOPEN(fp, value, filename)
#else
#define INSTR4_V(fp, value, filename)
#endif

/** 5th tunnable parameter */
#if INSTR5 == 1
#define INSTR5_V(fp, value, filename) MY_INSTR_SEEK(fp, value, filename)
#elif INSTR5 == 2
#define INSTR5_V(fp, value, filename) MY_INSTR_READ(fp, value, filename)
#elif INSTR5 == 3
#define INSTR5_V(fp, value, filename) MY_INSTR_WRITE(fp, value, filename)
#elif INSTR5 == 4
#define INSTR5_V(fp, value, filename) MY_INSTR_REOPEN(fp, value, filename)
#else
#define INSTR5_V(fp, value, filename)
#endif

/**
 @brief this main func
 @ return 0 on success
 */
int main ()
{
	char file_name[25]="dummy.txt";
	FILE *fp;
	int value;

	srand(time(NULL));

	while(1)
	{
		fp = fopen(file_name,"w");
 		if( fp == NULL )
   	{
			perror("Error while opening the file.\n");
			exit(EXIT_FAILURE);
		}

		INSTR1_V(fp, value, file_name);
		INSTR2_V(fp, value, file_name);
		INSTR3_V(fp, value, file_name);
		INSTR4_V(fp, value, file_name);
		INSTR5_V(fp, value, file_name);

		fclose(fp);

		int ret = remove(file_name);
		if ( ret == 1)
		{
			perror("Error while deleting file.\n");
			exit(EXIT_FAILURE);
		}
	}

	return 0;
}
