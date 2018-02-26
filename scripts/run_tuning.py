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

"""@package python_scripts
A python for tuning based on fuzzing and Bayesian Optimisation
"""

import json
import sys
import os

from bayes_opt import BayesianOptimization
from time import time
from random import randrange, uniform, choice

from run_sut_stress import SutStress
from common import cool_down


class ConfigurableEnemy(object):
    """
    Object that hold all information about a template
    """

    def __init__(self):
        """
        Initialise a template object with template file and template data
        """
        self._t_file = None
        self._d_file = None
        self._define_range = None

        self._core = None
        self._defines = None

    def set_core(self, core):
        """
        Set the core on which the enemy will run
        :param core: Core where the enemy will run
        :return:
        """

        self._core = core

    def get_core(self):
        """
        Return the core where the enemy will run on
        :return: Core where the enemy will run
        """

        return self._core

    def set_template(self, template_file, data_file):
        """
        Set the template C file and the JSON with the data ranges
        :param template_file: Template C file
        :param data_file: JSON file with data range
        :return:
        """

        self._t_file = template_file
        self._d_file = data_file

        self._read_range_data()

    def get_template(self):
        """
        :return: Get the enemy template file
        """

        return self._t_file

    def _read_range_data(self):
        """
        Read the template JSON data from the d_file and store in in defines
        :return:
        """

        # Read the configuration in the JSON file
        with open(self._d_file) as data_file:
            template_object = json.load(data_file)

        try:
            self._define_range = template_object["DEFINES"]
        except KeyError:
            print "Unable to find DEFINES in JSON"

    def set_defines(self, defines):
        """
        :param defines: Dictionary of instantiated defines
        :return:
        """
        # Make sure that the parameters are of the correct type
        # Workaround to force BO to generate init_points
        for key in defines:
            if self._define_range[key]["type"] == "int":
                self._defines[key] = int(defines[key])
            elif self._define_range[key]["type"] == "float":
                self._defines[key] = float(defines[key])
            else:
                print("Unknown data type for param " + str(key))
                sys.exit(1)

    def get_defines(self):
        """
        :return: A dict of defines
        """
        return self._defines

    def random_instantiate_defines(self):
        """
        Instantiate the template with random values
        :return:
        """
        self._defines = {}
        for param in self._define_range:
            min_val = self._define_range[param]["range"][0]
            max_val = self._define_range[param]["range"][1]
            if self._define_range[param]["type"] == "int":
                self._defines[param] = randrange(min_val, max_val)
            elif self._define_range[param]["type"] == "float":
                self._defines[param] = uniform(min_val, max_val)
            else:
                print("Unknown data type for param " + str(param))
                sys.exit(1)

    def create_bin(self, output_file):
        """
        :param output_file: The name of the file that will be outputted
        :return:
        """

        defines = ["-D" + d + "=" + str(self._defines[d]) for d in self._defines]
        cmd = "gcc -std=gnu11 -Wall -Wno-unused-variable " + " ".join(defines) + " " + self._t_file + " -lm" + " -o " + output_file
        print "Compiling:", cmd
        os.system(cmd)


