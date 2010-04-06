format ELF64

public example_increment

extrn Arguments

section '.code' executable

  ;Simple function to generate a "random" number
example_increment:

  mov rax, [Arguments + 0] ;Read the first argument

  inc rax

  mov [Arguments + 0], rax ;Write the value back as the first return

  ret

section '.data' writable

example_variable dq 42  ;Initialized public variable

