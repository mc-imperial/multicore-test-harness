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
STRESS_DIR = $(BIN_DIR)/pipeline_stress

CC = gcc
CFLAGS = -std=gnu11 -Wall
LDFLAGS =

all: full_pipeline_test buble_pipeline_test full_pipeline_stress buble_pipeline_stress

full_pipeline_test: pipeline.c create_folders
	$(CC) $(CFLAGS) -DFULL_PIPELINE pipeline.c $(LD_FLAGS) -o full_pipeline_test
	cp full_pipeline_test $(SUT_DIR)/

buble_pipeline_test: pipeline.c create_folders
	$(CC) $(CFLAGS) pipeline.c $(LD_FLAGS) -o buble_pipeline_test
	cp buble_pipeline_test $(SUT_DIR)/

full_pipeline_stress: pipeline.c create_folders
	$(CC) $(CFLAGS) -DINFINITE -DFULL_PIPELINE pipeline.c $(LD_FLAGS) -o full_pipeline_stress
	cp full_pipeline_stress $(STRESS_DIR)/

buble_pipeline_stress: pipeline.c create_folders
	$(CC) $(CFLAGS) -DINFINITE pipeline.c $(LD_FLAGS) -o buble_pipeline_stress
	cp buble_pipeline_stress $(STRESS_DIR)/

create_folders:
	mkdir -p $(BIN_DIR)
	mkdir -p $(SUT_DIR)
	mkdir -p $(STRESS_DIR)


.PHONY: clean
clean:
	rm -f *~ full_pipeline_test buble_pipeline_test full_pipeline_stress buble_pipeline_stress
	rm -f $(SUT_DIR)/*pipeline*
	rm -f $(STRESS_DIR)/*
