# Multicore test harness #

This software is a black-box testing technique with the capability of provoking interference behaviour in multi-core chips, enabling an assessment of the extent to which interference affects execution of a piece of Software Under Test (SUT).  Interference is analysed by having an “enemy” process run a configurable test harness that is designed, through a combination of manual and automated tuning, to maximize the degree of certain types of interference. The black-box nature of this technique makes it applicable to any multi-core microprocessor running any operating system, so long as compilation and execution of ANSI-C programs is supported.

## Benchmarks ##

The systems under stress are divided into 4 categories and range from synthetic tests designed to be especially vulnerable to interference, to actual benchmarks.  

1\. Victim Programs.

Basic tests designed to test a single feature. There is a litmus test corresponding to every single enemy process

2\. WCET.

Malardalen WCET benchmarks that can be found [here](http://www.mrtc.mdh.se/projects/wcet/benchmarks.html)

3\. EEMBC Coremark.

An industry-standard benchmark for embedded systems that can be found [here](http://www.eembc.org/coremark/index.php)

4\. RT tests

A benchmark suite to test the latency of real-time threads. It is based on lunching high-priority threads that should preempt any process running on the processor and measuring the actual time that is required to do so. It can be found [here](https://github.com/jlelli/rt-tests)

*Note*: If you plan to use one of the external SUTs, it is your responsibility to check the license associated with that SUT


## Structure ##
The enemy processes are written in C and the experiments are driven by scripts written in python 3.

* **src** : C source folder for the enemy processes
* **bin** : Default folder where the SUTs and enemy processes are built
* **templates** : C sources for the configurable templates used for tuning
* **scripts** : Python scripts used to drive the experiments
* **scripts/config_tune** : Example JSON files for the tuning process
* **scripts/config_attack** : Example JSON files for the interference experiments


## Building ##

The system has been tested on Ubuntu 16.04 and on an Raspberry Pi 3 running Raspbian Jessie. We make the assumption that the system has a gcc compiler for that architecture on which the harness will be run.

1\. Dependencies to install:

For Bayesian optimization:
```
  sudo apt install python3-pip
  sudo apt-get install python3-numpy python3-scipy
  sudo pip3 install bayesian-optimization
```
For RT-tests:
```
  sudo apt-get install libnuma-dev
```

For Simulated Annealing:
```
sudo pip3 install simanneal 
```

For result plotting:
```
  sudo apt-get install python3-matplotlib
```

2\. If desired, change the following parameters in the makefile:

* **CACHE_FILE** : JASON file describing the system cache structure
* **COREMARK_PORT_DIR** : Can be either cygwin, linux or linux64

3\. Build

```
  make all
```

## Framework steps ##

1. For each shared resource, create an enemy process and victim program pair.
2. Tune the enemy process with their corresponding victim program
3. Create the ranked list of hostile environments
4. Determine the Paretto Optimal hostile environment
5. Run benchmarks in the hostile environment

### 1. Enemy processes ###

We used the following enemy processes to stress individual resources. It is easy to extend the framework and stress different shared resources that we have not included and that might be particular to specific platforms.

a) **Bus stress**. We have designed the enemy with the aim of hindering data transfers between the CPU and main memory. It reads a series of numbers from a main memory data buffer and increments their value.

b) **Cache stress**. This enemy process causes interference in the shared cache. It executes operations that cause as many evictions as possible.

c) **Memory thrashing stress**. This enemy process causes interference in the shared bus and shared RAM controller. Memory thrashing enemy processes that make frequent RAM accesses and thus cause a lot of bus traffic and keep the RAM controller busy.

### 2. Tuning the enemy processes ###

There are three possibilities to train an enemy process to cause as much interference as possible

a) **Fuzzing** samples different configurations and remembers the best values. This approach has the advantage of being lightweight and providing a baseline for the more complicated techniques.

b) **Simulated Annealing** is a metaheuristic to approximate global optimisation in a large search space. It is often used when the search space is discrete (e.g., all tours that visit a given set of cities). For problems where finding an approximate global optimum is more important than finding a precise local optimum in a fixed amount of time, simulated annealing may be preferable.

c) **Bayesian Optimisation**. Bayesian optimization works by constructing an approximation of the interference caused by enemy process with various tuning parameters. This approximation is improved with every new observation of a new set of parameters.

1\. Create a JSON file that defines the type of training process, with the following parameters:

