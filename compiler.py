#! /usr/bin/python

import os, sys

cwd = os.getcwd()

  # Figure out where the binary probably lives, and therefore where its home directory is
guess = sys.argv[0]
guess = os.path.abspath( guess )
while os.path.islink(guess):
    guess = os.path.abspath( os.readlink(guess) )
  # Assume the home directory is the one in which the binary actually lives
homedir = os.path.dirname( guess )

  # Uncomment this next line if you want to install elegans in ~/.elegans
#homedir = os.path.join( os.path.expanduser("~"), ".elegans" )

sys.path.append( homedir )

import operators as module_operators
from operators import table as operator_table
from operators import rereferenced_table, rereferencing

usage_msg = "usage: %s [-ldc] [-(i|ii) path:path...] [-o output] path"

def test_args(*a):
    if len(a) == 1 and type(a[0]) == int:
        n, m = a[0], None
    elif len(a) == 1 and type(a[0]) == str:
        n, m = 1000000, a[0]
    else:
        n, m = a

    if len(sys.argv) < n:
        print usage_msg % sys.argv[0]
        if m:
            print m
        raise SystemExit

operators = set( ("+", "*", "-", "/", "%", ":","!", "=", "**", ";", "]", "`", "~", "[",
                    #"$",
                  ">", "<", "==", "!=", ">=", "<=", "and", "or", "@") )

arities = {
              #Basic
            "+" : 2, "*" : 2, "-" : 2, "/" : 2, "=" : 2, "**" : 2, ";" : 1, "]" : 1, "`" : 1, "~" : 1, "@" : 2, "%" : 2,

            #"$" : 1,

              #Comparison
            ">" : 2, "<" : 2, "==" : 2, "!=" : 2, ">=" : 2, "<=" : 2,

              #Logic
            "and" : 2, "or" : 2,
          }

  #The number of arguments to the left of an operator with variable number of arguments
arity_offset = {
                  ":" : 1,
                  "!" : 1,
                  "[" : 0,
               }

  #Used for determining argument spacing
  #The same as ordinary arities, but also knows about upgradable operators
max_arities = arities.copy()
max_arities[";"] = 2
max_arities["]"] = 2

upgrade = set( (";", "]") )

left_associative  = set( (
                          "+", "*", "-", "/", ";", "]", "%",
                          ">", "<", "==", "!=", ">=", "<=",
                          "|",
                          "and", "or",
                          "@",
                          ) )
right_associative = set( (
                          "=", "**", ":", "!", "(", "`", "~",
                           # "$",
                          ) )

presidence = {
                "+" : 6, "-" : 6, "*" : 7, "/" : 7, "%" : 8, "**" : 8, "`" : 10, "~" : 10, ":" : 3, "!" : 3, "=" : 2, "[" : 1.5, ";" : 1, "]" : 1,
                 #"$" : 12,
                ">" : 5, "<" : 5, "==" : 5, "!=" : 5, ">=" : 5, "<= " : 5,
                "and" : 4, "or" : 4, 
                "@" : 11
             }

groupers   = set( ("(", ")", "{", "}") )

opposite   = { ")" : "(", "}" : "{"}

delimiters = set( (" ", "\n") + tuple(operators) + tuple(groupers) )

ignored_symbols = set( ("", "\n", " ") )

preserved_separators = set( ("}",) )

type_table = {
                 #Special symbols
               "(" : "open", ")" : "close",
               "{" : "open", "}" : "close",
               #"[" : "open", "]" : "close",
             }

for operator in operators:
    type_table[operator] = "operator"

escape_table = {
                 "n"  : "\n",
                 "r"  : "\r",
                 "\\" : "\\",
                 "\"" : "\"",
                 "0"  : "\0",
                 "h"  : "Hello, world!\n",
               }

include_prefixes = [ ".", os.path.join( homedir, "lib" ) ]

def typeof(x):
    if type(x) == tuple:
        return "token"
    elif x in type_table:
        return type_table[x]
    else:
        return "token"

  #Uses shunting yard
  #  Output is of the form: [ (type, name, arity) ... ]
