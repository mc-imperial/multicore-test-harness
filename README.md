# Multicore test harness #

This software is a black-box testing technique with the capability of provoking interference behaviour in multi-core chips, enabling an assessment of the extent to which interference affects execution of a piece of a Program Under Test (PUT). Interference is analysed by having an “enemy” process run a configurable test harness that is designed, through a combination of manual and automated tuning, to maximize the degree of certain types of interference. The black-box nature of this technique makes it applicable to any multi-core microprocessor running any operating system, so long as compilation and execution of ANSI-C programs is supported.


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

* **src** : C source folder for the enemy programs
* **bin** : Default folder where the SUTs and enemy processes are built
* **templates** : C sources for the configurable templates used for tuning
* **scripts** : Python scripts used to drive the experiments
* **scripts/perf_scripts** : Some example perf scripts that can be run with the framework for more insignt into the slowdown
* **scripts/exp_configs/enemy_tune** : Example JSON files for the tuning enemies
* **scripts/exp_configs/env_rank** : Example JSON files for ranking the environments
* **scripts/exp_configs/eval_env** : Example JSON files for testing the benchmarks in hostile environments
* **scripts/exp_configs/eval_env/perf** : Example JSON files for testing the benchmarks in hostile environments, also running perf to gather PMC information


## Building ##

The system has been tested on Ubuntu 16.04 and on an Raspberry Pi 3 running Raspbian Jessie. We make the assumption that the system has a gcc compiler for that architecture on which the harness will be run.

1\. Dependencies to install:

For Bayesian optimization:
```
sudo apt install python3-pip
sudo apt-get install python3-numpy python3-scipy
sudo pip3 install bayesian-optimization
```

For color terminal:
```
sudo pip3 install termcolor

```

For Simulated Annealing:
```
sudo pip3 install simanneal
```

For quantile:
```
sudo pip3 install scipy
```


For RT-tests:
```
sudo apt-get install libnuma-dev
```


2\. If desired, change the following parameters in the makefile:

* **CACHE_FILE** : JSON file describing the system cache structure
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

c) **Thrashing stress**. This enemy process causes interference in the shared bus and shared RAM controller. Memory thrashing enemy processes that make frequent RAM accesses and thus cause a lot of bus traffic and keep the RAM controller busy.

### 2. Tuning the enemy processes ###

There are three possibilities to tune an enemy process to cause as much interference as possible

a) **Random search** samples different configurations and remembers the best values. This approach has the advantage of being lightweight and providing a baseline for the more complicated techniques.

b) **Simulated Annealing** is a metaheuristic to approximate global optimisation in a large search space. It is often used when the search space is discrete (e.g., all tours that visit a given set of cities). For problems where finding an approximate global optimum is more important than finding a precise local optimum in a fixed amount of time, simulated annealing may be preferable.

c) **Bayesian Optimisation**. Bayesian optimization works by constructing an approximation of the interference caused by enemy process with various tuning parameters. This approximation is improved with every new observation of a new set of parameters.

1\. Create a JSON file that defines the type of tuning process, with the following parameters:

* **sut** : The victim program used for tuning
* **enemy_range** : The JSON files that describes the parameters and the ranges of the tunable enemy process
* **enemy_template** : The template file of the enemy process. This files can be found in th templates folder
* **cores** : The number of cores on which to lunch the enemy process
* **method** : The tuning method to use (**ran**, **sa** or **bo**)
* **quantile** : When taking multiple measurements, what quantile to use.
* **max_file** : The files where the maximum interference is recorded and the parameters that caused it
* **output_binary** : Output folder where the best enemy binaries are stored
* **tuning_max_time**: Maximum minutes for tuning
* **tuning_max_iterations**: Maximum number of tuning iterations
* **measurement_iterations_step**: The minimum number of measurements when measuring a configuration
* **measurement_iterations_max**: The maximum number of measurements when measuring a configuration
* **max_confidence_variation**: The permitted size of the confidence interval when measuring a configuration
* **confidence_interval**: The confidence interval desired when measuring a configuration
* **stopping** : "fixed" will measure measurement_iterations_max times each configurations
                 "no_decrease" will try to quit measuring early if the confidence interval gets size gets bellow max_confidence_variation
* **governor** : The governor to set before starting experiments
* **max_temperature** : The maximum temperature allowed for a measurement to be considered valid.

*Note:* Examples of such JSON files can be found in scripts/enemy_tune

2\. Run the python script to start tuning:

```
    cd scripts
    sudo python3 run_tuning.py <enemy_tune>.json <log_file>.json
```

3\. A file describing all the iterations is stored in **<log_file>.json** . The best enemy files are stored in  **output_binary**

#### Demo scripts ###

