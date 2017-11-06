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
  * @file common.h
  * @author Dan Iorga, Tyler Sorenson, Alastair Donaldson
  * @date 1 Nov 2017
  * @brief Helper functions used throughout the code
  *
  * Helper functions used throughout the code
  */

#include <inttypes.h>
#include <stdio.h>
#include <time.h>

/** Helper defines for measuring time */
#define MICROSEC 1000000L

/** Macro used to asserts the exit code. If the exit code is diffeerent
 * than the expected one, it prints an error message and terminates execution
 */
#define DIE(assertion, call_description)    \
    do {                                    \
        if (assertion) {                    \
            fprintf(stderr, "(%s, %d): ",   \
                __FILE__, __LINE__);        \
            perror(call_description);       \
            exit(EXIT_FAILURE);             \
        }                                   \
    } while (0)

/**
 * @brief Gets the current time
 * Gets the current time in nonoseconds
 * *return The current time
 */
long get_current_time_us (void) {

  struct timespec spec;
  clock_gettime(CLOCK_REALTIME, &spec);
  return spec.tv_sec * MICROSEC + spec.tv_nsec / 1000;
}
