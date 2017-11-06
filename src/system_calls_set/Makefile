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
CC = gcc
CFLAGS = -std=gnu11 -Wall
LDFLAGS = -lm

all: system_calls_test system_calls_stress simple create_folders

system_calls_test: system_calls.c create_folders
	$(CC) $(CFLAGS) system_calls.c $(LDFLAGS) -o system_calls_test
	cp system_calls_test $(BIN_DIR)/sut/

system_calls_stress: system_calls.c create_folders
	$(CC) $(CFLAGS) -DINFINITE system_calls.c $(LDFLAGS) -o system_calls_stress
	cp system_calls_stress $(BIN_DIR)/system_stress/

simple: simple.sh create_folders
	cp simple.sh $(BIN_DIR)/system_stress/

create_folders:
	mkdir -p $(BIN_DIR)
	mkdir -p $(BIN_DIR)/sut/
	mkdir -p $(BIN_DIR)/system_stress/

.PHONY: clean
clean:
	rm -f *~ system_calls_test system_calls_stress
	rm -f $(BIN_DIR)/sut/system_calls*
	rm -f $(BIN_DIR)/system_stress/system_calls*
