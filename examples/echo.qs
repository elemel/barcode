    cli + main; Run main
    hcf; Halt program

; [argv] -> [exit_code]
main:
    dup, siz, beq + .break; Break if empty
.loop:
    dup, get; Next argument
    lds + stdout, cli + print; Print argument to standard output
    dup, siz, beq + .break; Break if empty
    ' ', lds + stdout, put; Write space to standard output
    bal + .loop
.break:
    pop
    '\n', lds + stdout, put; Write newline to standard output
    0, ret

; [string, stream] -> []
print:
.stream = 0
    ent + 1
    stl + .stream
.loop:
    dup, siz, beq + .break; Break if empty
    dup, get; Next character
    ldl + .stream, put; Write character to stream
    bal + .loop
.break:
    pop
    ret + 1
