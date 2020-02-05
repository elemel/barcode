all: build/opcode.ub build/register.ub build/stdio.ub

build/opcode.ub: build bin/gen_opcode underbar/operations.py
	PYTHONPATH=. bin/gen_opcode > build/opcode.ub

build/register.ub: build bin/gen_register underbar/register.py
	PYTHONPATH=. bin/gen_register > build/register.ub

build/stdio.ub: build bin/gen_stdio underbar/stdio.py
	PYTHONPATH=. bin/gen_stdio > build/stdio.ub

build:
	mkdir build

clean:
	rm -fr build

.PHONY: all clean
