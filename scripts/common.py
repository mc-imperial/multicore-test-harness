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
from copy import deepcopy


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
        self.cores = None
        self.quantile = 0.9
        self.measurement_iterations_step = 20
        self.measurement_iterations_max = 200
        self.max_confidence_variation = 5
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
            self.cores = int(json_object["cores"])
        except KeyError:
            print("Unable to find cores in JSON")
            sys.exit(1)

        try:
            self.quantile = int(json_object["quantile"])
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
        self.times = None
        self.temps = None
        self.stable_q = None
        self.q_value = None
        self.success = True
        self.mapping = mapping

    def get_dict(self):
        """
        :return: A dict with all the stored values
        """
        result = dict()
        result["times"] = self.times
        result["temps"] = self.temps
        result["stable_q"] = self.stable_q
        result["q_value"] = self.q_value
        result["success"] = self.success
        result["mapping"] = str(self.mapping)

        return result


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
        self._background_procs.append(subprocess.Popen(command, shell=True))
        time.sleep(self._sleep_startup)

    def kill_stress(self):
        """
        Kill all the background stress commands
        """

        print("killing stress ")
        for p in self._background_procs:
            p.terminate()
            time.sleep(self._sleep_shutdown)

        self._background_procs = []
        time.sleep(self._sleep_shutdown)


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
        self._data[experiment_name] = dict()

        self._data[experiment_name]["sut"] = \
            experiment_info.sut
        self._data[experiment_name]["cores"] = \
            experiment_info.cores
        self._data[experiment_name]["measurement_iterations_step"] = \
            experiment_info.measurement_iterations_step
        self._data[experiment_name]["measurement_iterations_max"] = \
            experiment_info.measurement_iterations_max
        self._data[experiment_name]["max_temperature"] = \
            experiment_info.max_temperature
        self._data[experiment_name]["quantile"] = \
            experiment_info.quantile
        self._data[experiment_name]["stopping"] = \
            experiment_info.stopping
        self._data[experiment_name]["governor"] = \
            experiment_info.governor
        self._data[experiment_name]["max_confidence_variation"] = \
            experiment_info.max_confidence_variation

    def cleanup(self):
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

        self._data[self._experiment_name][str(iteration)] = mapping_result.get_dict()

    def file_dump(self):
        """
        Dump what you have stored in the data dict to a file
        :return:
        """
        config_out_file = self._folder_name + self._experiment_name + ".json"

        with open(config_out_file, 'w') as outfile:
            json.dump(self._data, outfile, sort_keys=True, indent=4)

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

        with open(output_file, 'w') as outfile:
            json.dump(output, outfile, sort_keys=True, indent=4)
