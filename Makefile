all: build/opcode.ub build/register.ub build/stdio.ub

build/opcode.ub: build bin/generate_opcode_module.py underbar/operations.py
	PYTHONPATH=. python3 bin/generate_opcode_module.py > build/opcode.ub

build/register.ub: build bin/generate_register_module.py underbar/register.py
	PYTHONPATH=. python3 bin/generate_register_module.py > build/register.ub

build/stdio.ub: build bin/generate_stdio_module.py underbar/stdio.py
	PYTHONPATH=. python3 bin/generate_stdio_module.py > build/stdio.ub

build:
	mkdir build

clean:
	rm -fr build

.PHONY: all clean
