#ifndef _PYOBJ_H_
#define _PYOBJ_H_

#include <iostream>
#include <string>
#include <vector>
#include <map>
#include <vector>
#include <stdexcept>
/*
#ifdef __GNUC__
#include <ext/hash_map>
#else
#include <hash_map>
#endif
*/

#include "Base.h"
#include "singleton.h"

#include "objhandler/PyIntHandler.h"
#include "objhandler/PyFloatHandler.h"
#include "objhandler/PyBoolHandler.h"
#include "objhandler/PyFuncHandler.h"
#include "objhandler/PyTupleHandler.h"
#include "objhandler/PyDictHandler.h"
#include "objhandler/PyStrHandler.h"
#include "objhandler/PyClassHandler.h"
#include "objhandler/PyClassInstanceHandler.h"

namespace ff {

#define THROW_EVAL_ERROR(X) throw PyException::buildException(X)

class PyObjInt:public PyObj {
public:
    long value;
    PyObjInt(long n = 0):value(n) {
        this->handler = singleton_t<PyIntHandler>::instance_ptr();
    }
    virtual void dump() {
        DMSG(("%ld(int)", value));
    }
    
    virtual bool handleEQ(PyObjPtr arg){
        if (arg && arg->getType() == this->getType()){
            return arg.cast<PyObjInt>()->value == this->value;
        }
        return false;
    }
    
    virtual const ObjIdInfo& getObjIdInfo(){
        return singleton_t<ObjIdTypeTraits<PyObjInt> >::instance_ptr()->objInfo;
    }
};

class PyObjFloat:public PyObj {
public:
    double value;
    PyObjFloat(double n = 0):value(n) {
        this->handler = singleton_t<PyFloatHandler>::instance_ptr();
    }
    virtual const ObjIdInfo& getObjIdInfo(){
        return singleton_t<ObjIdTypeTraits<PyObjFloat> >::instance_ptr()->objInfo;
    }
};
class PyObjBool:public PyObj {
public:
    bool value;
    PyObjBool(bool n = false):value(n) {
        this->handler = singleton_t<PyBoolHandler>::instance_ptr();
    }

    virtual const ObjIdInfo& getObjIdInfo(){
        return singleton_t<ObjIdTypeTraits<PyObjBool> >::instance_ptr()->objInfo;
    }
};
typedef SmartPtr<PyObjBool> PyObjBoolPtr;

class PyObjStr:public PyObj {
public:
    std::string value;
    PyObjStr(const std::string& v):value(v) {
        this->handler = singleton_t<PyStrHandler>::instance_ptr();
    }

    virtual const ObjIdInfo& getObjIdInfo(){
        return singleton_t<ObjIdTypeTraits<PyObjStr> >::instance_ptr()->objInfo;
    }
};


class PyObjModule:public PyObj {
public:
    std::string moduleName;
    PyObjModule(const std::string& v):moduleName(v) {
        this->handler = new PyObjHandler();
        selfObjInfo = singleton_t<ObjIdTypeTraits<PyObjModule> >::instance_ptr()->objInfo;
        //!different function has different object id 
        selfObjInfo.nObjectId = singleton_t<ObjFieldMetaData>::instance_ptr()->allocObjId();
    }
    virtual int getType() const {
        return PY_MOD;
    }
    virtual const ObjIdInfo& getObjIdInfo(){
        return selfObjInfo;
    }
    ObjIdInfo  selfObjInfo;
};

class PyObjTuple:public PyObj {
public:
    PyObjTuple(){
        this->handler = singleton_t<PyTupleHandler>::instance_ptr();
    }

    virtual const ObjIdInfo& getObjIdInfo(){
        return singleton_t<ObjIdTypeTraits<PyObjTuple> >::instance_ptr()->objInfo;
    }

    std::vector<PyObjPtr> value;
};

class PyObjDict:public PyObj {
public:
    struct HashUtil{
        std::size_t operator()(const PyObjPtr& a) const {
            return size_t(a.get());
        }
    };
    
    //map�ıȽϺ���
    struct cmp_key
    {
        bool operator()(const PyObjPtr &k1, const PyObjPtr &k2)const
        {
            std::size_t a = k1->handler->handleHash(k1);
            std::size_t b = k2->handler->handleHash(k2);
            return a < b;
        }
    };
    PyObjDict(){
        this->handler = singleton_t<PyDictHandler>::instance_ptr();
    }
    virtual const ObjIdInfo& getObjIdInfo(){
        return singleton_t<ObjIdTypeTraits<PyObjTuple> >::instance_ptr()->objInfo;
    }
    typedef std::map<PyObjPtr, PyObjPtr, cmp_key> DictMap;
    DictMap value;
};

class PyObjFuncDef:public PyObj {
public:
    PyObjFuncDef(const std::string& n, ExprASTPtr& p, ExprASTPtr& s):name(n), parameters(p), suite(s){
        selfObjInfo = singleton_t<ObjIdTypeTraits<PyObjFuncDef> >::instance_ptr()->objInfo;
        //!different function has different object id 
        selfObjInfo.nObjectId = singleton_t<ObjFieldMetaData>::instance_ptr()->allocObjId();
        this->handler = singleton_t<PyFuncHandler>::instance_ptr();
    }

    //PyObjPtr& exeFunc(PyContext& context, PyObjPtr& self, ExprASTPtr& arglist);
    PyObjPtr& exeFunc(PyContext& context, PyObjPtr& self, std::vector<ArgTypeInfo>& allArgsVal, std::vector<PyObjPtr>& argAssignVal);
    
    virtual const ObjIdInfo& getObjIdInfo(){
        return selfObjInfo;
    }
    
    PyObjPtr forkClassFunc(PyObjPtr& obj){
        PyObjFuncDef* ret  = new PyObjFuncDef(name, parameters, suite);
        ret->classInstance = obj;
        return ret;
    }
    bool hasSelfParam();
    
    std::string     name;
    ExprASTPtr      parameters;
    ExprASTPtr      suite;
    ObjIdInfo       selfObjInfo;
    PyObjPtr        classInstance;
};

class PyObjClassDef:public PyObj {
public:
    PyObjClassDef(const std::string& s, ExprASTPtr& a, ExprASTPtr& b):name(s), testlist(a), suite(b) {
        selfObjInfo = singleton_t<ObjIdTypeTraits<PyObjFuncDef> >::instance_ptr()->objInfo;
        //!different function has different object id 
        selfObjInfo.nObjectId = singleton_t<ObjFieldMetaData>::instance_ptr()->allocObjId();
        this->handler = singleton_t<PyClassHandler>::instance_ptr();
    }

    virtual const ObjIdInfo& getObjIdInfo(){
        return selfObjInfo;
    }
    std::string             name;
    ExprASTPtr              testlist;
    ExprASTPtr              suite;
    ObjIdInfo  selfObjInfo;
};

class PyObjClassInstance:public PyObj {
public:
    PyObjClassInstance(PyObjPtr& v):classDefPtr(v){
        this->handler = singleton_t<PyClassInstanceHandler>::instance_ptr();
        
        selfObjInfo = classDefPtr->getObjIdInfo();
        m_objStack.resize(classDefPtr->m_objStack.size(), PyObjTool::buildNULL());
    }

    virtual const ObjIdInfo& getObjIdInfo(){
        return classDefPtr.cast<PyObjClassDef>()->getObjIdInfo();
    }
    
    virtual PyObjPtr& getVar(PyContext& context, PyObjPtr& self, unsigned int nFieldIndex);
    PyObjPtr            classDefPtr;
    ObjIdInfo           selfObjInfo;
};

}
#endif


