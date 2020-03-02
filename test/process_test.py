from fractions import Fraction as Q
import unittest

from underbar.assembler import assemble
from underbar.process import Process
from underbar.register import Register
from underbar.stdio import StandardStream

IR = Register.IR.value
JR = Register.JR.value
SR = Register.SR.value
FR = Register.FR.value

STDIN = Q(StandardStream.STDIN.value)
STDOUT = Q(StandardStream.STDOUT.value)


class ProcessTest(unittest.TestCase):
    def test_halt(self):
        process = Process(assemble('''

                13, hcf

        '''))

        process.run()
        self.assertEqual(process.peek(), Q(13))

    def test_call(self):
        process = Process(assemble('''

                0
                function, cal
                hcf

            function:
                13, stp
                ret

        '''))

        process.run()
        self.assertEqual(process.peek(), Q(13))

    def test_hello_world(self):
        process = Process(assemble('''

                message

            loop:
                dup, ldm
                dup
                beq + exit
                stdout, put
                inc
                bal + loop

            exit:
                0, hcf

            message:
                "Hello, World!\n", 0

        '''))

        process.run()
        self.assertEqual(process.readLine(), 'Hello, World!\n')

    def test_echo(self):
        process = Process(assemble('''

                main, cal; Run main
                hcf; Halt program

            main: .exit_code = 0, .argv = 1, .argc = 2
                0
            .loop:
                dup, ldp + .argc, sub, beq + .break; Break after last argument
                dup, beq + .first; Skip space before first argument
                " ", stdout, put; Write space to standard output
            .first:
                dup, ldp + .argv, add, ldm; Load argument
                stdout, print, cal, top - 2; Print argument to standard output
                inc, bal + .loop; Next argument
            .break:
                "\n", stdout, put; Write newline to standard output
                ret

            ; Print string to stream
            print: .stream = 0, .string = 1
                ldp + .string
            .loop:
                dup, ldm; Load character
                dup, beq + .break; Break on null character
                ldp + .stream, put; Write character to stream
                inc, bal + .loop; Next character
            .break:
                ret

        '''), args=['hello', 'world'])

        process.run()
        self.assertEqual(process.readLine(), 'hello world\n')

    def test_get_integer_line(self):
        process = Process(assemble('''

            bootstrap:
                stdin, 0, get_integer_line, cal
                hcf

            get_integer_line: .result = 0, .stream = 1
                0, stp + .result; Initialize result
                1; Positive sign
                ldp + .stream, get; First character
                dup, "-", sub, bne + .loop; If sign character
                top - 1; Discard sign character
                -1, mul; Negative sign
                ldp + .stream, get; First character after sign
            .loop:
                dup, "\n", sub, beq + .break; Break on newline
                "0", sub; Character to digit
                ldp + .result, 10, mul; Multiply result by base
                add, stp + .result; Add digit to result
                ldp + .stream, get; Next character
                bal + .loop
            .break:
                top - 1; Discard newline
                ldp + .result, mul, stp + .result; Apply sign
                ret

        '''))

        process.write('285793423\n')
        process.run()
        self.assertEqual(process.peek(), 285793423)

    def test_get_integer_line_negative(self):
        process = Process(assemble('''

            bootstrap:
                stdin, 0, get_integer_line, cal
                hcf

            get_integer_line: .result = 0, .stream = 1
                0, stp + .result; Initialize result
                1; Positive sign
                ldp + .stream, get; First character
                dup, "-", sub, bne + .loop; If sign character
                top - 1; Discard sign character
                -1, mul; Negative sign
                ldp + .stream, get; First character after sign
            .loop:
                dup, "\n", sub, beq + .break; Break on newline
                "0", sub; Character to digit
                ldp + .result, 10, mul; Multiply result by base
                add, stp + .result; Add digit to result
                ldp + .stream, get; Next character
                bal + .loop
            .break:
                top - 1; Discard newline
                ldp + .result, mul, stp + .result; Apply sign
                ret

        '''))

        process.write('-618584259\n')
        process.run()
        self.assertEqual(process.peek(), -618584259)

    def test_put_integer_line(self):
        process = Process(assemble('''

            bootstrap:
                285793423, stdout, put_integer_line, cal
                hcf

            put_integer_line: .stream = 0, .value = 1
                1
                ldp + .value, bge + .loop_1
                "-", ldp + .stream, put
                ldp + .value, neg, stp + .value
            .loop_1:
                10, mul
                dup, ldp + .value, sub, ble + .loop_1
            .loop_2:
                10, div, flr
                dup, beq + .break
                dup, ldp + .value, swp, div, flr
                "0", add, ldp + .stream, put
                dup, ldp + .value, swp, mod, stp + .value
                bal + .loop_2
            .break:
                "\n", ldp + .stream, put
                ret

        '''))

        process.run()
        self.assertEqual(process.readLine(), '285793423\n')

    def test_put_integer_line_negative(self):
        process = Process(assemble('''

            bootstrap:
                -618584259, stdout, put_integer_line, cal
                hcf

            put_integer_line: .stream = 0, .value = 1
                1
                ldp + .value, bge + .loop_1
                "-", ldp + .stream, put
                ldp + .value, neg, stp + .value
            .loop_1:
                10, mul
                dup, ldp + .value, sub, ble + .loop_1
            .loop_2:
                10, div, flr
                dup, beq + .break
                dup, ldp + .value, swp, div, flr
                "0", add, ldp + .stream, put
                dup, ldp + .value, swp, mod, stp + .value
                bal + .loop_2
            .break:
                "\n", ldp + .stream, put
                ret

        '''))

        process.run()
        self.assertEqual(process.readLine(), '-618584259\n')


if __name__ == '__main__':
    unittest.main()
