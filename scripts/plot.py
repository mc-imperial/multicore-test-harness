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
A python script that plots the data from the JSON file
"""

import numpy as np
import matplotlib.pyplot as plt
import json
import sys
import re


class Visualise(object):
    """A class used to visualise the JSON file produced by run_experiment
    This class is designed to plot the JSON file produced by the run_experiment
    """
    def __init__(self, file):
        """
        :param file: File to plot
        """
        self._file = file
        self._experiments_result = None

    def read_file(self):
        """
        :param file: File to plot
        :return:
        """
        with open(self._file) as data_file:
            self._experiments_result = json.load(data_file)

    def plot_experiment(self):
        """
        Loop over all the experiments and plot them
        :return:
        """

        for experiment in self._experiments_result:
            print "Display experiment " + experiment
            self.plot_configs(experiment)

    def plot_configs(self, experiment):
        """
        Loop over all the configs and plot them
        :param experiment: The experiment name in the JSON dict
        :return:
        """

        data_experiment = self._experiments_result[experiment]

        N = 0
        time_avg_baseline = []
        time_std_baseline = []
        time_avg = []
        time_std = []
        labels = []
        stress = []

        for config in sorted(data_experiment):
            N = N + 1

            labels.append(config)
            time_avg_baseline.append(data_experiment[config]['time_avg_baseline'])
            time_std_baseline.append(data_experiment[config]['time_std_baseline'])
            time_avg.append(data_experiment[config]['time_avg'])
            time_std.append(data_experiment[config]['time_std'])
            stress.append(data_experiment[config]['stress'])


        ind = np.arange(N)  # the x locations for the groups
        width = 0.35  # the width of the bars

        fig, ax = plt.subplots()
        rects1 = ax.bar(ind, time_avg_baseline, width, color='y', yerr=time_std_baseline)

        rects2 = ax.bar(ind + width, time_avg, width, color='r', yerr=time_std)

        # add some text for labels, title and axes ticks
        ax.set_ylabel('Time')
        ax.set_title('Experiment ' + experiment)
        ax.set_xticks(ind + width / 2)
        ax.set_xticklabels(labels)

        y_height = int(max(time_avg) * 1.5)
        ax.set_ylim([0,y_height])

        ax.legend((rects1[0], rects2[0]), ('Baseline', 'With Enemy'))

        def add_label(rects1, rects2, stress):
            """
            Attach a text label above each bar displaying its height
            """
            for i in range(0,len(rects2)):
                r1 = rects1[i]
                r2 = rects2[i]
                height = max(r1.get_height(), r2.get_height())
                ax.text(r2.get_x() + r2.get_width() / 2., 1.05 * height,
                        '%s' % (re.findall("/\w+", stress[i])[-1])[1:],
                        ha='center', va='bottom')


        add_label(rects1, rects2, stress)

        plt.show()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "usage: " + sys.argv[0] + " data_json_file\n"
        exit(1)

    vis = Visualise(sys.argv[1])
    vis.read_file()
    vis.plot_experiment()
