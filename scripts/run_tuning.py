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
import socket
import pickle

from time import time
from random import randrange, uniform, choice, random, shuffle, seed
from collections import OrderedDict
from copy import deepcopy

# optimization packages
from bayes_opt import BayesianOptimization
from simanneal import Annealer

# my packages
from run_sut_stress import SutStress
from common import ExperimentInfo, DataLog


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
        self.random_instantiate_defines()

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
                print("Unknown data type for param " + str(key))
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

        min_val = self._define_range[random_key]["range"][0]
        max_val = self._define_range[random_key]["range"][1]

        if self._define_range[random_key]["type"] == "int":
            temp = deepcopy(self)
            temp._defines[random_key] = randrange(min_val, max_val)
            return temp
        elif self._define_range[random_key]["type"] == "float":
            temp = deepcopy(self)
            temp._defines[random_key] = uniform(min_val, max_val)
            return temp
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
                            ("../templates/bus/template_bus.c",
                             "../templates/bus/parameters.json"),
                            ("../templates/cache/template_cache.c",
                             "../templates/cache/parameters.json"),
                            ("../templates/mem/template_mem.c",
                             "../templates/mem/parameters.json"),
                            ("../templates/pipeline/template_pipeline.c",
                             "../templates/pipeline/parameters.json")
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
        self.fixed_template = False
        # If this variable is true, all templates have the same parameters
        self.same_defines = False

        self.random_set_all()

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
        self.fixed_template = fix_template

    def set_same_defines(self, same_defines):
        """
        Set weather all enemies have the same defines
        :param same_defines: Boolean variable
        :return:
        """
        self.same_defines = same_defines
        if same_defines:
            defines = self.enemies[0].get_defines()
            for i in range(1, self.enemy_cores):
                self.enemies[i].set_defines(defines)

    def neighbour_template(self):
        """
        A generator for the configs with different templates
        """
        list_cores= list(range(self.enemy_cores))
        shuffle(list_cores)
        for core in list_cores:
            template = self.enemies[core].get_template()
            keyList = sorted(self.def_files.keys())

            for i, v in enumerate(keyList):
                if v == template:
                    self_copy = deepcopy(self)
                    index = (i+1) % len(self.def_files)
                    self_copy.enemies[core].set_template(keyList[index], self.def_files[keyList[index]])
                    self_copy.enemies[core].random_instantiate_defines()
                    yield self_copy

    def neighbour_define(self):
        """
        A generator for configs with different defines
        """
        if self.same_defines:
            temp = deepcopy(self)
            temp.enemies[0].neighbour()
            defines = temp.enemies[0].get_defines()
            for i in range(1, temp.enemy_cores):
                temp.enemies[i].set_defines(defines)
        else:
            enemy = randrange(self.enemy_cores)
            temp = deepcopy(self)
            temp.enemies[enemy] = self.enemies[enemy].neighbour()
        return temp

    def set_all_templates(self, t_file, t_data_file):
        """
        Sets the templates to all enemies and sets the flag to not modify them
        :param t_file: The template file to be used on all enemy processes
        :param t_data_file: The template data file to be used on all enemy processes
        :return:
        """
        for i in range(self.enemy_cores):
            self.enemies[i].set_template(t_file, t_data_file)

        self.fixed_template = True

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
        if self.same_defines:
            self.enemies[0].random_instantiate_defines()
            defines = self.enemies[0].get_defines()
            for i in range(1, self.enemy_cores):
                self.enemies[i].set_defines(defines)
        else:
            for i in range(self.enemy_cores):
                self.enemies[i].random_instantiate_defines()

    def random_set_all(self):
        """
        If the template type is not specified, set the template and defines
        If the template is set, just set the defines
        :return: A tuple of the set templates and defines
        """
        if self.fixed_template:
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

    def get_file_mapping(self, prefix="", output_folder=""):
        """
        Generated enemy files
        :param prefix: The prefix added to the filename
        :param output_folder: The output folder of the enemies
        :return: A dict representing a mapping of enemy files to cores
        """
        enemy_mapping = dict()

        for i in range(self.enemy_cores):
            filename = output_folder + prefix + str(i+1) + "_enemy"
            self.enemies[i].create_bin(filename)
            # Start mapping the enemies from core 1
            enemy_mapping[i + 1] = filename

        return enemy_mapping


