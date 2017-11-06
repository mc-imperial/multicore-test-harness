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

#include <inttypes.h>
#include <stdlib.h>

#include "../common/common.h"


#define main captured_main

#if defined(adpcm_app)
#include "adpcm.c"
#elif defined(bs_app)
#include "bs.c"
#elif defined(bsort100_app)
#include "bsort100.c"
#elif defined(cnt_app)
#include "cnt.c"
#elif defined(compress_app)
#include "compress.c"
#elif defined(cover_app)
#include "cover.c"
#elif defined(crc_app)
#include "crc.c"
#elif defined(duff_app)
#include "duff.c"
#elif defined(edn_app)
#include "edn.c"
#elif defined(expint_app)
#include "expint.c"
#elif defined(fac_app)
#include "fac.c"
#elif defined(fdct_app)
#include "fdct.c"
#elif defined(fft1_app)
#include "fft1.c"
#elif defined(fibcall_app)
#include "fibcall.c"
#elif defined(fir_app)
#include "fir.c"
#elif defined(insertsort_app)
#include "insertsort.c"
#elif defined(janne_complex_app)
#include "janne_complex.c"
#elif defined(jfdctint_app)
#include "jfdctint.c"
#elif defined(lcdnum_app)
#include "lcdnum.c"
#elif defined(lms_app)
#include "lms.c"
#elif defined(ludcmp_app)
#include "ludcmp.c"
#elif defined(matmult_app)
#include "matmult.c"
#elif defined(minver_app)
#include "minver.c"
#elif defined(ndes_app)
#include "ndes.c"
#elif defined(ns_app)
#include "ns.c"
#elif defined(nsichneu_app)
#include "nsichneu.c"
#elif defined(prime_app)
#include "prime.c"
#elif defined(qsort_exam_app)
#include "qsort_exam.c"
#elif defined(qurt_app)
#include "qurt.c"
#elif defined(select_app)
#include "select.c"
#elif defined(statemate_app)
#include "statemate.c"
#elif defined(ud_app)
#include "ud.c"
#else
#error "No wcep app defined!"
#endif

#undef main

int main(int argc, char *argv[]){
//  int iterations = 100000;
  int iterations = 1500;
  int i;
  long begin, end;
  if (argc > 1) {
    iterations = atoi(argv[1]);
  }

  begin = get_current_time_us();

#if defined(INFINITE)
  while(1) {
#else
  for (i = 0; i < iterations; i++) {
#endif
    captured_main();
  }

  end = get_current_time_us();

  printf("%d total-iterations\n", iterations);
  printf("total time(us): %ld\n", end - begin);

  return 0;
}
