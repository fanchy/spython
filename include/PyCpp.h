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
    virtual PyObjPtr& getVar(PyContext& context, PyObjPtr& self, unsigned int nFieldIndex, ExprAST* e){
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
    

    if (__init__func && PyCheckFunc(__init__func)){
        //DMSG(("__init__func =%d", __init__func->getType()));
        __init__func->getHandler()->handleCall(context, __init__func, allArgsVal, argAssignVal);
    }
    else{
        objcpp = new T();
    }
    PyObjPtr ret = new PyCppClassInstance<T>(objcpp, self);
    
    return context.cacheResult(ret);
}
}
#endif


