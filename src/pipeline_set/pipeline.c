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
  * @file pipeline.c
  * @author Dan Iorga, Tyler Sorenson, Alastair Donaldson
  * @date 31 Oct 2017
  * @brief A computational intensive process
  *
  * A computational intensive process that tries to heat up the processor
  * by giving it a lot to process.
  */

#include <stdio.h>
#include <stdlib.h>

#include "../common/common.h"

/** Wrap the code in a loop consisting of ITERATIONS iterations */
#define ITERATIONS       10000000

static double const a0 = +1.0;
static double const a1 = -1.666666666666580809419428987894207e-1;
static double const a2 = +8.333333333262716094425037738346873e-3;
static double const a3 = -1.984126982005911439283646346964929e-4;
static double const a4 = +2.755731607338689220657382272783309e-6;
static double const a5 = -2.505185130214293595900283001271652e-8;
static double const a6 = +1.604729591825977403374012010065495e-10;
static double const a7 = -7.364589573262279913270651228486670e-13;

/**
 * @brief Calculate sin with no stalls
 * This version of calculating sin is designed to keep the pipeline full by
 * having no data dependencies.
 * @param x The angle for which sin is calculated
 * *return Returns the sin of the angle
 */
double sin_full_pipeline(double x)
{
    return x * a0
         + x * x * x * a1
         + x * x * x * x * x * a2
         + x * x * x * x * x * x * x * a3
         + x * x * x * x * x * x * x * x * x * a4
         + x * x * x * x * x * x * x * x * x * x * x * a5
         + x * x * x * x * x * x * x * x * x * x * x * x * x * a6
         + x * x * x * x * x * x * x * x * x * x * x * x * x * x * x * a7;
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
    return x * (a0 + x2 * (a1 + x2 * (a2 + x2 * (a3 + x2 * (a4 + x2 * (a5 + x2 * (a6 + x2 * a7)))))));
}

/**
 @brief this main func
 @ return 0 on success
 */
int main()
{
    long begin = 0, end = 0;
    float x = 0;
    srand(time(NULL));

    begin = get_current_time_us();

    double sum = 0.0;
#ifdef INFINITE
    while(1)
    {
#else
    for (int i = 0; i < ITERATIONS; i++)
    {
#endif
#ifdef FULL_PIPELINE
        x = (float)rand()/(float)(RAND_MAX);
        sum += sin_full_pipeline(x);
#else
        sum += sin_buble_pipeline(x);
#endif
    }

    end = get_current_time_us();
    printf("total time(us): %ld\n", end - begin);

    return 0;

}
