#ifndef _PY_BASE_EXT_H_
#define _PY_BASE_EXT_H_

#include "ExprAST.h"
#include "PyObj.h"
#include "PyCpp.h"
#include "StrTool.h"

namespace ff {
    
struct PyBuiltinExt{
    static PyObjPtr len(PyContext& context, std::vector<PyObjPtr>& argAssignVal){
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
    static PyObjPtr isinstance(PyContext& context, std::vector<PyObjPtr>& argAssignVal){
        if (argAssignVal.size() != 2){
            throw PyException::buildException("TypeError: isinstance() takes exactly 2 argument (%u given)", argAssignVal.size());
        }
        PyObjPtr& paramObj   = argAssignVal[0];
        PyObjPtr& paramClass = argAssignVal[1];
        
        bool ret = paramClass->handler->handleIsInstance(context, paramClass, paramObj);
        return PyObjTool::buildBool(ret);
    }

};
struct PyStrExt{
    static PyObjPtr upper(PyContext& context, PyObjPtr& self, std::vector<PyObjPtr>& argAssignVal){
        if (self->getType() != PY_STR){
            throw PyException::buildException("str instance needed");
        }
        if (argAssignVal.size() != 0){
            throw PyException::buildException("TypeError: upper() takes exactly 0 argument (%u given)", argAssignVal.size());
        }
        
        return PyCppUtil::genStr(StrTool::upper(self.cast<PyObjStr>()->value));
    }
    static PyObjPtr lower(PyContext& context, PyObjPtr& self, std::vector<PyObjPtr>& argAssignVal){
        if (self->getType() != PY_STR){
            throw PyException::buildException("str instance needed");
        }
        if (argAssignVal.size() != 0){
            throw PyException::buildException("TypeError: lower() takes exactly 0 argument (%u given)", argAssignVal.size());
        }
        
        return PyCppUtil::genStr(StrTool::lower(self.cast<PyObjStr>()->value));
    }
};


struct PyExtException{
    
};


struct PyBaseExt{
    static bool init(PyContext& pycontext){
        pycontext.allBuiltin["None"] = PyObjTool::buildNone();
        //pycontext.allBuiltin["int"] = new PyBuiltinTypeInfo(PY_INT);
        pycontext.allBuiltin["float"] = new PyBuiltinTypeInfo(PY_FLOAT);
        
        pycontext.allBuiltin["tuple"] = new PyBuiltinTypeInfo(PY_TUPLE);
        pycontext.allBuiltin["list"] = new PyBuiltinTypeInfo(PY_LIST);
        pycontext.allBuiltin["dict"] = new PyBuiltinTypeInfo(PY_DICT);
        std::vector<PyObjPtr> tmpParent;
        pycontext.allBuiltin["exception"] = new PyCppClassDef<PyExtException>("exception", tmpParent);
        
        pycontext.allBuiltin["len"] = PyCppUtil::genFunc(PyBuiltinExt::len, "len");
        pycontext.allBuiltin["isinstance"] = PyCppUtil::genFunc(PyBuiltinExt::isinstance, "isinstance");
        
        {
            PyObjPtr strClass = PyObjClassDef::build(pycontext, "str", &singleton_t<ObjIdTypeTraits<PyObjStr> >::instance_ptr()->objInfo);
            
            PyCppUtil::setAttr(pycontext, strClass, "upper", PyCppUtil::genFunc(PyStrExt::upper, "upper"));
            PyCppUtil::setAttr(pycontext, strClass, "lower", PyCppUtil::genFunc(PyStrExt::lower, "lower"));
            pycontext.allBuiltin["str"] = strClass;
        }
        
        {
            PyObjPtr strClass = PyObjClassDef::build(pycontext, "int", &singleton_t<ObjIdTypeTraits<PyObjInt> >::instance_ptr()->objInfo);
    
            //PyCppUtil::setAttr(pycontext, strClass, "__class__", strClass);
            pycontext.allBuiltin["int"] = strClass;
        }
        return true;
    }
};
    
}
#endif