* **exp_configs/enemy_tune/demo/tune_cache.json** : This script will try to find the optimal parameters for the cache stress using **ran** for 30 min.
* **exp_configs/enemy_tune/demo/tune_mem.json** : This script will try to find the optimal parameters for the memory stress using **ran** for 30 min.
* **exp_configs/enemy_tune/demo/tune_bus.json** : This script will try to find the optimal parameters for the system bus stress using **ran** for 30 min.

*Note:* All scripts will record the detected parameters in .txt files and create the coresponding binary files in the **results_tuning** folder, one binary for each core.
*Note:* To uncover the most aggressive enemy processes, you should run a tuning technique for at least 10h


### 3. Creating the ranked list ###

We want to determine which combination of tuned enemy processes are the most effective at causing interference to a generic SUT.

1\. Create a JSON file that defines for which victim programs we need to rank the environments, with the following parameters:

* **sut** : The victim program
* **ranked_list** : The list of tuned enemy processes
* **cores** : The number of cores on which enemy processes will run
* **quantile** : What quantile will be used for measurement
* **measurement_iterations_step**: The minimum number of measurements when measuring a configuration
* **measurement_iterations_max**: The maximum number of measurements when measuring a configuration
* **max_confidence_variation**: The permitted size of the confidence interval when measuring a configuration
* **confidence_interval**: The confidence interval desired when measuring a configuration
* **stopping** : "fixed" will measure measurement_iterations_max times each configurations
                 "no_decrease" will try to quit measuring early if the confidence interval gets size gets bellow max_confidence_variation
* **governor** : The governor to set before starting experiments
* **max_temperature** : The maximum temperature allowed for a measurement to be considered valid.

2\. Run the python script the ranked list:

```
    python3 run_experiments <env_rank>.json <ranked_list>.json
```

3\. The output JSON file will contain ranked list of hostile environments fr each victim. Each environment will also contain a score.


#### Demo scripts ####

* **exp_configs/env_rank/demo/rank_litmus.json** : This script will rank all possible environments, for each one of the victim programs used by us

### 4. Determining the Paretto Optimal hostile environment ###

The next step involves running the script to determine the Paretto Optimal hostile environment for all the victim programs we have tried. As input , we used the ranked list from the previous step

```
    python3 <ranked_list>.json
```


### 5. Evaluating the hostile environment ###

1\. Create a JSON file that defines the experiment that needs to be run with the following parameters:

* **sut** : The system under test we want to evaluate.
* **intrument_cmd** : Optional atribute that can be used to run the sut with a script such as perf
* **mapping** : A dictionary of cores and their assigned enemy file
* **cores** : Number of cores to run the stress on
* **quantile** : What quantile will be used for measurement
* **measurement_iterations_step**: The minimum number of measurements when measuring a configuration
* **measurement_iterations_max**: The maximum number of measurements when measuring a configuration
* **max_confidence_variation**: The permitted size of the confidence interval when measuring a configuration
* **confidence_interval**: The confidence interval desired when measuring a configuration
* **stopping** : "fixed" will measure measurement_iterations_max times each configurations
                 "no_decrease" will try to quit measuring early if the confidence interval gets size gets bellow max_confidence_variation
* **governor** : The governor to set before starting experiments
* **max_temperature** : The maximum temperature allowed for a measurement to be considered valid.

*Note:* Examples of such JSON files can be found in scripts/exp_configs/eval_env. Examples of scripts that also use perf can be found in scripts/exp_configs/eval_env/perf.

2\. Run the python script to launch the experiments:

```
    cd scripts
    sudo python3 run_experiments.py <test_config>.json <output>.json
```

3\. Inspect the JSON output, which contains detailed information about the run. Out of which, the most important ones are:
* **it->baseline->q_value**: The quantile of the baseline execution time.
* **it->enemy->q_value**: The quantile of the execution time with the enemy process



### Demo run on Pi ###
```
    cd scripts
```
    

1. Tune the enemies
```
    sudo python3 run_tuning.py exp_configs/enemy_tune/tune_cache_small.json cache_small_log_pi.json
    sudo python3 run_tuning.py exp_configs/enemy_tune/tune_cache_large.json cache_large_log_pi.json
```
2. Create the ranked list
```
    sudo python3 run_experiments.py exp_configs/env_rank/rank_victim.json rank_pi.json
```
3. Determine the Paretto Optimal hostile environment. This will output the Paretto optimal hostile environment for the current development board. For the Raspberry Pi, this will probably consist of cache enemy on all cores.
```
    python3 calculate_rank.py rank_pi.json
```

4. If needed, change the mapping in scripts/exp_configs/eval_env/stress_all_pi.json to reflect the configuration found in the previous step.

5. Test the hostile environment on "coremark"
 
```
    sudo python3 run_experiments.py exp_configs/eval_env/stress_all_pi.json log.json
```
6. Investigate the log file for the effect of the enemy on the bechmark

* **coremark_HE->it->baseline->q_value**: The quantile of the baseline execution time, for out hostile environment
* **coremark_HE->it->enemy->q_value**: The quantile of the execution time with the enemy process, for our hostile environment
