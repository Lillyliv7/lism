#include <string>

class ELFFormat {
    public:
    std::string filename;
    ELFFormat(std::string);
    void writeFile();
};
