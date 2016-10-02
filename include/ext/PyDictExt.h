#ifndef _PY_DICT_EXT_H_
#define _PY_DICT_EXT_H_

#include <algorithm>

#include "ExprAST.h"
#include "PyObj.h"
#include "PyCpp.h"
#include "StrTool.h"

namespace ff {
    
class PyDictIterData:public PyInstanceData{
public:
    PyDictIterData():version(0){
    }
    size_t                       version;
    PyObjDict::DictMap::iterator it;
};
struct PyDictIterExt{
    static PyObjPtr iter__init__(PyContext& context, std::vector<PyObjPtr>& argAssignVal){

        if (argAssignVal.size() != 2){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: iter__init__() takes exactly 2 argument (%u given)", argAssignVal.size()));
        }
        PyObjPtr& iterself = argAssignVal[0];
        PyObjPtr& dictself = argAssignVal[1];
        
        PyAssertInstance(iterself);
        PyAssertDict(dictself);
        
        PyDictIterData* instanceData = new PyDictIterData();
        instanceData->it = dictself.cast<PyObjDict>()->value.begin();
        instanceData->version = dictself.cast<PyObjDict>()->version;
        instanceData->objValues.push_back(dictself);
        PyObjPtr iterRetTupleCache = new PyObjTuple();
        instanceData->objValues.push_back(iterRetTupleCache);
        
        iterself.cast<PyObjClassInstance>()->instanceData = instanceData;
        
        return PyObjTool::buildTrue();
    }
    static PyObjPtr next(PyContext& context, PyObjPtr& self, std::vector<PyObjPtr>& argAssignVal){
        PyAssertInstance(self);
        if (argAssignVal.size() != 0){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: next() takes exactly 0 argument (%u given)", argAssignVal.size()));
        }
        if (!(self.cast<PyObjClassInstance>()->instanceData)){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: next() takes exactly 0 argument (%u given)", argAssignVal.size()));
        }
        PyDictIterData* instanceData = self.cast<PyObjClassInstance>()->instanceData.cast<PyDictIterData>();
        PyObjPtr& iterRetTupleCache = self.cast<PyObjClassInstance>()->instanceData->objValues[1];
        
        PyObjPtr& dictself = self.cast<PyObjClassInstance>()->instanceData->objValues[0];
        if (instanceData->version != dictself.cast<PyObjDict>()->version){
            if (dictself.cast<PyObjDict>()->value.empty()){
                instanceData->it = dictself.cast<PyObjDict>()->value.end();
                return NULL;
            }
            instanceData->version = dictself.cast<PyObjDict>()->version;
            instanceData->it = dictself.cast<PyObjDict>()->value.begin();
            for (size_t i = 0; i < instanceData->nValue; ++i){
                ++instanceData->it;
            }
        }
        if (instanceData->it != dictself.cast<PyObjDict>()->value.end()){
            iterRetTupleCache.cast<PyObjTuple>()->clear();
            iterRetTupleCache.cast<PyObjTuple>()->append(DICT_ITER_KEY(instanceData->it));
            iterRetTupleCache.cast<PyObjTuple>()->append(DICT_ITER_VAL(instanceData->it));

            ++instanceData->it;
            ++instanceData->nValue;//!index
            return iterRetTupleCache;
        }
        return NULL;
    }
    
};

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
    static PyObjPtr iteritems(PyContext& context, PyObjPtr& self, std::vector<PyObjPtr>& argAssignVal){
        PyAssertDict(self);
        PY_ASSERT_ARG_SIZE(context, argAssignVal.size(), 0, "iteritems");
        
        std::vector<PyObjPtr> constructArgs;
        constructArgs.push_back(self);
        
        PyObjPtr ret = PyCppUtil::callPyfunc(context, context.allBuiltin["dict_iter"], constructArgs);
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
    static PyObjPtr popitem(PyContext& context, PyObjPtr& self, std::vector<PyObjPtr>& argAssignVal){
        PyAssertDict(self);
        if (argAssignVal.size() != 0){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: popitem() takes exactly 0 argument (%u given)", argAssignVal.size()));
        }
        PyObjPtr ret = self.cast<PyObjDict>()->popitem();
        if (!ret){
            PY_RAISE_STR(context, PyCppUtil::strFormat("KeyError: 'popitem(): dictionary is empty'"));
        }

        return ret;
    }
    static PyObjPtr setdefault(PyContext& context, PyObjPtr& self, std::vector<PyObjPtr>& argAssignVal){
        PyAssertDict(self);
        if (argAssignVal.size() < 1){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: setdefault() takes exactly 2 argument (%u given)", argAssignVal.size()));
        }
        
        PyObjPtr& indexObj = argAssignVal[0];
        PyObjPtr ret = self.cast<PyObjDict>()->setdefault(context, indexObj, argAssignVal[1]);
        return ret;
    }
    static PyObjPtr update(PyContext& context, PyObjPtr& self, std::vector<PyObjPtr>& argAssignVal){
        PyAssertDict(self);
        PY_ASSERT_ARG_SIZE(context, argAssignVal.size(), 1, "update");
        
        PyObjPtr& arg1 = argAssignVal[0];
  
        self.cast<PyObjDict>()->update(context, arg1);

        return PyObjTool::buildNone();
    }
    static PyObjPtr values(PyContext& context, PyObjPtr& self, std::vector<PyObjPtr>& argAssignVal){
        PyAssertDict(self);
        PY_ASSERT_ARG_SIZE(context, argAssignVal.size(), 0, "values");
        
        PyObjPtr ret = new PyObjList();
        
        PyObjDict::DictMap::iterator it = self.cast<PyObjDict>()->value.begin();
        for (; it != self.cast<PyObjDict>()->value.end(); ++it){
            ret.cast<PyObjList>()->append(DICT_ITER_VAL(it));
        }
  
        return ret;
    }
    static bool init(PyContext& pycontext){
        {
            PyObjPtr objClass  = PyObjClassDef::build(pycontext, "dictionary-itemiterator");
            PyCppUtil::setAttr(pycontext, objClass, "__init__", PyCppUtil::genFunc(PyDictIterExt::iter__init__, "__init__"));
            PyCppUtil::setAttr(pycontext, objClass, "next", PyCppUtil::genFunc(PyDictIterExt::next, "next"));
            pycontext.allBuiltin["dict_iter"] = objClass;
        }
        {            
            PyObjPtr objClass = PyObjClassDef::build(pycontext, "dict", &singleton_t<ObjIdTypeTraits<PyObjDict> >::instance_ptr()->objInfo);
            
            PyCppUtil::setAttr(pycontext, objClass, "clear", PyCppUtil::genFunc(PyDictExt::clear, "clear"));
            PyCppUtil::setAttr(pycontext, objClass, "copy", PyCppUtil::genFunc(PyDictExt::copy, "copy"));
            PyCppUtil::setAttr(pycontext, objClass, "fromkeys", PyCppUtil::genFunc(PyDictExt::fromkeys, "fromkeys"));
            PyCppUtil::setAttr(pycontext, objClass, "get", PyCppUtil::genFunc(PyDictExt::get, "get"));
            PyCppUtil::setAttr(pycontext, objClass, "has_key", PyCppUtil::genFunc(PyDictExt::has_key, "has_key"));
            PyCppUtil::setAttr(pycontext, objClass, "items", PyCppUtil::genFunc(PyDictExt::items, "items"));
            PyCppUtil::setAttr(pycontext, objClass, "iteritems", PyCppUtil::genFunc(PyDictExt::iteritems, "iteritems"));
            PyCppUtil::setAttr(pycontext, objClass, "keys", PyCppUtil::genFunc(PyDictExt::keys, "keys"));
            PyCppUtil::setAttr(pycontext, objClass, "pop", PyCppUtil::genFunc(PyDictExt::pop, "pop"));
            PyCppUtil::setAttr(pycontext, objClass, "popitem", PyCppUtil::genFunc(PyDictExt::popitem, "popitem"));
            PyCppUtil::setAttr(pycontext, objClass, "setdefault", PyCppUtil::genFunc(PyDictExt::setdefault, "setdefault"));
            PyCppUtil::setAttr(pycontext, objClass, "update", PyCppUtil::genFunc(PyDictExt::update, "update"));
            PyCppUtil::setAttr(pycontext, objClass, "values", PyCppUtil::genFunc(PyDictExt::values, "values"));
            pycontext.allBuiltin["dict"] = objClass;
        }
        return true;
    }
};
    
}
#endif

