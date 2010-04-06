format ELF64

public sys_exit
public sys_read
public sys_write
public sys_open
public sys_close
public sys_brk
public sys_nanosleep

extrn Arguments

section '.code' executable

sys_exit:

  mov rdi, [Arguments + 0]  ; Exit code
  mov eax,60    ; sys_exit
  syscall

sys_read:

  pushq r11

  mov rdi, [Arguments + 0]  ; File descriptor
  mov rdx, [Arguments + 8]  ; Data length
  mov rsi, [Arguments + 16] ; Data pointer
  mov eax, 0    ; sys_read
  syscall

  popq r11

  ret

sys_write:

  pushq r11

  mov rdi, [Arguments + 0]  ; File descriptor
  mov rdx, [Arguments + 8]  ; Data length
  mov rsi, [Arguments + 16] ; Data pointer
  mov eax, 1    ; sys_write
  syscall

  popq r11

  ret

sys_open:

  pushq r11

  mov rdi, [Arguments + 0]  ; Path string pointer
  mov rsi, [Arguments + 8]  ; Flags for opening the new file
  mov rdx, [Arguments + 16]  ; Mode for (potentially) newly created file
  mov eax, 2    ; sys_open
  syscall

  mov [Arguments + 0], rax  ; File descriptor

  popq r11

  ret

sys_close:

  pushq r11

  mov rdi, [Arguments + 0]  ; File descriptor
  mov eax, 3    ; sys_close
  syscall

  popq r11

  ret

sys_brk:

  pushq r11

  mov rdi, [Arguments + 0]  ; Break point
  mov eax, 12    ; sys_brk
  syscall

  mov [Arguments + 0], rax  ; Returned pointer

  popq r11

  ret

sys_nanosleep:

  pushq r11

  mov rdi, [Arguments + 0]  ; Sleep structure
  mov rsi, [Arguments + 8]  ; Remaining sleep structure
  mov eax, 35     ; sys_nanosleep
  syscall

  popq  r11

  ret

section '.data' writable

