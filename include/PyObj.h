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
#include "objhandler/PyModHandler.h"
#include "objhandler/PyBuiltinTypeHandler.h"

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
    PyObjPtr& getVar(PyContext& context, PyObjPtr& self, unsigned int nFieldIndex, ExprAST* e);
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
    PyObjPtr& getVar(PyContext& context, PyObjPtr& self, unsigned int nFieldIndex, ExprAST* e);
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
    PyObjPtr& getVar(PyContext& context, PyObjPtr& self, unsigned int nFieldIndex, ExprAST* e);
};


class PyObjModule:public PyObj {
public:
    enum {
        MOD_LOADING = 0,
        MOD_LOADOK
    };
    static PyObjPtr BuildModule(PyContext& context, const std::string& s, const std::string& p);
    PyObjModule(const std::string& v, std::string p = "built-in"):loadFlag(MOD_LOADING), moduleName(v),path(p) {
        this->handler = singleton_t<PyModHandler>::instance_ptr();
        selfObjInfo = singleton_t<ObjIdTypeTraits<PyObjModule> >::instance_ptr()->objInfo;
        //!different function has different object id 
        selfObjInfo.nObjectId = singleton_t<ObjFieldMetaData>::instance_ptr()->allocObjId();
    }

    virtual const ObjIdInfo& getObjIdInfo(){
        return selfObjInfo;
    }
public:
    int                             loadFlag; //!0 loading 1 load ok
    std::string                     moduleName;
    std::string                     path;
    ObjIdInfo                       selfObjInfo;  
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
    
    //map的比较函数
    struct cmp_key
    {
        bool operator()(const PyObjPtr &k1, const PyObjPtr &k2)const
        {
            std::size_t a = k1->getHandler()->handleHash(k1);
            std::size_t b = k2->getHandler()->handleHash(k2);
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

class PyCppFunc{
public:
    virtual ~PyCppFunc(){
    }
    
    virtual PyObjPtr& exeFunc(PyContext& context, PyObjPtr& self, std::vector<ArgTypeInfo>& allArgsVal, std::vector<PyObjPtr>& argAssignVal) = 0;
};
typedef SmartPtr<PyCppFunc> PyCppFuncPtr;

class PyObjFuncDef:public PyObj {
public:
    PyObjFuncDef(const std::string& n, ExprASTPtr p, ExprASTPtr s, PyCppFuncPtr f = NULL):name(n), parameters(p), suite(s), pyCppfunc(f){
        selfObjInfo = singleton_t<ObjIdTypeTraits<PyObjFuncDef> >::instance_ptr()->objInfo;
        //!different function has different object id 
        selfObjInfo.nObjectId = singleton_t<ObjFieldMetaData>::instance_ptr()->allocObjId();
        this->handler = singleton_t<PyFuncHandler>::instance_ptr();
    }
    PyObjFuncDef(const std::string& n):name(n){
        this->handler = singleton_t<PyFuncHandler>::instance_ptr();
    }
    //PyObjPtr& exeFunc(PyContext& context, PyObjPtr& self, ExprASTPtr& arglist);
    void processParam(PyContext& context, PyObjPtr& self, std::vector<ArgTypeInfo>& allArgsVal, std::vector<PyObjPtr>& argAssignVal);
    PyObjPtr& exeFunc(PyContext& context, PyObjPtr& self, std::vector<ArgTypeInfo>& allArgsVal, std::vector<PyObjPtr>& argAssignVal);
    
    virtual const ObjIdInfo& getObjIdInfo(){
        return selfObjInfo;
    }
    
    PyObjPtr forkClassFunc(PyObjPtr& obj){
        PyObjFuncDef* ret  = new PyObjFuncDef(name);
        ret->selfObjInfo   = selfObjInfo;
        ret->parameters    = parameters;
        ret->suite         = suite;
        ret->classInstance = obj;
        ret->pyCppfunc     = pyCppfunc;
        return ret;
    }
    bool hasSelfParam();
    
    std::string     name;
    ExprASTPtr      parameters;
    ExprASTPtr      suite;
    ObjIdInfo       selfObjInfo;
    PyObjPtr        classInstance;
    
    PyCppFuncPtr    pyCppfunc;
};

class PyObjClassDef:public PyObj {
public:
    static PyObjPtr build(PyContext& context, const std::string& s, ObjIdInfo* p = NULL);
    static PyObjPtr build(PyContext& context, const std::string& s, std::vector<PyObjPtr>& parentClass);
    PyObjClassDef(const std::string& s, ObjIdInfo* p = NULL);
    virtual const ObjIdInfo& getObjIdInfo(){
        return selfObjInfo;
    }
    void processInheritInfo(PyContext& context, PyObjPtr& self);
    PyObjPtr& getVar(PyContext& pc, PyObjPtr& self2, unsigned int nFieldIndex, ExprAST* e);
    
    std::string             name;
    std::vector<PyObjPtr>   parentClass;
    ObjIdInfo               selfObjInfo;
    //int                     __class__fieldindex;
    ExprAST*                expr__class__;
};

class PyObjClassInstance:public PyObj {
public:
    PyObjClassInstance(PyObjPtr& v):classDefPtr(v){
        this->handler = singleton_t<PyClassInstanceHandler>::instance_ptr();
        
        selfObjInfo = classDefPtr->getObjIdInfo();
    }

    virtual const ObjIdInfo& getObjIdInfo(){
        return classDefPtr.cast<PyObjClassDef>()->getObjIdInfo();
    }
    virtual int getFieldNum() const { 
        return std::max(m_objStack.size(), classDefPtr->m_objStack.size()); 
    }
    virtual PyObjPtr& getVar(PyContext& context, PyObjPtr& self, unsigned int nFieldIndex, ExprAST* e);
    
    virtual PyObjPtr& assignToField(PyContext& context, PyObjPtr& self, ExprASTPtr& fieldName, PyObjPtr& v); //!special process field assign
    
    
    PyObjPtr            classDefPtr;
    ObjIdInfo           selfObjInfo;
};

class PyBuiltinTypeInfo:public PyObj {
public:
    PyBuiltinTypeInfo(int n):nType(n){
        this->handler = singleton_t<PyBuiltinTypeHandler>::instance_ptr();
    }

    virtual const ObjIdInfo& getObjIdInfo(){
        return singleton_t<ObjIdTypeTraits<PyBuiltinTypeInfo> >::instance_ptr()->objInfo;
    }

    int nType;
};


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
    static PyObjPtr getAttr(PyContext& context, PyObjPtr& obj, const std::string& filedname);
    static void setAttr(PyContext& context, PyObjPtr& obj, const std::string& fieldName, PyObjPtr v);
    
    static std::map<std::string, PyObjPtr> getAllFieldData(PyObjPtr obj);
};
}
#endif


