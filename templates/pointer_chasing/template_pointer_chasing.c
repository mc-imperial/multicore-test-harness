#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <stdint.h>

#include "../../src/common/common.h"

#define CACHE_LINE_SIZE   (64)
#define PAD_CACHE_LINEPTR (CACHE_LINE_SIZE - sizeof(void *))


#if defined(__i386__) || defined(__amd64__)
/** Load instruction x86 */
#define MY_INSTR_LOAD "mov (%rdx), %rdx;"
/** Store instruction x86*/
#define MY_INSTR_STORE "movl $10, 8(%rdx);"
/** Nop instruction x86*/
#define MY_INSTR_NOP "nop"
#elif __arm__
/** Load instruction ARM*/
#define MY_INSTR_LOAD "ldr r3, [r3];"
/** Store instruction ARM*/
#define MY_INSTR_STORE "str r2, [r3,8]
/** Store instruction ARM*/
#define MY_INSTR_NOP "nop"
#endif

/** 1st tunnable parameter */
#if INSTR1 == 1
#define INSTR1_V MY_INSTR_STORE
#elif INSTR1 == 2
#define INSTR1_V MY_INSTR_LOAD
#else
#define INSTR1_V MY_INSTR_NOP
#endif

/** 2nd tunnable parameter */
#if INSTR2 == 1
#define INSTR2_V MY_INSTR_STORE
#elif INSTR2 == 2
#define INSTR2_V MY_INSTR_LOAD
#else
#define INSTR2_V MY_INSTR_NOP
#endif

/** 3rd tunnable parameter */
#if INSTR3 == 1
#define INSTR3_V MY_INSTR_STORE
#elif INSTR3 == 2
#define INSTR3_V MY_INSTR_LOAD
#else
#define INSTR3_V MY_INSTR_NOP
#endif

/** 4th tunnable parameter */
#if INSTR4 == 1
#define INSTR4_V MY_INSTR_STORE
#elif INSTR4 == 2
#define INSTR4_V MY_INSTR_LOAD
#else
#define INSTR4_V MY_INSTR_NOP
#endif

/** 5th tunnable parameter */
#if INSTR5 == 1
#define INSTR5_V MY_INSTR_STORE
#elif INSTR5 == 2
#define INSTR5_V MY_INSTR_LOAD
#else
#define INSTR5_V MY_INSTR_NOP
#endif

struct line
{
	struct line *next;
	uint8_t pad[PAD_CACHE_LINEPTR];
} __attribute__((packed));


/**
  * @brief Infinity pointer chasing for x86
  * *return NULL
  */
#if defined(__i386__) || defined(__amd64__)
long benchmark_x86(struct line *ptr)
{

	register struct line *next asm("rdx");
	next = ptr->next;
  __asm__ __volatile__ (
  	"start_loop:"
    INSTR1_V
    INSTR2_V
    INSTR3_V
    INSTR4_V
    INSTR5_V
    "jmp start_loop;"
  );

  // It should not get stuck here
	return (long) next;
}
#endif


/**
  * @brief Infinity pointer chasing for ARM
  * *return NULL
  */
	#ifdef __arm__
long benchmark_arm(struct line *ptr)
{

	register struct line *next asm("r3");
	next = ptr->next;
	asm volatile (
	  "start_loop:;"
      INSTR1_V
      INSTR2_V
      INSTR3_V
      INSTR4_V
      INSTR5_V
	  "b start_loop;"
	  :
      :
      :"r2", "r3", "cc", "memory"
  );

    // It should not get stuck here
	return (long) next;
}
#endif

/**
  * @brief Create the memory buffer and launch the corresponding benchmark
  * *return NULL
  */

int launch()
{
	unsigned long j;
	struct line *mem_chunk;

	mem_chunk = (struct line *) calloc(ELEMENTS, sizeof(struct line));

	DIE ( mem_chunk == NULL, "Failed to allocate memory ");


  for ( j = 0 ; j < (unsigned long) ELEMENTS; j++ )
	{
		mem_chunk[j].next = &mem_chunk[(j + (unsigned long) STRIDE) % (unsigned long) ELEMENTS];
	}

	#if defined(__i386__) || defined(__amd64__)
		benchmark_x86(mem_chunk);
	#elif __arm__
		benchmark_arm(mem_chunk);
	#endif

	return(EXIT_SUCCESS);

}


int main(int argc, char *argv[]) {

    launch();

    return(EXIT_SUCCESS);
}
