from fractions import Fraction as Q
import unittest

from quest.assembler import assemble
from quest.process import Process
from quest.register import Register
from quest.stdio import StandardStream

STDIN = StandardStream.STDIN.value
STDOUT = StandardStream.STDOUT.value
STDERR = StandardStream.STDERR.value


class ProcessTest(unittest.TestCase):
    def test_halt(self):
        process = Process(assemble('''

                13, hcf

        '''))

        process.run()
        self.assertEqual(process.pop_data(), Q(13))

    def test_call(self):
        process = Process(assemble('''

                cls + function
                hcf

            function:
                13, ret

        '''))

        process.run()
        self.assertEqual(process.pop_data(), Q(13))

    def test_hello_world(self):
        process = Process(assemble('''

                dis
                message
            loop:
                dup, adi - message.end, beq + break
                dup, ldm, lds + stdout, psh
                adi + 1, bal + loop
            break:
                dis
                0, hcf

            message:
                "Hello, World!\n"
            .end:

        '''))

        process.run()
        self.assertEqual(process.read(), 'Hello, World!\n')

    def test_print(self):
        process = Process(assemble('''

                message, lds + stdout, cls + print
                13, hcf

            ; [stream, string] -> []
            print: .stream = 0
                ent + 1
                stl + .stream
            .loop:
                dup, ldm; Load character
                dup, beq + .break; Break on null character
                ldl + .stream, psh; Write character to stream
                adi + 1, bal + .loop; Next character
            .break:
                dis, dis
                ret + 1

            message:
                "Hello, World!\n", 0

        '''))

        process.run()
        self.assertEqual(process.pop_data(), Q(13))
        self.assertEqual(process.read(), 'Hello, World!\n')

    def test_echo(self):
        process = Process(assemble('''

                cls + main; Run main
                hcf; Halt program

            ; [argv] -> [exit_code]
            main:
            .argv = 0
                ent + 1, stl + .argv
                0
                dup, ldl + .argv, siz, sub, beq + .break
            .loop:
                dup, ldl + .argv, add, ldm
                lds + stdout, cls + print
                adi + 1
                dup, ldl + .argv, siz, sub, beq + .break
                ' ', lds + stdout, psh
                bal + .loop
            .break:
                dis
                '\n', lds + stdout, psh
                0, ret + 1

            ; [string, stream] -> []
            print:
            .stream = 0, .string = 1
                ent + 2, stl + .stream, stl + .string
                0
            .loop:
                dup, ldl + .string, siz, sub, beq + .break
                dup, ldl + .string, add, ldm
                ldl + .stream, psh
                adi + 1, bal + .loop
            .break:
                dis
                ret + 2

        '''), argv=['hello', 'world'])

        process.run()
        self.assertEqual(process.read(), 'hello world\n')

    def test_get_integer_line(self):
        process = Process(assemble('''

                lds + stdin, cls + get_integer_line
                hcf

            ; [stream] -> [result]
            get_integer_line: .stream = 0, .result = 1
                ent + 2, stl + .stream
                0, stl + .result; Initialize result
                1; Positive sign
                ldl + .stream, pop; First character
                dup, adi - '-', bne + .loop; If sign character
                dis; Discard sign character
                neg; Negative sign
                ldl + .stream, pop; First character after sign
            .loop:
                dup, adi - '\n', beq + .break; Break on newline
                adi - '0'; Character to digit
                ldl + .result, mli + 10; Multiply result by base
                add, stl + .result; Add digit to result
                ldl + .stream, pop; Next character
                bal + .loop
            .break:
                dis; Discard newline
                ldl + .result, mul, stl + .result; Apply sign
                ldl + .result, ret + 2

        '''))

        process.write('285793423\n')
        process.run()
        self.assertEqual(process.pop_data(), 285793423)

    def test_get_integer_line_negative(self):
        process = Process(assemble('''

                lds + stdin, cls + get_integer_line
                hcf

            ; [stream] -> [result]
            get_integer_line: .stream = 0, .result = 1
                ent + 2, stl + .stream
                0, stl + .result; Initialize result
                1; Positive sign
                ldl + .stream, pop; First character
                dup, adi - '-', bne + .loop; If sign character
                dis; Discard sign character
                neg; Negative sign
                ldl + .stream, pop; First character after sign
            .loop:
                dup, adi - '\n', beq + .break; Break on newline
                adi - '0'; Character to digit
                ldl + .result, mli + 10; Multiply result by base
                add, stl + .result; Add digit to result
                ldl + .stream, pop; Next character
                bal + .loop
            .break:
                dis; Discard newline
                ldl + .result, mul, stl + .result; Apply sign
                ldl + .result, ret + 2

        '''))

        process.write('-618584259\n')
        process.run()
        self.assertEqual(process.pop_data(), -618584259)

    def test_put_integer_line(self):
        process = Process(assemble('''

                285793423, lds + stdout, cls + put_integer_line
                hcf

            ; [stream, value] -> []
            put_integer_line: .stream = 0, .value = 1
                ent + 2, stl + .stream, stl + .value
                1
                ldl + .value, bge + .loop_1
                '-', ldl + .stream, psh
                ldl + .value, neg, stl + .value
            .loop_1:
                mli + 10
                dup, ldl + .value, sub, ble + .loop_1
            .loop_2:
                fdi + 10
                dup, beq + .break
                dup, ldl + .value, swp, div, fdi + 1
                adi + '0', ldl + .stream, psh
                dup, ldl + .value, swp, mod, stl + .value
                bal + .loop_2
            .break:
                '\n', ldl + .stream, psh
                ret + 2

        '''))

        process.run()
        self.assertEqual(process.read(), '285793423\n')

    def test_put_integer_line_negative(self):
        process = Process(assemble('''

                -618584259, lds + stdout, cls + put_integer_line
                hcf

            ; [stream, value] -> []
            put_integer_line: .stream = 0, .value = 1
                ent + 2, stl + .stream, stl + .value
                1
                ldl + .value, bge + .loop_1
                '-', ldl + .stream, psh
                ldl + .value, neg, stl + .value
            .loop_1:
                mli + 10
                dup, ldl + .value, sub, ble + .loop_1
            .loop_2:
                fdi + 10
                dup, beq + .break
                dup, ldl + .value, swp, div, fdi + 1
                adi + '0', ldl + .stream, psh
                dup, ldl + .value, swp, mod, stl + .value
                bal + .loop_2
            .break:
                '\n', ldl + .stream, psh
                ret + 2

        '''))

        process.run()
        self.assertEqual(process.read(), '-618584259\n')


if __name__ == '__main__':
    unittest.main()
