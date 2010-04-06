#! /usr/bin/python

track = ["r0", "r1", "r2", "r3", "r4", "r5", "r6", "r7"]

def stack_optimize( code ):
    stack = []   #Entry: ( source, [], codepoint )

    for x in xrange(len( code )):
        line = code[x]
        if line[:8] != "  push; " and line[:7] != "  pop; ":
            stack = []
        elif line[:8] == "  push; ":
            for i in stack:
                i[1].append( line[8:].strip() )
            stack.append( [ line[8:], [], x ] )
        elif line[:7] == "  pop; " and stack:
            target = line[7:]
            if stack:
                source = stack.pop()
                if not target in source[1] and not source[0] in source[1]:  #Nothing affected, straight move
                    if source[0] != target:
                        code[ source[2] ] = "  mov; %s, %s" % (source[0], target)
                    else:
                        code[ source[2] ] = None
                    code[x] = None
                if target in source[1] and not source[0] in source[1]:      #Target affected, local move
                    code[ source[2] ] = ""
                    code[x] = "  mov; %s, %s" % (source[0], target)
                if not target in source[1] and source[0] in source[1]:      #Source affected, straight move
                    code[ source[2] ] = "  mov; %s, %s" % (source[0], target)
                    code[x] = None
            for i in stack:
                i[1].append( target.strip() )

    return code

def same_value_optimize( code ):
    holds = { }
    value_id = 0

    for x in xrange(len( code )):
        line = code[x]
        if line[:7] != "  mov; ":
            holds = { }
        else:
            source, dest = line[7:].split(",")
            source, dest = source.strip(), dest.strip()
            if source not in holds:
                value_id += 1
                holds[source] = value_id
            if dest in holds and holds[dest] == holds[source]:
                code[x] = None
            holds[dest] = holds[source]

    return code

def optimize( code ):

    code = code.split("\n")

        #Optimization stages:

      #1) Stack optimization: Remove pushes followed by pops, and more complicated operations
    code = stack_optimize( code )

    while None in code:
        code.remove( None )

      #2) Same value optimization: Remove instructions that put a value somewhere it already is
    code = same_value_optimize( code )

    while None in code:
        code.remove( None )

        #End optimization

    code = "\n".join( code )

    return code

  #Simple test case if run directly
if __name__ == "__main__":
    start_code = "  push; r0\n  pop; r1\n  push; r1\n  pop; r0\n"

    print "Code to optimize:"
    print start_code

    optimized = optimize( start_code )

    print "Optimized code:"
    print optimized

