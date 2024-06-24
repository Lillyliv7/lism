nasm -f elf64 -o print.o print.asm
ld -o print print.o
./print