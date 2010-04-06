#! /usr/bin/python

usage_msg = "usage: %s [-l] [-a arch] [-i path:path...] [-o output] path"

import os

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
 
if __name__ == "__main__":

    import sys

    cwd = os.getcwd()

      # Figure out where the binary probably lives, and therefore where its home directory is
    guess = sys.argv[0]
    guess = os.path.abspath( guess )
    while os.path.islink(guess):
        guess = os.path.abspath( os.readlink(guess) )
      # Assume the home directory is the one in which the binary actually lives
    homedir = os.path.dirname( guess )

      # Uncomment this next line if you want to install v64 in ~/.v64
    #homedir = os.path.join( os.path.expanduser("~"), ".v64" )

    sys.path.append( homedir )

    flags = {
                "object" : False,
                "dest"   : "main",
                "arch"   : "x64",
                "link"   : []
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
            if arg == "-a":
                if len(sys.argv)-1 <= i:
                    test_args("  no architecture specified after -a")
                sys.argv.pop(i)
                flags["arch"] = sys.argv.pop(i)
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
                    flags["link"].append( p )
                break
        else:
            break

    test_args(2, "  no file specified, only options")

    try:
        arch      = __import__("arch.%s" % (flags["arch"]))
        lib       = getattr(arch, flags["arch"])
        lib.lib_directory = os.path.join(homedir, "lib")
        table     = getattr(lib, "table")
        simple    = getattr(lib, "simple")
        translate = getattr(lib, "translate")
        assemble  = getattr(lib, "assemble")
    except:
        test_args("  no architecture: %s" % flags["arch"])

    openfile = open( sys.argv[1] )
    data = openfile.read()
    openfile.close()

    code, data, externs, includes = assemble( data )

    for path in includes:
        flags["link"].append( path )

    os.chdir( homedir )

    openfile = open( "tmp/code.asm", "w" )
    openfile.write( code )
    openfile.close()

    openfile = open( "tmp/data.asm", "w" )
    openfile.write( data )
    openfile.close()

    openfile = open( "tmp/externs.asm", "w" )
    openfile.write( externs )
    openfile.close()

    #os.realsystem = os.system

    #def ns( x ):
        #print "Calling:", x
        #os.realsystem(x)

    #os.system = ns

    if flags["object"]:
        os.system("fasm Library.asm")
        os.system("mv Library.o /tmp/v64-out")
    else:
        os.system("fasm Executable.asm")
        os.system("ld Executable.o %s-o /tmp/v64-out" % "".join( '"%s" ' % i for i in flags["link"]) )
        os.system("rm Executable.o")

    os.chdir( cwd )

    os.rename("/tmp/v64-out", flags["dest"])