class EnemyConfiguration(object):
    """Hold the configuration on how an attack should look like"""
    def_files = {"../templates/cache/template_cache_stress.c":
                 "../templates/cache/parameters.json",
                 "../templates/mem_thrashing/template_mem_thrashing.c":
                 "../templates/mem_thrashing/parameters.json",
                 "../templates/pipeline_stress/template_pipeline_stress.c":
                 "../templates/pipeline_stress/parameters.json",
                 "../templates/system_calls/template_system_calls.c":
                 "../templates/system_calls/parameters.json"}

    def __init__(self, enemy_cores):
        """
        If no template file and data file is provided we use all of them since every configuration is possible
        :param enemy_cores: The total number of enemy processes
        """
        self._enemy_cores = enemy_cores
        self._enemies = []
        self._enemy_files = []

        for i in range(self._enemy_cores):
            enemy = ConfigurableEnemy()
            enemy.set_core(i+1)
            self._enemies.append(enemy)

        # If this variable is true, the templates can not be changed
        self._fixed_template = False

    def set_all_defines(self, list_dict):
        """
        :param list_dict: List where each element is a dict with defines for each template
        :return:
        """

        assert len(list_dict) == len(self._enemies), "List of defs does not match list of enemies"

        for i in range(len(list_dict)):
            self._enemies[i].set_defines(list_dict[i])

    def get_all_defines(self):
        """
        :return: A dict that contains core and its corresponding defines
        """
        defines = {}
        for i in range(self._enemy_cores):
            defines[self._enemies[i].get_core()] = self._enemies[i].get_defines()

        return defines

    def set_all_templates(self, t_file, t_data_file):
        """
        Sets the templates to all enemies and sets the flag to not modify them
        :param t_file: The template file to be used on all enemy processes
        :param t_data_file: The template data file to be used on all enemy processes
        :return:
        """
        for i in range(self._enemy_cores):
            self._enemies[i].set_template(t_file, t_data_file)

        self._fixed_template = True

    def random_set_all_enemy_types(self):
        """
        Randomly set what type of enemy process you have
        :return:
        """
        for i in range(self._enemy_cores):
            template_file, json_file = choice(list(EnemyConfiguration.def_files.items()))
            self._enemies[i].set_template(template_file, json_file)

    def random_instantiate_all_defines(self):
        """
        Randomly instantiate the parameters of the enemy
        :return:
        """
        for i in range(self._enemy_cores):
            self._enemies[i].random_instantiate_defines()

    def random_set_all(self):
        """
        If the template type is not specified, set the template and defines
        If the template is set, just set the defines
        :return:
        """
        if self._fixed_template:
            self.random_instantiate_all_defines()
        else:
            self.random_set_all_enemy_types()
            self.random_instantiate_all_defines()

    def get_mapping(self):
        """
        Generated enemy files
        :return: A dict representing a mapping of enemy files to cores
        """
        enemy_mapping = dict()
        self._enemy_files = []

        for i in range(self._enemy_cores):
            filename = str(self._enemies[i].get_core()) + "_enemy.out"
            self._enemies[i].create_bin(filename)
            self._enemy_files.append(filename)
            enemy_mapping[self._enemies[i].get_core()] = filename

        return enemy_mapping

    def __del__(self):
        """
        Clean all generated files
        :return:
        """

        for enemy_file in self._enemy_files:
            cmd = "rm " + enemy_file
            print "Deleting:", cmd
            os.system(cmd)


