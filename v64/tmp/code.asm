  ; libname;mm
  ; defines;init,resize,alloc,free,realloc,dump_structure,getsize
  ; defines;memalloc
  ; include;sys,std
  ; label;init
mm_init:
  ; push;r0
  pushq r8
  ; push;r1
  pushq r9
  ; sys:brk;l0
  mov qword [Arguments + 0], 0
  call sys_brk
  ; arg;l0,r0
  mov r8, qword [Arguments + (8*0)]
  ; >;r0,eompointer
  mov qword [mm_eompointer], r8
  ; >;r0,second_to_last
  mov qword [mm_second_to_last], r8
  ; mov;l4096,r0
  mov r8, 4096
  ; >;r0,memalloc
  mov qword [mm_memalloc], r8
  ; mm:resize;r0
  mov qword [Arguments + 0], r8
  call mm_resize
  ; <;eompointer,r0
  mov r8, qword [mm_eompointer]
  ; mov;r0,r1
  mov r9, r8
  ; add;wordbytes,r1
  add r9, 8
  ; >;r1,second_to_last
  mov qword [mm_second_to_last], r9
  ; >;r1,r0
  mov qword [r8], r9
  ; sub;wordbytes,r0
  sub r8, 8
  ; add;l4096,r0
  add r8, 4096
  ; >;r0,r1
  mov qword [r9], r8
  ; >;r0,r0
  mov qword [r8], r8
  ; pop;r1
  popq r9
  ; pop;r0
  popq r8
  ; return;
  ret
  ; label;resize
mm_resize:
  ; push;r0
  pushq r8
  ; push;r1
  pushq r9
  ; arg;l0,r0
  mov r8, qword [Arguments + (8*0)]
  ; <;eompointer,r1
  mov r9, qword [mm_eompointer]
  ; add;r0,r1
  add r9, r8
  ; sys:brk;r1
  mov qword [Arguments + 0], r9
  call sys_brk
  ; >;r0,memalloc
  mov qword [mm_memalloc], r8
  ; sub;wordbytes,r1
  sub r9, 8
  ; >;r1,r1
  mov qword [r9], r9
  ; <;second_to_last,r0
  mov r8, qword [mm_second_to_last]
  ; >;r1,r0
  mov qword [r8], r9
  ; pop;r1
  popq r9
  ; pop;r0
  popq r8
  ; return;
  ret
  ; label;alloc
mm_alloc:
  ; push;r0
  pushq r8
  ; push;r1
  pushq r9
  ; push;r2
  pushq r10
  ; push;r3
  pushq r11
  ; push;r4
  pushq r12
  ; push;r5
  pushq r13
  ; push;r6
  pushq r14
  ; arg;l0,r4
  mov r12, qword [Arguments + (8*0)]
  ; ?<;r4,l0,r0
  cmp r12, 0
  mov r8, 1
  jl @f
  dec r8
 @@:
  ; if;r0,alloc_error
  cmp r8, 0
  jne mm_alloc_error
  ; add;wordbytes,r4
  add r12, 8
  ; sub;l1,r4
  sub r12, 1
  ; div;r4,wordbytes,r1
  xor rdx, rdx
  mov rax, r12
  mov rbx, 8
  idiv rbx
  mov r9, rax
  ; sub;rx,r4
  sub r12, rdx
  ; add;wordbytes,r4
  add r12, 8
  ; add;wordbytes,r4
  add r12, 8
  ; label;alloc_loop
mm_alloc_loop:
  ; <;eompointer,r1
  mov r9, qword [mm_eompointer]
  ; <;r1,r2
  mov r10, qword [r9]
  ; <;r2,r3
  mov r11, qword [r10]
  ; label;alloc_next_frame