class ObjectiveFunction:
    """
    Class to evaluate an enemy config
    """

    def __init__(self, experiment_info, log, socket_connect=None):
        """
        :param experiment_info: An experiment info object
        :param log: A data log object
        :param socket_connect: Socket if the network approach is desired
        """

        assert isinstance(experiment_info, ExperimentInfo)
        self._experiment_info = experiment_info

        assert isinstance(log, DataLog)
        self._log = log

        # Keep the created file names for cleanup
        self._enemy_mapping = None

        # Keep track of the best evaluation
        self.best_mapping = None
        self.best_score = None

        # Stored mapping, workaround for BO
        self.stored_mapping = None
        self.optimized_core = None

        # Logging information
        self.iteration = 0
        self._t_start = time()
        self._log.experiment_info(experiment_info)

        # Network connection
        self.socket = socket_connect

    def bo_call(self, **kwargs):
        """
        Wrapper for __call__ so that is compatible with BO
        :param kwargs: Parameters for the mapping
        :return:
        """

        def_param = dict()
        for key in kwargs:
            def_param[key] = kwargs[key]

        if self.stored_mapping.same_defines:
            for i in range(self.stored_mapping.enemy_cores):
                self.stored_mapping.enemies[i].set_defines(def_param)
        else:
            self.stored_mapping.enemies[self.optimized_core].set_defines(def_param)
        return self.__call__(self.stored_mapping)

    def __call__(self, enemy_config):
        """
        :param enemy_config: An EnemyConfiguration object
        :return: The quantile value
        """

        # if self.socket:
            # Dissable the networking thing for the moment
            # pickled_enemy_config = pickle.dumps(enemy_config)

            # Then send actual enemy config + delim
            # self.socket.sendall(pickled_enemy_config + b'data_end')

            # Receive the execution time
            # pickled_ex_time = self.socket.recv(1024)
            # times = pickle.loads(pickled_ex_time)
        # else:
        self._enemy_mapping = enemy_config.get_file_mapping()
        s = SutStress()

        result = s.run_mapping(experiment_info= self._experiment_info,
                               mapping=self._enemy_mapping,
                               iteration_name=str(enemy_config))
        if self.best_score is None or result.q_value > self.best_score:
            self.best_score = result.q_value
            self.best_mapping = enemy_config

        result.time = time() - self._t_start
        self._log.log_data_mapping(mapping_result=result, iteration=self.iteration)
        self.iteration += 1

        return result.q_value

    def __del__(self):
        """
        Clean all generated files
        :return:
        """

        if self._enemy_mapping:
            for key in self._enemy_mapping:
                cmd = "rm " + self._enemy_mapping[key]
                print("Deleting:", cmd)
                os.system(cmd)


class DefineAnneal(Annealer):
    """
    A wrapper class for the python annealer class
    """
    def __init__(self, experiment_info, initial_state, exit_time, log=None, network_socket=None):
        """
        :param experiment_info: ExperimentInfo object
        :param initial_state: EnemyConfig object
        :param exit_time: Exit time
        :param log: A log object
        :param network_socket: For future network connection
        """
        assert isinstance(experiment_info, ExperimentInfo)
        self._experiment_info = experiment_info
        assert isinstance(log, DataLog)
        self._experiment_info = experiment_info

        assert isinstance(initial_state, EnemyConfiguration)
        Annealer.__init__(self, initial_state)
        self.steps = experiment_info.tuning_max_iterations

        self.objective_function = ObjectiveFunction(experiment_info=experiment_info,
                                                    log=log,
                                                    socket_connect=network_socket)
        self._exit_time = exit_time

    def move(self):
        self.state = self.state.neighbour_define()

    def energy(self):

        q_value = self.objective_function(self.state)
        score = 1/q_value
        if time() > self._exit_time:
            self.user_exit = True

        return score


