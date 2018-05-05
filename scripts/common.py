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

import subprocess
import os
import signal
import re
import sys
import time


def get_event(data,field):
    """
    From data, Read the number in e field
    :param data: The output to process
    :param field: The field to search for
    :return: Int found in the field
    """
    # First try to find a float
    value = None

    data = str(data)

    data = re.sub(' +',' ',data)
    try:
        line = re.findall(re.escape(field) + "\d+\.\d+", data)[0]
        value = float(re.findall("\d+\.\d+", line)[0])
    except IndexError:
        # else try to find an int, solution could be more elegnat
        try:
            line = re.findall(re.escape(field) + "\d+", data)[-1]
            value = float(re.findall("\d+", line)[0])
        except IndexError:
            value = None

    return value


def get_temp():
    """
    Get the temperature
    :return: The system temperature
    """
    c = ProcessManagement()
    cmd = "cat /sys/class/thermal/thermal_zone0/temp"
    command_output = c.system_call(cmd, True)[0]
    try:
        temp = float(command_output) / 1000
    except ValueError:
        print("\n\tWARNING: Unable to find temperature for this system\n")
        return None
    return temp


def cool_down(temp_threshold=70):
    """
    If the temperature is above a certain threshold, this function will delay
    the next experiment until the chip has cooled down.
    :param temp_threshold: The maximum temperature allowed
    """
    temp = get_temp()
    if temp:
        while temp > temp_threshold:
            print("Temperature " + str(temp) + " is too high! Cooling down")
            time.sleep(5)
            temp = get_temp()
        print("Temperature " + str(temp) + " is ok. Running experiment")
    else:
        print("\n\tWARNING: Using default cooldown time of 30 s\n")
        time.sleep(30)


class ProcessManagement:
    """A class used to manage processes
    This class is designed to manage background classes and foreground processes
    and to be able to kill them efficiantly when necessary.
    """
    def __init__(self, sleep_startup=0.01, sleep_shutdown=0.01):
        """
        :param sleep_startup:  Delay between starting tasks
        :param sleep_shutdown: Delay between killing tasks
        """
        self._background_procs = []
        self._sleep_startup = sleep_startup
        self._sleep_shutdown = sleep_shutdown
        signal.signal(signal.SIGINT, self._signal_handler)

    def _signal_handler(self,signal, frame):
        """
        To prevent any backround processes from remaining in memory
        when Ctrl+C is pressed.
        """
        print('\n\nYou pressed Ctrl+C!')
        print("Cleaning background processes before exit")
        self.kill_stress()
        sys.exit(0)

    @staticmethod
    def system_call(command, silent=False):
        """
        Call a background system command and wait for it to terminate
        :param command: Shell command to run
        :param silent: Surpress verbose
        :return: Call output and error
        """
        if not silent:
            print("executing command: " + command)

        p = subprocess.Popen([command], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

        # return p.stdout.read(),p.stderr.read()
        return p.communicate()

    def system_call_background(self, command):
        """
        Call a background system command and leave it in the background
        :param command: Shell command to run
        """
        print("executing command: " + command + " in the background")
        self._background_procs.append(subprocess.Popen(command, shell = True, preexec_fn=os.setsid))
        time.sleep(self._sleep_startup)

    def kill_stress(self):
        """
        Kill all the background stress commands
        """
        print("killing stress")
        for b in self._background_procs:
            os.killpg(os.getpgid(b.pid), signal.SIGTERM)
            time.sleep(self._sleep_shutdown)

        self._background_procs = []
        time.sleep(self._sleep_shutdown)
