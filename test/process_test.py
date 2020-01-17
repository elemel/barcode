from fractions import Fraction as Q
import unittest

from serviam.assembly import assemble, assemble_text
from serviam.opcode import Opcode
from serviam.process import Process
from serviam.register import Register
from serviam.standard_stream import StandardStream

ADD = Opcode.ADD.value
CALL = Opcode.CALL.value
COPY = Opcode.COPY.value
DISCARD = Opcode.DISCARD.value
HALT = Opcode.HALT.value
INCREMENT = Opcode.INCREMENT.value
JUMP = Opcode.JUMP.value
JUMP_FALSE = Opcode.JUMP_FALSE.value
LOAD = Opcode.LOAD.value
LOAD_PARAMETER = Opcode.LOAD_PARAMETER.value
RETURN = Opcode.RETURN.value
STORE_PARAMETER = Opcode.STORE_PARAMETER.value
SUBTRACT = Opcode.SUBTRACT.value
WRITE = Opcode.WRITE.value

STDIN = StandardStream.INPUT.value
STDOUT = StandardStream.OUTPUT.value


class ProcessTest(unittest.TestCase):
    def test_halt(self):
        process = Process([
            Q(13), HALT,
        ])

        process.run()
        self.assertEqual(process.peek(), Q(13))

    def test_call(self):
        process = Process(assemble([
            0,
            'function', CALL,
            HALT,

            ['function'],
            13,
            STORE_PARAMETER,
            RETURN,
        ]))

        process.run()
        self.assertEqual(process.peek(), Q(13))

    def test_hello_world(self):
        process = Process(assemble([
            'message',

            ['loop'],
            COPY, LOAD,
            COPY,
            'exit', JUMP_FALSE,
            STDOUT, WRITE,
            INCREMENT,
            'loop', JUMP,

            ['exit'],
            0, HALT,

            ['message'],
            {'Hello, World!\n'}, 0,
        ]))

        process.run()
        self.assertEqual(process.readLine(), 'Hello, World!\n')

    def test_echo(self):
#         assemble_text("""    main call
#     halt

# main:
#     0
# main_loop:
#     duplicate 2*load_parameter subtract
#     main_end jump_false
#     duplicate
#     main_first jump_false
#     " " stdout write
# main_first:
#     duplicate 3*load_parameter add
#     load stdout print call
#     2*discard
#     increment
#     main_loop jump
# main_end:
#     "\n" stdout write
#     return

# print:
#     2*load_parameter
# print_loop:
#     duplicate load
#     duplicate
#     print_end jump_false
#     load_parameter write
#     increment
#     print_loop jump
# print_end:
#     return
# """)

        process = Process(assemble([
            'main', CALL,
            HALT,

            ['main'],
            0,

            ['main.loop'],
            COPY, LOAD_PARAMETER * 2, SUBTRACT,
            'main.return', JUMP_FALSE,
            COPY,
            'main.first', JUMP_FALSE,
            {' '}, STDOUT, WRITE,

            ['main.first'],
            COPY, LOAD_PARAMETER * 3, ADD,
            LOAD, STDOUT, 'print', CALL,
            DISCARD * 2,
            INCREMENT,
            'main.loop', JUMP,

            ['main.return'],
            {'\n'}, STDOUT, WRITE,
            RETURN,

            ['print'],
            LOAD_PARAMETER * 2,

            ['print.loop'],
            COPY, LOAD,
            COPY,
            'print.return', JUMP_FALSE,
            LOAD_PARAMETER, WRITE,
            INCREMENT,
            'print.loop', JUMP,

            ['print.return'],
            RETURN,
        ]), args=['hello', 'world'])

        process.run()
        self.assertEqual(process.readLine(), 'hello world\n')


if __name__ == '__main__':
    unittest.main()
