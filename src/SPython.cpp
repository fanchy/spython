
#include "SPython.h"
#include "ExprAST.h"
#include "PyObj.h"
#include "PyCpp.h"
#include "StrTool.h"
#include "ext/PyBaseExt.h"

using namespace std;
using namespace ff;

SPython::SPython(){
    pycontext.curstack = new PyObjModule("__main__", "built-in");
    PyBaseExt::init(pycontext);
}

PyObjPtr SPython::importFile(const std::string& modname){
    return PyOpsUtil::importFile(pycontext, modname, modname);
}

