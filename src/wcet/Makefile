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

SRCS = $(filter-out driver.c, $(wildcard *.c))
PROGS = $(patsubst %.c,%,$(SRCS))
BIN_DIR=../../bin

all: $(PROGS)

%: %.c driver.c
	gcc $(CFLAGS) -D$@_app -o $@ driver.c
#	gcc $(CFLAGS) -D$@_app -DINFINITE -o $@_infinite driver.c
	cp $@ $(BIN_DIR)/sut/$@_wcet
#	cp $@_infinite $(BIN_DIR)/stress/$@_wcet

clean:
	rm -f $(PROGS)
	rm -f *_wcet
	rm -f $(BIN_DIR)/sut/*_wcet
#	rm -f $(BIN_DIR)/stress/*_wcet
#	rm -f *_infinite
	rm -f *~
