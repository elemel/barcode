from fractions import Fraction as Q
import unittest

from underbar.assembler import assemble
from underbar.process import Process


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


if __name__ == '__main__':
    unittest.main()
