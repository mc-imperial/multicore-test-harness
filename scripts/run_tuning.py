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
A python for tuning based on fuzzing and baysian optimisation
"""

import json
import sys
import os

from bayes_opt import BayesianOptimization
from time import time
from random import randrange, uniform

from run_sut_stress import SutStress
from common import cooldown


class Training(object):
    """Run tuning based on fuzzing or baysian optimisation
    Reads and runs the trainnings described in the JSON file.
    """
    def __init__(self):
        """
        Create a tuning object
        """
        self._sut = None
        self._template_data_file = None
        self._cores = None
        self._method = None
        self._kappa = None
        self._training_time = None
        self._max_temperature = None
        self._cooldown_time = None

        self._t_file = None
        self._defines = None

        self._log_file = None
        self._max_file = None

    def read_json_object(self, json_object):
        """
        Sets the tunning data based on JSON object
        :param file: The JSON Object
        :return:
        """

        try:
            self._sut = str(json_object["sut"])
        except KeyError:
            print "Unable to find sut in JSON"
            sys.exit(1)

        try:
            self._template_data_file = str(json_object["template_data"])
        except KeyError:
            print "Unable to find template_data in JSON"
            sys.exit(1)

        try:
            self._t_file = str(json_object["template_file"])
        except KeyError:
            print "Unable to find T_FILE in JSON"
            sys.exit(1)

        try:
            self._cores = int(json_object["cores"])
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

    def process_templete_data(self):
        """
        :param json_file: The JSON file containing the templete data
        :return:
        """

        # Read the configuration in the JSON file
        with open(self._template_data_file) as data_file:
            template_object = json.load(data_file)

        try:
            self._defines = template_object["DEFINES"]
        except KeyError:
            print "Unable to find DEFINES in JSON"

    def create_bin(self, inst):
        """
        :param inst: A dictionary of defines
        :return:
        """
        defines = ["-D" + d + "=" + str(inst[d]) for d in inst]
        cmd = "gcc -std=gnu11 -Wall " + " ".join(defines) + " " + self._t_file + " -lm"
        print "Compiling:"
        print cmd
        os.system(cmd)

    def random_instantiate_defines(self):
        """
        :return
        """
        ret = {}
        for param in self._defines:
            min_val = self._defines[param]["range"][0]
            max_val = self._defines[param]["range"][1]
            if self._defines[param]["type"] == "int":
                ret[param] = randrange(min_val, max_val)
            elif self._defines[param]["type"] == "float":
                ret[param] = uniform(min_val, max_val)
            else:
                print("Unknown data type for param " + str(param) )
                sys.exit(1)

        return ret

    def run_experiment(self, **kwargs):
        """
        :param **kwargs: keyworded, variable-length argument list
        :return: Execution time (latency)
        """
        def_param = dict()

        # Make sure that the parameters are of the correct type
        # Workaround to force BO to generate init_points
        for key in kwargs:
            if self._defines[key]["type"] == "int":
                def_param[key] = int(kwargs[key])
            elif self._defines[key]["type"] == "float":
                def_param[key] = float(kwargs[key])
            else:
                print("Unknown data type for param " + str(key) )
                sys.exit(1)

        cooldown(self._max_temperature)

        self.create_bin(def_param)
        s = SutStress()
        ex_time, ex_temp = s.run_sut_stress(self._sut, "a.out", self._cores)

        return ex_time

    def _pp_d(self, d):
        ret = []
        for x in d:
            ret.append(x + ": " + str(d[x]))

        return " ".join(ret)

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
                + str(max_value) + "\t\t" + str(cur_value) +"\t\t" + self._pp_d(conf) + "\n"
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

        bo.init(init_points = init_pts)
        iteration = init_pts # I consider the init_points also as iterations, BO does not
        while time() < t_end:
            bo.maximize(n_iter = 1, kappa = self._kappa)
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
            def_param = self.random_instantiate_defines()
            ex_time = self.run_experiment(**def_param)
            print "found time of " + str(ex_time)
            if ex_time > max_time:
                max_time = ex_time
            iteration = iteration + 1
            self._log_data(iteration,
                           int(time() - t_start),
                           max_time,
                           ex_time,
                           def_param)

        f = open(self._max_file, 'w')
        f.write("Max time " + str(max_time) + "\n" + self._pp_d(def_param))
        f.close()

    def run(self, input_file):
        """
        Run the configured experiment
        :param input_file: The JSON file where the trainnings are defined
        :param output_file: The JSON file where the trainning results are stored
        """

        output_file = "temp.txt"

        # Read the configuration in the JSON file
        with open(input_file) as data_file:
            training_object = json.load(data_file)



        for training_sesion in training_object:
            self.read_json_object(training_object[training_sesion])
            self.process_templete_data()

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

    tr = Training()

    tr.run(sys.argv[1])
