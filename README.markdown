
The Elegans Compiler
====================

C. Elegans is a compiled language like C, only more elegant.
Also, it's slow like a worm.

### Dependencies and Setup ###
Highly unfortunately, C. Elegans currently only compiles to v64 code,
which in turn only compiles to 64-bit Linux ELFs. While I hope to
change this in the near future, for now it is a reality, so you must
be running 64-bit Linux to run the results you compile.

The current Elegans compiler depends on v64, which in turn depends on
the FASM assembler. Even more stringently Elegans assumes that v64 is
on your path, and in turn v64 assumes that FASM is on your path. You
can download FASM for your system here: [http://flatassembler.net/download.php](http://flatassembler.net/download.php)

The current distributed version of v64 is in this archive.

To set up dependencies, run setup.sh. Once you have run this script,
you should be all set to run compiler.py, and start compiling code.
If you wish, you may symlink compiler.py to, for example,
/usr/bin/elg. The compiler will automatically find its "home"
directory by following argv[0] as a trail of symlinks. Therefore, you
may not hardlink elegans to /usr/bin/elg, or it won't be able to find
it's home directory any more.

### Using Elegans ###
(This assumes you ran: `ln -s /usr/bin/elg $PWD/compiler.py` during setup. Optional.)  

Elegans usage: elg [-ldc] [-(i|ii) path:path...] [-o output] path  
Options:

    -l       -- Don't produce an entry point. (library mode)
    -c       -- Produce crappy code. (no optimization)
    -d       -- Debug mode. (dumps parsing information)
    -i path  -- Add path to the end of the include search path
    -ii path -- Add path to the beginning of the include search path

### Examples ###
Are under examples/

#### Makefile notes ####
For your Makefiles you may include the patterns:

    %.o: %.elg
    	elg -l $< -o $@

    %: %.elg
    	elg $< -o $@

