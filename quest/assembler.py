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

    operand =
        number / character / identifier / ('(' space? expression space? ')')

    add_operator = '+' / '-'
    multiply_operator = '*' / '/'
    unary_operator = '+' / '-' / '*' / '/'

    number = ~'0|[1-9][0-9]*'
    character = ~"'(\\[^\n]|[^'])*'"
    string = ~'"(\\[^\n]|[^"])*"'
    identifier = ~'[.A-Z_a-z][.0-9A-Z_a-z]*'
    space = ~'[ \t]+'
    comment = ~';.*'
    end_of_line = ~'\n|$'
""")


class Visitor(NodeVisitor):
    def __init__(self):
        super().__init__()
        self.prefix = None

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

        if identifier.startswith('.'):
            identifier = self.prefix + identifier
        else:
            self.prefix = identifier

        return 'label', identifier

    def visit_constant(self, node, visited_children):
        [_, identifier], _, _, _, [_, expression] = visited_children

        if identifier.startswith('.'):
            identifier = self.prefix + identifier
        else:
            self.prefix = identifier

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
        elif operand[0] == 'identifier' and operand[1].startswith('.'):
            _, identifier = operand
            operand = 'identifier', self.prefix + identifier

        return operand

    def visit_add_operator(self, node, visited_children):
        return node.text

    def visit_multiply_operator(self, node, visited_children):
        return node.text

    def visit_unary_operator(self, node, visited_children):
        return node.text

    def visit_number(self, node, visited_children):
        return 'number', int(node.text)

    def visit_character(self, node, visited_children):
        # TODO: Handle escapes properly
        return 'character', node.text[1:-1].replace('\\n', '\n')

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

        ir = 0
        dr = 1
        cr = 2

        add = 5/7; add
        adi = 3/7; add_integer
        bal = 7/10; branch_always
        beq = 9/10; branch_equal
        bge = 2/5; branch_greater_equal
        bgt = 5/9; branch_greater_than
        ble = 1/10; branch_less_equal
        blt = 3/11; branch_less_than
        bne = 3/10; branch_not_equal
        cal = 5/11; call
        cls = 4/11; call_static
        del = 4/9; delete
        den = 6/11; denominator
        dis = 2/11; discard
        div = 1/9; divide
        dup = 1/5; duplicate
        ent = 1/2; enter
        fdi = 4/7; floor_divide_integer
        get = 10/11; get
        hcf = 7/9; halt
        inv = 5/6; invert
        ldd = 1/7; load_dynamic
        ldi = 0; load_integer
        ldl = 1/11; load_local
        ldr = 7/11; load_register
        lds = 8/11; load_static
        mli = 1/4; multiply_integer
        mod = 2/9; modulo
        mul = 1/8; multiply
        neg = 3/8; negate
        new = 2/3; new
        num = 4/5; numerator
        pop = 2/7; pop
        psh = 1/3; push
        put = 9/11; put
        ret = 8/9; return_
        siz = 3/4; size
        stl = 7/8; store_local
        stm = 3/5; store_memory
        str = 5/8; store_register
        sub = 1/6; subtract
        swp = 6/7; swap
        tel = 1/12; tell

        stdin = 0
        stdout = 1
        stderr = 2

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
        elif expression[0] == 'character':
            return Q(ord(expression[1]))
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
                        f'Undefined symbol or cyclic reference: '
                        f'{key} = {expression}')
                else:
                    raise Exception(
                        f'Undefined symbol: {key}: {expression}')

    return machine_code
