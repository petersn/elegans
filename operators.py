#! /usr/bin/python

def add( l ):
    output = "  pop; r1\n"
    for i in xrange(l-1):
        output += "  pop; r0\n  add; r0, r1\n"
    output += "  push; r1\n"
    return output

def multiply( l ):
    output = "  pop; r1\n"
    for i in xrange(l-1):
        output += "  pop; r0\n  mul; r0, r1, r1\n"
    output += "  push; r1\n"
    return output

def subtract( l ):
    output = "  pop; r0\n"
    for i in xrange(l-1):
        output += "  pop; r1\n  sub; r0, r1\n"
    output += "  push; r1\n"
    return output

def divide( l ):
    output = "  pop; r0\n"
    for i in xrange(l-1):
        output += "  pop; r1\n  div; r1, r0, r1\n"
    output += "  push; r1\n"
    return output

def modulo( l ):
    output = "  pop; r0\n"
    for i in xrange(l-1):
        output += "  pop; r1\n  div; r1, r0, r1\n  mov; rx, r1\n"
    output += "  push; r1\n"
    return output

def assign( l ):
    return "  pop; r0\n  pop; r1\n  >; r0, r1\n  push; r0\n"

def addr_of( l ):
    return ""

def bind( l ):
    output = ""
    for i in xrange( l ):
        output += "  pop; r0\n  arg; l%s, r1\n  >; r1, r0\n" % (l-i-1)
    output += "  push; l0\n"
    return output

#def fetch_arg( l ):
#    return "  pop; r0\n  arg; r0, r0\n  push; r0\n"

def fetch( l ):
    return "  pop; r0\n  <; r0, r0\n  push; r0\n"

def rr_fetch( l ):
    return ""

def at_fetch( l ):
    return "  pop; r0\n  pop; r1\n  mul; r0, wordbytes, r0\n  add; r0, r1\n  <; r1, r1\n  push; r1\n"

def rr_at_fetch( l ):
    return "  pop; r0\n  pop; r1\n  mul; r0, wordbytes, r0\n  add; r0, r1\n  push; r1\n"

def greater_than( l ):
    return "  pop; r0\n  pop; r1\n  ?>; r1, r0, r0\n  push; r0\n"

def less_than( l ):
    return "  pop; r0\n  pop; r1\n  ?<; r1, r0, r0\n  push; r0\n"

def equals( l ):
    return "  pop; r0\n  pop; r1\n  ?=; r1, r0, r0\n  push; r0\n"

def not_equals( l ):
    return "  pop; r0\n  pop; r1\n  ?!=; r1, r0, r0\n  push; r0\n"

def greater_than_equals( l ):
    return "  pop; r0\n  pop; r1\n  ?>=; r1, r0, r0\n  push; r0\n"

def less_than_equals( l ):
    return "  pop; r0\n  pop; r1\n  ?<=; r1, r0, r0\n  push; r0\n"

def logical_and( l ):
    return "  pop; r0\n  pop; r1\n  and; r1, r0\n  push; r0\n"

def logical_or( l ):
    return "  pop; r0\n  pop; r1\n  or; r1, r0\n  push; r0\n"

registers = ["r0", "r1", "r2", "r3", "r4", "r5", "r6", "r7"]

def call( l ):
    output = ""
    for i in xrange(l-1, -1, -1):
        output += "  pop; %s\n" % ( registers[i] )
    output += "  call; %s\n  arg; l0, r0\n  push; r0\n" % ( ", ".join( registers[:l] ) )
    return output

def call_closure( l ):
    newtag = Tag()
    output = ""
    for i in xrange(l-2, -1, -1):
        output += "  pop; r0\n  ret; r0, l%s" % ( i )
    output += """
  pop; r4
  mov; r4, r0
  <; r0, r1
  label; <tag>_a
    add; wordbytes, r0
    <; r0, r2
    ?=; r2, l0, r3
    if; r3, <tag>_b
      <; r2, r3
      push; r3
      add; wordbytes, r0
      <; r0, r3
      >; r3, r2
    jump; <tag>_a
  label; <tag>_b
  push; r0
  push; r4
  call; r1
  pop; r1
  pop; r0
  label; <tag>_c
    sub; wordbytes, r0
    ?=; r0, r1, r3
    if; r3, <tag>_d
      sub; wordbytes, r0
      <; r0, r2
      pop; r3
      >; r3, r2
    jump; <tag>_c
  label; <tag>_d
  arg; l0, r0
  push; r0
"""
    return output.replace("<tag>", newtag)

def tree( l ):
    return "  pop; r0\n  call; r0\n  arg; l0, r0\n  sys:exit; r0\n"

def semicolon( l ):
    if l == 0:
        return "  # Note: Strange semi-colon with null arguments..."
    if l == 1:
        return ""
    elif l == 2:
        return "  pop; r0\n  pop; r1\n  push; r0\n"
    print "Warning: Semi-colon with argument count:", l

table = {
          ":"  : call,
          "!"  : call_closure,
          "+"  : add,
          "*"  : multiply,
          "-"  : subtract,
          "/"  : divide,
          "%"  : modulo,

          "="  : assign,
          "`"  : fetch,
          "~"  : addr_of,
          #"$"  : fetch_arg,
          "["  : bind,
          ";"  : semicolon,
          "]"  : semicolon,

          ">"  : greater_than,
          "<"  : less_than,
          "==" : equals,
          "!=" : not_equals,
          ">=" : greater_than_equals,
          "<=" : less_than_equals,

          "and" : logical_and,
          "or"  : logical_or,

          "@"  : at_fetch,

          "tree" : tree,
        }

rereferenced_table = {
                        "`" : rr_fetch,
                        "@" : rr_at_fetch,
                     }

rereferencing = {
                   "=" : lambda x : (0,),
                   "~" : lambda x : (0,),
                   "[" : lambda l : range(l),
                }