mm_alloc_next_frame:
  ; mov;r3,r0
  mov r8, r11
  ; sub;r2,r0
  sub r8, r10
  ; sub;wordbytes,r0
  sub r8, 8
  ; ?<;r0,r4,r0
  cmp r8, r12
  mov r8, 1
  jl @f
  dec r8
 @@:
  ; if;r0,alloc_frame_skip
  cmp r8, 0
  jne mm_alloc_frame_skip
  ; mov;r2,r5
  mov r13, r10
  ; add;wordbytes,r5
  add r13, 8
  ; mov;r2,r6
  mov r14, r10
  ; add;r4,r6
  add r14, r12
  ; >;r5,r2
  mov qword [r10], r13
  ; >;r6,r5
  mov qword [r13], r14
  ; >;r3,r6
  mov qword [r14], r11
  ; <;r3,r0
  mov r8, qword [r11]
  ; ?!=;r3,r0,r0
  cmp r11, r8
  mov r8, 1
  jne @f
  dec r8
 @@:
  ; if;r0,alloc_not_last_frame
  cmp r8, 0
  jne mm_alloc_not_last_frame
  ; >;r6,second_to_last
  mov qword [mm_second_to_last], r14
  ; label;alloc_not_last_frame
mm_alloc_not_last_frame:
  ; add;wordbytes,r5
  add r13, 8
  ; ret;r5,l0
  mov qword [Arguments + (8*0)], r13
  ; jump;alloc_return
  jmp mm_alloc_return
  ; label;alloc_frame_skip
mm_alloc_frame_skip:
  ; mov;r3,r1
  mov r9, r11
  ; <;r1,r2
  mov r10, qword [r9]
  ; <;r2,r3
  mov r11, qword [r10]
  ; ?!=;r2,r3,r0
  cmp r10, r11
  mov r8, 1
  jne @f
  dec r8
 @@:
  ; if;r0,alloc_next_frame
  cmp r8, 0
  jne mm_alloc_next_frame
  ; mm:increase_heap;
  call mm_increase_heap
  ; arg;l0,r0
  mov r8, qword [Arguments + (8*0)]
  ; ?!=;r0,l0,r0
  cmp r8, 0
  mov r8, 1
  jne @f
  dec r8
 @@:
  ; if;r0,alloc_loop
  cmp r8, 0
  jne mm_alloc_loop
  ; label;alloc_error
mm_alloc_error:
  ; ret;l0,l0
  mov qword [Arguments + (8*0)], 0
  ; label;alloc_return
mm_alloc_return:
  ; pop;r6
  popq r14
  ; pop;r5
  popq r13
  ; pop;r4
  popq r12
  ; pop;r3
  popq r11
  ; pop;r2
  popq r10
  ; pop;r1
  popq r9
  ; pop;r0
  popq r8
  ; return;
  ret
  ; label;free
mm_free:
  ; push;r0
  pushq r8
  ; push;r1
  pushq r9
  ; push;r2
  pushq r10
  ; push;r3
  pushq r11
  ; arg;l0,r0
  mov r8, qword [Arguments + (8*0)]
  ; sub;wordbytes,r0
  sub r8, 8
  ; <;eompointer,r1
  mov r9, qword [mm_eompointer]
  ; <;r1,r2
  mov r10, qword [r9]
  ; <;r2,r1
  mov r9, qword [r10]
  ; label;free_loop
mm_free_loop:
  ; ?=;r0,r1,r3
  cmp r8, r9
  mov r11, 1
  je @f
  dec r11
 @@:
  ; if;r3,free_loop_break
  cmp r11, 0
  jne mm_free_loop_break
  ; <;r1,r2
  mov r10, qword [r9]
  ; <;r2,r1
  mov r9, qword [r10]
  ; ?=;r1,r2,r3
  cmp r9, r10
  mov r11, 1
  je @f
  dec r11
 @@:
  ; if;r3,free_error
  cmp r11, 0
  jne mm_free_error
  ; jump;free_loop
  jmp mm_free_loop
  ; label;free_loop_break
mm_free_loop_break:
  ; <;r1,r1
  mov r9, qword [r9]
  ; <;r1,r1
  mov r9, qword [r9]
  ; >;r1,r2
  mov qword [r10], r9
  ; <;r1,r0
  mov r8, qword [r9]
  ; ?!=;r1,r0,r3
  cmp r9, r8
  mov r11, 1
  jne @f
  dec r11
 @@:
  ; if;r3,free_not_last_frame
  cmp r11, 0
  jne mm_free_not_last_frame
  ; >;r2,second_to_last
  mov qword [mm_second_to_last], r10
  ; label;free_not_last_frame
mm_free_not_last_frame:
  ; ret;l1,l0
  mov qword [Arguments + (8*0)], 1
  ; label;free_return
mm_free_return:
  ; pop;r3
  popq r11
  ; pop;r2
  popq r10
  ; pop;r1
  popq r9
  ; pop;r0
  popq r8
  ; return;
  ret
  ; label;free_error
mm_free_error:
  ; ret;l0,l0
  mov qword [Arguments + (8*0)], 0
  ; jump;free_return
  jmp mm_free_return
  ; label;realloc
mm_realloc:
  ; push;r0
  pushq r8
  ; push;r1
  pushq r9
  ; push;r2
  pushq r10
  ; arg;l0,r0
  mov r8, qword [Arguments + (8*0)]
  ; arg;l1,r1
  mov r9, qword [Arguments + (8*1)]
  ; mm:alloc;r1
  mov qword [Arguments + 0], r9
  call mm_alloc
  ; arg;l0,r2
  mov r10, qword [Arguments + (8*0)]
  ; std:copy;r0,r2,r1
  mov qword [Arguments + 0], r8
  mov qword [Arguments + 8], r10
  mov qword [Arguments + 16], r9
  call std_copy
  ; ret;r2,l0
  mov qword [Arguments + (8*0)], r10
  ; pop;r2
  popq r10
  ; pop;r1
  popq r9
  ; pop;r0
  popq r8
  ; return;
  ret
  ; label;dump_structure
mm_dump_structure:
  ; push;r0
  pushq r8
  ; push;r1
  pushq r9
  ; push;r2
  pushq r10
  ; push;r3
  pushq r11
  ; <;eompointer,r3
  mov r11, qword [mm_eompointer]
  ; mov;r3,r1
  mov r9, r11
  ; label;dump_structure_loop
mm_dump_structure_loop:
  ; mov;r1,r0
  mov r8, r9
  ; sub;r3,r0
  sub r8, r11
  ; std:print;r0
  mov qword [Arguments + 0], r8
  call std_print
  ; std:putch;l10
  mov qword [Arguments + 0], 10
  call std_putch
  ; <;r1,r2
  mov r10, qword [r9]
  ; ?!=;r1,r2,r0
  cmp r9, r10
  mov r8, 1
  jne @f
  dec r8
 @@:
  ; mov;r2,r1
  mov r9, r10
  ; if;r0,dump_structure_loop
  cmp r8, 0
  jne mm_dump_structure_loop
  ; std:putch;l10
  mov qword [Arguments + 0], 10
  call std_putch
  ; pop;r3
  popq r11
  ; pop;r2
  popq r10
  ; pop;r1
  popq r9
  ; pop;r0
  popq r8
  ; return;
  ret
  ; label;increase_heap
mm_increase_heap:
  ; push;r0
  pushq r8
  ; <;memalloc,r0
  mov r8, qword [mm_memalloc]
  ; add;r0,r0
  add r8, r8
  ; mm:resize;r0
  mov qword [Arguments + 0], r8
  call mm_resize
  ; ret;r0,l0
  mov qword [Arguments + (8*0)], r8
  ; pop;r0
  popq r8
  ; return;
  ret
  ; label;getsize
mm_getsize:
  ; push;r0
  pushq r8
  ; push;r1
  pushq r9
  ; arg;l0,r0
  mov r8, qword [Arguments + (8*0)]
  ; sub;wordbytes,r0
  sub r8, 8
  ; <;r0,r1
  mov r9, qword [r8]
  ; sub;r0,r1
  sub r9, r8
  ; ret;r1,l0
  mov qword [Arguments + (8*0)], r9
  ; pop;r1
  popq r9
  ; pop;r0
  popq r8
  ; return;
  ret
  ; buffer;eompointer:1
  ; buffer;second_to_last:1
  ; buffer;memalloc:1
