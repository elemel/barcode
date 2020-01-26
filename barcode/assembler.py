from fractions import Fraction as Q
from sys import stderr, stdin

from parsimonious.grammar import Grammar, NodeVisitor

grammar = Grammar(r"""
    program = line*

    line =
        space? (label space?)?
        (statement (space? ',' space? statement)* space?)?
        comment? end_of_line

    statement = constant / expression / string

    label = identifier space? ':'
    constant = identifier space? '=' space? expression

    expression =
        multiply_expression (space? add_operator space? multiply_expression)*

    multiply_expression =
        unary_expression (space? multiply_operator space? unary_expression)*

    unary_expression = (unary_operator space?)* operand
    operand = number / identifier / ('(' space? expression space? ')')

    add_operator = '+' / '-'
    multiply_operator = '*' / '/'
    unary_operator = '+' / '-' / '*' / '/'

    number = ~'0|[1-9][0-9]*'
    string = ~'"(\\[^\n]|[^"])*"'
    identifier = ~'[.A-Z_a-z][.0-9A-Z_a-z]*'
    space = ~'[ \t]+'
    comment = ~';.*'
    end_of_line = ~'\n|$'
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
        _, label, statements, _, _ = visited_children

        if label:
            [[label, _]] = label
            line.append(label)

        if statements:
            [[[statement], statements, _]] = statements
            line.append(statement)

            for statement in statements:
                _, _, _, [statement] = statement
                line.append(statement)

        return line

    def visit_label(self, node, visited_children):
        [_, identifier], _, _ = visited_children
        return 'label', identifier

    def visit_constant(self, node, visited_children):
        [_, identifier], _, _, _, [_, expression] = visited_children
        return 'constant', identifier, expression

    def visit_expression(self, node, visited_children):
        expression, expressions = visited_children

        if not expressions:
            return 'expression', expression

        result = ['binary', expression]

        for expression in expressions:
            [_, operator, _, expression] = expression
            result.append(operator)
            result.append(expression)

        return 'expression', result

    def visit_multiply_expression(self, node, visited_children):
        expression, expressions = visited_children

        if not expressions:
            return expression

        result = ['binary', expression]

        for expression in expressions:
            [_, operator, _, expression] = expression
            result.append(operator)
            result.append(expression)

        return result

    def visit_unary_expression(self, node, visited_children):
        operators, operand = visited_children

        if not operators:
            return operand

        result = ['unary']

        for operator in operators:
            [operator, _] = operator
            result.append(operator)

        result.append(operand)
        return result

    def visit_operand(self, node, visited_children):
        [operand] = visited_children

        if type(operand) is list:
            [_, _, [_, operand], _, _] = operand

        return operand

    def visit_add_operator(self, node, visited_children):
        return node.text

    def visit_multiply_operator(self, node, visited_children):
        return node.text

    def visit_unary_operator(self, node, visited_children):
        return node.text

    def visit_number(self, node, visited_children):
        return 'number', int(node.text)

    def visit_string(self, node, visited_children):
        # TODO: Handle escapes properly
        return 'string', node.text[1:-1].replace('\\n', '\n')

    def visit_identifier(self, node, visited_children):
        return 'identifier', node.text

    def visit_whitespace(self, node, visited_children):
        return 'space', ' '

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

    def evaluate(expression):
        if expression[0] == 'binary':
            left = evaluate(expression[1])

            if left is None:
                return None

            for i in range(2, len(expression), 2):
                right = evaluate(expression[i + 1])

                if right is None:
                    return None

                operator = expression[i]

                if operator == '+':
                    left += right
                elif operator == '-':
                    left -= right
                elif operator == '*':
                    left *= right
                elif operator == '/':
                    left /= right
                else:
                    raise Exception(f'Invalid binary operator: {operator}')

            return left
        elif expression[0] == 'unary':
            result = evaluate(expression[-1])

            if result is None:
                return None

            for i in range(len(expression) - 2, 0, -1):
                operator = expression[i]

                if operator == '+':
                    pass
                elif operator == '-':
                    result = -result
                elif operator == '*':
                    pass
                elif operator == '/':
                    result = 1 / result
                else:
                    raise Exception(f'Invalid unary operator: {operator}')

            return result
        elif expression[0] == 'number':
            return Q(expression[1])
        elif expression[0] == 'identifier':
            return symbols.get(expression[1])
        else:
            raise Exception(f'Invalid expression type: {expression[0]}')

    for statement in intermediate_code:
        if statement[0] == 'label':
            _, identifier = statement
            symbols[identifier] = Q(len(machine_code))
        elif statement[0] == 'constant':
            _, identifier, expression = statement
            value = evaluate(expression)

            if value is not None:
                symbols[identifier] = value
            else:
                errata[identifier] = expression
        elif statement[0] == 'expression':
            _, expression = statement
            value = evaluate(expression)

            if value is not None:
                machine_code.append(value)
            else:
                errata[len(machine_code)] = expression
                machine_code.append(Q(0))
        elif statement[0] == 'string':
            for char in statement[1]:
                machine_code.append(Q(ord(char)))
        else:
            raise Exception(f'Invalid statement type: {statement[0]}')

    while errata:
        for key, expression in errata.items():
            value = evaluate(expression)

            if value is not None:
                if type(key) is str:
                    symbols[key] = value
                else:
                    machine_code[key] = value

                del errata[key]
                break
        else:
            for key, expression in errata.items():
                if type(key) is str:
                    raise Exception(
                        f'Undefined symbol or cyclic reference: {key}')

    return machine_code


if __name__ == '__main__':
    for q in assemble(stdin.read()):
        print(q)