class Optimization:
    """
    Class for Optimization
    """

    def __init__(self, experiment_info, log, network_socket=None):
        """
        Create an Optimization object
        :param experiment_info: ExperimentInfo object
        :param log: A data log object
        :param network_socket: In case we want to go for networking
        """

        assert isinstance(experiment_info, ExperimentInfo)
        self._experiment_info = experiment_info

        assert isinstance(log, DataLog)
        self._log = log

        self._t_start = time()
        self._t_end = time() + 60 * experiment_info.tuning_max_time

        self._socket = network_socket

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

    def inner_random(self, enemy_config):
        """
        Use RAN to determine the best configuration, given the template
        :param enemy_config: An enemy mapping object
        :return: Best mapping and its corresponding result
        """

        assert isinstance(enemy_config, EnemyConfiguration)

        objective_function = ObjectiveFunction(experiment_info=self._experiment_info,
                                               log=self._log,
                                               socket_connect=self._socket)

        while objective_function.iteration < self._experiment_info.tuning_max_time and \
                time() < self._t_end:
            enemy_config.random_set_all_defines()
            objective_function(enemy_config)

        best_mapping = objective_function.best_mapping
        best_score = objective_function.best_score

        return best_mapping, best_score

    def inner_hill_climb(self, enemy_config):
        """
        Use HC to determine the best configuration, given the template
        :param enemy_config: An enemy mapping object
        :return: Best mapping and its corresponding result
        """

        assert isinstance(enemy_config, EnemyConfiguration)

        objective_function = ObjectiveFunction(experiment_info=self._experiment_info,
                                               log=self._log,
                                               socket_connect=self._socket)

        current_config = enemy_config
        current_score = 0

        while objective_function.iteration < self._experiment_info.tuning_max_time and \
                time() < self._t_end:

            next_config = current_config.neighbour_define()

            # see if this move is better than the current
            q_value = objective_function(next_config)

            if q_value > current_score:
                current_config = next_config
                current_score = q_value

        best_mapping = objective_function.best_mapping
        best_score = objective_function.best_score

        return best_mapping, best_score

    def inner_anneal(self, enemy_config):
        """
        Use SA to determine the best configuration, given the template
        :param enemy_config: An enemy mapping object
        :return: Best mapping and its corresponding result
        """

        inner_anneal = DefineAnneal(initial_state=enemy_config,
                                    experiment_info=self._experiment_info,
                                    exit_time=self._t_end,
                                    log= self._log,
                                    network_socket=self._socket
                                    )

        inner_anneal.anneal()

        best_mapping = inner_anneal.objective_function.best_mapping
        best_score = inner_anneal.objective_function.best_score

        return best_mapping, best_score

    def inner_bo(self, enemy_config, kappa_val=6):
        """
        Use BO to determine the best configuration, given the template
        :param enemy_config: An enemy mapping object
        :return: Best mapping and its corresponding result
        """

        objective_function = ObjectiveFunction(experiment_info=self._experiment_info,
                                               log=self._log,
                                               socket_connect=self._socket)
        config = enemy_config

        # Devide the evaluations for each core
        init_pts = 5
        if config.same_defines:
            iterations = self._experiment_info.tuning_max_iterations
            assert iterations > 0, "Bayesian optimization needs more iterations to work"
            objective_function.stored_mapping = config
            data_range = config.enemies[0].get_defines_range()
            bo = BayesianOptimization(objective_function.bo_call, data_range, verbose=0)
            bo.init(init_points=init_pts)
            bo.maximize(n_iter=1, kappa=kappa_val)
            it = 1
            while it < iterations and time() < self._t_end:
                bo.maximize(n_iter=1, kappa=kappa_val)
                it += 1
            for core in range(config.enemy_cores):
                config.enemies[core].set_defines(bo.res['max']['max_params'])
        else:
            iterations = int(self._experiment_info.tuning_max_iterations/config.enemy_cores - init_pts)
            assert iterations > 0, "Bayesian optimization needs more iterations to work"

            for core in range(config.enemy_cores):
                objective_function.optimized_core = core
                objective_function.stored_mapping = config
                data_range = config.enemies[core].get_defines_range()

                bo = BayesianOptimization(objective_function.bo_call, data_range, verbose=0)
                bo.init(init_points=init_pts)
                bo.maximize(n_iter=1, kappa=kappa_val)
                it = 1
                while it < iterations and time() < self._t_end:
                    bo.maximize(n_iter=1, kappa=kappa_val)
                    it += 1
                config.enemies[core].set_defines(bo.res['max']['max_params'])

        best_score = objective_function.best_score

        return config, best_score

    def outer_random(self, enemy_config, inner_tune,  max_evaluations=100):

        objective_function = ObjectiveFunction(experiment_info=self._experiment_info,
                                               log=self._log,
                                               socket_connect=self._socket)

        current_config = enemy_config
        objective_function(enemy_config)

        while objective_function.iteration < max_evaluations and time() < self._t_end:
            current_config.random_set_all_templates()

            # The inner tune part
            if inner_tune == "ran":
                best_inner_config, score = self.inner_random(current_config)
            elif inner_tune == "hc":
                best_inner_config, score = self.inner_hill_climb(current_config)
            elif inner_tune == "sa":
                best_inner_config, score = self.inner_anneal(current_config)
            elif inner_tune == "bo":
                best_inner_config, score = self.inner_bo(current_config)
            else:
                print("I do not know how to tune like that")

        best_score = objective_function.best_score
        best_mapping = objective_function.best_mapping

        return best_score, best_mapping

    def outer_anneal(self, enemy_config, inner_tune, max_evaluations=100, outer_temp=100, outer_alpha=0.8):

        objective_function = ObjectiveFunction(experiment_info=self._experiment_info,
                                               log=self._log,
                                               socket_connect=self._socket)

        # Initialise SA
        current_outer_config = enemy_config.random_set_all()
        current_outer_score = objective_function(enemy_config)

        num_evaluations = 1

        outer_cooling_schedule = self.kirkpatrick_cooling(outer_temp, outer_alpha)

        for outer_temperature in outer_cooling_schedule:
            done = False

            if time() > self._t_end:
                break

            for next_outer_config in current_outer_config.neighbour_template():
                if num_evaluations >= max_evaluations or time() > self._t_end:
                    done = True
                    break

                # The inner tune part
                if inner_tune == "ran":
                    best_inner_config, score = self.inner_random(next_outer_config)
                elif inner_tune == "hc":
                    best_inner_config, score = self.inner_hill_climb(next_outer_config)
                elif inner_tune == "sa":
                    best_inner_config, score = self.inner_anneal(next_outer_config)
                elif inner_tune == "bo":
                    best_inner_config, score = self.inner_bo(next_outer_config)
                else:
                    print("I do not know how to tune like that")

                next_outer_score = score

                num_evaluations += 1

                # probabilistically accept this solution
                # always accepting better solutions
                p = self.p_score(current_outer_score, next_outer_score, outer_temperature)
                if random() < p:
                    current_outer_config = best_inner_config
                    current_outer_score = next_outer_score
                    break
            # see if completely finished
            if done:
                break

        best_score = objective_function.best_score
        best_mapping = objective_function.best_mapping

        return best_score, best_mapping


