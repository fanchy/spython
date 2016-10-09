#ifndef _PY_TUPLE_EXT_H_
#define _PY_TUPLE_EXT_H_

#include "ExprAST.h"
#include "PyObj.h"
#include "PyCpp.h"
#include "StrTool.h"

namespace ff {

struct PyTupleExt{
    static PyObjPtr count(PyContext& context, PyObjPtr& self, std::vector<PyObjPtr>& argAssignVal){
        PyAssertTuple(self);
        if (argAssignVal.size() != 1){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: count() takes exactly 1 argument (%u given)", argAssignVal.size()));
        }
        PyObjPtr& param = argAssignVal[0];
        PyObjTuple* pTuple = self.cast<PyObjTuple>();
        long ret = 0;
        for (size_t i = 0; i < pTuple->value.size(); ++i){
            if (param->getHandler()->handleEqual(context, param, pTuple->value[i])){
                ++ret;
            }
        }
        return PyCppUtil::genInt(ret);
    }
    static PyObjPtr index(PyContext& context, PyObjPtr& self, std::vector<PyObjPtr>& argAssignVal){
        PyAssertTuple(self);
        if (argAssignVal.size() != 1){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: index() takes exactly 1 argument (%u given)", argAssignVal.size()));
        }
        PyObjPtr& param = argAssignVal[0];
        PyObjTuple* pTuple = self.cast<PyObjTuple>();

        for (size_t i = 0; i < pTuple->value.size(); ++i){
            if (param->getHandler()->handleEqual(context, param, pTuple->value[i])){
                return PyCppUtil::genInt(i);
            }
        }
        PY_RAISE(context, PyCppUtil::genStr("ValueError: tuple.index(x): x not in tuple"));
        return PyCppUtil::genInt(0);
    }
    
    static bool init(PyContext& pycontext){
        {
            PyObjPtr objClass = PyObjClassDef::build(pycontext, "tuple", &singleton_t<ObjIdTypeTraits<PyObjTuple> >::instance_ptr()->objInfo);
            
            PyCppUtil::setAttr(pycontext, objClass, "count", PyCppUtil::genFunc(PyTupleExt::count, "count"));
            PyCppUtil::setAttr(pycontext, objClass, "index", PyCppUtil::genFunc(PyTupleExt::index, "index"));
            pycontext.addBuiltin("tuple", objClass);
        }
        return true;
    }
};
    
}
#endif

