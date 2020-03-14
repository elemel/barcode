    pop
    message
loop:
    dup, adi - message.end, beq + break
    dup, ldm, lds + stdout, put
    adi + 1, bal + loop
break:
    pop
    0, hcf

message:
    "Hello, World!\n"
.end:
