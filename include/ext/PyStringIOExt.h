#ifndef _PY_STRING_IO_EXT_H_
#define _PY_STRING_IO_EXT_H_

#include "ExprAST.h"
#include "PyObj.h"

#include "StrTool.h"

namespace ff {
class PyStringIOData:public SafeTypeHelper<PyStringIOData, PyInstanceData>{
public:
    PyStringIOData(){
    }
    std::string buff;
};

struct PyStringIOExt{
    static PyObjPtr StringIO__init__(PyContext& context, std::vector<PyObjPtr>& argAssignVal){
        if (argAssignVal.size() < 1){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: StringIO__init__() takes exactly 1 argument (%u given)", argAssignVal.size()));
        }
        PyObjPtr& iterself = argAssignVal[0];
        PyAssertInstance(iterself);

        PyStringIOData* instanceData = new PyStringIOData();
        iterself.cast<PyObjClassInstance>()->instanceData = instanceData;
        return PyObjTool::buildTrue();
    }
    static PyObjPtr StringIO_write(PyContext& context, PyObjPtr& self, std::vector<PyObjPtr>& argAssignVal){
        if (argAssignVal.size() < 1){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: StringIO__init__() takes exactly 1 argument (%u given)", argAssignVal.size()));
        }
        PyAssertInstance(self);
        PyObjPtr& param = argAssignVal[0];
        

        PyStringIOData* instanceData = self.cast<PyObjClassInstance>()->instanceData->cast<PyStringIOData>();
        instanceData->buff += PyCppUtil::toStr(param);
        return self;
    }
    static PyObjPtr StringIO_getvalue(PyContext& context, PyObjPtr& self, std::vector<PyObjPtr>& argAssignVal){
        if (argAssignVal.size() != 0){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: StringIO__init__() takes exactly 0 argument (%u given)", argAssignVal.size()));
        }
        PyAssertInstance(self);

        PyStringIOData* instanceData = self.cast<PyObjClassInstance>()->instanceData->cast<PyStringIOData>();
        return PyCppUtil::genStr(instanceData->buff);
    }
    static PyObjPtr StringIO_close(PyContext& context, PyObjPtr& self, std::vector<PyObjPtr>& argAssignVal){
        if (argAssignVal.size() != 0){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: StringIO_close() takes exactly 0 argument (%u given)", argAssignVal.size()));
        }
        PyAssertInstance(self);

        PyStringIOData* instanceData = self.cast<PyObjClassInstance>()->instanceData->cast<PyStringIOData>();
        instanceData->buff.clear();
        return PyObjTool::buildTrue();
    }
    
    static bool init(PyContext& pycontext){
        {
            PyObjPtr mod = PyObjModule::BuildModule(pycontext, "StringIO", "built-in");
            {
                PyObjPtr objClass = PyObjClassDef::build(pycontext, "StringIO");
                PyCppUtil::setAttr(pycontext, objClass, "__init__", PyCppUtil::genFunc(PyStringIOExt::StringIO__init__, "__init__"));
                PyCppUtil::setAttr(pycontext, objClass, "write", PyCppUtil::genFunc(PyStringIOExt::StringIO_write, "write"));
                PyCppUtil::setAttr(pycontext, objClass, "getvalue", PyCppUtil::genFunc(PyStringIOExt::StringIO_getvalue, "getvalue"));
                PyCppUtil::setAttr(pycontext, objClass, "close", PyCppUtil::genFunc(PyStringIOExt::StringIO_close, "close"));
                PyCppUtil::setAttr(pycontext, mod, "StringIO", objClass);
                PyCppUtil::setAttr(pycontext, mod, "cStringIO", objClass);
            }
            
            pycontext.addModule("StringIO", mod);
        }
        return true;
    }
};
    
}
#endif

