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
import socket
import pickle

from random import randrange, uniform, choice
from collections import OrderedDict
from copy import deepcopy

# my packages
from run_sut_stress import SutStress


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
                            ("../templates/cache/template_cache.c",
                             "../templates/cache/parameters.json"),
                            ("../templates/mem/template_mem.c",
                             "../templates/mem/parameters.json"),
                            ("../templates/pipeline/template_pipeline.c",
                             "../templates/pipeline/parameters.json"),
                            ("../templates/system/template_system.c",
                             "../templates/system/parameters.json")
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
        self._same_defines = False

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

        self._enemy_files = enemy_config.get_file_mapping()
        s = SutStress()
        ex_time = s.run_mapping(self._sut, self._enemy_files, self._max_temperature)

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


class PackedStart:
    def __init__(self, sut, temperature):
        self.sut = sut
        self.temperature = temperature


def read_lines(sock, recv_buffer=4096, delim=b'data_end'):
    buffer = b''
    data = True
    while data:
        data = sock.recv(recv_buffer)
        buffer += data 

        while buffer.find(delim) != -1:
            line, buffer = buffer.split(b'data_end', 1)
            yield line
    return


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: " + sys.argv[0] + " hostname\n")
        exit(1)

    host = sys.argv[1]  # Get local machine name

    s = socket.socket()
    port = 12345                    # Reserve a port for your service.
    #s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((host, port))            # Bind to the port

    while True:
        s.listen(5)                 # Now wait for client connection.

        c, addr = s.accept()        # Establish connection with client

        pickle_pack = c.recv(1024)
        pack = pickle.loads(pickle_pack)
        c.send(pickle.dumps("Sync"))
        print(pack.sut, pack.temperature)
        objective_function = ObjectiveFunction(pack.sut, pack.temperature)

        for line in read_lines(c):

            # Receive message
            print(line)
            print(sys.getsizeof(line))
            message = pickle.loads(line)
            # print(message)
            if message == "Finished!":
                print(message)
                break
            elif isinstance(message, EnemyConfiguration):
                ex_time = objective_function(message)
                c.send(pickle.dumps(ex_time))
            else:
                print("I received something strange")
                sys.exit(1)

        c.close()  # Close the connection
    s.close()



