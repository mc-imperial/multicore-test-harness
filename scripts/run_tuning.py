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
import math

from bayes_opt import BayesianOptimization
from time import time

from random import randrange, uniform, choice, random
from collections import OrderedDict
from copy import deepcopy


from run_sut_stress import SutStress
from common import cool_down


class ConfigurableEnemy:
    """
    Object that hold all information about an enemy
    """

    def __init__(self, template=None, data_file=None):
        """
        Initialise an enemy with template file and template data
        :param template: The C template file that contains the enemy process
        :param data_file: The JSON file containing the maximum data range for the template
        """
        self._t_file = template
        self._d_file = data_file

        self._read_range_data()

        self._define_range = None
        self._defines = dict()

    def __str__(self):
        """
        :return: Template name and defines
        """
        string = "Template: " + str(self._t_file)
        for key in self._defines:
            string += "\t" + str(key) + " " + str(self._defines[key])
        string += "\n"
        return string

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

    def get_defines_range(self):
        """
        Return the define dictionary, the way BO wants it
        :return: A dictionary with param as keyword and a tuple with (min,max)
        """
        data_range = {}
        for param in self._define_range:
            min_val = self._define_range[param]["range"][0]
            max_val = self._define_range[param]["range"][1]
            data_range[str(param)] = (min_val, max_val)

        return data_range

    def _read_range_data(self):
        """
        Read the template JSON data from the d_file and store in in defines
        :return:
        """

        if self._t_file is None:
            return

        # Read the configuration in the JSON file
        with open(self._d_file) as data_file:
            template_object = json.load(data_file)

        try:
            self._define_range = template_object["DEFINES"]
        except KeyError:
            print("Unable to find DEFINES in JSON")

    def set_defines(self, defines):
        """
        :return:
        """
        def_param = dict()

        # Make sure that the parameters are of the correct type
        # Workaround to force BO to generate int when needed
        for key in defines:
            if self._define_range[key]["type"] == "int":
                def_param[key] = int(defines[key])
            elif self._define_range[key]["type"] == "float":
                def_param[key] = float(defines[key])
            else:
                print("Unknown data type for param " + str(key) )
                sys.exit(1)

        self._defines = def_param

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

    def neighbour(self):
        """
        A generator for the neighbour defines
        """
        random_key = choice(list(self._defines))

        value = self._defines[random_key]
        min_val = self._define_range[random_key]["range"][0]
        max_val = self._define_range[random_key]["range"][1]

        if self._define_range[random_key]["type"] == "int":
            temp = deepcopy(self)
            temp._defines[random_key] = randrange(min_val, max_val)
            yield temp
        elif self._define_range[random_key]["type"] == "float":
            temp = deepcopy(self)
            temp._defines[random_key] = uniform(min_val, max_val)
            yield temp
        else:
            print("Unknown data type for param " + str(random_key))
            sys.exit(1)

    def create_bin(self, output_file):
        """
        :param output_file: The name of the file that will be outputted
        :return:
        """

        defines = ["-D" + d + "=" + str(self._defines[d]) for d in self._defines]
        cmd = "gcc -std=gnu11 -Wall -Wno-unused-variable " + " ".join(defines) + " " \
              + self._t_file + " -lm" + " -o " + output_file
        print("Compiling:", cmd)
        os.system(cmd)


