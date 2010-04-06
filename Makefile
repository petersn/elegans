# Extremely simple installation Makefile for Elegans

BINDIR=/usr/bin

default:
	# To install FASM, v64, and Elegans, run: make install

install:
	# Placing binaries into $(BINDIR)
	ln -s `pwd`/fasm/fasm $(BINDIR)/fasm
	ln -s `pwd`/v64/compiler.py $(BINDIR)/v64
	ln -s `pwd`/compiler.py $(BINDIR)/elg 
	v64/build_libs.sh
	python build_libs.py

remove-bins:
	rm $(BINDIR)/fasm $(BINDIR)/v64 $(BINDIR)/elg

