#include "MyLib.h"

MyLib::MyLib()
{
    getUsage();
}

std::string MyLib::getUsage()
{
    std::string usage = "Hello! \n"
    "The only function available in this Library is: \n"
    "\t\t void libraryFunction() : which just prints a test message to the screen\n";

    return usage;
}

void MyLib::libraryFunction()
{
    std::cout << "Hello from the SO Library!" << std::endl;
    std::cout << "MyLib::libraryFunction() -> hello, world!" << std::endl;
}