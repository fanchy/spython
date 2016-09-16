
#include "SPython.h"
#include "ExprAST.h"
#include "PyObj.h"

using namespace std;
using namespace ff;

SPython::SPython(){
    pycontext.curstack = new PyObjModule("__main__", "built-in");
    pycontext.allBuiltin["int"] = new PyBuiltinTypeInfo(PY_INT);
    pycontext.allBuiltin["float"] = new PyBuiltinTypeInfo(PY_FLOAT);
    pycontext.allBuiltin["str"] = new PyBuiltinTypeInfo(PY_STR);
    pycontext.allBuiltin["tuple"] = new PyBuiltinTypeInfo(PY_TUPLE);
    pycontext.allBuiltin["list"] = new PyBuiltinTypeInfo(PY_LIST);
    pycontext.allBuiltin["dict"] = new PyBuiltinTypeInfo(PY_DICT);
}

PyObjPtr SPython::importFile(const std::string& modname){
    return PyOpsUtil::importFile(pycontext, modname, modname);
}

