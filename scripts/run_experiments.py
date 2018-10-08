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
A python script that reads and runs the experiments described in the JSON file
"""

import json
import sys
import itertools
from common import DataLog, ExperimentInfo

from run_sut_stress import SutStress


class Experiment(object):
    """A class used to run batch experiments
    Reads and runs the experiments described in the JSON file
    """
    _TEMP_FOLDER_PREFIX ="./temp_"

    def __init__(self):
        """
        Create an experiment object
        """
        self._experiment_info = None

        # The 2 possible ways of running
        self._mapping = None
        self._ranked_list = None

    def read_json_object(self, json_object):
        """
        Sets the experiment data based on the JSON object
        :param json_object: The JSON object
        """

        if "mapping" in json_object:
            self._mapping = json_object['mapping']
        elif "ranked_list" in json_object:
            self._ranked_list = json_object['ranked_list']
        else:
            raise ValueError("No stress or mapping given")

    def run(self, input_file, output_file):
        """
        Run the configured experiment
        :param input_file: The JSON file where the experiments are defined
        :param output_file: The JSON file where the experiment results are stored
        """

        # Read the configuration in the JSON file
        with open(input_file) as data_file:
            experiments_object = json.load(data_file)

        log = DataLog()

        for experiment in experiments_object:
            self._experiment_info = ExperimentInfo(experiment)
            self._experiment_info.read_json_object(experiments_object[experiment])
            self.read_json_object(experiments_object[experiment])

            log.experiment_info(self._experiment_info)

            if self._mapping:
                s = SutStress()

                result_baseline = s.run_mapping(self._experiment_info, mapping=dict())
                result_enemy = s.run_mapping(self._experiment_info, mapping=self._mapping)

                log.log_data_mapping(result_baseline, "baseline")
                log.log_data_mapping(result_enemy, "enemy")

                log.file_dump()

            elif self._ranked_list:
                s = SutStress()

                total_cores = self._experiment_info.cores
                c = [p for p in itertools.product(self._ranked_list, repeat=total_cores)]

                i = 0
                for conf in c:
                    conf_mapping = dict()
                    for core in range(1, total_cores + 1):
                        conf_mapping[core] = conf[core - 1]

                    result_enemy = s.run_mapping(self._experiment_info, mapping=conf_mapping)

                    config_name = "config_" + str(i)
                    i += 1
                    log.log_data_mapping(result_enemy, config_name)

                log.file_dump()

        log.merge_docs(output_file)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("usage: " + sys.argv[0] + " <experments_file>.json  <results>.json \n")
        exit(1)

    exp = Experiment()

    exp.run(sys.argv[1], sys.argv[2])
