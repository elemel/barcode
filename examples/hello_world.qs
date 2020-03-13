    message

loop:
    dup, ldm
    dup
    beq + exit
    ldi + stdout, put
    adi + 1
    bal + loop

exit:
    0, hcf

message:
    "Hello, World!\n"
.end:
