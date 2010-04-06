#! /usr/bin/python

import os, random

table  = {
           "r0" : "r8",
           "r1" : "r9",
           "r2" : "r10",
           "r3" : "r11",
           "r4" : "r12",
           "r5" : "r13",
           "r6" : "r14",
           "r7" : "r15",
           "rx" : "rdx",

              #Constants
           "NULL"      : "0",
           "False"     : "0",
           "True"      : "1",
           "wordbytes" : "1",
           "wordbits"  : "8",
         }

simple = {

             #Arithmetic
           "mov"    : "  mov <2>, <1>\n",
           "add"    : "  add <2>, <1>\n",
           "neg"    : "  neg <1>\n",
           "|add"   : "  adc <2>, <1>\n",
           "sub"    : "  sub <2>, <1>\n",
           "|sub"   : "  sbb <2>, <1>\n",
           "xor"    : "  xor <2>, <1>\n",
           "and"    : "  and <2>, <1>\n",
           "or"     : "  or <2>, <1>\n",
           "<<"     : "  shl <2>, <1>\n",
           ">>"     : "  shr <2>, <1>\n",
           "mul"    : "  xor rdx, rdx\n  mov rax, <1>\n  mov rbx, <2>\n  mul rbx\n  mov <3>, rax\n",
           "div"    : "  xor rdx, rdx\n  mov rax, <1>\n  mov rbx, <2>\n  div rbx\n  mov <3>, rax\n",

             #Memory access
           "push"   : "  pushq <1>\n",
           "pop"    : "  popq <1>\n",
           ">"      : "  mov qword [<2>], <1>\n",
           "<"      : "  mov <2>, qword [<1>]\n",
           "<b"     : "  xor rax, rax\n  mov al, byte [<1>]\n  mov <2>, rax\n",
           ">b"     : "  mov rax, <1>\n  mov byte [<2>], al\n",
           "arg"    : "  mov rax, <1>\n  shl rax, 3\n  add rax, Arguments\n  mov <2>, qword [rax]\n",
           "ret"    : "  mov rax, <2>\n  shl rax, 3\n  add rax, Arguments\n  mov qword [rax], <1>\n",
           #"arg"    : "  mov <2>, [Arguments + (8*<1>)]\n",

             #Flow control
           "jump"   : "  jmp <1>\n",
           "if"     : "  cmp <1>, 0\n  jne <2>\n",
           "return" : "  ret\n",
           #"call"   : "  call <1>\n",

              #Comparison operators
           "?>"     : "  cmp <1>, <2>\n  mov <3>, 1\n  jg @f\n  dec <3>\n @@:\n",
           "?<"     : "  cmp <1>, <2>\n  mov <3>, 1\n  jl @f\n  dec <3>\n @@:\n",
           "?="     : "  cmp <1>, <2>\n  mov <3>, 1\n  je @f\n  dec <3>\n @@:\n",
           "?!="    : "  cmp <1>, <2>\n  mov <3>, 1\n  jne @f\n  dec <3>\n @@:\n",
           "?>="    : "  cmp <1>, <2>\n  mov <3>, 1\n  jge @f\n  dec <3>\n @@:\n",
           "?<="    : "  cmp <1>, <2>\n  mov <3>, 1\n  jle @f\n  dec <3>\n @@:\n",

         }

def translate(x):
    if x in table:
        return table[x]
    elif x[0] == "$":
        return x[1:]
    elif x[0] == "l":
        return str(int(x[1:]))
    elif ":" in x:
        return "%s_%s" % tuple(x.split(":"))
    elif True:
        return "%s_%s" % (libname, x)
    else:
        print "Unknown value: %s" % x
        raise SystemExit

def assemble(code):
    global libname

    code = code.replace(" ","").split("\n")

    output, data, externs = "", "", ""

    includes = set()

    libname = ""

    for op in code:

        op = op.split("#")[0]

        if not op:
            continue

          #Move instuction
        if "->" in op:
            source, destination = op.split("->")
            output += "  mov %s, %s\n" % ( translate(destination), translate(source) )
            continue

        try:
            op, operands = op.split(";")
        except:
            print "Invalid syntax: %s" % op
            raise SystemExit

        if op == "include":

            operands = operands.split(",")

            for lib in operands:

                includes.add( os.path.expanduser( os.path.join("~", "lib", "v64", lib, "main.o") ) )
                externs += "include '%s'\n" % ( os.path.expanduser( os.path.join("~", "lib", "v64", lib, "declares.asm") ) )

                  #Dep files not used, as they were an ill-thought-out idea

#                depfile = open( os.path.expanduser( os.path.join("~", "lib", "v64", lib, "depends") ) )
#                for line in depfile:
#                    line = line.split("#")[0].strip()
#                    if not line: continue
#                    if line.split(" ")[0] == "WARNING:" and len(line.split(" ")) > 1:
#                        print "Warning from library %s: %s" % (lib, " ".join(line.split(" ")[1:]))
#                        continue
#                    includes.add( os.path.expanduser( os.path.join("~", "lib", "v64", line, "main.o") ) )
#                    externs += "include '%s'\n" % ( os.path.expanduser( os.path.join("~", "lib", "v64", line, "declares.asm") ) )
#                depfile.close()

        elif op == "libname":
            libname = operands

        elif op == "defines":

            if libname == "":
                insult = ""
                if random.randint(0, 1000) == 0:
                    insult = ", dumbass"
                print "Define a library name before exporting symbols%s" % (insult)

            operands = operands.split(",")

            for operand in operands:
                externs += "public %s_%s\n" % (libname, operand)

        elif op == "label":

            operands = operands.split(",")

            for operand in operands:
                output += "%s_%s:\n" % (libname, operand)

        elif op == "buffer":
            operands = operands.split(",")

            for operand in operands:
                name, init = operand.split(":", 1)

                if init[0] == "l":
                    data += "%s_%s dq %s\n" % (libname, name, init[1:])
                elif init[0] == "s":
                    data += "%s_%s db %s, 0\n" % (libname, name, ", ".join( str(ord(i)) for i in init[1:] ))
                elif init[0] == "d":
                    data += "%s_%s db %s\n" % (libname, name, ", ".join( str(int(i)) for i in init[1:].split(".") ) )
                else:
                    data += "%s_%s rq %s\n" % (libname, name, int(init))

        elif op in simple:

            operands = operands.split(",")

            o = simple[op]

            if operands != [""]:
                for i, operand in enumerate(operands):
                    o = o.replace( "<%i>" % (i+1), translate(operand) )

            output += o
            continue

        elif ":" in op:
            lib, op = op.split(":")

            operands = operands.split(",")
            if operands != [""]:
                for i, operand in enumerate(operands):
                    output += "  mov qword [Arguments + %s], %s\n" % (i*8, translate(operand))

            output += "  call %s_%s\n" % (lib, op)

        elif op == "call":

            operands = operands.split(",")
            if operands != [""]:
                for i, operand in enumerate(operands[1:]):
                    output += "  mov qword [Arguments + %s], %s\n" % (i*8, translate(operand))

            output += "  call %s\n" % (translate(operands[0]))

    return output, data, externs, includes

