#include <iostream>
#include <fstream>
#include <string>
#include <stdint.h>

#include "./include/generate_elf.hh"

int main(int argc, char** argv) {
    std::cout << "Starting Assembly" << std::endl;

    ELFFormat myelf("hi");
    myelf.writeFile();
}
