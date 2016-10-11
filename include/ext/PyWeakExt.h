#ifndef _PY_WEAK_EXT_H_
#define _PY_WEAK_EXT_H_

#include "ExprAST.h"
#include "PyObj.h"

#include "StrTool.h"

namespace ff {
typedef weak_ptr_t<PyObj> PyObjWeakRef;

class PyWeakData:public PyInstanceData{
public:
    PyWeakData(PyObjPtr& v):ref(v){
    }
    PyObjWeakRef ref;
};
struct PyWeakExt{
    static PyObjPtr WeakRef__init__(PyContext& context, std::vector<PyObjPtr>& argAssignVal){

        if (argAssignVal.size() != 2){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: WeakRef__init__() takes exactly 2 argument (%u given)", argAssignVal.size()));
        }
        PyObjPtr& iterself = argAssignVal[0];
        PyObjPtr& destself = argAssignVal[1];
        
        PyAssertInstance(iterself);
        PyAssertInstance(destself);
        
        PyWeakData* instanceData = new PyWeakData(destself);
        
        iterself.cast<PyObjClassInstance>()->instanceData = instanceData;
        
        return PyObjTool::buildTrue();
    }
    static PyObjPtr ref(PyContext& context, std::vector<PyObjPtr>& argAssignVal){

        if (argAssignVal.size() != 1){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: iter__init__() takes exactly 1 argument (%u given)", argAssignVal.size()));
        }

        PyObjPtr mod = context.getModule("weakref");
        PyObjPtr objClass = PyCppUtil::getAttr(context, mod, "weakref");

        return PyCppUtil::callPyfunc(context, objClass, argAssignVal);
    }
    static PyObjPtr weak__call__(PyContext& context, PyObjPtr& self, std::vector<PyObjPtr>& argAssignVal){
        PyAssertInstance(self);
        PY_ASSERT_ARG_SIZE(context, argAssignVal.size(), 0, "__call__");
        
        PyObjPtr ret = self.cast<PyObjClassInstance>()->instanceData.cast<PyWeakData>()->ref.lock();
        if (ret){
            return ret;
        }
        return PyObjTool::buildNone();
    }
    static bool init(PyContext& pycontext){
        {
            PyObjPtr mod = PyObjModule::BuildModule(pycontext, "weakref", "built-in");
            
            PyObjPtr objClass = PyObjClassDef::build(pycontext, "weakref");
            PyCppUtil::setAttr(pycontext, objClass, "__init__", PyCppUtil::genFunc(PyWeakExt::WeakRef__init__, "__init__"));
            PyCppUtil::setAttr(pycontext, objClass, "__call__", PyCppUtil::genFunc(PyWeakExt::weak__call__, "__call__"));
            PyCppUtil::setAttr(pycontext, mod, "weakref", objClass);
            PyCppUtil::setAttr(pycontext, mod, "ref", PyCppUtil::genFunc(PyWeakExt::ref, "ref"));
            pycontext.addModule("weakref", mod);
        }
        return true;
    }
};
    
}
#endif