def parse( symbols ):
    output = []

    oper_stack = []

    tokens = 0

    for s in symbols:
        t = typeof(s)

        #print "%s:" % (tokens), s, "of type", t, "with stack:", oper_stack

        if t == "token":

            #print "Token on:", oper_stack
            if oper_stack and oper_stack[-1][0] in upgrade:
                #print "Incrementing."
                oper_stack[-1][2] += 1

              #XXX: WARNING: This was moved after the above while loop from before!
            output.append( ( "token", s, None ) )

              #XXX: WATCH OUT! I changed this to tokens+2 from tokens+1. I have no idea if this is correct...
            while oper_stack and oper_stack[-1][0] in max_arities and tokens+1 >= oper_stack[-1][3] + max_arities[oper_stack[-1][0]]:
                op = oper_stack.pop()

                #print "Forced push, as argument space detected:", op

                if op[0] in upgrade:
                    #print "Upgraded value being retunred A:", op
                    arity = op[2]
                elif op[0] in arities:
                    arity = arities[ op[0] ]
                    #arity = op[2]
                else:
                    arity = tokens-op[2]+arity_offset[ op[0] ]

                tokens -= arity
                tokens += 1
                output.append( ( "op", op[0], arity ) )

            tokens += 1
        elif t == "open":
            oper_stack.append( (s, t, None) )
        elif t == "close":
            while oper_stack[-1][0] != opposite[s]:
                op = oper_stack.pop()

                if op[0] in upgrade:
                    #print "Upgraded value being retunred B:", op
                    arity = op[2]
                elif op[0] in arities:
                    arity = arities[ op[0] ]
                    #arity = op[2]
                else:
                    arity = tokens-op[2]+arity_offset[ op[0] ]

                tokens -= arity
                tokens += 1
                output.append( ( "op", op[0], arity ) )

            oper_stack.pop()

              #xx: Warning: Makes the assumption that all parens give one token
            if oper_stack and oper_stack[-1][0] in upgrade:
                oper_stack[-1][2] += 1

            if s in preserved_separators:
                output.append( ("op", s, 1) )
        elif t == "operator":
            while oper_stack and not oper_stack[-1][1] in ("open",) and \
                ( s in left_associative and presidence[s] <= presidence[oper_stack[-1][0]] or \
                  s in right_associative and presidence[s] < presidence[oper_stack[-1][0]] ):

                op = oper_stack.pop()

                if op[0] in upgrade:
                    #print "Upgraded value being retunred C:", op
                    arity = op[2]
                elif op[0] in arities:
                    arity = arities[ op[0] ]
                    #arity = op[2]
                else:
                    arity = tokens-op[2]+arity_offset[ op[0] ]

                tokens -= arity
                tokens += 1
                output.append( ( "op", op[0], arity ) )

            if s in arities:
                oper_stack.append( [s, t, arities[s], tokens] )
            else:
                oper_stack.append( [s, t, tokens, tokens] )

    while oper_stack:
        op = oper_stack.pop()

        if op[0] in upgrade:
            #print "Upgraded value being retunred D:", op
            arity = op[2]
        elif op[0] in arities:
            arity = arities[ op[0] ]
            #arity = op[2]
        else:
            arity = tokens-op[2]+arity_offset[ op[0] ]

        tokens -= arity
        tokens += 1
        output.append( ( "op", op[0], arity ) )

    return output

  #Takes a set of parsed postfix symbols, and converts them to a symbolic tree
def symbolize_tree( postfix ):
    postfix = postfix[::-1]

    tree = [ "tree", [] ]
    work_stack = [ tree ]
    depths = []

    for t, s, arity in postfix:

        if t == "op":
            work_stack[-1][-1].insert( 0, [s, []] )
            work_stack.append( work_stack[-1][-1][0] )
            depths.append( arity )
        if t == "token":
            work_stack[-1][-1].insert( 0, s )
            while work_stack and depths and len(work_stack[-1][-1]) == depths[-1]:
                work_stack.pop()
                depths.pop()

    return tree

  #Returns the character defined by an escape value
