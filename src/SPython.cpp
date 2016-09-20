
#include "SPython.h"
#include "ExprAST.h"
#include "PyObj.h"
#include "PyCpp.h"
#include "StrTool.h"

using namespace std;
using namespace ff;

static PyObjPtr pyLen(PyContext& context, std::vector<PyObjPtr>& argAssignVal){
    if (argAssignVal.size() != 1){
        throw PyException::buildException("TypeError: len() takes exactly 1 argument (%u given)", argAssignVal.size());
    }
    PyObjPtr& param = argAssignVal[0];
    long ret = param->handler->handleLen(context, param);
    if (ret < 0){
        throw PyException::buildException("TypeError: object of type '%d' has no len()", param->getType());
    }
    return PyCppUtil::genInt(ret);
}
static PyObjPtr pyIsinstance(PyContext& context, std::vector<PyObjPtr>& argAssignVal){
    if (argAssignVal.size() != 2){
        throw PyException::buildException("TypeError: pyIsinstance() takes exactly 2 argument (%u given)", argAssignVal.size());
    }
    PyObjPtr& paramObj   = argAssignVal[0];
    PyObjPtr& paramClass = argAssignVal[1];
    
    bool ret = paramClass->handler->handleIsInstance(context, paramClass, paramObj);
    return PyObjTool::buildBool(ret);
}

static PyObjPtr strUpper(PyContext& context, PyObjPtr& self, std::vector<PyObjPtr>& argAssignVal){
    if (self->getType() != PY_STR){
        throw PyException::buildException("str instance needed");
    }
    if (argAssignVal.size() != 0){
        throw PyException::buildException("TypeError: upper() takes exactly 0 argument (%u given)", argAssignVal.size());
    }
    
    return PyCppUtil::genStr(StrTool::upper(self.cast<PyObjStr>()->value));
}

struct PyExtException{
    
};

SPython::SPython(){
    pycontext.curstack = new PyObjModule("__main__", "built-in");
    pycontext.allBuiltin["None"] = PyObjTool::buildNone();
    //pycontext.allBuiltin["int"] = new PyBuiltinTypeInfo(PY_INT);
    pycontext.allBuiltin["float"] = new PyBuiltinTypeInfo(PY_FLOAT);
    
    pycontext.allBuiltin["tuple"] = new PyBuiltinTypeInfo(PY_TUPLE);
    pycontext.allBuiltin["list"] = new PyBuiltinTypeInfo(PY_LIST);
    pycontext.allBuiltin["dict"] = new PyBuiltinTypeInfo(PY_DICT);
    vector<PyObjPtr> tmpParent;
    pycontext.allBuiltin["exception"] = new PyCppClassDef<PyExtException>("exception", tmpParent);
    
    pycontext.allBuiltin["len"] = PyCppUtil::genFunc(pyLen, "len");
    pycontext.allBuiltin["isinstance"] = PyCppUtil::genFunc(pyIsinstance, "isinstance");
    
    {
        PyObjPtr strClass = PyObjClassDef::build(pycontext, "str", &singleton_t<ObjIdTypeTraits<PyObjStr> >::instance_ptr()->objInfo);
        
        PyCppUtil::setAttr(pycontext, strClass, "upper", PyCppUtil::genFunc(strUpper, "upper"));
        //PyCppUtil::setAttr(pycontext, strClass, "__class__", strClass);
        pycontext.allBuiltin["str"] = strClass;
    }
    
    {
        PyObjPtr strClass = PyObjClassDef::build(pycontext, "int", &singleton_t<ObjIdTypeTraits<PyObjInt> >::instance_ptr()->objInfo);

        //PyCppUtil::setAttr(pycontext, strClass, "__class__", strClass);
        pycontext.allBuiltin["int"] = strClass;
    }
}

PyObjPtr SPython::importFile(const std::string& modname){
    return PyOpsUtil::importFile(pycontext, modname, modname);
}

