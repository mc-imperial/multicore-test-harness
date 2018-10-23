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
from common import ProcessManagement, ExperimentInfo, get_event, get_temp, MappingResult
from scipy.stats.mstats import mquantiles
from scipy.stats import binom
from time import sleep


def confidence_variation(times, experiment_info):
    """
    Calculate the confidence interval
    :param times: The list of times for the calculation
    :param experiment_info: An experiment info object
    :return: confidence variation, lower confidence, upper confidence
    """

    assert isinstance(times, list)
    assert isinstance(experiment_info, ExperimentInfo)

    quantile = experiment_info.quantile
    desired_confidence = experiment_info.confidence_interval

    times.sort()
    q = mquantiles(times, quantile)[0]
    n = len(times)

    confidence = 0
    middle = round(quantile * (n+1))
    ui = middle
    li = middle
    while confidence < desired_confidence:
        if ui < n-1:
            ui = ui + 1
        if li > 0:
            li = li-1
        confidence = binom.cdf(ui-1, n, quantile) - binom.cdf(li-1, n, quantile)

        if ui >= n-1 and li <= 0:
            break

    if ui >= n-1:
        ui = n-1
    if li <= 0:
        li = 0

    lower_range = times[li]
    upper_range = times[ui]

    confidence_range = upper_range - lower_range

    return (confidence_range/q)*100, lower_range, upper_range


class SutStress:
    """
    A class used to run individual SUT tests
    Used to run an SUT together with enemy processes
    """
    # Profiling tools options for the SUT
    INSTRUMENT_CMDS = ["", "bash my_perf_script.sh", "bash my_perf.sh", "strace -c"]

    def __init__(self):
        """
        Create a stressed SUT object
        """
        self._processes = ProcessManagement()

    @staticmethod
    def _get_taskset_cmd(core):
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
        elif get_event(s_out, "time(ns)="):
            metric = get_event(s_out, "time(ns)=")

        else:
            print("Unable find execution time or maximum latency")
            sys.exit(0)

        return metric

    def run_mapping(self, experiment_info, mapping, iteration_name=None, style=0):
        """
        Run a mapping described by a mapping object
        :param experiment_info: An ExperimentInfo object
        :param mapping: A dict of core mappings
        :param iteration_name: For tning, we can store the exact param
        :param style: In case you need to run with perf
        :return:
        """

        assert isinstance(experiment_info, ExperimentInfo)

        # Make sure the governor is correctly
        cmd = "echo " + experiment_info.governor + \
              " | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor"
        self._processes.system_call(cmd)

        delta_temp = 5
        total_times = []
        total_temps = []

        # start from 95 and decrease to 50 by 1
        candidate_quantiles= [x / 100.0 for x in range(95, 49, -1)]

        if iteration_name is None:
            iteration_name = mapping
        result = MappingResult(iteration_name)

        while len(total_temps) < experiment_info.measurement_iterations_max:
            it = 0

            # start up the stress in accordance with the mapping
            for core in mapping:
                self.start_stress(mapping[core], core)

            while it < experiment_info.measurement_iterations_step:
                if self.cool_down(experiment_info.max_temperature - delta_temp, mapping):
                    for core in mapping:
                        self.start_stress(mapping[core], core)

                # Clear the cache first
                cmd = "sync; echo 1 > /proc/sys/vm/drop_caches"
                s_out, s_err = self._processes.system_call(cmd)
                self._check_error(s_err)

                # Run the program on core 0
                s_out,s_err = self.run_program_single(experiment_info.sut, 0, style)
                self._check_error(s_err)

                final_temp = get_temp()
                if final_temp < experiment_info.max_temperature:
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

            # This part runs if we have variable iterations based on confidence interval
            # and can stop early
            if experiment_info.stopping == "no_decrease" or experiment_info.stopping == "optimistic":
                (conf_var, conf_min, conf_max) = confidence_variation(total_times, experiment_info)
                print("The confidence variation is ", conf_var)
                if conf_var < experiment_info.max_confidence_variation:
                    result.times = total_times
                    result.temps = total_temps
                    result.stable_q = experiment_info.quantile
                    result.q_value = mquantiles(total_times, experiment_info.quantile)[0]
                    result.q_min = conf_min
                    result.q_max = conf_max
                    result.success = True
                    return result
            elif experiment_info.stopping == "pessimistic":
                for q in candidate_quantiles:
                    (conf_var, conf_min, conf_max) = confidence_variation(total_times, experiment_info)
                    if conf_var < experiment_info.max_confidence_variation:
                        result.times = total_times
                        result.temps = total_temps
                        result.stable_q = q
                        result.q_value = mquantiles(total_times, q)[0]
                        result.q_min = conf_min
                        result.q_max = conf_max
                        result.success = True
                        return result

        # At this point we know that we have hit max iterations
        if experiment_info.stopping == "optimistic":
            for q in candidate_quantiles:
                (conf_var, conf_min, conf_max) = confidence_variation(total_times, experiment_info)
                if conf_var < experiment_info.max_confidence_variation:
                    result.times = total_times
                    result.temps = total_temps
                    result.stable_q = q
                    result.q_value = mquantiles(total_times, q)[0]
                    result.q_min = conf_min
                    result.q_max = conf_max
                    result.success = True
                    return result

        # If we hit this and we did not intend to (not using "fixed"), we failed
        # to get a stable quantile basically
        (conf_var, conf_min, conf_max) = confidence_variation(total_times, experiment_info)
        result.times = total_times
        result.temps = total_temps
        result.stable_q = experiment_info.quantile
        result.q_value = mquantiles(total_times, experiment_info.quantile)[0]
        result.q_min = conf_min
        result.q_max = conf_max
        result.success = True if experiment_info.stopping == "fixed" else False
        return result

    def run_sut_stress(self, sut, stress, cores, style=0):
        """
        :param sut: System under stress
        :param stress: Enemy process
        :param cores: Number of cores to start the enemy on
        :param style: Run the SUT with perf or some similar instrument
        """
        # start up the stress on cores 1-cores+1
        if (cores > 0):
            for i in range(1, cores + 1):
                self.start_stress(stress, i)

        # Run the program on core 0
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
