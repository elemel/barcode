from fractions import Fraction as Q
from sys import stderr, stdin

from parsimonious.grammar import Grammar, NodeVisitor

grammar = Grammar(r"""
    program = line*
    line = space? (statement (space statement)* space?)? comment? eol
    statement = label / constant / value / string

    label = identifier space? ':'
    constant = identifier space? '=' space? value

    value = ((sign operand)? '/' operand) / (sign operand)
    sign = '-'?
    operand = natural / identifier

    natural = ~'0|[1-9][0-9]*'
    string = ~'"(\\[^\n]|[^"])*"'
    identifier = ~'[.A-Z_a-z][.0-9A-Z_a-z]*'
    space = ~' +'
    comment = ~';.*'
    eol = ~'\n|$'
""")


class Visitor(NodeVisitor):
    def visit_program(self, node, visited_children):
        program = []

        for line in visited_children:
            for statement in line:
                program.append(statement)

        return program

    def visit_line(self, node, visited_children):
        line = []
        _, statements, _, _ = visited_children

        if statements:
            [[[statement], statements, _]] = statements
            line.append(statement)

            for statement in statements:
                _, [statement] = statement
                line.append(statement)

        return line

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
        sr = 2
        fr = 3

        ldi = 1
        swp = 3
        dec = 9
        ldm = 18
        new = 33
        inv = 49
        div = 76
        add = 81
        mul = 107
        stm = 125
        inc = 143
        neg = 147
        cal = 164
        den = 171
        sub = 183
        ret = 193
        jmp = 199
        del = 211
        lds = 214
        num = 222
        dis = 223
        ldr = 227
        str = 229
        stp = 233
        dup = 236
        ldl = 239
        ldp = 241
        sts = 245
        stl = 251
        jeq = 252
        hcf = 255

        stdin = 1
        stdout = 2
        stderr = 3

    """

    parse_tree = grammar.parse(assembly_code)
    intermediate_code = Visitor().visit(parse_tree)

    machine_code = []
    symbols = {}
    errata = {}

    previous_symbol = None

    def get_symbol(symbol):
        if symbol.startswith('.'):
            symbol = previous_symbol + symbol

        return symbol

    def set_symbol(symbol):
        nonlocal previous_symbol

        if symbol.startswith('.'):
            symbol = previous_symbol + symbol
        else:
            previous_symbol = symbol

        return symbol

    for statement in intermediate_code:
        if statement[0] == 'label':
            identifier = set_symbol(statement[1])
            symbols[identifier] = Q(len(machine_code))
        elif statement[0] == 'constant':
            _, identifier, sign, numerator, denominator = statement
            identifier = set_symbol(identifier)

            if type(numerator) is str:
                numerator = get_symbol(numerator)
                numerator = symbols.get(numerator, numerator)

            if type(denominator) is str:
                denominator = get_symbol(denominator)
                denominator = symbols.get(denominator, denominator)

            if type(numerator) is not str and type(denominator) is not str:
                symbols[identifier] = Q(sign * numerator, denominator)
            else:
                errata[identifier] = sign, numerator, denominator
        elif statement[0] == 'value':
            _, sign, numerator, denominator = statement

            if type(numerator) is str:
                numerator = get_symbol(numerator)
                numerator = symbols.get(numerator, numerator)

            if type(denominator) is str:
                denominator = get_symbol(denominator)
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