class EnemyConfiguration:
    """
    Hold the configuration on how an attack should look like
    """

    def_files = OrderedDict([
                            ("../templates/cache/template_cache_stress.c",
                             "../templates/cache/parameters.json"),
                            ("../templates/mem_thrashing/template_mem_thrashing.c",
                             "../templates/mem_thrashing/parameters.json"),
                            ("../templates/pipeline_stress/template_pipeline_stress.c",
                             "../templates/pipeline_stress/parameters.json"),
                            ("../templates/system_calls/template_system_calls.c",
                             "../templates/system_calls/parameters.json")
                            ])

    def __init__(self, enemy_cores):
        """
        If no template file and data file is provided we use all of them since every configuration is possible
        :param enemy_cores: The total number of enemy processes
        """

        self.enemy_cores = enemy_cores
        self.enemies = []

        for i in range(self.enemy_cores):
            enemy = ConfigurableEnemy()
            self.enemies.append(enemy)

        # If this variable is true, the template across all enemies
        self._fixed_template = False
        # If this variable is true, all templates have the same parameters
        self._same_defines = False

    def __str__(self):
        """
        :return: The template and defines for each core
        """
        string = ""
        for enemy in self.enemies:
            string += str(enemy)

        string += "\n"
        return string

    def set_fixed_template(self, fix_template):
        """
        Set weather it is the same template across all enemies
        :param fix_template: Boolean variable
        :return:
        """
        self._fixed_template = fix_template

    def set_same_defines(self, same_defines):
        """
        Set weather all enemies have the same defines
        :param same_defines: Boolean variable
        :return:
        """
        self._same_defines = same_defines

    def neighbour_template(self):
        """
        A generator for the configs with different templates
        """
        for i in range(self.enemy_cores):
            template = self.enemies[i].get_template()
            for v in self.def_files.keys():
                if v != template:
                    self_copy = deepcopy(self)
                    self_copy.enemies[i].set_template(v, self.def_files[v])
                    self_copy.enemies[i].random_instantiate_defines()
                    yield self_copy

    def neighbour_define(self):
        """
        A generator for configs with different defines
        """
        while True:
            enemy = randrange(self.enemy_cores)
            for j in self.enemies[enemy].neighbour():
                temp = deepcopy(self)
                temp.enemies[enemy] = j
                yield temp

    def set_all_templates(self, t_file, t_data_file):
        """
        Sets the templates to all enemies and sets the flag to not modify them
        :param t_file: The template file to be used on all enemy processes
        :param t_data_file: The template data file to be used on all enemy processes
        :return:
        """
        for i in range(self.enemy_cores):
            self.enemies[i].set_template(t_file, t_data_file)

        self._fixed_template = True

    def random_set_all_templates(self):
        """
        Randomly set what type of enemy process you have
        :return: A dict of assigned templates
        """
        for i in range(self.enemy_cores):
            template_file, json_file = choice(list(EnemyConfiguration.def_files.items()))
            self.enemies[i].set_template(template_file, json_file)

        return self.get_all_templates()

    def random_set_all_defines(self):
        """
        Randomly instantiate the parameters of the enemy
        :return:
        """
        if self._same_defines:
            self.enemies[0].random_instantiate_defines()
            defines = self.enemies[0].get_defines()
            for i in range(1, self.enemy_cores):
                self.enemies[i].set_define(defines)
        else:
            for i in range(self.enemy_cores):
                self.enemies[i].random_instantiate_defines()

    def random_set_all(self):
        """
        If the template type is not specified, set the template and defines
        If the template is set, just set the defines
        :return: A tuple of the set templates and defines
        """
        if self._fixed_template:
            self.random_set_all_defines()
        else:
            self.random_set_all_templates()
            self.random_set_all_defines()

        return self

    def get_all_templates(self):
        """
        :return: A dict that contains core and its corresponding template
        """
        templates = {}
        for i in range(self.enemy_cores):
            templates[i] = self.enemies[i].get_template()

        return templates

    def get_all_defines(self):
        """
        :return: A dict that contains core and its corresponding defines
        """
        defines = {}
        for i in range(self.enemy_cores):
            defines[i] = self.enemies[i].get_defines()

        return defines

    def get_file_mapping(self):
        """
        Generated enemy files
        :return: A dict representing a mapping of enemy files to cores
        """
        enemy_mapping = dict()

        for i in range(self.enemy_cores):
            filename = str(i+1) + "_enemy.out"
            self.enemies[i].create_bin(filename)
            # Start mapping the enemies from core 1
            enemy_mapping[i + 1] = filename

        return enemy_mapping


