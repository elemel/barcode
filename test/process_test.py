from fractions import Fraction as Q
import unittest

from serviam.assembler import assemble
from serviam.process import Process


class ProcessTest(unittest.TestCase):
    def test_halt(self):
        process = Process(assemble('''

            13 /halt

        '''))

        process.run()
        self.assertEqual(process.peek(), Q(13))

    def test_call(self):
        process = Process(assemble('''

                0
                function /call
                /halt

            function:
                13 /store_parameter
                /return

        '''))

        process.run()
        self.assertEqual(process.peek(), Q(13))

    def test_hello_world(self):
        process = Process(assemble('''

                message

            loop:
                /duplicate /load_memory
                /duplicate
                exit /jump_equal
                stdout /store_stream
                /increment
                loop /jump

            exit:
                0 /halt

            message:
                "Hello, World!\n" 0

        '''))

        process.run()
        self.assertEqual(process.readLine(), 'Hello, World!\n')

    def test_echo(self):
        process = Process(assemble('''

                main /call
                /halt

            main:
                0
            main_loop:
                /duplicate 2/load_parameter /subtract
                main_end /jump_equal
                /duplicate
                main_first /jump_equal
                " " stdout /store_stream
            main_first:
                /duplicate 3/load_parameter /add
                /load_memory stdout print /call
                2/discard
                /increment
                main_loop /jump
            main_end:
                "\n" stdout /store_stream
                /return

            print:
                2/load_parameter
            print_loop:
                /duplicate /load_memory
                /duplicate
                print_end /jump_equal
                /load_parameter /store_stream
                /increment
                print_loop /jump
            print_end:
                /return

        '''), args=['hello', 'world'])

        process.run()
        self.assertEqual(process.readLine(), 'hello world\n')


if __name__ == '__main__':
    unittest.main()
