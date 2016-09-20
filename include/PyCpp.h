#ifndef _PY_CPP_H_
#define _PY_CPP_H_

#include <iostream>
#include <string>
#include <vector>
#include <map>
#include <vector>
#include <stdexcept>

#include "Base.h"
#include "singleton.h"
#include "PyObj.h"

namespace ff {

class PyCppFuncWrap: public PyCppFunc{
public:
    typedef PyObjPtr  (*PyCppFunc)(PyContext& context, std::vector<PyObjPtr>& argAssignVal);
    
    PyCppFuncWrap(PyCppFunc f):cppFunc(f){
    }
    virtual PyObjPtr& exeFunc(PyContext& context, PyObjPtr& self, std::vector<ArgTypeInfo>& allArgsVal, std::vector<PyObjPtr>& argAssignVal){
        if (cppFunc){
            PyObjPtr v = (*cppFunc)(context, argAssignVal);
            return context.cacheResult(v);
        }
        return context.cacheResult(PyObjTool::buildNone());
    }
public:
    PyCppFunc     cppFunc;
};
class PyCppClassFuncWrap: public PyCppFunc{
public:
    typedef PyObjPtr  (*PyCppFunc)(PyContext& context, PyObjPtr& self, std::vector<PyObjPtr>& argAssignVal);
    
    PyCppClassFuncWrap(PyCppFunc f):cppFunc(f){
    }
    virtual PyObjPtr& exeFunc(PyContext& context, PyObjPtr& self, std::vector<ArgTypeInfo>& allArgsVal, std::vector<PyObjPtr>& argAssignVal){
        if (cppFunc){
            PyObjPtr& selfobj = self.cast<PyObjFuncDef>()->classInstance;
            if (!selfobj){
                throw PyException::buildException("arg self not assigned");
            }
            PyObjPtr v = (*cppFunc)(context, selfobj, argAssignVal);
            return context.cacheResult(v);
        }
        return context.cacheResult(PyObjTool::buildNone());
    }
public:
    PyCppFunc     cppFunc;
};

struct PyCppUtil{
    static PyObjPtr genInt(long n){
        return new PyObjInt(n);
    }
    static PyObjPtr genStr(const std::string& s){
        return new PyObjStr(s);
    }
    static PyObjPtr genFunc(PyCppFuncWrap::PyCppFunc f, std::string n = ""){
        return new PyObjFuncDef(n, NULL, NULL, new PyCppFuncWrap(f));
    }
    static PyObjPtr genFunc(PyCppClassFuncWrap::PyCppFunc f, std::string n = ""){
        return new PyObjFuncDef(n, NULL, NULL, new PyCppClassFuncWrap(f));
    }
    static PyObjPtr getAttr(PyContext& context, PyObjPtr& obj, const std::string& filedname){
        PyContextBackUp backup(context);
        context.curstack = obj;
        
        ExprASTPtr expr = singleton_t<VariableExprAllocator>::instance_ptr()->alloc(filedname);
        return expr->eval(context);
    }
    static void setAttr(PyContext& context, PyObjPtr& obj, const std::string& fieldName, PyObjPtr v){
        PyContextBackUp backup(context);
        context.curstack = obj;
        
        ExprASTPtr expr = singleton_t<VariableExprAllocator>::instance_ptr()->alloc(fieldName);
        expr->assignVal(context, v);
    }
};
template <typename T>
class PyCppClassHandler: public PyClassHandler{
public:
    PyCppClassHandler(){
    }

    virtual PyObjPtr& handleCall(PyContext& context, PyObjPtr& self, std::vector<ArgTypeInfo>& allArgsVal, std::vector<PyObjPtr>& argAssignVal);
};

template<typename T>
class PyCppClassDef:public PyObjClassDef {
public:
    PyCppClassDef(const std::string& s, std::vector<PyObjPtr>& a):PyObjClassDef(s){
        this->handler = singleton_t<PyCppClassHandler<T> >::instance_ptr();
    }

    //!TODO virtual std::map<std::string, PyObjPtr> getAllFieldData();
};

template<typename T>
class PyCppInstanceHandler: public PyClassInstanceHandler{
public:
    PyCppInstanceHandler(){
    }
    virtual int getType() const {
        return PY_CLASS_INST;
    }
    //!TODO virtual PyObjPtr& handleCall(PyContext& context, PyObjPtr& self, std::vector<ArgTypeInfo>& allArgsVal, std::vector<PyObjPtr>& argAssignVal);
};

template<typename T>
class PyCppClassInstance:public PyObjClassInstance {
public:
    typedef SmartPtr<T> PyCppPtr;
    
    PyCppClassInstance(T* o, PyObjPtr& v):cppobj(o), PyObjClassInstance(v){
        this->handler = singleton_t<PyCppInstanceHandler<T> >::instance_ptr();
    }

    virtual int getFieldNum() const { 
        return std::max(m_objStack.size(), classDefPtr->m_objStack.size()); 
    }
    virtual PyObjPtr& getVar(PyContext& context, PyObjPtr& self, unsigned int nFieldIndex){
        return self;//!TODO
    }
    
    virtual PyObjPtr& assignToField(PyContext& context, PyObjPtr& self, ExprASTPtr& fieldName, PyObjPtr& v){ //!special process field assign
        return self;//!TODO
    }
    
    PyCppPtr cppobj;
};

template<typename T>
PyObjPtr& PyCppClassHandler<T>::handleCall(PyContext& context, PyObjPtr& self, std::vector<ArgTypeInfo>& allArgsVal, std::vector<PyObjPtr>& argAssignVal){
    PyContextBackUp backup(context);
    
    PyObjPtr tmp = context.curstack;
    context.curstack = self;

    PyObjPtr __init__func = __init__->getFieldVal(context);
    context.curstack      = tmp;

    T* objcpp = NULL;
    

    if (__init__func && __init__func->getType() == PY_FUNC_DEF){
        //DMSG(("__init__func =%d", __init__func->getType()));
        __init__func->handler->handleCall(context, __init__func, allArgsVal, argAssignVal);
    }
    else{
        objcpp = new T();
    }
    PyObjPtr ret = new PyCppClassInstance<T>(objcpp, self);
    
    return context.cacheResult(ret);
}
}
#endif


