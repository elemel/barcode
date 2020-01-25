from fractions import Fraction as Q
import unittest

from barcode.assembler import assemble
from barcode.process import Process


class ProcessTest(unittest.TestCase):
    def test_halt(self):
        process = Process(assemble('''

            13 /hcf

        '''))

        process.run()
        self.assertEqual(process.peek(), Q(13))

    def test_call(self):
        process = Process(assemble('''

                0
                function /cal
                /hcf

            function:
                13 /stp
                /ret

        '''))

        process.run()
        self.assertEqual(process.peek(), Q(13))

    def test_hello_world(self):
        process = Process(assemble('''

                message

            loop:
                /dup /ldm
                /dup
                exit /jeq
                stdout /sts
                /inc
                loop /jmp

            exit:
                0 /hcf

            message:
                "Hello, World!\n" 0

        '''))

        process.run()
        self.assertEqual(process.readLine(), 'Hello, World!\n')

    def test_echo(self):
        process = Process(assemble('''

                main /cal
                /hcf

            main:
                0
            .loop:
                /dup 2/ldp /sub
                .end /jeq
                /dup
                .first /jeq
                " " stdout /sts
            .first:
                /dup 3/ldp /add
                /ldm stdout print /cal
                2/dis
                /inc
                .loop /jmp
            .end:
                "\n" stdout /sts
                /ret

            print:
                2/ldp
            .loop:
                /dup /ldm
                /dup
                .end /jeq
                /ldp /sts
                /inc
                .loop /jmp
            .end:
                /ret

        '''), args=['hello', 'world'])

        process.run()
        self.assertEqual(process.readLine(), 'hello world\n')


if __name__ == '__main__':
    unittest.main()
