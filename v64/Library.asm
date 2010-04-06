format ELF64

extrn Arguments
extrn _end

include 'tmp/externs.asm'

section '.code' executable

include 'tmp/code.asm'

section '.data' writable

include 'tmp/data.asm'

