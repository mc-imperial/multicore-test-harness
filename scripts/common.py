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
import sys
import re
import time
import os
import json
import signal
from copy import deepcopy
from collections import Counter

from statistics import median
from math import sqrt
from scipy.special import erfcinv
from scipy.stats.mstats import mquantiles


class ExperimentInfo:
    """
    Class to store information about the tunning process
    """
    def __init__(self, experiment_name):
        """
        Create a TuningInfo object
        """

        self.experiment_name = experiment_name

        # General attributes
        self.sut = None
        self.instrument_cmd = ""
        self.cores = None
        self.quantile = 0.9
        self.measurement_iterations_step = 20
        self.measurement_iterations_max = 200
        self.max_confidence_variation = 5
        self.confidence_interval = 0.95
        self.max_temperature = 80
        self.stopping = "fixed"
        self.governor = "powersave"

        # Tuning info
        self.tuning_max_time = None
        self.tuning_max_iterations = None
        self.method = None

        # Store the enemy config
        self.enemy_config = None

        # Log and results
        self.max_file = None
        self.output_binary = None

    def get_dict(self):

        result = dict()

        result["sut"] = self.sut
        result["instrument_cmd"] = self.instrument_cmd
        result["cores"] = self.cores
        result["quantile"] = self.quantile
        result["measurement_iterations_step"] = self.measurement_iterations_step
        result["measurement_iterations_max"] = self.measurement_iterations_max
        result["max_confidence_variation"] = self.max_confidence_variation
        result["confidence_interval"] = self.confidence_interval
        result["max_temeperature"] = self.max_temperature
        result["stopping"] = self.stopping
        result["governor"] = self.governor

        result["tuning_max_time"] = self.tuning_max_time
        result["tuning_max_iterations"] = self.tuning_max_iterations
        result["method"] = self.method

        result["enemy_config"] = self.enemy_config

        result["max_file"] = self.max_file
        result["output_binary"] = self.output_binary

        return result

    def read_json_object(self, json_object):
        """
        Sets the tuning data based on JSON object
        :param json_object: The JSON Object
        :return:
        """

        # General attributes
        try:
            self.sut = str(json_object["sut"])
        except KeyError:
            print("Unable to find sut in JSON")
            sys.exit(1)

        try:
            self.instrument_cmd = str(json_object["instrument_cmd"])
        except KeyError:
            print("No instrumentation script in JSON so not using any")

        try:
            self.cores = int(json_object["cores"])
        except KeyError:
            print("Unable to find cores in JSON")
            sys.exit(1)

        try:
            self.quantile = float(json_object["quantile"])
            assert 0 < self.quantile < 1, "Quantile value is " + str(self.quantile)
        except KeyError:
            print("Unable to find quantile in JSON, going for default 0.9 ")

        try:
            self.measurement_iterations_step = int(json_object["measurement_iterations_step"])
        except KeyError:
            print("Unable to find measurement_iterations_step in JSON, going for"
                  " default of 20 ")

        try:
            self.measurement_iterations_max = int(json_object["measurement_iterations_max"])
        except KeyError:
            print("Unable to find measurement_iterations_max in JSON, going for"
                  "default of 200")

        try:
            self.max_confidence_variation = int(json_object["max_confidence_variation"])
        except KeyError:
            print("Unable to find max_confidence_variation in JSON, going for"
                  "default of 5")
        try:
            self.confidence_interval = float(json_object["confidence_interval"])
        except KeyError:
            print("Unable to find confidence_interval in JSON, going for"
                  "default of 0.95")

        try:
            self.max_temperature = int(json_object["max_temperature"])
        except KeyError:
            print("Unable to find temperature in JSON, going for"
                  "default of 80")

        try:
            self.stopping = str(json_object["stopping"])
        except KeyError:
            print("Unable to find stopping criteria in JSON, going for"
                  "default of fixed")

        try:
            self.governor = str(json_object["governor"])
        except KeyError:
            print("Unable to find governor in JSON, going for"
                  "default of powersave")

        # Tuning info
        try:
            self.tuning_max_time = int(json_object["tuning_max_time"])
        except KeyError:
            # This means this is not a tuning, maybe I can make it more elegant somehow
            pass

        try:
            self.tuning_max_iterations = int(json_object["tuning_max_iterations"])
        except KeyError:
            # This means this is not a tuning, maybe I can make it more elegant somehow
            pass

        try:
            self.method = str(json_object["method"])
        except KeyError:
            # This means this is not a tuning, maybe I can make it more elegant somehow
            pass

        # Log and results
        try:
            self.output_binary = str(json_object["output_binary"])
            if not os.path.exists(self.output_binary):
                os.makedirs(self.output_binary)
        except KeyError:
            # This means this is not a tuning, maybe I can make it more elegant somehow
            pass

        try:
            self.max_file = str(json_object["max_file"])
        except KeyError:
            # This means this is not a tuning, maybe I can make it more elegant somehow
            pass


class MappingResult:
    """
    Class used as a result after a run mapping
    """

    def __init__(self, mapping):
        """
        Create a MappingResult object
        :param mapping: A mapping dict
        """
        self.measurements = None                # List of times for the mapping
        self.perf = None                        # A dict of the output of perf
        self.no_outliers_measurements = None    # List of times with outliers removed
        self.temps = None                       # List of temperatures for the mapping
        self.stable_q = None                    # The quantile that was found stable
        self.q_value = None                     # The value of the quantile that was stable
        self.q_min = None                       # The minimum value in the confidence interval
        self.q_max = None                       # The maximum value in the confidence interval
        self.time = None                        # Time since the experiment started
        self.success = True                     # If the experiment was able to find a stable quantile
        self.mapping = mapping                  # The mapping of enemy processes

    def log_result(self, perf_results, total_times, total_temps, quantile, conf_min, conf_max, success):
        """
        Log the parameters of the result
        :param perf_results: A dict of all the params gathered by perf
        :param total_times: A list of the total execution time
        :param total_temps: All the temperatures of the measurement
        :param quantile: The quantile that was chosen for the results
        :param conf_min: The minimum value of the confidence interval
        :param conf_max: The maximum value of the confidence interval
        :param success: If we were are able successfully get a stable quantile
        :return:
        """
        sums = dict()
        for res in perf_results:
            sums = dict(Counter(sums) + Counter(res))
        means = {k: sums[k] / float(len(perf_results)) for k in sums}
        self.perf = means
        self.measurements = total_times
        self.no_outliers_measurements = remove_outliers(total_times)
        self.temps = total_temps
        self.stable_q = quantile
        self.q_value = mquantiles(self.no_outliers_measurements, quantile)[0]
        self.q_min = conf_min
        self.q_max = conf_max
        self.success = success

    def get_dict(self):
        """
        :return: A dict with all the stored values
        """
        result = dict()
        result["measurements"] = self.measurements
        result['perf'] = self.perf
        result["no_outliers_measurements"] = self.no_outliers_measurements
        result["temps"] = self.temps
        result["stable_q"] = self.stable_q
        result["q_value"] = self.q_value
        result["q_min"] = self.q_min
        result["q_max"] = self.q_max
        result["time"] = self.time
        result["success"] = self.success
        result["mapping"] = str(self.mapping)

        return result


