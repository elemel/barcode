from collections import defaultdict, namedtuple
from fractions import Fraction as Q
import re


def assemble(assembly_code):
    machine_code = []

    definition_lists = defaultdict(list)
    reference_lists = defaultdict(list)

    for item in assembly_code:
        if type(item) == str:
            reference_lists[item].append(len(machine_code) + 1)
            machine_code.append(Q(0))
        elif type(item) == list:
            [label] = item
            definition_lists[label].append(len(machine_code) + 1)
        elif type(item) == set:
            [s] = item

            for c in s:
                machine_code.append(Q(ord(c)))
        else:
            machine_code.append(Q(item))

    for label, references in reference_lists.items():
        [definition] = definition_lists[label]

        for reference in references:
            machine_code[reference - 1] = definition

    return machine_code


Token = namedtuple('Token', ['type', 'value', 'line', 'column'])


def tokenize(assembly_code):
    token_patterns = [
        ('space', r' +'),
        ('newline', r'\n'),
        ('comment', r'#[^\n]*\n'),
        ('integer', r'\d+'),
        ('string', r'"(\\[^\n]|[^"])*"'),
        ('identifier', r'[_A-Za-z]+'),
        ('operator', r'[+\-*/]'),
        ('colon', r':'),
        ('mismatch', r'.'),
    ]

    token_re = re.compile('|'.join('(?P<%s>%s)' % p for p in token_patterns))
    line = 1
    start_of_line = 0

    for match in token_re.finditer(assembly_code):
        type_ = match.lastgroup
        value = match.group()
        column = match.start() - start_of_line + 1

        if type_ == 'space':
            continue
        elif type_ == 'newline':
            line += 1
            start_of_line = match.end()
            continue
        elif type_ == 'comment':
            line += 1
            start_of_line = match.end()
            continue
        elif type_ == 'integer':
            value = int(value)
        elif type_ == 'string':
            pass
        elif type_ == 'identifier':
            pass
        elif type_ == 'operator':
            pass
        elif type_ == 'colon':
            pass
        else:
            raise RuntimeError(f'{line}:{column}: Invalid token: {value!r}')

        yield Token(type_, value, line, column)


def assemble_text(assembly_code):
    for token in tokenize(assembly_code):
        print(token)

    machine_code = []

    definition_lists = defaultdict(list)
    reference_lists = defaultdict(list)

    for item in assembly_code:
        if type(item) == str:
            reference_lists[item].append(len(machine_code) + 1)
            machine_code.append(Q(0))
        elif type(item) == list:
            [label] = item
            definition_lists[label].append(len(machine_code) + 1)
        elif type(item) == set:
            [s] = item

            for c in s:
                machine_code.append(Q(ord(c)))
        else:
            machine_code.append(Q(item))

    for label, references in reference_lists.items():
        [definition] = definition_lists[label]

        for reference in references:
            machine_code[reference - 1] = definition

    return machine_code
