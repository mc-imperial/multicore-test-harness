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
  * @file template_cache_stress.c
  * @author Dan Iorga, Tyler Sorenson, Alastair Donaldson
  * @date 1 Nov 2017
  * @brief A configurable template based on cache_stress
  * (found in src/cache_set)
  *
  * Parameters to randomise:
  *  MY_FACTOR
  *  CACHE_LINE
  *  ASSOCIATIVITY
  *  instructions: a value between 1-3
  *  1 - STORE
  *  2 - LOAD
  *  3 - NOOP

  */


#include "stdio.h"
#include "stdlib.h"

/** Load instruction */
#define MY_INSTR_LOAD(array, index, value) value += array[index]
/** Store instruction */
#define MY_INSTR_STORE(array, index, value) array[index] = value

/** 1st tunnable parameter */
#if INSTR1 == 1
#define INSTR1_V(array, index, svalue, lvalue) MY_INSTR_STORE(array, index, svalue)
#elif INSTR1 == 2
#define INSTR1_V(array, index, svalue, lvalue) MY_INSTR_LOAD(array, index, lvalue)
#else
#define INSTR1_V(array, index, svalue, lvalue)
#endif

/** 2nd tunnable parameter */
#if INSTR2 == 1
#define INSTR2_V(array, index, svalue, lvalue) MY_INSTR_STORE(array, index, svalue)
#elif INSTR2 == 2
#define INSTR2_V(array, index, svalue, lvalue) MY_INSTR_LOAD(array, index, lvalue)
#else
#define INSTR2_V(array, index, svalue, lvalue)
#endif

/** 3rd tunnable parameter */
#if INSTR3 == 1
#define INSTR3_V(array, index, svalue, lvalue) MY_INSTR_STORE(array, index, svalue)
#elif INSTR3 == 2
#define INSTR3_V(array, index, svalue, lvalue) MY_INSTR_LOAD(array, index, lvalue)
#else
#define INSTR3_V(array, index, svalue, lvalue)
#endif

/** 4th tunnable parameter */
#if INSTR4 == 1
#define INSTR4_V(array, index, svalue, lvalue) MY_INSTR_STORE(array, index, svalue)
#elif INSTR4 == 2
#define INSTR4_V(array, index, svalue, lvalue) MY_INSTR_LOAD(array, index, lvalue)
#else
#define INSTR4_V(array, index, svalue, lvalue)
#endif

/** 5th tunnable parameter */
#if INSTR5 == 1
#define INSTR5_V(array, index, svalue, lvalue) MY_INSTR_STORE(array, index, svalue)
#elif INSTR5 == 2
#define INSTR5_V(array, index, svalue, lvalue) MY_INSTR_LOAD(array, index, lvalue)
#else
#define INSTR5_V(array, index, svalue, lvalue)
#endif

/** Helper defines for memory allocation */
#define KB              ((1) << 10)

/** 6th tunnable parameter */
#define CACHE_SIZE KB * SIZE


/**
 @brief this main func
 @ return 0 on success
 */
int main() {


  volatile int * my_array_1 = (int *) malloc(CACHE_SIZE);
  register unsigned long total = 0;
  int max_elements = CACHE_SIZE/sizeof(int);

  while(1) {

    for (int i = 0; i < max_elements; i+=STRIDE) {
        INSTR1_V(my_array_1, i, i, total);
        INSTR2_V(my_array_1, i, i, total);
        INSTR3_V(my_array_1, i, i, total);
        INSTR4_V(my_array_1, i, i, total);
        INSTR5_V(my_array_1, i, i, total);
      }
    }

    // Just to make sure that no optimisation takes place
    if (total) array[0] = total;
    printf("Total is %d", total);



  free( (void *) my_array_1);

  return 0;
}