class ObjectiveFunction:
    """
    Class to evaluate an enemy config
    """

    def __init__(self, sut, max_temperature=70):
        """
        :param sut: The system under test
        :param max_temperature: The maximum temperature before starting an evaluation
        """
        self._sut = sut
        self._max_temperature = max_temperature

        # Keep the created files for cleanup
        self._enemy_files = None

        # Keep track of the best evaluation
        self.best_mapping = None
        self.best_score = None

        # Stored mapping, workaround for BO
        self.stored_mapping = None
        self.optimized_core = None

    def bo_call(self, **kwargs):

        def_param = dict()
        for key in kwargs:
            def_param[key] = kwargs[key]

        self.stored_mapping.enemies[self.optimized_core] .set_defines(def_param)
        return self.__call__(self.stored_mapping)

    def __call__(self, enemy_config):
        """
        :param enemy_config: An EnemyConfiguration object
        :return: Execution time (latency)
        """
        cool_down(self._max_temperature)

        self._enemy_files = enemy_config.get_file_mapping()
        s = SutStress()
        ex_time, ex_temp = s.run_mapping(self._sut, self._enemy_files)

        if self.best_score is None or ex_time > self.best_score:
            self.best_score = ex_time
            self.best_mapping = enemy_config

        return ex_time

    def __del__(self):
        """
        Clean all generated files
        :return:
        """

        if self._enemy_files:
            for key in self._enemy_files:
                cmd = "rm " + self._enemy_files[key]
                print("Deleting:", cmd)
                os.system(cmd)


