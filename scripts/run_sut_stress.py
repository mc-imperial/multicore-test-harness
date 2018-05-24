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
Runs individual tests.
"""

import sys
from common import ProcessManagement, get_event, get_temp
from statistics import pstdev
from time import sleep


class SutStress:
    """A class used to run individual SUT tests
    Used to run an SUT together with enemy processes
    """
    ## Profiling tools options for the SUT
    INSTRUMENT_CMDS = ["", "bash my_perf_script.sh", "bash my_perf.sh", "strace -c"]

    def __init__(self):
        """
        Create a stressed SUT object
        """
        self._processes = ProcessManagement()

    def _get_taskset_cmd(self, core):
        """
        Start a command on a aspecific core
        :param core: Core to start on
        """
        return "taskset -c " + str(core) + " "

    def start_stress(self, stress, core):
        """
        Start an enemy process on a specific core
        :param stress: Enemy process
        :param core: Core to start on
        :return: Output and error
        """
        assert(core != 0)
        cmd = self._get_taskset_cmd(core) + " " + "./" + stress
        self._processes.system_call_background(cmd)

    def run_program_single(self, sut, core, style):
        """
        Start the SUT with perf to gather more info
        :param sut: System under stress
        :param core: Core to start on
        :param style: Run the SUT with perf or some simillar instrument
        :return: Output and error
        """
        cmd = self._get_taskset_cmd(core) + " " + "nice -20" + \
              self.INSTRUMENT_CMDS[style] + " " + "./" + sut
        s_out,s_err = self._processes.system_call(cmd)
        return s_out, s_err

    @staticmethod
    def _check_error(s_err):
        """
        If there are errors. print them and terminate
        :param s_err: The possible error message
        :return:
        """

        if s_err:
            print(s_err)
            sys.exit(1)

    def cool_down(self, temp_threshold=80, stress_present=False):
        """
        If the temperature is above a certain threshold, this function will delay
        the next experiment until the chip has cooled down.
        :param temp_threshold: The maximum temperature allowed
        :param stress_present: If true, we need to kill the stress before cooldown
        :return: If it was forced to kill stress
        """
        killed_stress = False
        temp = get_temp()
        if temp:
            while temp > temp_threshold:
                print("Temperature " + str(temp) + " is too high! Cooling down")
                if stress_present:
                    self._processes.kill_stress()
                    killed_stress = True
                sleep(10)
                temp = get_temp()
            print("Temperature " + str(temp) + " is ok. Running experiment")
        else:
            print("\n\tWARNING: Using default cooldown time of 30 s\n")
            sleep(30)

        return killed_stress

    @staticmethod
    def get_metric(s_out):
        """
        Get the time from the output string
        :param s_out: The string to be processed
        :return: The numerical metric
        """
        if get_event(s_out, "total time(us): "):
            metric = get_event(s_out, "total time(us): ")
        elif get_event(s_out, "Total time (secs): "):
            metric = get_event(s_out, "Total time (secs): ")
        elif get_event(s_out, "Max: "):
            metric = get_event(s_out, "Max: ")
        else:
            print("Unable find execution time or maximum latency")
            sys.exit(0)

        return metric

    def run_mapping(self, sut,  mapping, iterations=50, max_temperature=50, style=0, governor="powersave"):
        """
        :param sut: System under stress
        :param mapping: A mapping of enemies o cores
        :param max_temperature: If the temperature is above this, discard the result
        :param style: Run the SUT with perf or some similar instrument
        """

        # Make sure the governor is correctly
        cmd = "echo " + governor + " | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor"
        self._processes.system_call_background(cmd)


        delta_temp = 12
        total_times = []
        total_temps = []

        it = 0

        # start up the stress in accordance with the mapping
        for core in mapping:
            self.start_stress(mapping[core], core)

        while it < iterations:
            if self.cool_down(max_temperature - delta_temp, mapping):
                for core in mapping:
                    self.start_stress(mapping[core], core)

            # Clear the cache first
            cmd = "sync; echo 1 > /proc/sys/vm/drop_caches"
            s_out, s_err = self._processes.system_call(cmd)
            self._check_error(s_err)

            # Run the program on core 0

            s_out,s_err = self.run_program_single(sut, 0, style)
            self._check_error(s_err)

            final_temp = get_temp()
            if final_temp < max_temperature:
                total_times.append(self.get_metric(s_out))
                total_temps.append(final_temp)
                it = it + 1
            else:
                print("The final temperature was to high, redoing experiment")
                delta_temp += 5
                if delta_temp > 25:
                    print("The test heats up the processor more than 25 degrees, I o not know what to do")
                    exit(1)

        if len(mapping) > 0:
            self._processes.kill_stress()

        print(total_times)
        print("Standard deviation " + str(pstdev(total_times)))

        return total_times, total_temps

    def run_sut_stress(self, sut, stress, cores, style = 0):
        """
        :param sut: System under stress
        :param stress: Enemy process
        :param cores: Number of cores to start the enemy on
        :param style: Run the SUT with perf or some similar instrument
        """
        #start up the stress on cores 1-cores+1
        if (cores > 0):
            for i in range(1, cores + 1):
                self.start_stress(stress, i)


        #Run the program on core 0
        s_out,s_err = self.run_program_single(sut,0, style)
        self._check_error(s_err)

        if cores > 0:
            self._processes.kill_stress()

        if get_event(s_out, "total time(us): "):
            ex_time = get_event(s_out, "total time(us): ")
        elif get_event(s_out, "Total time (secs): "):
            ex_time = get_event(s_out, "Total time (secs): ")
        elif get_event(s_out, "Max: "):
            ex_time = get_event(s_out, "Max: ")
        else:
            print("Unable find execution time or maximum latency")
            sys.exit(0)

        ex_temp = get_temp()

        return ex_time, ex_temp


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("usage: sut_exe stress_exe num_stress_cores output_style(0 or 1)")
        exit(1)
    s = SutStress()
    ex_time, ex_temp = s.run_sut_stress(sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
    print("Execution time " + str(ex_time))
    print("Execution temperature " + str(ex_temp))
