#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <stdint.h>

#include "../../src/common/common.h"

#define CACHE_LINE_SIZE   (64)
#define PAD_CACHE_LINEPTR (CACHE_LINE_SIZE - sizeof(void *))

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
int benchmark_x86(struct line *ptr)
{

	register struct line *next asm("rdx");
	next = ptr->next;
  __asm__ __volatile__ (
  	"start_loop:"
    	"mov (%rdx), %rdx;"
      "jmp start_loop;"
  );

  // It should not get stuck here
	return (int) next;
}
#endif


/**
  * @brief Infinity pointer chasing for ARM
  * *return NULL
  */
	#ifdef __arm__
int benchmark_arm(struct line *ptr)
{

	register struct line *next asm("r3");
	next = ptr->next;
	asm volatile (
		"start_loop:;"
	    "ldr r3, [r3];"
			"b start_loop;"
			:
      :
      :"r3", "cc", "memory"
  );

    // It should not get stuck here
	return (int) next;
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
		if (j < (unsigned long) ELEMENTS - (unsigned long) STRIDE)
		{
			mem_chunk[j].next = &mem_chunk[j + (unsigned long) STRIDE];
		}
		else
		{
			mem_chunk[j].next = mem_chunk;
		}
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
