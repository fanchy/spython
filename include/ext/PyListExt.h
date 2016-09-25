#ifndef _PY_LIST_EXT_H_
#define _PY_LIST_EXT_H_

#include <algorithm>

#include "ExprAST.h"
#include "PyObj.h"
#include "PyCpp.h"
#include "StrTool.h"

namespace ff {
struct PyListCmp{
    PyListCmp(PyContext& c, PyObjPtr& f, PyObjPtr& k, bool flag = false):context(c),funcArg(f),keyArg(k),flagReverse(flag){
    }
    bool operator()(const PyObjPtr &a, const PyObjPtr &b)
    {
        bool ret = false;
        if (funcArg){
            std::vector<PyObjPtr> params;
            params.push_back(a);
            params.push_back(b);
            PyObjPtr retObj = PyCppUtil::callPyfunc(context, funcArg, params);
            PyAssertInt(retObj);
            ret = (retObj.cast<PyObjInt>()->value < 0);
        }
        else{
            ret = a->getHandler()->handleLess(context, a, b);
        }
        if (flagReverse){
            ret = !ret;
        }
        return ret;
    }
    PyListCmp(const PyListCmp& src):context(src.context),funcArg(src.funcArg),keyArg(src.keyArg),flagReverse(src.flagReverse){
    }
    PyContext& context;
    PyObjPtr funcArg;
    PyObjPtr keyArg;
    bool flagReverse;
};
struct PyListExt{
    static PyObjPtr count(PyContext& context, PyObjPtr& self, std::vector<PyObjPtr>& argAssignVal){
        PyAssertList(self);
        if (argAssignVal.size() != 1){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: count() takes exactly 1 argument (%u given)", argAssignVal.size()));
        }
        PyObjPtr& param = argAssignVal[0];
        PyObjList* pList = self.cast<PyObjList>();
        long ret = 0;
        for (size_t i = 0; i < pList->value.size(); ++i){
            if (param->getHandler()->handleEqual(context, param, pList->value[i])){
                ++ret;
            }
        }
        return PyCppUtil::genInt(ret);
    }
    static PyObjPtr index(PyContext& context, PyObjPtr& self, std::vector<PyObjPtr>& argAssignVal){
        PyAssertList(self);
        if (argAssignVal.size() != 1){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: index() takes exactly 1 argument (%u given)", argAssignVal.size()));
        }
        PyObjPtr& param = argAssignVal[0];
        PyObjList* pList = self.cast<PyObjList>();

        for (size_t i = 0; i < pList->value.size(); ++i){
            if (param->getHandler()->handleEqual(context, param, pList->value[i])){
                return PyCppUtil::genInt(i);
            }
        }
        PY_RAISE(context, PyCppUtil::genStr("ValueError: list.index(x): x not in list"));
        return PyCppUtil::genInt(0);
    }
    static PyObjPtr append(PyContext& context, PyObjPtr& self, std::vector<PyObjPtr>& argAssignVal){
        PyAssertList(self);
        if (argAssignVal.size() != 1){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: append() takes exactly 1 argument (%u given)", argAssignVal.size()));
        }
        PyObjPtr& param = argAssignVal[0];
        self.cast<PyObjList>()->value.push_back(param);
        return PyObjTool::buildNone();
    }
    static PyObjPtr extend(PyContext& context, PyObjPtr& self, std::vector<PyObjPtr>& argAssignVal){
        PyAssertList(self);
        if (argAssignVal.size() != 1){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: extend() takes exactly 1 argument (%u given)", argAssignVal.size()));
        }
        PyObjPtr& param = argAssignVal[0];
        if (PyCheckList(param)){
            self.cast<PyObjList>()->value.insert(self.cast<PyObjList>()->value.end(),
                param.cast<PyObjList>()->value.begin(), param.cast<PyObjList>()->value.end());
        }
        else if (PyCheckTuple(param)){
            self.cast<PyObjList>()->value.insert(self.cast<PyObjList>()->value.end(),
                param.cast<PyObjTuple>()->value.begin(), param.cast<PyObjTuple>()->value.end());
        }
        else{
            PY_RAISE_STR(context, "TypeError:  object is not iterable");
        }
        return PyObjTool::buildNone();
    }
    static PyObjPtr insert(PyContext& context, PyObjPtr& self, std::vector<PyObjPtr>& argAssignVal){
        PyAssertList(self);
        if (argAssignVal.size() != 2){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: append() takes exactly 2 argument (%u given)", argAssignVal.size()));
        }
        PyObjPtr& indexObj = argAssignVal[0];
        PyObjPtr& val = argAssignVal[1];
        PyAssertInt(indexObj);
        long index = indexObj.cast<PyObjInt>()->value;
        if (index < 0){
            index = 0;
        }
        else if (index > self.cast<PyObjList>()->value.size()){
            index = self.cast<PyObjList>()->value.size();
        }
        self.cast<PyObjList>()->value.insert(self.cast<PyObjList>()->value.begin() + index, val);
        return PyObjTool::buildNone();
    }
    static PyObjPtr pop(PyContext& context, PyObjPtr& self, std::vector<PyObjPtr>& argAssignVal){
        PyAssertList(self);
        if (argAssignVal.size() > 1){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: pop() takes exactly 1 argument (%u given)", argAssignVal.size()));
        }
        if (self.cast<PyObjList>()->value.empty()){
            PY_RAISE_STR(context, "IndexError: pop from empty list");
        }
        if (argAssignVal.empty()){
            self.cast<PyObjList>()->value.pop_back();
        }
        else{
            PyObjPtr& indexObj = argAssignVal[0];
            PyAssertInt(indexObj);
            long index = indexObj.cast<PyObjInt>()->value;
            if (index < 0){
                PY_RAISE_STR(context, "IndexError: pop index out of range");
            }
            else if (index >= self.cast<PyObjList>()->value.size()){
                PY_RAISE_STR(context, "IndexError: pop index out of range");
            }
            self.cast<PyObjList>()->value.erase(self.cast<PyObjList>()->value.begin() + index);
        }
        return PyObjTool::buildNone();
    }
    static PyObjPtr remove(PyContext& context, PyObjPtr& self, std::vector<PyObjPtr>& argAssignVal){
        PyAssertList(self);
        if (argAssignVal.size() != 1){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: remove() takes exactly 1 argument (%u given)", argAssignVal.size()));
        }
        PyObjPtr& param = argAssignVal[0];
        PyObjList* pList = self.cast<PyObjList>();

        for (size_t i = 0; i < pList->value.size(); ++i){
            if (param->getHandler()->handleEqual(context, param, pList->value[i])){
                pList->value.erase(pList->value.begin() + i);
                return PyObjTool::buildNone();
            }
        }
        PY_RAISE_STR(context, "ValueError: list.remove(x): x not in list");
        return PyObjTool::buildNone();
    }
    static PyObjPtr reverse(PyContext& context, PyObjPtr& self, std::vector<PyObjPtr>& argAssignVal){
        PyAssertList(self);
        if (argAssignVal.size() != 0){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: count() takes exactly 0 argument (%u given)", argAssignVal.size()));
        }
        std::reverse(self.cast<PyObjList>()->value.begin(), self.cast<PyObjList>()->value.end());
        return PyObjTool::buildNone();
    }
    //!sort(func=None, key=None, reverse=False) 
    static PyObjPtr sort(PyContext& context, PyObjPtr& self, std::vector<ArgTypeInfo>& allArgsVal, std::vector<PyObjPtr>& argAssignVal){
        PyAssertList(self);
        bool flagReverse = false;
        PyObjPtr reverseArg = PyCppUtil::getArgVal(allArgsVal, argAssignVal, 2, "reverse");
        PyObjPtr keyArg     = PyCppUtil::getArgVal(allArgsVal, argAssignVal, 1, "key");
        PyObjPtr funcArg    = PyCppUtil::getArgVal(allArgsVal, argAssignVal, 0, "func");
        if (reverseArg){
            flagReverse = reverseArg->getHandler()->handleBool(context, reverseArg);
        }
        PyListCmp cmp(context, funcArg, keyArg, flagReverse);
        std::sort(self.cast<PyObjList>()->value.begin(), self.cast<PyObjList>()->value.end(), cmp);
        return PyObjTool::buildNone();
    }
    static bool init(PyContext& pycontext){
        {
            PyObjPtr objClass = PyObjClassDef::build(pycontext, "list", &singleton_t<ObjIdTypeTraits<PyObjList> >::instance_ptr()->objInfo);
            
            PyCppUtil::setAttr(pycontext, objClass, "count", PyCppUtil::genFunc(PyListExt::count, "count"));
            PyCppUtil::setAttr(pycontext, objClass, "index", PyCppUtil::genFunc(PyListExt::index, "index"));
            PyCppUtil::setAttr(pycontext, objClass, "append", PyCppUtil::genFunc(PyListExt::append, "append"));
            PyCppUtil::setAttr(pycontext, objClass, "extend", PyCppUtil::genFunc(PyListExt::extend, "extend"));
            PyCppUtil::setAttr(pycontext, objClass, "insert", PyCppUtil::genFunc(PyListExt::insert, "insert"));
            PyCppUtil::setAttr(pycontext, objClass, "pop", PyCppUtil::genFunc(PyListExt::pop, "pop"));
            PyCppUtil::setAttr(pycontext, objClass, "remove", PyCppUtil::genFunc(PyListExt::remove, "remove"));
            PyCppUtil::setAttr(pycontext, objClass, "reverse", PyCppUtil::genFunc(PyListExt::reverse, "reverse"));
            PyCppUtil::setAttr(pycontext, objClass, "sort", PyCppUtil::genFunc(PyListExt::sort, "sort"));
            pycontext.allBuiltin["list"] = objClass;
        }
        return true;
    }
};
    
}
#endif

