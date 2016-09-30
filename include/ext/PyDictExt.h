#ifndef _PY_DICT_EXT_H_
#define _PY_DICT_EXT_H_

#include <algorithm>

#include "ExprAST.h"
#include "PyObj.h"
#include "PyCpp.h"
#include "StrTool.h"

namespace ff {
struct PyDictExt{
    static PyObjPtr clear(PyContext& context, PyObjPtr& self, std::vector<PyObjPtr>& argAssignVal){
        PyAssertDict(self);
        if (argAssignVal.size() != 0){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: clear() takes exactly 0 argument (%u given)", argAssignVal.size()));
        }
        
        self.cast<PyObjDict>()->clear();
        return PyObjTool::buildNone();
    }
    static PyObjPtr copy(PyContext& context, PyObjPtr& self, std::vector<PyObjPtr>& argAssignVal){
        PyAssertDict(self);
        if (argAssignVal.size() != 0){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: copy() takes exactly 0 argument (%u given)", argAssignVal.size()));
        }
        
        return self.cast<PyObjDict>()->copy();
    }
    static PyObjPtr fromkeys(PyContext& context, std::vector<PyObjPtr>& argAssignVal){
        if (argAssignVal.size() < 1){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: copy() takes exactly 1/2 argument (%u given)", argAssignVal.size()));
        }
        PyObjPtr ret = PyObjDict::build();
        PyObjPtr& arg1 = argAssignVal[0];
        PyObjPtr arg2  = PyObjTool::buildNone();
        if (argAssignVal.size() >= 2){
            arg2 = argAssignVal[1];
        }
        IterUtil iterUtil(context, arg1);
        PyObjPtr key = iterUtil.next();
        while (key){
            ret.cast<PyObjDict>()->set(context, key, arg2);
            key = iterUtil.next();
        }
        return ret;
    }
    static PyObjPtr get(PyContext& context, PyObjPtr& self, std::vector<PyObjPtr>& argAssignVal){
        PyAssertDict(self);
        if (argAssignVal.size() < 1){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: get() takes exactly 1/2 argument (%u given)", argAssignVal.size()));
        }
        PyObjPtr& key = argAssignVal[0];
        PyObjPtr ret = self.cast<PyObjDict>()->get(context, key);
        if (!ret){
            if (argAssignVal.size() >= 2){
                ret = argAssignVal[1];
            }
            else{
                ret = PyObjTool::buildNone();
            }
        }
        return ret;
    }
    static PyObjPtr has_key(PyContext& context, PyObjPtr& self, std::vector<PyObjPtr>& argAssignVal){
        PyAssertDict(self);
        if (argAssignVal.size() != 1){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: get() takes exactly 1 argument (%u given)", argAssignVal.size()));
        }
        PyObjPtr& key = argAssignVal[0];
        PyObjPtr ret = self.cast<PyObjDict>()->get(context, key);
        if (ret){
            return PyObjTool::buildTrue();
        }
        return PyObjTool::buildFalse();
    }
    static PyObjPtr items(PyContext& context, PyObjPtr& self, std::vector<PyObjPtr>& argAssignVal){
        PyAssertDict(self);
        PY_ASSERT_ARG_SIZE(context, argAssignVal.size(), 0, "items");
        
        PyObjPtr ret = self.cast<PyObjDict>()->getValueAsList();
        return ret;
    }
    static PyObjPtr keys(PyContext& context, PyObjPtr& self, std::vector<PyObjPtr>& argAssignVal){
        PyAssertDict(self);
        PY_ASSERT_ARG_SIZE(context, argAssignVal.size(), 0, "keys");
        
        PyObjPtr ret = self.cast<PyObjDict>()->keys();
        return ret;
    }
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
    static bool init(PyContext& pycontext){
        {
            PyObjPtr objClass = PyObjClassDef::build(pycontext, "dict", &singleton_t<ObjIdTypeTraits<PyObjDict> >::instance_ptr()->objInfo);
            
            PyCppUtil::setAttr(pycontext, objClass, "clear", PyCppUtil::genFunc(PyDictExt::clear, "clear"));
            PyCppUtil::setAttr(pycontext, objClass, "copy", PyCppUtil::genFunc(PyDictExt::copy, "copy"));
            PyCppUtil::setAttr(pycontext, objClass, "fromkeys", PyCppUtil::genFunc(PyDictExt::fromkeys, "fromkeys"));
            PyCppUtil::setAttr(pycontext, objClass, "get", PyCppUtil::genFunc(PyDictExt::get, "get"));
            PyCppUtil::setAttr(pycontext, objClass, "has_key", PyCppUtil::genFunc(PyDictExt::has_key, "has_key"));
            PyCppUtil::setAttr(pycontext, objClass, "items", PyCppUtil::genFunc(PyDictExt::items, "items"));
            PyCppUtil::setAttr(pycontext, objClass, "keys", PyCppUtil::genFunc(PyDictExt::keys, "keys"));
            PyCppUtil::setAttr(pycontext, objClass, "pop", PyCppUtil::genFunc(PyDictExt::pop, "pop"));
            pycontext.allBuiltin["dict"] = objClass;
        }
        return true;
    }
};
    
}
#endif

