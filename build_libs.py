#! /usr/bin/python

import os, sys, shutil, subprocess

print "Going to library directory..."
os.chdir( "lib" )

subdirs = os.listdir(".")

for sub in subdirs:
    try:
        print "Compiling library:", sub
        os.chdir( sub )

          # Determine the type of library
        if os.path.exists( "interface" ):
            print "  * Type: object file"
            if os.path.exists("where"):
                openfile = open("where")
                path = openfile.read().strip()
                openfile.close()
                path = os.path.abspath( os.path.expanduser( path ) )
                end_name = os.path.split( path )[1]
                print "  * Gets %s from `%s'" % (end_name, path)

                if not os.path.isfile( path ):
                    print " [X] No such file"
                    raise Exception

                shutil.copyfile( path, end_name )

        if os.path.exists("main.asm"):
            print "  * Type: assembler"
            cmd = ["fasm", "main.asm"]
            print " ".join(cmd)
            x = subprocess.Popen( cmd )
            x.wait()

            print " Done"

        if os.path.exists("main.v64"):
            print "  * Type: v64"
            cmd = ["v64", "-l", "main.v64", "-o", "main.o"]
            print " ".join(cmd)
            x = subprocess.Popen( cmd )
            x.wait()

            print " Done"

        if os.path.exists("main.elg"):
            print "  * Type: pure Elegans"
            print " Done"

        os.chdir( ".." )

    except:
        os.chdir( ".." )

