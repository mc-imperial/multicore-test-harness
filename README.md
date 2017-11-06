# Multicore test harness #

This software is a black-box testing technique with the capability of provoking interference behaviour in multi-core chips, enabling an assessment of the extent to which interference affects execution of a piece of Software Under Test (SUT).  Interference is analysed by having an “enemy” process run a configurable test harness that is designed, through a combination of manual and automated tuning, to maximize the degree of certain types of interference. The black-box nature of this technique makes it applicable to any multi-core microprocessor running any operating system, so long as compilation and execution of ANSI-C programs is supported.

## Enemy processes ##

The enemy processes are divided into four categories and are meant to target individual shared resources.

1\. Cache stress

This enemy process causes interference in the shared cache. It executes operations that cause as many evictions as possible.

2\. Memory thrashing stress

This enemy process causes interference in the shared bus and shared RAM controller. Memory thrashing enemy processes that make frequent RAM accesses and thus cause a lot of bus traffic and keep the RAM controller busy.

3\. System calls stress

This enemy process causes interference by causing software interrupts. System calls enemy process that cause a lot of software interrupts and therefore force the processor to switch between user mode and privileged mode.

4\. Pipeline stress

This enemy process causes interference by heating up the processor and causing energy throttling. The pipeline stress enemy process that keeps the ALU of the processor busy by performing a lot of computational intensive operations.

## Systems under test ##

The systems under stress are divided into 4 categories and range from synthetic tests designed to be especially vulnerable to interference, to actual benchmarks.  

1\. Litmus tests.

Basic tests designed to test a single feature. There is a litmus test corresponding to every single enemy process

2\. WCET.

Malardalen WCET benchmarks that can be found [here](http://www.mrtc.mdh.se/projects/wcet/benchmarks.html)

3\. EEMBC Coremark.

An industry-standard benchmark for embedded systems that can be found [here](http://www.eembc.org/coremark/index.php)

4\. RT tests

A benchmark suite to test the latency of real-time threads. It is based on lunching high-priority threads that should preempt any process running on the processor and measuring the actual time that is required to do so. It can be found [here](https://github.com/jlelli/rt-tests)


## Structure
The enemy processes are written in C and the experiments are driven by scripts written in python 2.

* **src** : C source folder for the enemy processes
* **bin** : Default folder where the SUTs and enemy processes are built
* **templates** : C sources for the configurable templates used for tuning
* **scripts** : Python scripts used to drive the experiments
* **scripts/config_tune** : Example JSON files for the tuning process
* **scripts/config_attack** : Example JSON files for the interference experiments


## Building

1\. Dependencies to install:

For Bayesian optimization:
```
  sudo apt install python-pip
  pip install bayesian-optimization
```
For RT-tests:
```
  sudo apt-get install libnuma-dev
```
For result plotting:
```
  sudo apt-get install python-matplotlib
```

2\. If desired, change the following parameters in the makefile:

* **CACHE_FILE** : JASON file describing the system cache structure
* **COREMARK_PORT_DIR** : Can be either cygwin, linux or linux64

3\. Build

```
  make all
```

## Tuning the enemy processes

There are two possibilities to train an enemy process to cause as much interference as possible

* **Fuzzing**. Tries different possible configurations of the enemy process and record which one causes the highest impact on the SUT
* **Bayesian Optimisation**. Bayesian optimization works by constructing an approximation of the interference caused by enemy process with various tuning parameters. This approximation is improved with every new observation of a new set of parameters.

1\. Create a JSON file that defines the type of training process, with the following parameters:

* **sut** : The SUT to which you want to train against
* **template_data** : The JSON files that describes the parameters and the ranges of the tunable enemy process.
* **template_file** : The template file of the enemy process. This files can be found in th templates folder
* **cores** : The number of cores on which to lunch the enemy process.
* **method** : The training method to use. Either **fuzz** or **baysian**
* **kappa** : If Bayesian optimization is used as a trainning method, this parameter allows setting the exploitation/exploration trade-off. A lower parameter encourages exploitation and a higher parameter encourages exploration.
* **log_file** : The log files where all the training iterations.
* **max_file** : The files where the maximum interference is recorded and the parameters that caused it.
* **training_time** : The total training time, in minutes
* **max_temperature** : The maximum temperature allowed before starting a training iteration
* **cooldown_time** : Cooldown time to be used between iterations, if no maximum temperature is defined

*Note:* An example of such JSON files can be found in scripts/config_tune

2\. Run the python script to start training:

```
    cd scripts
    python run_tuning <train_config>.json
```

3\. A file describing all the iterations **log_file** and a file describing the parameters for the maximum interference **max_file** will be created. This parameters can be used as defines to compile the template file.

## Running the SUT in the precedence of enemy processes

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
    python run_experiments.py <test_config>.json <output>.json
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
    python plot.py <output>.json
```

## Doxygen (Doxygen)

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

## Raspberry Pi 3 Results

In this section, we provide the results of the the multicore test harness on the Raspberry Pi 3 with a Real-Time Kernel.

### Tuning

**Cache enemy**

|               | Fuzzing       | Bayesian optimization  |
| ------------- |:-------------:|:----------------------:|
| ASSOCIATIVITY | 154           | 113                    |
| INSTR1        | 1             | 1                      |
| INSTR2        | 1             | 3                      |
| INSTR3        | 1             | 2                      |
| INSTR4        | 1             | 4                      |
| CACHE_LINE    | 82            | 70                     |
| MY_FACTOR     | 4             | 3                      |
| INSTR5        | 1             | 4                      |

**Memory enemy**

|                  | Fuzzing       | Bayesian optimization  |
| ---------------- |:-------------:|:----------------------:|
| SIZE_MB          | 29            | 95                     |
| PAGE_SIZE_BYTES  | 9853          | 8907                   |

**System enemy**

|               | Fuzzing       | Bayesian optimization  |
| ------------- |:-------------:|:----------------------:|
| INSTR1        | 2             | 2                      |
| INSTR2        | 3             | 4                      |
| INSTR3        | 4             | 5                      |
| INSTR4        | 2             | 3                      |
| INSTR5        | 5             | 4                      |

## Interference

Legend:

U - not tuned

F - tuned using Fuzzing

B - Tuned using Bayesian optimization

|                  | Cache litmus | Memory litmus | System litmus | Pipeline litmus| Coremark |
| ---------------- |:------------:|:-------------:|:-------------:|:--------------:|:--------:|
| baseline         | 605113       | 800807        | 1608829       | 3543630        | 12490000 |
| U cache          | 3345717      | 1079123       | 1945448       | 3594554        | 12720000 |
| F cache          | 9480042      | 4192268       | 32056466      | 3615523        | 13200000 |
| B cache          | 9844489      | 4685625       | 37882536      | 3843269        | 15900000 |
| U memory         | 5744788      | 1649468       | 22460072      | 3646462        | 13180000 |
| F memory         | 5811896      | 4031728       | 27482135      | 3759266        | 13380000 |
| B memory         | 5745578      | 3456403       | 26076934      | 3639061        | 12870000 |
| U system         | 1200801      | 777247        | 11759146      | 3611831        | 12580000 |
| F system         | 668841       | 831726        | 74241977      | 3631331        | 12590000 |
| B system         | 750045       | 845161        | 65560406      | 3613417        | 12510000 |
| U pipeline       | 684527       | 804182        | 1613253       | 3512416        | 12480000 |
