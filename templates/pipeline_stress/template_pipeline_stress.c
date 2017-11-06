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
	* @file template_pipeline_stress.c
	* @author Dan Iorga, Tyler Sorenson, Alastair Donaldson
	* @date 1 Nov 2017
	* @brief A configurable template based on pipeline
	* (found in src/pipeline_set)
	*
	* Parameters to randomise:
  * A0
  * A1
  * A2
  * A3
  * A4
  * A5
  * A6
  * A7
  * INSTR1
  * INSTR2
  * INSTR3
	*/


#include <stdio.h>
#include <math.h>
#include <stdlib.h>
#include <time.h>

/**
 * @brief Calculate sin with no stalls
 * This version of calculating sin is designed to keep the pipeline full by
 * having no data dependencies.
 * @param x The angle for which sin is calculated
 * *return Returns the sin of the angle
 */
double sin_full_pipeline(double x)
{
    return x * (A0)
         + x * x * x * (A1)
         + x * x * x * x * x * (A2)
         + x * x * x * x * x * x * x * (A3)
         + x * x * x * x * x * x * x * x * x * (A4)
         + x * x * x * x * x * x * x * x * x * x * x * (A5)
         + x * x * x * x * x * x * x * x * x * x * x * x * x * (A6)
         + x * x * x * x * x * x * x * x * x * x * x * x * x * x * x * (A7);
}

/**
  * @brief Calculate sin with stalls
  * This version of calculating sin is designed to have a lot of data
  * dependencies and therefore keep introduceing a lot of bubles/stalls
  * in the computation
  * @param x The angle for which sin is calculated
  * *return Returns the sin of the angle
  */
double sin_buble_pipeline(double x)
{
    long x2 = x * x;
    return x * ((A0) + x2 * ((A1) + x2 * ((A2) + x2 * ((A3) + x2 * ((A4) + x2 * ((A5) + x2 * ((A6) + x2 * (A7))))))));
}

/** Full pipeline polinomial calculation */
#define FULL_PIPELINE(x, res) res+= sin_full_pipeline(x)
/** Stall pipeline polinomial calculation */
#define BUBLE_PIPELINE(x,res) res+= sin_buble_pipeline(x)

/** 1st tunnable parameter */
#if INSTR1 == 1
#define INSTR1_V(x, res) FULL_PIPELINE(x, res)
#elif INSTR1 == 2
#define INSTR1_V(x, res) BUBLE_PIPELINE(x, res)
#else
#define INSTR1_V(x, res)
#endif

/** 2nd tunnable parameter */
#if INSTR2 == 1
#define INSTR2_V(x, res) FULL_PIPELINE(x, res)
#elif INSTR2 == 2
#define INSTR2_V(x, res) BUBLE_PIPELINE(x, res)
#else
#define INSTR2_V(x, res)
#endif

/** 3rd tunnable parameter */
#if INSTR3 == 1
#define INSTR3_V(x, res) FULL_PIPELINE(x, res)
#elif INSTR3 == 2
#define INSTR3_V(x, res) BUBLE_PIPELINE(x, res)
#else
#define INSTR3_V(x, res)
#endif

/**
 @brief this main func
 @ return 0 on success
 */
int main()
{
    srand(time(NULL));


    double sum = 0.0;

    while(1)
    {
        INSTR1_V(rand(), sum);
        INSTR2_V(rand(), sum);
        INSTR3_V(rand(), sum);

    }


    return 0;

}
