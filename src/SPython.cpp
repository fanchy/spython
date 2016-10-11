
#include "SPython.h"
#include "ExprAST.h"
#include "PyObj.h"

#include "StrTool.h"
#include "ext/PyBaseExt.h"
#include "ext/PyTupleExt.h"
#include "ext/PyListExt.h"
#include "ext/PyDictExt.h"
#include "ext/PyWeakExt.h"
#include "ext/PyTimeExt.h"
 
using namespace std;
using namespace ff;
               
SPython::SPython(){
    pycontext.curstack = PyObjModule::BuildModule(pycontext, "__main__", "built-in");
    pycontext.curstack.cast<PyObjModule>()->loadFlag = PyObjModule::MOD_LOADOK;
    PyBaseExt::init(pycontext);
    PyTupleExt::init(pycontext);
    PyListExt::init(pycontext);
    PyDictExt::init(pycontext);
    PyWeakExt::init(pycontext);
    PyTimeExt::init(pycontext);
}

PyObjPtr SPython::importFile(const std::string& modname, string __module__){
    if (__module__.empty()){
        __module__ = modname;
    }
    return PyOpsUtil::importFile(pycontext, modname, __module__);
}

