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
                exit, jeq
                stdout, put
                inc
                loop, str + jr

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

            main: main.exit_code = 0, main.argc = 1, main.argv = 2
                0
            main.loop:
                dup, ldp + main.argc, sub, main.break, jeq; Break after last argument
                dup, main.first, jeq; Skip space before first argument
                " ", stdout, put; Write space to standard output
            main.first:
                dup, ldp + main.argv, add, ldm; Load argument
                stdout, print, cal, top - 2; Print argument to standard output
                inc, main.loop, str + jr; Next argument
            main.break:
                "\n", stdout, put; Write newline to standard output
                ret

            ; Print string to stream
            print: print.stream = 0, print.string = 1
                ldp + print.string
            print.loop:
                dup, ldm; Load character
                dup, print.break, jeq; Break on null character
                ldp + print.stream, put; Write character to stream
                inc, print.loop, str + jr; Next character
            print.break:
                ret

        '''), args=['hello', 'world'])

        process.run()
        self.assertEqual(process.readLine(), 'hello world\n')


if __name__ == '__main__':
    unittest.main()