def string_escape( ch ):
    if ch in escape_table:
        return escape_table[ch]
    else:
        return "\\"+ch

  #Delimits the entire text, and applies minor preprocessing
def delimit( data ):
    output = []
    collected = ""

    state = "normal"

    for ch in data:

        if state == "normal":
            if ch == "#":
                if collected not in ignored_symbols:
                    output.append( collected )
                collected = ""
                state = "comment"
            elif ch == '"':
                collected = ""
                state = "string"
            elif ch in delimiters:
                if collected not in ignored_symbols:
                    output.append( collected )
                if ch not in ignored_symbols:
                    output.append( ch )
                collected = ""
            else:
                collected += ch

        elif state == "comment":
            if ch == "\n":
                state = "normal"

        elif state == "string":
            if ch == "\\":
                state = "string-escape"
            elif ch == '"':
                output.append( (str, collected) )
                collected = ""
                state = "normal"
            else:
                collected += ch

        elif state == "string-escape":
            collected += string_escape( ch )
            state = "string"

    if collected not in ignored_symbols:
        output.append( collected )

    return output

tag_count = 0
def Tag():
    global tag_count
    tag_count += 1
    return "tag%s" % (tag_count)

module_operators.Tag = Tag

constant_table = {
                     #Standard functions
                   #"if" : "defs_if", "while" : "defs_while",

                     #Library calls
                        #sys
                   #"exit" : "sys:exit", "write" : "sys:write", 
                        #std
                   #"print" : "std:print", "out" : "std:stringprint",
                        #mm
                   #"alloc" : "mm:alloc", "free" : "mm:free", "realloc" : "mm:realloc",

                    "wordsize" : "wordbytes",

                 }

var_table      = { }

alpha_underscore = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_"
alpha_numerics_underscore = alpha_underscore + "0123456789"

def valid_word( x ):
    return x[0] in alpha_underscore and all( i in alpha_numerics_underscore for i in x[1:] )

bindings_stack = [ ]

