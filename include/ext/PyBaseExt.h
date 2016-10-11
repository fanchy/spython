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
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: len() takes exactly 1 argument (%u given)", argAssignVal.size()));
        }
        PyObjPtr& param = argAssignVal[0];
        long ret = param->getHandler()->handleLen(context, param);
        if (ret < 0){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: object of type '%d' has no len()", param->getType()));
        }
        return PyCppUtil::genInt(ret);
    }
    static PyObjPtr isinstance(PyContext& context, std::vector<PyObjPtr>& argAssignVal){
        if (argAssignVal.size() != 2){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: isinstance() takes exactly 2 argument (%u given)", argAssignVal.size()));
        }
        PyObjPtr& paramObj   = argAssignVal[0];
        PyObjPtr& paramClass = argAssignVal[1];
        
        bool ret = paramClass->getHandler()->handleIsInstance(context, paramClass, paramObj);
        return PyObjTool::buildBool(ret);
    }
    static PyObjPtr __import__(PyContext& context, std::vector<PyObjPtr>& argAssignVal){
        if (argAssignVal.size() != 1){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: __import__() takes exactly 1 argument (%u given)", argAssignVal.size()));
        }
        PyObjPtr& param = argAssignVal[0];
        PyAssertStr(param);
        std::string& modname = param.cast<PyObjStr>()->value;
        return PyOpsUtil::importFile(context, modname, modname);
    }
};
struct PyStrExt{
    static PyObjPtr upper(PyContext& context, PyObjPtr& self, std::vector<PyObjPtr>& argAssignVal){
        PyAssertStr(self);
        if (argAssignVal.size() != 0){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: upper() takes exactly 0 argument (%u given)", argAssignVal.size()));
        }
        
        return PyCppUtil::genStr(StrTool::upper(self.cast<PyObjStr>()->value));
    }
    static PyObjPtr lower(PyContext& context, PyObjPtr& self, std::vector<PyObjPtr>& argAssignVal){
        PyAssertStr(self);
        if (argAssignVal.size() != 0){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: lower() takes exactly 0 argument (%u given)", argAssignVal.size()));
        }
        
        return PyCppUtil::genStr(StrTool::lower(self.cast<PyObjStr>()->value));
    }
};

struct PyPropertExt{
    static PyObjPtr property__init__(PyContext& context, std::vector<PyObjPtr>& argAssignVal){

        if (argAssignVal.size() < 2){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: property__init__() takes exactly 2/3/4 argument (%u given)", argAssignVal.size()));
        }
        PyObjPtr& propertySelf = argAssignVal[0];
        PyObjPtr& func = argAssignVal[1];
        PyAssertInstance(propertySelf);
        
        PyCppUtil::setAttr(context, propertySelf, "fget", func);
        PyCppUtil::setAttr(context, propertySelf, "fset", PyObjTool::buildNone());
        PyCppUtil::setAttr(context, propertySelf, "fdel", PyObjTool::buildNone());
        
        return PyObjTool::buildTrue();
    }
    static PyObjPtr setter(PyContext& context, PyObjPtr& self, std::vector<PyObjPtr>& argAssignVal){
        PyAssertInstance(self);
        if (argAssignVal.size() != 1){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: setter() takes exactly 2 argument (%u given)", argAssignVal.size()));
        }

        PyCppUtil::setAttr(context, self, "fset", argAssignVal[0]);;

        return self;
    }
};


struct PyBaseExceptionExt{
    static PyObjPtr BaseException__init__(PyContext& context, std::vector<PyObjPtr>& argAssignVal){
        if (argAssignVal.size() < 1){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: BaseException__init__() takes exactly >=1 argument (%u given)", argAssignVal.size()));
        }
        PyObjPtr& propertySelf = argAssignVal[0];
        PyAssertInstance(propertySelf);
        PyObjPtr args = new PyObjTuple();
        for (size_t i = 1; i < argAssignVal.size(); ++i){
            args.cast<PyObjTuple>()->append(argAssignVal[i]);
        }
        PyCppUtil::setAttr(context, propertySelf, "args", args);
        return PyObjTool::buildTrue();
    }
    static PyObjPtr BaseException__str__(PyContext& context, PyObjPtr& self, std::vector<PyObjPtr>& argAssignVal){
        PyAssertInstance(self);
        PyObjPtr args = PyCppUtil::getAttr(context, self, "args");
        PyObjPtr ret = PyCppUtil::genStr(std::string("BaseException")+args->getHandler()->handleStr(context, args));
        return ret;
    }
};

struct PyBaseExt{
    static bool init(PyContext& pycontext){
        pycontext.addBuiltin("None", PyObjTool::buildNone());
        pycontext.addBuiltin("True", PyObjTool::buildTrue());
        pycontext.addBuiltin("False", PyObjTool::buildFalse());
        
        pycontext.addBuiltin("len", PyCppUtil::genFunc(PyBuiltinExt::len, "len"));
        pycontext.addBuiltin("isinstance", PyCppUtil::genFunc(PyBuiltinExt::isinstance, "isinstance"));
        pycontext.addBuiltin("__import__", PyCppUtil::genFunc(PyBuiltinExt::__import__, "__import__"));
        
        {
            PyObjPtr strClass = PyObjClassDef::build(pycontext, "str", &singleton_t<ObjIdTypeTraits<PyObjStr> >::instance_ptr()->objInfo);
            
            PyCppUtil::setAttr(pycontext, strClass, "upper", PyCppUtil::genFunc(PyStrExt::upper, "upper"));
            PyCppUtil::setAttr(pycontext, strClass, "lower", PyCppUtil::genFunc(PyStrExt::lower, "lower"));
            pycontext.addBuiltin("str", strClass);
        }
        
        {
            PyObjPtr strClass = PyObjClassDef::build(pycontext, "int");
            pycontext.addBuiltin("int", strClass);
        }
        {
            PyObjPtr strClass = PyObjClassDef::build(pycontext, "float");
            pycontext.addBuiltin("float", strClass);
        }
        {
            PyObjPtr objClass  = PyObjClassDef::build(pycontext, "property");
            PyCppUtil::setAttr(pycontext, objClass, "__init__", PyCppUtil::genFunc(PyPropertExt::property__init__, "__init__"));
            PyCppUtil::setAttr(pycontext, objClass, "setter", PyCppUtil::genFunc(PyPropertExt::setter, "setter"));
            pycontext.addBuiltin("property", objClass);
            pycontext.propertyClass = objClass;
        }
        
        {
            PyObjPtr objClass  = PyObjClassDef::build(pycontext, "BaseException");
            PyCppUtil::setAttr(pycontext, objClass, "__init__", PyCppUtil::genFunc(PyBaseExceptionExt::BaseException__init__, "__init__"));
            PyCppUtil::setAttr(pycontext, objClass, "__str__", PyCppUtil::genFunc(PyBaseExceptionExt::BaseException__str__, "__str__"));
            pycontext.addBuiltin("BaseException", objClass);
            pycontext.propertyClass = objClass;
            
            pycontext.addBuiltin("Exception", objClass);
        }
        return true;
    }
};
    
}
#endif

