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

            main: main.exit_code = 0, main.argv = 1, main.argc = 2
                0
            main.loop:
                dup, ldp + main.argc, sub, beq + main.break; Break after last argument
                dup, beq + main.first; Skip space before first argument
                " ", stdout, put; Write space to standard output
            main.first:
                dup, ldp + main.argv, add, ldm; Load argument
                stdout, print, cal, top - 2; Print argument to standard output
                inc, bal + main.loop; Next argument
            main.break:
                "\n", stdout, put; Write newline to standard output
                ret

            ; Print string to stream
            print: print.stream = 0, print.string = 1
                ldp + print.string
            print.loop:
                dup, ldm; Load character
                dup, beq + print.break; Break on null character
                ldp + print.stream, put; Write character to stream
                inc, bal + print.loop; Next character
            print.break:
                ret

        '''), args=['hello', 'world'])

        process.run()
        self.assertEqual(process.readLine(), 'hello world\n')


if __name__ == '__main__':
    unittest.main()