def _generate( tree, rereference = False ):
    global bindings_stack

      #If it's a string, and starts with a $, then it's a bound variable, and we should respond appropriately
    if type(tree) == str and tree[0] == "$":
        tree = tree[1:]
        if len(bindings_stack) == 0:
            print "Bound variable %s out side of scope" % tree
            raise SystemExit
        bindings_stack[-1].add( tree )

      #There are only a few things to test if the value is to be rereferenced
      #Get that out of the way, and otherwise do the normal tests
    if rereference:
        if type(tree) == str:
            if tree in var_table:
                return "  push; %s\n" % (var_table[tree])
            elif valid_word( tree[0] ):
                tag = Tag()
                var_table[tree] = tag
                return "  push; %s\n  buffer; %s:1\n" % (tag, tag)
        elif tree[0] in rereferenced_table:
            output = ""
            for i, v in enumerate(tree[1]):
                output += _generate( v, (i in rereferencing.get( tree[0], (lambda l : ()) )(len(tree[1])) ) )
            return output + rereferenced_table[ tree[0] ]( len(tree[1]) )

        print "Unreferencable: %s" % (tree)
        raise SystemExit

    if type(tree) == str:
        if tree in var_table:
            #print "Var access to:", tree
            return "  mov; %s, r0\n  <; r0, r0\n  push; r0\n" % (var_table[tree])
        elif tree in constant_table:
            #print "Constant access to:", tree
            return "  push; %s\n" % (constant_table[tree])
        elif valid_word( tree[0] ):
            tag = Tag()
            var_table[tree] = tag
            return "  mov; %s, r0\n  <; r0, r0\n  push; r0\n  buffer; %s:1\n" % (tag, tag)
        else:
            return "  push; l%s\n" % (int(tree))
    elif tree[0] in operator_table:
        output = ""
        for i, v in enumerate(tree[1]):
            output += _generate( v, (i in rereferencing.get( tree[0], (lambda l : ()) )(len(tree[1])) ) )
        return output + operator_table[ tree[0] ]( len(tree[1]) )
    elif tree[0] == "}":
        beginningtag, endtag = Tag(), Tag()
        output = "  jump; %s\n label; %s\n" % (endtag, beginningtag)

        bindings_stack.append( set() )

        for i, v in enumerate(tree[1]):
            output += _generate( v, (i in rereferencing.get( tree[0], (lambda l : ()) )(len(tree[1])) ) )

        bound_up = bindings_stack.pop()

        if not bound_up:
            output += "  pop; r0\n  ret; r0, l0\n  return;\n label; %s\n  push; %s\n" % (endtag, beginningtag)

        else:
            buffer_size = 1 + len( bound_up )*2 + 1
            output += "  pop; r0\n  ret; r0, l0\n  return;\n label; %s\n  mul; l%s, wordbytes, r0\n  mm:alloc; r0\n  arg; l0, r0\n  >; %s, r0\n  push; r0\n" % (endtag, buffer_size, beginningtag)
            for i in bound_up:
                output += "  add; wordbytes, r0\n  mov; %s, r1\n  >; r1, r0\n  <; r1, r1\n  add; wordbytes, r0\n  >; r1, r0\n" % ( var_table[i] )

            output += "  add; wordbytes, r0\n  >; l0, r0\n"

            if flags["debug"]:
                print "Made binding of:", bound_up

        return output
    elif tree[0] == str:
        tag = Tag()
        return "  buffer; %s:d%s.0\n  push; %s\n" % (tag, ".".join( str(ord(i)) for i in tree[1] ), tag)
    else:
        print "Unknown tree segment: %s" % repr(tree)
        raise SystemExit

def generate( tree ):
    #output = "include; sys, std, mm\n\n mm:init;\n  push; l0\n"
    output = ""
    output += _generate( tree )
    return output

def pretty( x ):
    if type(x) == list:
        return "(%s %s %s)" % ( pretty(x[1][0]), x[0], " ".join( pretty(i) for i in x[1][1:] ) )
    elif type(x) == tuple:
        return repr(x[1])
    elif type(x) == str:
        return x

include_cache = set()
def include_file( path ):
    path = path.strip()
    if path in include_cache:
        return " # Already included file %s" % (repr(path))
    include_cache.add( path )

    path = os.path.expanduser( path )

    result_path = None

    if path[0] == "/":
        result_path = path

    else:
        for prefix in flags["includes"]:
            test_path = os.path.join( prefix, path )
            if os.path.isfile( test_path ):
                result_path = test_path
                break
            test_path = os.path.join( prefix, path, "main.elg" )
            if os.path.isfile( test_path ):
                result_path = test_path
                break

    if result_path == None:
        print "Couldn't find '%s' to include" % ( path )
        raise SystemExit

    openfile = open( result_path )
    data = openfile.read()
    openfile.close()

    return preprocess( data )

link_cache = set()
def link_file( path ):
    path = path.strip()
    if path in link_cache:
        return " # Already linked file %s" % (repr(path))
    link_cache.add( path )

    path = os.path.expanduser( path )

    if path[0] == "/":
        object_path = os.path.join( path, "main.o" )
        interface_path = os.path.join( path, "interface" )

    else:
        for prefix in flags["includes"]:
            object_path = os.path.join( prefix, path, "main.o" )
            interface_path = os.path.join( prefix, path, "interface" )
            if os.path.isfile( object_path ) and os.path.isfile( interface_path ):
                break

    if not (os.path.isfile( object_path ) and os.path.isfile( interface_path )):
        print "Couldn't find '%s' to link in" % ( path )
        raise SystemExit

    use = ""

    openfile = open( interface_path )
    for line in openfile:
        line = line.split("#")[0].strip()
        if not line: continue
        if "--" in line:
            objname, realname = line.split("--")
            objname, realname = objname.strip(), realname.strip()
            constant_table[realname] = objname
            use += "uses; %s\n" % (objname)
        elif "-$-" in line:
            objname, realname = line.split("-$-")
            objname, realname = objname.strip(), realname.strip()
            var_table[realname] = objname
            use += "uses; %s\n" % (objname)

    flags["link"].append( object_path )

    return use

