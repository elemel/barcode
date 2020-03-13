all: build/opcode.qs build/register.qs build/stdio.qs

build/opcode.qs: build bin/gen_opcode quest/operations.py
	PYTHONPATH=. bin/gen_opcode > build/opcode.qs

build/register.qs: build bin/gen_register quest/register.py
	PYTHONPATH=. bin/gen_register > build/register.qs

build/stdio.qs: build bin/gen_stdio quest/stdio.py
	PYTHONPATH=. bin/gen_stdio > build/stdio.qs

build:
	mkdir build

clean:
	rm -fr build

.PHONY: all clean