def get_event(data,field):
    """
    From data, Read the number in e field
    :param data: The output to process
    :param field: The field to search for
    :return: Float(Int) found in the field
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


def remove_outliers(times, scale=3):
    """
    Remove elements more than scale scaled MAD from the median.
    :param times: The list of times to remove from
    :param scale: The order of magnitude (aggressivness)
    :return: The list without outliers
    """

    assert isinstance(times, list)
    median_value = median(times)

    c = -1 / (sqrt(2) * erfcinv(3 / 2))
    temp = [abs(x-median_value) for x in times]
    scaled_mad = c * median(temp)

    new_values = [x for x in times if median_value - scale * scaled_mad <= x <= median_value + scale * scaled_mad]

    return new_values


def get_perf_event(data, separator="      "):
    """
    From data, Read the numbers provided by perf
    :param data: The output to process
    :param separator: In perf, it is usally number+<separator>+descriptor>
    :return: A dict of all the values found by perf
    """

    data = str(data)
    result = dict()

    line = re.findall("\d+(?:,\d+)*" + separator + "(?:[^\s]+)", data)
    for counter in line:
        value = re.findall("\d+(?:,\d+)*", counter)[0]
        name = re.findall("\d+(?:,\d+)*" + separator + "([^\s]+)", counter)[0]
        result[name] = int(value.replace(',', ''))

    return result


def get_temp():
    """
    Get the temperature
    :return: The system temperature
    """
    c = ProcessManagement()

    # Try to get the time from multiple thermal zones
    cmd = "cat /sys/class/thermal/thermal_zone*/temp"
    command_output = c.system_call(cmd, True)[0].decode('ascii')

    try:
        temperatures = command_output.splitlines()
        # print("Got the following temperatures", str(command_output))
        # Check which of the values look realistic
        temperature = 0
        for temp in temperatures:
            if float(temp)>1000:
                value = float(temp) / 1000
            else:
                value = float(temp)
            # A realistic value would be between 20 (room temperature) and 100 (this is the usual limit in the BIOS)
            if 20 < value < 100:
                temperature = value
                break

        return temperature
    except ValueError:
        print("\n\tWARNING: Unable to find temperature for this system\n")
        return None


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
        self._background_procs.append(subprocess.Popen(command,
                                                       stdout=subprocess.PIPE,
                                                       shell=True,
                                                       preexec_fn=os.setsid))
        time.sleep(self._sleep_startup)

    def kill_stress(self):
        """
        Kill all the background stress commands
        """

        for p in self._background_procs:
            os.killpg(os.getpgid(p.pid), signal.SIGTERM)
            time.sleep(self._sleep_shutdown)

        self._background_procs = []

        # To make sure nothing is left, I suspect the previous step does not always work
        p = subprocess.Popen(['ps', '-A'], stdout=subprocess.PIPE)
        out, err = p.communicate()

        for line in out.splitlines():
            if b'_enemy' in line:
                pid = int(line.split(None, 1)[0])
                try:
                    os.kill(pid, signal.SIGKILL)
                except OSError:
                    pass

        time.sleep(self._sleep_shutdown)

    def __del__(self):
        """
        Cleanup for whatever is running in the background
        :return:
        """
        pass
        # self.kill_stress()


class DataLog:
    """
    A class used for storing and logging all data.
    """
    _TEMP_FOLDER_PREFIX = "./temp_"

    def __init__(self):
        """
        Init a data log object, create a folder for it
        """

        self._data = dict()
        self._experiment_name = None
        self._folder_name = self._TEMP_FOLDER_PREFIX + time.strftime("%H%M%S") + "/"

        # Create a folder for the temp files
        if not os.path.exists(self._folder_name):
            os.makedirs(self._folder_name)

    def experiment_info(self, experiment_info):
        """
        The experiment data that is copied from input
        :param experiment_info: A tuning info object
        """

        assert isinstance(experiment_info, ExperimentInfo)

        experiment_name = experiment_info.experiment_name
        self._experiment_name = experiment_name
        self._data[experiment_name] = experiment_info.get_dict()
        self._data[self._experiment_name]["it"] = dict()

    def __del__(self):
        """
        Remove temp files and temp dir
        """

        config_files = [f for f in os.listdir(self._folder_name) if os.path.isfile(os.path.join(self._folder_name, f))]

        for file in config_files:
            os.remove(self._folder_name + file)

        os.rmdir(self._folder_name)

    def log_data_mapping(self, mapping_result, iteration ="default"):
        """
        Logs the data produced by a run_mapping command, per iteration
        :param mapping_result: A MappingResult object
        :param iteration: Which iteration is this
        :return:
        """
        assert isinstance(mapping_result, MappingResult)

        self._data[self._experiment_name]["it"][str(iteration)] = mapping_result.get_dict()

    def file_dump(self):
        """
        Dump what you have stored in the data dict to a file
        :return:
        """

        config_out_file = self._folder_name + self._experiment_name + ".json"

        with open(config_out_file, 'w') as outfile:
            json.dump(self._data, outfile, indent=4)

        self._data.pop(self._experiment_name)

    def _merge_dict(self, dict1, dict2):
        """
        Recursively merge two dictionaries
        :param dict1: First dict to merge
        :param dict2: Second dict to merge
        :return: Merged dict
        """

        if isinstance(dict1, dict) and isinstance(dict2, dict):
            dict1_and_dict2 = set(dict1).intersection(dict2)
            every_key = set(dict1).union(dict2)
            return dict((k, self._merge_dict(dict1[k], dict2[k]) if k in dict1_and_dict2 else
            deepcopy(dict1[k] if k in dict1 else dict2[k])) for k in every_key)
        return deepcopy(dict2)

    def merge_docs(self, output_file):
        """
        Merge the separate output files in a single one
        :param output_file: The JSON file where the experiment results are stored
        """

        output = dict()
        config_files = [f for f in os.listdir(self._folder_name) if os.path.isfile(os.path.join(self._folder_name, f))]

        for file in config_files:
            with open(self._folder_name + file) as data_file:
                experiments_object = json.load(data_file)
                output = self._merge_dict(output, experiments_object)

        # Note to self, do not sort the keys, it will make the iterations strange
        with open(output_file, 'w') as outfile:
            json.dump(output, outfile, indent=4, sort_keys=False)