class Optimization:
    """
    Class for Optimization
    """

    def __init__(self, sut, log_file, max_temperature=70):
        """
        Create an Optimization object
        :param sut: The system under test
        :param max_temperature: The maximum temperature allowed before an experiment starts
        """

        self._sut = sut
        self._log_file = log_file
        self._write_log_header()
        self._max_temperature = max_temperature

        self._t_start = time()

    def _write_log_header(self):
        """
        Write the log file header
        :return:
        """
        with open(self._log_file, 'w') as data_file:
            d = "Iterations\tTraining Time\tMax value found\t\tCurrent value\t\tParams\n"
            data_file.write(d)

    def _log_data(self, iterations, tuning_time, max_value, cur_value, conf):
        """
        Log the maximum time found after time to determine "convergence" speed
        :param iterations: Total number of iterations so far
        :param tuning_time: The time the record was made
        :param max_value: The maximum value detected so far
        :param cur_value: The value found with the current config
        """
        with open(self._log_file, 'a') as data_file:
            d = str(iterations) + "\t\t" + str(tuning_time) + "\t\t" \
                + str(max_value) + "\t\t" + str(cur_value) + "\t\t" + conf + "\n"
            data_file.write(d)

    @staticmethod
    def kirkpatrick_cooling(start_temp, alpha):
        temp = start_temp
        while temp > 1:
            yield temp
            temp = alpha * temp

    @staticmethod
    def p_score(prev_score, next_score, temperature):
        if next_score > prev_score:
            return 1.0
        else:
            return math.exp(-abs(next_score - prev_score) / temperature)

    def inner_random(self, enemy_config, max_evaluations=100, max_time=30):

        objective_function = ObjectiveFunction(self._sut, self._max_temperature)

        num_evaluations = 1
        t_end = time() + 60 * max_time

        while num_evaluations < max_evaluations and time() < t_end:
            enemy_config.random_set_all_defines()
            next_inner_score = objective_function(enemy_config)
            num_evaluations += 1

            self._log_data(num_evaluations,
                           int(time() - self._t_start),
                           objective_function.best_score,
                           next_inner_score,
                           str(enemy_config))

        best_score = objective_function.best_score
        best_mapping = objective_function.best_mapping

        return best_score, best_mapping

    def inner_hill_climb(self, enemy_config, max_evaluations=100, max_time=30):

        objective_function = ObjectiveFunction(self._sut, self._max_temperature)

        current_inner_config = enemy_config
        current_inner_score = objective_function(enemy_config)

        num_evaluations = 1
        t_end = time() + 60 * max_time

        while num_evaluations < max_evaluations and time() < t_end:
            # examine moves around our current position
            for next_inner_config in current_inner_config.neighbour_define():
                if num_evaluations > max_evaluations:
                    break

                # see if this move is better than the current
                next_inner_score = objective_function(next_inner_config)
                num_evaluations += 1
                if next_inner_score > current_inner_score:
                    current_inner_config = next_inner_config
                    current_inner_score = next_inner_score
                    break  # depth first search

                self._log_data(num_evaluations,
                               int(time() - self._t_start),
                               objective_function.best_score,
                               next_inner_score,
                               str(next_inner_config))

        best_score = objective_function.best_score
        best_mapping = objective_function.best_mapping

        return best_score, best_mapping

    def inner_anneal(self, enemy_config, max_evaluations=100, inner_temp=50, inner_alpha=0.8):

        # wrap the objective function (so we record the best)
        objective_function = ObjectiveFunction(self._sut, self._max_temperature)

        # Initialise SA
        current_inner_config = enemy_config
        current_inner_score = objective_function(enemy_config)
        num_evaluations = 1

        inner_cooling_schedule = self.kirkpatrick_cooling(inner_temp, inner_alpha)

        for inner_temperature in inner_cooling_schedule:
            done = False

            for next_inner_config in current_inner_config.neighbour_define():

                if num_evaluations >= max_evaluations:
                    done = True
                    break

                next_inner_score = objective_function(next_inner_config)
                num_evaluations += 1

                # probabilistically accept this solution
                # always accepting better solutions
                p = self.p_score(current_inner_score, next_inner_score, inner_temperature)
                if random() < p:
                    current_inner_config = next_inner_config
                    current_inner_score = next_inner_score
                    break

                self._log_data(num_evaluations,
                               int(time() - self._t_start),
                               objective_function.best_score,
                               next_inner_score,
                               str(next_inner_config))

            # see if completely finished
            if done:
                break

        best_score = objective_function.best_score
        best_mapping = objective_function.best_mapping

        return best_score, best_mapping

    def inner_bo(self, enemy_config, max_evaluations=30, kappa_val=6):

        objective_function = ObjectiveFunction(self._sut, self._max_temperature)
        config = enemy_config

        # Devide the evaluations for each core
        init_pts = 5
        iterations = int(max_evaluations/config.enemy_cores - init_pts)

        init_pts = 5

        for core in range(config.enemy_cores):
            objective_function.optimized_core = core
            objective_function.stored_mapping = config
            data_range = config.enemies[core].get_defines_range()

            print(data_range)

            bo = BayesianOptimization(objective_function.bo_call, data_range)
            bo.init(init_points=init_pts)
            bo.maximize(n_iter=iterations, kappa=kappa_val)

            config.enemies[core].set_defines(bo.res['max']['max_params'])

        return config

    def outer_random(self, enemy_config, inner_tune,  max_evaluations=40, max_time=600):

        objective_function = ObjectiveFunction(self._sut, self._max_temperature)

        current_config = enemy_config
        current_score = objective_function(enemy_config) 

        num_evaluations = 1
        t_end = time() + 60 * max_time

        while num_evaluations < max_evaluations and time() < t_end:
            current_config.random_set_all_templates()

            # The inner tune part
            if inner_tune == "sa":
                score, config = self.inner_anneal(current_config)
            elif inner_tune == "ran":
                score, config = self.inner_random(current_config)
            elif inner_tune == "hc":
                score, config = self.inner_hill_climb(current_config)
            else:
                print("I do not know how to tune like that")

            objective_function(config)

        best_score = objective_function.best_score
        best_mapping = objective_function.best_mapping

        return best_score, best_mapping

    def outer_anneal(self, enemy_config, inner_tune, max_evaluations=40, outer_temp=20, outer_alpha=0.6):

        # wrap the objective function (so we record the best)
        objective_function = ObjectiveFunction(self._sut, self._max_temperature)

        # Initialise SA
        current_outer_config = enemy_config.random_set_all()
        current_outer_score = objective_function(enemy_config)
        num_evaluations = 1

        outer_cooling_schedule = self.kirkpatrick_cooling(outer_temp, outer_alpha)

        for outer_temperature in outer_cooling_schedule:
            done = False

            for next_outer_config in current_outer_config.neighbour_template():
                if num_evaluations >= max_evaluations:
                    done = True
                    break

                #The inner tune part
                if inner_tune == "sa":
                    next_outer_score, next_outer_config = self.inner_anneal(next_outer_config)
                elif inner_tune == "ran":
                    next_outer_score, next_outer_config = self.inner_random(next_outer_config)
                elif inner_tune == "hc":
                    next_outer_score, next_outer_config = self.inner_hill_climb(next_outer_config)
                elif inner_tune == "bo":
                    next_outer_config = self.inner_bo(next_outer_config)
                else:
                    print("I do not know how to tune like that")

                next_outer_score = objective_function(next_outer_config)

                num_evaluations += 1

                # probabilistically accept this solution
                # always accepting better solutions
                p = self.p_score(current_outer_score, next_outer_score, outer_temperature)
                if random() < p:
                    current_outer_config = next_outer_config
                    current_outer_score = next_outer_score
                    break
            # see if completely finished
            if done:
                break

        best_score = objective_function.best_score
        best_mapping = objective_function.best_mapping

        return best_score, best_mapping


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

        self._training_time = None
        self._max_temperature = None

        # Store the enemy config
        self._enemy_config = None

        self._log_file = None
        self._max_file = None

    def read_json_object(self, json_object):
        """
        Sets the tuning data based on JSON object
        :param json_object: The JSON Object
        :return:
        """

        try:
            self._sut = str(json_object["sut"])
        except KeyError:
            print("Unable to find sut in JSON")
            sys.exit(1)

        try:
            self._cores = int(json_object["cores"])
        except KeyError:
            print("Unable to find cores in JSON")
            sys.exit(1)

        try:
            self._method = str(json_object["method"])
        except KeyError:
            print("Unable to find method in JSON")
            sys.exit(1)

        try:
            self._log_file = str(json_object["log_file"])
            # Delete the file contents
            open(self._log_file, 'w').close()
        except KeyError:
            print("Unable to find log_file in JSON")
            sys.exit(1)

        try:
            self._max_file = str(json_object["max_file"])
            # Delete the file contents
            open(self._max_file, 'w').close()
        except KeyError:
            print("Unable to find max_file in JSON")
            sys.exit(1)

        try:
            self._training_time = int(json_object["training_time"])
        except KeyError:
            print("Unable to find training_time in JSON")
            sys.exit(1)

        try:
            self._max_temperature = int(json_object["max_temperature"])
        except KeyError:
            print("Unable to find max_temperature in JSON")
            sys.exit(1)

        self._enemy_config = EnemyConfiguration(self._cores)

    def sa_tune(self, inner_tune_method):
        """
        Tuning by simulated annealing on the outer loop
        :param inner_tune_method: Optimization method for the inner loop
        :return:
        """

        sa = Optimization(sut=self._sut, log_file=self._log_file)
        best_state, best_score = sa.outer_anneal(self._enemy_config, inner_tune=inner_tune_method)

        f = open(self._max_file, 'w')
        f.write("Max time " + str(best_score) + "\n" + str(best_state))
        f.close()

    def ran_tune(self, inner_tune_method):
        """
        Tuning by randomising on the outer loop
        :param inner_tune_method: Optimization method for the inner loop
        :return:
        """

        sa = Optimization(sut=self._sut, log_file=self._log_file)
        best_state, best_score = sa.outer_random(self._enemy_config, inner_tune=inner_tune_method)

        f = open(self._max_file, 'w')
        f.write("Max time " + str(best_score) + "\n" + str(best_state))
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

            if self._method == "sa_ran":
                print("Tuning by simulated annealing on the outer loop and random on the inner loop")
                self.sa_tune("ran")
            elif self._method == "sa_hc":
                print("Tuning by simulated annealing on the outer loop and hill climbing on the inner loop")
                self.sa_tune("hc")
            elif self._method == "sa_sa":
                print("Tuning by simulated annealing on the outer loop and simulated annealing on the inner loop")
                self.sa_tune("sa")
            elif self._method == "sa_bo":
                print("Tuning by simulated annealing on the outer loop and bayesian optimization on the inner loop")
                self.sa_tune("bo")
            elif self._method == "ran_ran":
                print("Tuning by randomising on the outer loop and random on the inner loop")
                self.ran_tune("ran")
            elif self._method == "ran_hc":
                print("Tuning by randomising on the outer loop and hill climbing on the inner loop")
                self.ran_tune("hc")
            elif self._method == "ran_sa":
                print("Tuning by randomising on the outer loop and simulated annealing on the inner loop")
                self.ran_tune("sa")
            else:
                print("I do not know how to train that way")
                sys.exit(0)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: " + sys.argv[0] + " <experments_file>.json\n")
        exit(1)

    tr = Tuning()

    tr.run(sys.argv[1])
