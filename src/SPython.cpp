
#include "SPython.h"
#include "ExprAST.h"

using namespace std;
using namespace ff;

SPython::SPython(){
}

PyObjPtr SPython::importFile(const std::string& modname){
    return PyOpsUtil::importFile(pycontext, modname, modname);
}

