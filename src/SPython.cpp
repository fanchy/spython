
#include "SPython.h"
#include "ExprAST.h"
#include "PyObj.h"
#include "PyCpp.h"

using namespace std;
using namespace ff;

static PyObjPtr pyLen(PyContext& context, std::vector<PyObjPtr>& argAssignVal){
    if (argAssignVal.size() != 1){
        throw PyException::buildException("TypeError: len() takes exactly one argument (%d given)", argAssignVal.size());
    }
    PyObjPtr& param = argAssignVal[0];
    long ret = param->handler->handleLen(context, param);
    if (ret < 0){
        throw PyException::buildException("TypeError: object of type '%d' has no len()", param->getType());
    }
    return PyCppUtil::genInt(ret);
}
struct PyExtException{
    
};

SPython::SPython(){
    pycontext.curstack = new PyObjModule("__main__", "built-in");
    pycontext.allBuiltin["None"] = PyObjTool::buildNone();
    pycontext.allBuiltin["int"] = new PyBuiltinTypeInfo(PY_INT);
    pycontext.allBuiltin["float"] = new PyBuiltinTypeInfo(PY_FLOAT);
    pycontext.allBuiltin["str"] = new PyBuiltinTypeInfo(PY_STR);
    pycontext.allBuiltin["tuple"] = new PyBuiltinTypeInfo(PY_TUPLE);
    pycontext.allBuiltin["list"] = new PyBuiltinTypeInfo(PY_LIST);
    pycontext.allBuiltin["dict"] = new PyBuiltinTypeInfo(PY_DICT);
    vector<PyObjPtr> tmpParent;
    pycontext.allBuiltin["exception"] = new PyCppClassDef<PyExtException>("exception", tmpParent);
    
    pycontext.allBuiltin["len"] = PyCppUtil::genFunc(pyLen, "len");
}

PyObjPtr SPython::importFile(const std::string& modname){
    return PyOpsUtil::importFile(pycontext, modname, modname);
}

