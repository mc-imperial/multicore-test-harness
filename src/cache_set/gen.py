################################################################################
 # Copyright (c) 2017 Dan Iorga, Tyler Sorenson, Alastair Donaldson

 # Permission is hereby granted, free of charge, to any person obtaining a copy
 # of this software and associated documentation files (the "Software"), to deal
 # in the Software without restriction, including without limitation the rights
 # to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 # copies of the Software, and to permit persons to whom the Software is
 # furnished to do so, subject to the following conditions:

 # The above copyright notice and this permission notice shall be included in all
 #copies or substantial portions of the Software.

 # THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 # IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 # FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 # AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 # LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 # OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 # SOFTWARE.
################################################################################

"""@package cache_generate
A simple script that reads cache JSON info and generates the cache litmus
test and enemy process.
"""

import os
import sys
import json

## Path to store the variables
PATH = "../../bin/"

## The "template" file to use to generatte the sut and enemy process
FILE = "cache_stress.c"

def create_folders():
    """
    Create all folders
    :return:
    """

    cmd = "mkdir -p " + PATH
    os.system(cmd)
    cmd = "mkdir -p " + PATH + "sut"
    os.system(cmd)
    cmd = "mkdir -p " + PATH + "cache_stress"
    os.system(cmd)


def instantiate_tests(file):
    """
    Generate suts and enemy based on json file
    :param file: JASON file describing cache conf
    :return:
    """
    with open(file) as data_file:
        caches_object = json.load(data_file)

    for cache in caches_object:
        print "Generating litmus, stress and stress sequance for " + cache
        inst={}
        inst.update(caches_object[cache])

        defines = ["-D" + d.upper()+ "=" + str(inst[d]) for d in inst]

        output = PATH + "sut/" + cache + "_test"
        print "\t output file " + output
        cmd = "gcc -std=gnu11 -Wall " + " ".join(defines) + " " + FILE + " -o " + output
        os.system(cmd)

        output = PATH + "cache_stress/" + cache + "_stress"
        print "\t output file " + output
        cmd = "gcc -std=gnu11 -Wall " + " ".join(defines) + " -DINFINITE"+ " " + FILE + " -o " + output
        os.system(cmd)


def make_all(file):
    """
    Create folders and generate
    :param file: ASON file describing cache conf
    :return:
    """

    create_folders()
    instantiate_tests(file)


def clean():
    """
    Clean all generated files
    :return:
    """

    cmd = "rm -f " + PATH + "sut/" + "*_litmus_test"
    print cmd
    os.system(cmd)
    cmd = "rm -f " + PATH + "cache_stress/" + "*_stress"
    print cmd
    os.system(cmd)
    cmd = "rm -f " + PATH + "cache_stress/" + "*_stress_sequence"
    print cmd
    os.system(cmd)


if __name__ == "__main__":
  if len(sys.argv) != 2:
    print "usage: " + sys.argv[0] + " cache_json_file\n"
    exit(1)

  create_folders()
  instantiate_tests(sys.argv[1])
