#! /bin/sh

echo "Building v64 libraries"

cd v64
cd lib

echo "  * sys"
cd sys
fasm main.asm
cd ..

echo "  * std"
cd std
python ../../compiler.py -l main.v64 -o main.o
cd ..

echo "  * mm"
cd mm
python ../../compiler.py -l main.v64 -o main.o
cd ..

