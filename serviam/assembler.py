from fractions import Fraction as Q
from sys import stderr, stdin

from parsimonious.grammar import Grammar, NodeVisitor

grammar = Grammar(r"""
    program = whitespace? (statement (whitespace statement)*)? whitespace?
    statement = label / constant / value / string

    label = identifier whitespace? ':'
    constant = identifier whitespace? '=' whitespace? value

    value = ((sign operand)? '/' operand) / (sign operand)
    sign = '-'?
    operand = natural / identifier

    natural = ~'0|[1-9][0-9]*'
    string = ~'"(\\[^\n]|[^"])*"'
    identifier = ~"[A-Z_a-z][0-9A-Z_a-z]*"
    whitespace = ~'([ \n]|#[^\n]*(\n|$))+'
""")


class Visitor(NodeVisitor):
    def visit_program(self, node, visited_children):
        program = []
        _, statements, _ = visited_children

        if statements:
            [[[statement], statements]] = statements
            program.append(statement)

            for statement in statements:
                _, [statement] = statement
                program.append(statement)

        return program

    def visit_label(self, node, visited_children):
        identifier, _, _ = visited_children
        return 'label', identifier

    def visit_constant(self, node, visited_children):
        identifier, _, _, _, value = visited_children
        _, sign, numerator, denominator = value
        return 'constant', identifier, sign, numerator, denominator

    def visit_value(self, node, visited_children):
        [value] = visited_children

        if len(value) == 3:
            numerator, _, [denominator] = value

            if numerator:
                [[sign, [numerator]]] = numerator
            else:
                sign = 1
                numerator = 1
        else:
            sign, [numerator] = value
            denominator = 1

        return 'value', sign, numerator, denominator

    def visit_sign(self, node, visited_children):
        return -1 if node.text else 1

    def visit_natural(self, node, visited_children):
        return int(node.text)

    def visit_string(self, node, visited_children):
        # TODO: Handle escapes properly
        return 'string', node.text[1:-1].replace('\\n', '\n')

    def visit_identifier(self, node, visited_children):
        return node.text

    def visit_whitespace(self, node, visited_children):
        return ' '

    def generic_visit(self, node, visited_children):
        return visited_children


def assemble(assembly_code):
    assembly_code += """

        ir = 1
        gr = 2
        hr = 3
        sr = 4
        fr = 5

        load_integer = 1
        swap = 3
        decrement = 9
        load_memory = 18
        new = 33
        invert = 49
        divide = 76
        add = 81
        multiply = 107
        store_memory = 125
        increment = 143
        negate = 147
        call = 164
        denominator = 171
        subtract = 183
        return = 193
        jump = 199
        delete = 211
        load_stream = 214
        numerator = 222
        discard = 223
        load_register = 227
        store_register = 229
        store_parameter = 233
        duplicate = 236
        load_variable = 239
        load_parameter = 241
        store_stream = 245
        load_rational = 247
        store_variable = 251
        jump_equal = 252
        halt = 255

        stdin = 1
        stdout = 2
        stderr = 3

    """

    parse_tree = grammar.parse(assembly_code)
    intermediate_code = Visitor().visit(parse_tree)

    machine_code = []
    symbols = {}
    errata = {}

    for statement in intermediate_code:
        if statement[0] == 'label':
            symbols[statement[1]] = Q(len(machine_code))
        elif statement[0] == 'constant':
            _, identifier, sign, numerator, denominator = statement

            numerator = symbols.get(numerator, numerator)
            denominator = symbols.get(denominator, denominator)

            if type(numerator) is not str and type(denominator) is not str:
                symbols[identifier] = Q(sign * numerator, denominator)
            else:
                errata[identifier] = sign, numerator, denominator
        elif statement[0] == 'value':
            _, sign, numerator, denominator = statement

            numerator = symbols.get(numerator, numerator)
            denominator = symbols.get(denominator, denominator)

            if type(numerator) is not str and type(denominator) is not str:
                machine_code.append(Q(sign * numerator, denominator))
            else:
                errata[len(machine_code)] = sign, numerator, denominator
                machine_code.append(Q(666))
        elif statement[0] == 'string':
            for char in statement[1]:
                machine_code.append(Q(ord(char)))
        else:
            raise Exception('Invalid statement type')

    while errata:
        for identifier, (sign, numerator, denominator) in errata.items():
            numerator = symbols.get(numerator, numerator)
            denominator = symbols.get(denominator, denominator)

            if type(numerator) is not str and type(denominator) is not str:
                if type(identifier) is str:
                    symbols[identifier] = Q(sign * numerator, denominator)
                else:
                    machine_code[identifier] = Q(sign * numerator, denominator)

                del errata[identifier]
                break
        else:
            for _, (_, numerator, denominator) in errata.items():
                for identifier in [numerator, denominator]:
                    identifier = symbols.get(identifier, identifier)

                    if type(identifier)is str:
                        if identifier in errata:
                            raise Exception(f'Cyclic reference: {identifier}')
                        else:
                            raise Exception(f'Undefined symbol: {identifier}')

    return machine_code


if __name__ == '__main__':
    for q in assemble(stdin.read()):
        print(q)
