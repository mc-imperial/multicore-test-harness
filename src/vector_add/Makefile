################################################################################
 # Copyright (c) 2017 Dan Iorga, Tyler Sorenson, Alastair Donaldson

 # Permission is hereby granted, free of charge, to any person obtaining a copy
 # of this software and associated documentation files (the "Software"), to deal
 # in the Software without restriction, including without limitation the rights
 # to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 # copies of the Software, and to permit persons to whom the Software is
 # furnished to do so, subject to the following conditions:

 # The above copyright notice and this permission notice shall be included in all
 # copies or substantial portions of the Software.

 # THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 # IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 # FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 # AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 # LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 # OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 # SOFTWARE.
################################################################################


BIN_DIR = ../../bin
SUT_DIR = $(BIN_DIR)/sut

CC = gcc
CFLAGS = -std=gnu11 -Wall -O3
LDFLAGS =

all: vector_add_test

vector_add_test: vector_add.c create_folders
	$(CC) $(CFLAGS) vector_add.c $(LD_FLAGS) -o vector_add_test
	cp vector_add_test $(SUT_DIR)/

create_folders:
	mkdir -p $(BIN_DIR)
	mkdir -p $(SUT_DIR)

.PHONY: clean
clean:
	rm -f *~ vector_add_test
	rm -f $(SUT_DIR)/vector_add_test
