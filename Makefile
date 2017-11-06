CACHE_FILE = dan-laptop_cache.json
COREMARK_PORT_DIR = linux64


CACHE_DIR = ./src/cache_set
MEM_DIR = ./src/mem_thrashing_set
SYS_DIR = ./src/system_calls_set
PIPE_DIR = ./src/pipeline_set
COREMARK_DIR = ./src/coremark_v1.0
RT_TESTS_DIR = ./src/rt-tests

WCET_DIR = ./src/wcet

all: cache_set mem_set sys_set pipeline_set wcet_sut coremark_sut cyclictest

cache_set:
	(cd $(CACHE_DIR); python gen.py ./cache_info/$(CACHE_FILE))
mem_set:
	(cd $(MEM_DIR); make all)
sys_set:
	(cd $(SYS_DIR); make all)
pipeline_set:
	(cd $(PIPE_DIR); make all)

wcet_sut:
	(cd $(WCET_DIR); make all)
coremark_sut:
	(cd $(COREMARK_DIR); make link PORT_DIR=$(COREMARK_PORT_DIR))
cyclictest:
	(cd $(RT_TESTS_DIR); make cyclictest)

.PHONY: clean
clean:
	(cd $(CACHE_DIR); python -c 'import gen; gen.clean()')
	(cd $(MEM_DIR); make clean)
	(cd $(SYS_DIR); make clean)
	(cd $(PIPE_DIR); make clean)
	(cd $(WCET_DIR); make clean)
	(cd $(COREMARK_DIR); make clean PORT_DIR=$(COREMARK_PORT_DIR) )
	(cd $(RT_TESTS_DIR); make clean)
	rm -r bin
