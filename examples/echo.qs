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
    stdout, cls + print
    adi + 1
    dup, ldl + .argv, siz, sub, beq + .break
    ' ', stdout, put
    bal + .loop
.break:
    dis
    '\n', stdout, put
    0, ret + 1

; [string, stream] -> []
print:
.stream = 0, .string = 1
    ent + 2, stl + .stream, stl + .string
    0
.loop:
    dup, ldl + .string, siz, sub, beq + .break
    dup, ldl + .string, add, ldm
    ldl + .stream, put
    adi + 1, bal + .loop
.break:
    dis
    ret + 2