class Tuning(object):
    """Run tuning based on fuzzing or Bayesian Optimisation
    Reads and runs the tuning described in the JSON file.
    """

    def __init__(self):
        """
        Create a tuning object
        """
        self._sut = None
        self._cores = None
        self._method = None
        self._kappa = None
        self._training_time = None
        self._max_temperature = None
        self._cooldown_time = None

        # Store the enemy config
        self._enemy_config = None

        self._log_file = None
        self._max_file = None

    def read_json_object(self, json_object):
        """
        Sets the tunning data based on JSON object
        :param json_object: The JSON Object
        :return:
        """

        try:
            self._sut = str(json_object["sut"])
        except KeyError:
            print "Unable to find sut in JSON"
            sys.exit(1)

        try:
            self._cores = int(json_object["cores"])
            self._enemy_config = EnemyConfiguration(self._cores)
        except KeyError:
            print "Unable to find cores in JSON"
            sys.exit(1)

        try:
            self._method = str(json_object["method"])
        except KeyError:
            print "Unable to find method in JSON"
            sys.exit(1)

        try:
            self._kappa = int(json_object["kappa"])
        except KeyError:
            print "Unable to find kappa in JSON"
            sys.exit(1)

        try:
            self._log_file = str(json_object["log_file"])
            # Delete the file contents
            open(self._log_file, 'w').close()
        except KeyError:
            print "Unable to find log_file in JSON"
            sys.exit(1)

        try:
            self._max_file = str(json_object["max_file"])
            # Delete the file contents
            open(self._max_file, 'w').close()
        except KeyError:
            print "Unable to find max_file in JSON"
            sys.exit(1)

        try:
            self._training_time = int(json_object["training_time"])
        except KeyError:
            print "Unable to find training_time in JSON"
            sys.exit(1)

        try:
            self._max_temperature = int(json_object["max_temperature"])
        except KeyError:
            print "Unable to find max_temperature in JSON"
            sys.exit(1)

        try:
            self._cooldown_time = unicode(json_object["cooldown_time"])
        except KeyError:
            print "Unable to find cooldown_time in JSON"
            sys.exit(1)

        try:
            template_data_file = str(json_object["template_data"])
            t_file = str(json_object["template_file"])
            self._enemy_config.set_all_templates(t_file, template_data_file)
        except KeyError:
            print "No template file specified, will tune with every known template"

    def run_experiment(self):
        """
        :param **kwargs: keyworded, variable-length argument list
        :return: Execution time (latency)
        """
        cool_down(self._max_temperature)

        mapping = self._enemy_config.get_mapping()
        s = SutStress()
        ex_time, ex_temp = s.run_mapping(self._sut, mapping)

        return ex_time

    def _write_log_header(self):
        """
        Write the log file header
        :return:
        """
        with open(self._log_file, 'w') as data_file:
            d = "Iterations\tTraining Time\tMax value found\t\tCurrent value\t\tParams\n"
            data_file.write(d)

    def _log_data(self, iterations, time, max_value, cur_value, conf):
        """
        Log the maximum time found after time to determine "convergence" speed
        :param iterations: Total number of iterations so far
        :param time: The time the record was made
        :param max_value: The maximum value detected so far
        :param cur_value: The value found with the current config
        :param config: The configuration used
        """
        with open(self._log_file, 'a') as data_file:
            d = str(iterations) + "\t\t" + str(time) + "\t\t" \
                + str(max_value) + "\t\t" + str(cur_value) + "\t\t" + conf + "\n"
            data_file.write(d)

    def bayesian_train(self):
        """
        Training using Baysian Optimisation
        :return:
        """
        init_pts = 5
        data_range = {}
        for d in self._defines:
            data_range[str(d)] = (self._defines[d]["range"][0], self._defines[d]["range"][1])
        bo = BayesianOptimization(self.run_experiment, data_range)

        t_start = time()
        t_end = time() + 60 * self._training_time

        bo.init(init_points=init_pts)
        iteration = init_pts  # I consider the init_points also as iterations, BO does not
        while time() < t_end:
            bo.maximize(n_iter=1, kappa=self._kappa)
            print bo.res['max']
            print bo.res['all']['values']
            self._log_data(iteration,
                           int(time() - t_start),
                           bo.res['max']['max_val'],
                           bo.res['all']['values'][iteration - init_pts],
                           bo.res['all']['params'][iteration - init_pts])
            iteration = iteration + 1

        f = open(self._max_file, 'w')
        f.write(str(bo.res['max']))
        f.close()

    def fuzz_train(self):
        """
        Training by fuzzing
        :return:
        """

        iteration = 0
        max_time = 0

        t_start = time()
        t_end = time() + 60 * self._training_time

        while time() < t_end:

            # def_param = self.random_instantiate_defines()
            self._enemy_config.random_set_all()
            ex_time = self.run_experiment()

            print "found time of " + str(ex_time)
            if ex_time > max_time:
                max_time = ex_time
            iteration = iteration + 1
            self._log_data(iteration,
                           int(time() - t_start),
                           max_time,
                           ex_time,
                           json.dumps(self._enemy_config.get_all_defines()))

        f = open(self._max_file, 'w')
        f.write("Max time " + str(max_time) + "\n" + json.dumps(self._enemy_config.get_all_defines()))
        f.close()

    def run(self, input_file):
        """
        Run the configured experiment
        :param input_file: The JSON file where the tuning are defined
        """

        # Read the configuration in the JSON file
        with open(input_file) as data_file:
            tuning_object = json.load(data_file)

        for tuning_session in tuning_object:
            self.read_json_object(tuning_object[tuning_session])

            self._write_log_header()
            if self._method == "fuzz":
                print "Training by fuzzing"
                self.fuzz_train()
            elif self._method == "bayesian":
                print "Training by Baysian Optimisation"
                self.bayesian_train()
            else:
                print "I do not know how to train that way"
                sys.exit(0)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "usage: " + sys.argv[0] + " <experments_file>.json\n"
        exit(1)

    tr = Tuning()

    tr.run(sys.argv[1])
