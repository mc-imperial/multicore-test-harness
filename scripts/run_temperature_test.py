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
A python script that plots the data from the JSON file
"""

import sys
import subprocess
import os
import signal
import sched, time

BACKGROUND_PROCS = []
SLEEP_AMOUNT_STARTUP = 1
LOG_FILE="rasp_temp.txt"

s = sched.scheduler(time.time, time.sleep)


def system_call(command, silent = False):
    if not silent:
        print("executing command: " + command)
    p = subprocess.Popen([command], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    return p.stdout.read(),p.stderr.read()


def system_call_background(command):
    global BACKGROUND_PROCS
    print("executing command: " + command + " in the background")
    BACKGROUND_PROCS.append(subprocess.Popen(command, shell = True, preexec_fn=os.setsid))
    time.sleep(SLEEP_AMOUNT_STARTUP)


def get_taskset_cmd(i):
    return "taskset -c " + str(i) + " "


def start_stress(stress, i):
    cmd = get_taskset_cmd(i) + " " + "./" + stress
    system_call_background(cmd)


def log_data(prev_temp):
    cmd = "vcgencmd measure_clock arm"
    freq_vcgen = system_call(cmd, True)[0]
    cmd = "cat /sys/class/thermal/thermal_zone*/temp"
    temp = system_call(cmd, True)[0]
    temp_increase = int(temp) - int(prev_temp)
    prev_temp = temp
    f = open(LOG_FILE, 'a')
    data = time.strftime("%H:%M:%S") + "\t" + freq_vcgen[14:-4] + "\t" + temp[:-1] + "\t" + str(prev_temp) +  "\n"
    f.write(data)
    f.close()

    # do your stuff
    s.enter(1, 1, log_data, (prev_temp,))


def run_raspberry_stress(stress, processors):

    #start up the stress on processors 0-processors
    if (processors > 0):
        for i in range(0, processors ):
            start_stress(stress, i)

    # Log file header
    f = open(LOG_FILE, 'w')
    data = "Experiment with " + stress + " stress, running on " + str(processors) + " processors" + "\n"
    f.write(data)
    data = "Time \t\tFreq[Hz]\tTemp['C]\tIncrease['C/s]\n"
    f.write(data)
    f.close()

    time.ctime()
    cmd = "cat /sys/class/thermal/thermal_zone*/temp"
    temp = system_call(cmd, True)[0]
    s.enter(1, 1, log_data, (temp,))
    s.run()


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("usage: stress_exe num_stress_cores governor")
        exit(1)

    # Set the governor
    cmd = "echo " + sys.argv[3] + \
        " > /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor "
    s_out,s_err = system_call(cmd)
    if s_out:
        print("stdout:" + s_out)
    if s_err:
        print("stderr:" + s_err)

    s_out, s_err = run_raspberry_stress(sys.argv[1], int(sys.argv[2]))
    if s_out:
        print("stdout:" + s_out)
    if s_err:
        print("stderr:" + s_err)
