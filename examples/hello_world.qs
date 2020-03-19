    dis
    message
loop:
    dup, adi - message.end, beq + break
    dup, ldd, stdout, put
    adi + 1, bal + loop
break:
    dis
    0, hcf

message:
    "Hello, World!\n"
.end:
