#ifndef _PY_DICT_EXT_H_
#define _PY_DICT_EXT_H_

#include <algorithm>

#include "ExprAST.h"
#include "PyObj.h"
#include "PyCpp.h"
#include "StrTool.h"

namespace ff {
struct PyDictExt{
    static PyObjPtr pop(PyContext& context, PyObjPtr& self, std::vector<PyObjPtr>& argAssignVal){
        PyAssertDict(self);
        if (argAssignVal.size() < 1){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: pop() takes exactly 1/2 argument (%u given)", argAssignVal.size()));
        }
        
        PyObjPtr& indexObj = argAssignVal[0];
        PyObjPtr ret = self.cast<PyObjDict>()->pop(context, indexObj);
        if (ret){
            return ret;
        }
        if (argAssignVal.size() >= 2){
            return argAssignVal[1];
        }
        PY_RAISE_STR(context, PyCppUtil::strFormat("KeyError: %s", indexObj->getHandler()->handleStr(context, indexObj).c_str()));
        return PyObjTool::buildNone();
    }
    static PyObjPtr items(PyContext& context, PyObjPtr& self, std::vector<PyObjPtr>& argAssignVal){
        PyAssertDict(self);
        if (argAssignVal.size() != 0){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: pop() takes exactly 0 argument (%u given)", argAssignVal.size()));
        }
        
        PyObjPtr ret = self.cast<PyObjDict>()->getValueAsList();
        return ret;
    }
    static bool init(PyContext& pycontext){
        {
            PyObjPtr objClass = PyObjClassDef::build(pycontext, "dict", &singleton_t<ObjIdTypeTraits<PyObjDict> >::instance_ptr()->objInfo);
            
            PyCppUtil::setAttr(pycontext, objClass, "pop", PyCppUtil::genFunc(PyDictExt::pop, "pop"));
            PyCppUtil::setAttr(pycontext, objClass, "items", PyCppUtil::genFunc(PyDictExt::items, "items"));
            pycontext.allBuiltin["dict"] = objClass;
        }
        return true;
    }
};
    
}
#endif

