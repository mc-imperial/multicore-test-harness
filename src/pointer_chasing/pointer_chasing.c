#include <unistd.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <stdint.h>

#include "../common/common.h"


#define ELEMENTS					2097152LU
#define STRIDE						1000LU

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

#ifndef INFINITE
	register int i asm("ecx");
	i = 1000000;
#endif

	register struct line *next asm("rdx");
	next = ptr->next;
  __asm__ __volatile__ (
  	"start_loop:"
    	"mov (%rdx), %rdx;"
#ifdef INFINITE
      "jmp start_loop;"
#else
			"dec %ecx;"
			"jnz start_loop;"
#endif
  );

  // It should not get stuck here
	return 0;
}
#endif


/**
  * @brief Infinity pointer chasing for ARM
  * *return NULL
  */
	#ifdef __arm__
int benchmark_arm(struct line *ptr)
{
#ifndef INFINITE
	register int i asm("r4");
	i = 1000000;
#endif

	register struct line *next asm("r3");
	next = ptr->next;
	asm volatile (
		"start_loop:;"
	    "ldr r3, [r3];"
#ifdef INFINITE
			"b start_loop;"
#else
			"cmp r4, #0;"
			"ble done;"
			"sub r4, #1;"
			"done:;"
#endif
			:
      :
      :"r3", "r4", "cc", "memory"
  );

    // It should not get stuck here
	return 0;
}
#endif

/**
  * @brief Create the memory buffer and launch the corresponding benchmark
  * *return NULL
  */

int launch()
{
	long j;
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

		long begin = 0, end = 0;

    printf("We have %lu ELEMENTS\n", ELEMENTS);
    printf("The stride is %lu\n", STRIDE);
		begin = get_current_time_us();

    launch();

		end = get_current_time_us();
		printf("total time(us): %ld\n", end - begin);

    return(EXIT_SUCCESS);
}