class MySocket:
    def __init__(self, sock=None):
        if sock is None:
            self.sock = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock

    def connect(self, host, port):
        self.sock.connect((host, port))

    def mysend(self, msg, msglen):
        totalsent = 0
        while totalsent < msglen:
            sent = self.sock.send(msg[totalsent:])
            if sent == 0:
                raise RuntimeError("socket connection broken")
            totalsent = totalsent + sent

    def myreceive(self, msglen):
        chunks = []
        bytes_recd = 0
        while bytes_recd < msglen:
            chunk = self.sock.recv(min(msglen - bytes_recd, 2048))
            if chunk == '':
                raise RuntimeError("socket connection broken")
            chunks.append(chunk)
            bytes_recd = bytes_recd + len(chunk)
        return ''.join(chunks)


class PackedStart:
    def __init__(self, sut, temperature):
        self.sut = sut
        self.temperature = temperature


class Tuning:
    """
    Run tuning based on random, SA or Bayesian Optimisation
    Reads and runs the tuning described in the JSON file.
    """

    def __init__(self):
        """
        Create a tuning object
        """

        self._experiment_info = None
        self._log = DataLog()

        # Store the enemy config
        self._enemy_config = None

        # For network connection
        self._socket = None

    def cleanup(self):
        if self._socket:
            self._socket.send(pickle.dumps("Finished!") + b'data_end')
            self._socket.close()
            self._socket = None

    def read_json_object(self, json_object):
        """
        Sets the tuning data based on JSON object
        :param json_object: The JSON Object
        :return:
        """

        self._enemy_config = EnemyConfiguration(self._experiment_info.cores)

        try:
            enemy_template = str(json_object["enemy_template"])
            enemy_range = str(json_object["enemy_range"])
            self._enemy_config.set_all_templates(enemy_template, enemy_range)
            self._enemy_config.set_same_defines(True)
        except KeyError:
            pass

        try:
            host = str(json_object["network"])
            self._socket = socket.socket()
            port = 12345  # Reserve a port for your service
            print(host, port)
            self._socket.connect((host, port))

            pack = PackedStart(self._experiment_info.sut, self._experiment_info.sut)
            pickle_pack = pickle.dumps(pack)
            self._socket.send(pickle_pack)
            pickle_sync = self._socket.recv(1024)      # Sync message
            print(pickle.loads(pickle_sync))

        except KeyError:
            self._socket = None

    def bilevel_tune(self, outer_tune_method, inner_tune_method):
        """
        Tuning by using a nested method for both the outer and inner loop
        :param outer_tune_method: Optimization method for the outer loop
        :param inner_tune_method: Optimization method for the inner loop
        :return:
        """

        start_time = time()

        sa = Optimization(experiment_info=self._experiment_info,
                          log=self._log,
                          network_socket=self._socket)

        if outer_tune_method == "ran":
            best_state, best_score = sa.outer_random(
                enemy_config=self._enemy_config,
                inner_tune=inner_tune_method)
        elif outer_tune_method == "sa":
            best_state, best_score = sa.outer_anneal(
                enemy_config=self._enemy_config,
                inner_tune=inner_tune_method)
        else:
            print("I do not know how to bilevel train that way")
            sys.exit(0)

        f = open(self._experiment_info.max_file, 'w')
        f.write("Max time " + str(best_score) +
                "\n" + str(best_state) +
                "\n" + "Total time " + str(time()-start_time))
        f.close()

    def simple_tune(self, tune_method):
        """
        This method can be used only if the template is fixed and we only need to determine the parameters
        :param tune_method: Optimization method
        :return:
        """
        assert self._enemy_config.fixed_template, "Can not train this way if the template is not given"

        sa = Optimization(experiment_info=self._experiment_info,
                          log=self._log,
                          network_socket=self._socket)

        if tune_method == "ran":
            best_state, best_score = sa.inner_random(self._enemy_config)
        elif tune_method == "hc":
            best_state, best_score = sa.inner_hill_climb(self._enemy_config)
        elif tune_method == "sa":
            best_state, best_score = sa.inner_anneal(self._enemy_config)
        elif tune_method == "bo":
            best_state, best_score = sa.inner_bo(self._enemy_config)
        else:
            print("I do not know how to simple train that way")
            sys.exit(0)

        best_state.get_file_mapping(prefix=str(self._experiment_info.experiment_name) + "_",
                                    output_folder=self._experiment_info.output_binary)

        f = open(self._experiment_info.max_file, 'w')
        f.write("Max time " + str(best_score) + "\n" + str(best_state))
        f.close()

    def run(self, input_file, output_file):
        """
        Run the configured experiment
        :param input_file: The JSON file where the tuning are defined
        :param output_file: The JSON file where the result is stored
        """

        # Read the configuration in the JSON file
        with open(input_file) as data_file:
            tuning_object = json.load(data_file)

        for experiment_name in tuning_object:
            self._experiment_info = ExperimentInfo(experiment_name)
            self._experiment_info.read_json_object(tuning_object[experiment_name])
            self.read_json_object(tuning_object[experiment_name])

            # To give each tuning a fair chance
            seed(1000)

            if self._experiment_info.method == "sa_ran":
                print("Tuning by simulated annealing on the "
                      "outer loop and random on the inner loop")
                self.bilevel_tune("sa", "ran")
            elif self._experiment_info.method == "sa_hc":
                print("Tuning by simulated annealing on the "
                      "outer loop and hill climbing on the inner loop")
                self.bilevel_tune("sa", "hc")
            elif self._experiment_info.method == "sa_sa":
                print("Tuning by simulated annealing on the "
                      "outer loop and simulated annealing on the inner loop")
                self.bilevel_tune("sa", "sa")
            elif self._experiment_info.method == "sa_bo":
                print("Tuning by simulated annealing on the "
                      "outer loop and bayesian optimization on the inner loop")
                self.bilevel_tune("sa", "bo")
            elif self._experiment_info.method == "ran_ran":
                print("Tuning by randomising on the outer "
                      "loop and random on the inner loop")
                self.bilevel_tune("ran", "ran")
            elif self._experiment_info.method == "ran_hc":
                print("Tuning by randomising on the outer "
                      "loop and hill climbing on the inner loop")
                self.bilevel_tune("ran", "hc")
            elif self._experiment_info.method == "ran_sa":
                print("Tuning by randomising on the outer "
                      "loop and simulated annealing on the inner loop")
                self.bilevel_tune("ran", "sa")
            elif self._experiment_info.method == "ran_bo":
                print("Tuning by randomising on the outer "
                      "loop and bayesian optimization on the inner loop")
                self.bilevel_tune("ran", "bo")
            elif self._experiment_info.method == "ran":
                print("Tuning by randomising with a fixed template")
                self.simple_tune("ran")
            elif self._experiment_info.method == "hc":
                print("Tuning by hillclimbing with a fixed template")
                self.simple_tune("hc")
            elif self._experiment_info.method == "sa":
                print("Tuning by simulated annealing with a fixed template")
                self.simple_tune("sa")
            elif self._experiment_info.method == "bo":
                print("Tuning with bayesian optimization with a fixed template")
                self.simple_tune("bo")
            else:
                print("I do not know how to train that way")
                sys.exit(0)

            self._log.file_dump()

            self.cleanup()

        self._log.merge_docs(output_file)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("usage: " + sys.argv[0] + " <tuning_file>.json <results>.json\n")
        exit(1)

    tr = Tuning()

    tr.run(sys.argv[1], sys.argv[2])