* **sut** : The victim program used for tuning
* **enemy_range** : The JSON files that describes the parameters and the ranges of the tunable enemy process
* **enemy_template** : The template file of the enemy process. This files can be found in th templates folder
* **cores** : The number of cores on which to lunch the enemy process
* **method** : The training method to use. Either **ran**, **sa** or **bo**
* **quantile** : When taking multiple measurements, what quantile to use.
* **log_file** : The log files where all the training iterations
* **output_binary** : Output folder where the best enemy binaries are sored 
* **max_file** : The files where the maximum interference is recorded and the parameters that caused it
* **max_tuning_time** : The time (in minutes) after which the tuning process is stopped
* **max_inner_iterations** : The number of iterations after which the tuning process is stopped.
* **max_temperature** : The maximum temperature allowed for a measurement to be considered valid.

*Note:* Examples of such JSON files can be found in scripts/config_tune

2\. Run the python script to start training:

```
    cd scripts
    python3 run_tuning.py <train_config>.json
```

3\. A file describing all the iterations **log_file** and a file describing the parameters for the maximum interference **max_file** will be created. This parameters can be used as defines to compile the template file.

#### Demo scripts ###

* **config_tune/tune_cache.json** : This script will try to find the optimal parameters for the cache stress using **ran**, **sa** and **bo**
* **config_tune/tune_mem.json** : This script will try to find the optimal parameters for the memory stress using **ran**, **sa** and **bo**
* **config_tune/tune_bus.json** : This script will try to find the optimal parameters for the system stress using **ran**, **sa** and **bo**

*Note:* All scripts will run for 2 hours, record the detected parameters in .txt files and create the binary files.

### 3. Creating the ranked list ###

### 4. Determining the Paretto Optimal hostile environment ###


### 5. Evaluating the hostile environment ###

1\. Create a JSON file that defines the experiment that needs to be run with the following parameters:

* **sut** : Can be either a single system under test or a list of systems under stress.
* **stress** : Can be either a single enemy process or a list of enemy processes
* **cores** : Number of cores to run the stress o
* **iterations** : Number of times to run a configuration
* **max_temperature** : The maximum temperature allowed before starting an experiment
* **cooldown_time** : Cooldown time to be used between experiments, if no maximum temperature is defined

This will run experiments with the cross product of all the applications in the sut and stress

*Note:* Examples of such JSON files can be found in scripts/config_attack

2\. Run the python script to launch the experiments:

```
    cd scripts
    python3 run_experiments.py <test_config>.json <output>.json
```

3\. Inspect the JSON output, which has the following form:

* **temp_list_baseline** : A list of temp
* **temp_avg_baseline** : Average temperature for baseline
* **temp_std_baseline** : Standard temperature deviation for baseline
* **temp_list** : All the temperatures for the configuration
* **temp_avg** : Average temperature for the configuration
* **temp_std** : Standard temperature deviation for the configuration
* **time_list_baseline** : All the execution times for the baseline
* **time_avg_baseline** : Average execution time for the baseline
* **time_std_baseline** : Standard deviation of the execution time of the baseline
* **time_list** : All the execution times for the configuration
* **time_avg** : Average execution time for the configuration
* **time_std** : Standard deviation of the execution time of the configuration

4\. Furthermore, the plot script can be used on the JSON file for a graphical representation.

```
    python3 plot.py <output>.json
```

#### Demo scripts ###

* **config_attack/stress_cache.json** : This script will stress the cache intensive applications with the untrained enemy processes.
* **config_attack/stress_coremark.json** : This script will stress the coremark benchmark with the untrained enemy processes.
* **config_attack/stress_memory.json** : This script will stress the memory intensive application by running all alongside the untrained enemy processes.
* **config_attack/stress_RT.json** : This script will stress the real-time capabilities of the system by running with the untrained enemy processes. The benchmark will ask for sudo permission.
* **config_attack/stress_system_calls.json** : This script will stress a system calls intensive application with the untrained enemy processes.
* **config_attack/stress_wcet.json** : This script will stress the Malardalen WCET benchmarks with the untrained enemy processes.

*Note 1:* All the demo scripts are configured to run with enemy processes on 1, 2 and 3 cores. Each configuration will run a number of 50 times and will only start if the temperature is below 70C.

*Note 2:* Compile and add the tuned enemy processes to the **stress** list in for your specific platform.


## Doxygen (Doxygen) ##

Doxygen is used to generate documentation from annotated source files. It will generate HTML and Latex documentation in the /doc folder.

1\. Installation

```
  sudo apt-get install doxygen
  sudo apt-get install graphviz
```

2\. Running

```
  doxygen Doxyfile
```