def preprocess( source ):
    global header
    output = []
    source = source.split("\n")
    for line in source:
        if line[:10] == "--include ":
            output.append( include_file( line[10:] ) )
        elif line[:7] == "--link ":
            header += link_file( line[7:] )
        else:
            output.append( line )
    return "\n".join( output )

def Compile( path ):
    global header

    try:
        openfile = open( path )
        data = openfile.read()
        openfile.close()
    except:
        print "%s: No such file or directory" % (path)
        raise SystemExit

    header = ""

    if os.path.isfile( os.path.join( homedir, "elgrc" ) ):
        data = include_file( os.path.join( homedir, "elgrc" ) ) + "\n" + data
    else:
        print "Warning: no elgrc file"

    data = preprocess( data )

    if flags["debug"]:
        print data
    #print constant_table

    symbols = delimit( data )
    if flags["debug"]:
        print symbols

    parsed = parse( symbols )
    if flags["debug"]:
        print parsed

    #print " ".join( str(i[1]) for i in parsed )

    tree = symbolize_tree( parsed )
    #print tree
    #print

    if flags["debug"]:
        print pretty(tree)
        print

    code = generate(tree)

    #print code

    return code

if __name__ == "__main__":
    import sys

    flags = {
                "object"   : False,
                "dest"     : "main",
                "debug"    : False,
                "optimize" : True,
                "includes" : include_prefixes,
                "link"     : [],
            }

    test_args(2)

    while True:
        for i, arg in enumerate(sys.argv[1:]):
            i += 1
            if arg == "-l":
                flags["object"] = True
                flags["dest"]   = "main.o"
                sys.argv.pop(i)
                break
            if arg == "-d":
                flags["debug"] = True
                sys.argv.pop(i)
                break
            if arg == "-c":
                flags["optimize"] = False
                sys.argv.pop(i)
                break

            if arg == "-o":
                if len(sys.argv)-1 <= i:
                    test_args("  no path specified after -o")
                sys.argv.pop(i)
                flags["dest"] = sys.argv.pop(i)
                break

            if arg == "-i":
                if len(sys.argv)-1 <= i:
                    test_args("  no paths specified after -i")
                sys.argv.pop(i)
                for p in sys.argv.pop(i).split(":"):
                    flags["includes"].append( p )
                break

            if arg == "-ii":
                if len(sys.argv)-1 <= i:
                    test_args("  no paths specified after -ii")
                sys.argv.pop(i)
                for p in sys.argv.pop(i).split(":"):
                    flags["includes"].insert( 0, p )
        else:
            break

    test_args(2, "  no file specified, only options")

    if len( sys.argv ) > 2:
        test_args("  too many arguments given")

    code = Compile( sys.argv[1] )

    if flags["optimize"]:
        import optimizer
        code = optimizer.optimize( code )

    os.chdir( homedir )

    #print constant_table

    #openfile = open( "ref/header.v64" )
    #headercode = openfile.read()
    #openfile.close()

    #code = code + headercode

    openfile = open( "tmp/code.v64", "w" )
    openfile.write( header )
    openfile.write( code )
    openfile.close()

    linkcode = ""
    if flags["link"]:
        linkcode = "-i \"%s\" " % (":".join(flags["link"]))

    if flags["object"]:
        os.system( "v64 -l %s-o /tmp/elg-out tmp/code.v64" % (linkcode))
    else:
        os.system( "v64 %s-o /tmp/elg-out tmp/code.v64" % (linkcode))

    os.chdir( cwd )

    os.rename("/tmp/elg-out", flags["dest"])

