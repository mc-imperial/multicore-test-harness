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

"""@package python_scripts
A python script for throttling the Raspberry PI
"""

import sys
import subprocess
import os
import signal
import sched, time

BACKGROUND_PROCS = []
SLEEP_AMOUNT_STARTUP = 1
LOG_FILE="throttling.txt"

s = sched.scheduler(time.time, time.sleep)


def system_call(command, silent = False):
    if (silent  == False):
        print "executing command: " + command
    p = subprocess.Popen([command], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    return p.stdout.read(),p.stderr.read()

def system_call_background(command):
    global BACKGROUND_PROCS
    print "executing command: " + command + " in the background"
    BACKGROUND_PROCS.append(subprocess.Popen(command, shell = True, preexec_fn=os.setsid))
    time.sleep(SLEEP_AMOUNT_STARTUP)

def get_taskset_cmd(i):
    return "taskset -c " + str(i) + " "

def start_stress(stress, i):
    cmd = get_taskset_cmd(i) + " " + "./" + stress
    system_call_background(cmd)

def log_data(sc):
    cmd = "vcgencmd measure_temp"
    temp = system_call(cmd, True)[0]
    cmd = "vcgencmd measure_clock arm"
    freq_vcgen = system_call(cmd, True)[0]
    cmd = "cat /sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq"
    freq_cat = system_call(cmd, True)[0]
    cmd = "vcgencmd measure_volts core"
    volt = system_call(cmd, True)[0]
    f = open(LOG_FILE, 'a')
    data = time.strftime("%H:%M:%S") + "\t" + temp[5:-3] + "\t\t" + freq_vcgen[14:-4] + "\t\t" + freq_cat[:-1] + "\t\t" + volt[5:-2] + "\n"
    f.write(data)
    f.close()

    # do your stuff
    s.enter(10, 1, log_data, (sc,))

def run_raspberry_stress(stress, processors):

    #start up the stress on processors 0-processors
    if (processors > 0):
        for i in range(0, processors ):
            start_stress(stress, i)

    # Log file header
    f = open(LOG_FILE, 'w')
    data = "Time \t\tTemp['C]\tFreq[Hz]\tFreq OS[Hz]\tVoltage[V]\n"
    f.write(data)
    f.close()

    time.ctime()
    s.enter(1, 1, log_data, (s,))
    s.run()


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print "usage: stress_exe num_stress_cores governor"
        exit(1)

    # Set the governor
    cmd = "echo " + sys.argv[3] + \
        " > /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor "
    s_out,s_err = system_call(cmd)
    if s_out:
        print "stdout:" + s_out
    if s_err:
        print "stderr:" + s_err

    s_out, s_err = run_raspberry_stress(sys.argv[1], int(sys.argv[2]))
    if s_out:
        print "stdout:" + s_out
    if s_err:
        print "stderr:" + s_err
