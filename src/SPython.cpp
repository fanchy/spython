
#include "SPython.h"
#include "ExprAST.h"
#include "PyObj.h"
#include "PyCpp.h"
#include "StrTool.h"
#include "ext/PyBaseExt.h"
#include "ext/PyTupleExt.h"

using namespace std;
using namespace ff;

SPython::SPython(){
    pycontext.curstack = PyObjModule::BuildModule(pycontext, "__main__", "built-in");
    pycontext.curstack.cast<PyObjModule>()->loadFlag = PyObjModule::MOD_LOADOK;
    PyBaseExt::init(pycontext);
    PyTupleExt::init(pycontext);
}

PyObjPtr SPython::importFile(const std::string& modname){
    return PyOpsUtil::importFile(pycontext, modname, modname);
}

