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
STRESS_DIR = $(BIN_DIR)/pointer_chasing

CC = gcc
CFLAGS = -std=gnu11 
LDFLAGS =

all: pointer_chasing_stress pointer_chasing_test create_folders

pointer_chasing_test: pointer_chasing.c create_folders
	$(CC) $(CFLAGS) pointer_chasing.c $(LD_FLAGS) -o pointer_chasing_test
	cp pointer_chasing_test $(SUT_DIR)/

pointer_chasing_stress: pointer_chasing.c create_folders
	$(CC) $(CFLAGS) -DINFINITE pointer_chasing.c $(LD_FLAGS) -o pointer_chasing_stress
	cp pointer_chasing_stress $(STRESS_DIR)/

create_folders:
	mkdir -p $(BIN_DIR)
	mkdir -p $(SUT_DIR)
	mkdir -p $(STRESS_DIR)


.PHONY: clean
clean:
	rm -f *~ pointer_chasing_stress pointer_chasing_test
	rm -f $(SUT_DIR)/pointer_chasing*
	rm -f $(STRESS_DIR)/pointer_chasing*
