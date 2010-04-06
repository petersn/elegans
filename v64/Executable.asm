format ELF64

public _start
public bre
public main
public Arguments

include 'tmp/externs.asm'

section '.code' executable

_start:
main:

  nop

bre:

include 'tmp/code.asm'

   ; For safety, include magic exit code
   ; Unclean, but so much more safe
  mov rdi, 1     ; exit code 1, as something (probably) went wrong if we got here
  mov eax, 60    ; sys_exit
  syscall

section '.data' writable

include 'tmp/data.asm'

Arguments dq 16 dup 0

