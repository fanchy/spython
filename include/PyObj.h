#ifndef _PYOBJ_H_
#define _PYOBJ_H_

#include <iostream>
#include <string>
#include <vector>
#include <map>
#include <vector>
#include <stdexcept>

#include <iostream> 
#include <sstream> 
/*
#if __cplusplus < 201103L
    #ifdef __GNUC__
    #include <ext/hash_map>
    #else
    #include <hash_map>
    #endif
#else
    #include <unordered_map>
#endif
*/

#include "Base.h"
#include "Singleton.h"

#include "objhandler/PyIntHandler.h"
#include "objhandler/PyFloatHandler.h"
#include "objhandler/PyBoolHandler.h"
#include "objhandler/PyFuncHandler.h"
#include "objhandler/PyTupleHandler.h"
#include "objhandler/PyListHandler.h"
#include "objhandler/PyDictHandler.h"
#include "objhandler/PyStrHandler.h"
#include "objhandler/PyClassHandler.h"
#include "objhandler/PyClassInstanceHandler.h"
#include "objhandler/PyModHandler.h"

namespace ff {

#define THROW_EVAL_ERROR(X) throw PyException::buildException(X)
struct PyObjBuiltinTool{
    static PyObjPtr& getVar(PyContext& context, PyObjPtr& self, ExprAST* e, const std::string& strType);
};
class PyObjInt:public PyObj {
public:
    PyInt value;
    PyObjInt(PyInt n = 0):value(n) {
        this->handler = singleton_t<PyIntHandler>::instance_ptr();
    }
    virtual void dump() {
        std::ostringstream  ostr;
        ostr << value;
        DMSG(("%s", ostr.str().c_str()));
    }
    
    virtual const ObjIdInfo& getObjIdInfo(){
        return singleton_t<ObjIdTypeTraits<PyObjInt> >::instance_ptr()->objInfo;
    }
    PyObjPtr& getVar(PyContext& context, PyObjPtr& self, ExprAST* e){
        return PyObjBuiltinTool::getVar(context, self, e, "int");
    }
};

class PyObjFloat:public PyObj {
public:
    PyFloat value;
    PyObjFloat(PyFloat n = 0):value(n) {
        this->handler = singleton_t<PyFloatHandler>::instance_ptr();
    }
    virtual const ObjIdInfo& getObjIdInfo(){
        return singleton_t<ObjIdTypeTraits<PyObjFloat> >::instance_ptr()->objInfo;
    }
    PyObjPtr& getVar(PyContext& context, PyObjPtr& self, ExprAST* e){
        return PyObjBuiltinTool::getVar(context, self, e, "float");
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
    PyObjPtr& getVar(PyContext& context, PyObjPtr& self, ExprAST* e){
        return PyObjBuiltinTool::getVar(context, self, e, "bool");
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
    PyObjPtr& getVar(PyContext& context, PyObjPtr& self, ExprAST* e){
        return PyObjBuiltinTool::getVar(context, self, e, "str");
    }
    void append(const std::string& s){
        value += s;
    }
    void append(const char* s, size_t n){
        value.append(s, n);
    }
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
    PyObjPtr& getVar(PyContext& context, PyObjPtr& self, ExprAST* e){
        return PyObjBuiltinTool::getVar(context, self, e, "tuple");
    }
    void clear(){
        value.clear();
    }
    PyObjTuple& append(const PyObjPtr& v){
        value.push_back(v);
        return *this;
    }
    PyObjPtr& at(size_t i){
        return value.at(i);
    }
    size_t size() const{
        return value.size();
    }
    std::vector<PyObjPtr>& getValue(){
        return value;
    }
public:
    std::vector<PyObjPtr> value;
};
class PyObjList:public PyObj {
public:
    PyObjList(){
        this->handler = singleton_t<PyListHandler>::instance_ptr();
    }

    virtual const ObjIdInfo& getObjIdInfo(){
        return singleton_t<ObjIdTypeTraits<PyObjList> >::instance_ptr()->objInfo;
    }
    PyObjPtr& getVar(PyContext& context, PyObjPtr& self, ExprAST* e){
        return PyObjBuiltinTool::getVar(context, self, e, "list");
    }
    void clear(){
        value.clear();
    }
    PyObjList& append(const PyObjPtr& v){
        value.push_back(v);
        return *this;
    }
    size_t size(){
        return value.size();
    }
    void randShuffle();
    std::vector<PyObjPtr>& getValue(){
        return value;
    }
public:
    std::vector<PyObjPtr> value;
};
#define DICT_ITER_KEY(X) (X->first.key)
#define DICT_ITER_VAL(X) (X->second)

class PyObjDict:public PyObj {
public:
    struct Key{
        Key():hash(0), context(NULL){
        }
        Key(const Key& src):hash(src.hash), context(src.context), key(src.key){
        }
        bool operator==(const Key& src){
            return key->getHandler()->handleEqual(*context, key, src.key);
        }
        Key& operator =(const Key& src){
            hash = src.hash;
            context = src.context;
            key = src.key;
            return *this;
        }
        size_t      hash;
        PyContext*  context;
        PyObjPtr    key;
    };
    struct HashUtil{
        std::size_t operator()(const PyObjPtr& a) const {
            return size_t(a.get());
        }
    };
    
    //map的比较函数
    struct cmp_key
    {
        bool operator()(const Key &k1, const Key &k2)const;
    };
    PyObjDict();
    static PyObjPtr build();
    virtual const ObjIdInfo& getObjIdInfo(){
        return singleton_t<ObjIdTypeTraits<PyObjDict> >::instance_ptr()->objInfo;
    }
    PyObjPtr& getVar(PyContext& context, PyObjPtr& self, ExprAST* e){
        return PyObjBuiltinTool::getVar(context, self, e, "dict");
    }
    PyObjDict& set(PyContext& context, PyObjPtr &k, PyObjPtr &v);
    PyObjPtr get(PyContext& context, const PyObjPtr &k);
    PyObjPtr pop(PyContext& context, const PyObjPtr &k);
    PyObjPtr getValueAsList();//!return all dict key and value as [(key, value), ....]
    void clear();
    PyObjPtr copy();
    PyObjPtr keys();
    size_t   size();
    PyObjPtr popitem();
    PyObjPtr setdefault(PyContext& context, PyObjPtr &k, PyObjPtr &v);
    void update(PyContext& context, PyObjPtr& v);
    bool delByKey(PyContext& context, PyObjPtr &k);
public:
    typedef std::map<Key, PyObjPtr, cmp_key> DictMap;
    DictMap     value;
    size_t      version;
    size_t      versionCache;
    PyObjPtr    cacheAsList;
};

class PyCppFunc{
public:
    virtual ~PyCppFunc(){
    }
    
    virtual PyObjPtr& exeFunc(PyContext& context, PyObjPtr& self, std::vector<ArgTypeInfo>& allArgsVal, std::vector<PyObjPtr>& argAssignVal) = 0;
};
typedef SmartPtr<PyCppFunc> PyCppFuncPtr;

class PyCallTmpStack:public PyObj {
public:
    PyCallTmpStack(const ObjIdInfo& m, PyObjPtr v, PyObjPtr c):modBelong(v), closureStack(c){
        this->handler = singleton_t<PyCallStackHandler>::instance_ptr();
        selfObjInfo   = m;
    }
    virtual const ObjIdInfo& getObjIdInfo(){
        return selfObjInfo;
    }
    PyObjPtr& getVar(PyContext& context, PyObjPtr& self, ExprAST* e);
    PyObjPtr copy();
    bool isGlobalVar(ExprAST* e);
    void addGlobalVar(ExprAST* e);
    ObjIdInfo       selfObjInfo;
    PyObjPtr        modBelong;
    PyObjPtr        closureStack;
    std::set<ExprAST*>   globalVar;
};
#define IsFuncCallStack(o) (o->getType() == PY_CALL_STACK && o.cast<PyCallTmpStack>()->modBelong)

class PyObjFuncDef:public PyObj {
public:
    PyObjFuncDef(const std::string& n, ExprASTPtr p, ExprASTPtr s, PyCppFuncPtr f = NULL):name(n), parameters(p), suite(s), pyCppfunc(f){
        selfObjInfo = singleton_t<ObjIdTypeTraits<PyObjFuncDef> >::instance_ptr()->objInfo;
        //!different function has different object id 
        selfObjInfo.nObjectId = singleton_t<ObjFieldMetaData>::instance_ptr()->allocObjId();
        this->handler = singleton_t<PyFuncHandler>::instance_ptr();
        hasCopyClosure = false;
    }
    PyObjFuncDef(const std::string& n):name(n){
        this->handler = singleton_t<PyFuncHandler>::instance_ptr();
        hasCopyClosure = false;
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
        ret->closureStack  = closureStack;
        ret->hasCopyClosure= hasCopyClosure;
        ret->m_objStack = this->m_objStack;
        return ret;
    }
    bool hasSelfParam();
    PyObjPtr& getClosureStack();
    
    std::string     name;
    ExprASTPtr      parameters;
    ExprASTPtr      suite;
    ObjIdInfo       selfObjInfo;
    PyObjPtr        classInstance;
    
    PyCppFuncPtr    pyCppfunc;
    PyObjPtr        closureStack;
    bool            hasCopyClosure;//! try avoid loop reference
};

class PyObjClassDef:public PyObj {
public:
    static PyObjPtr build(PyContext& context, const std::string& s, ObjIdInfo* p = NULL, int nFileIdBelong = 0);
    static PyObjPtr build(PyContext& context, const std::string& s, std::vector<PyObjPtr>& parentClass, int nFileIdBelong = 0);
    PyObjClassDef(const std::string& s, ObjIdInfo* p = NULL, int n = 0);
    virtual const ObjIdInfo& getObjIdInfo(){
        return selfObjInfo;
    }
    void processInheritInfo(PyContext& context, PyObjPtr& self);
    PyObjPtr& getVar(PyContext& pc, PyObjPtr& self2, ExprAST* e);
    //virtual PyObjPtr& setVar(PyContext& c, PyObjPtr& self, ExprAST* e, PyObjPtr& v);
    std::string getModName(PyContext& context) const;
    PyObjPtr  getMod(PyContext& context) const ;
    std::string             name;
    int                     nFileId;
    std::vector<PyObjPtr>   parentClass;
    ObjIdInfo               selfObjInfo;
    ExprAST*                expr__class__;
};

class PyInstanceData: public BaseTypeInfo{
public:
    PyInstanceData():nValue(0){
    }
    virtual ~PyInstanceData(){}
    
    int                        nValue;
    std::vector<ExprASTPtr>    exprValues;
    std::vector<PyObjPtr>      objValues;
};
typedef SmartPtr<PyInstanceData> PyInstanceDataPtr;

class PyObjClassInstance:public PyObj {
public:
    PyObjClassInstance(PyObjPtr& v):classDefPtr(v){
        this->handler = singleton_t<PyClassInstanceHandler>::instance_ptr();
        
        selfObjInfo = classDefPtr->getObjIdInfo();
    }

    virtual const ObjIdInfo& getObjIdInfo(){
        return classDefPtr.cast<PyObjClassDef>()->getObjIdInfo();
    }
    virtual PyObjPtr& getVar(PyContext& context, PyObjPtr& self, ExprAST* e);
    
    virtual PyObjPtr& assignToField(PyContext& context, PyObjPtr& self, ExprASTPtr& fieldName, PyObjPtr& v); //!special process field assign
    void delField(PyContext& context, PyObjPtr& self, ExprASTPtr& fieldName); //!special process field del
    
    
    PyObjPtr            classDefPtr;
    ObjIdInfo           selfObjInfo;
    PyInstanceDataPtr   instanceData;
};

#define IS_PROPERTY_OBJ(context, x) (x->getType() == PY_CLASS_INST && x.cast<PyObjClassInstance>()->classDefPtr.get() == context.propertyClass.get())


class PyCppFuncWrap: public PyCppFunc{
public:
    typedef PyObjPtr  (*PyCppFunc)(PyContext& , std::vector<PyObjPtr>& );
    
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

class PyCppFuncWrapWithData: public PyCppFunc{
public:
    typedef PyObjPtr  (*PyCppFunc)(PyContext&, std::vector<PyObjPtr>&, std::vector<ExprASTPtr>&);
    
    PyCppFuncWrapWithData(PyCppFunc f, std::vector<ExprASTPtr>& data):cppFunc(f), funcdata(data){
    }
    virtual PyObjPtr& exeFunc(PyContext& context, PyObjPtr& self, std::vector<ArgTypeInfo>& allArgsVal, std::vector<PyObjPtr>& argAssignVal){
        if (cppFunc){
            PyObjPtr v = (*cppFunc)(context, argAssignVal, funcdata);
            return context.cacheResult(v);
        }
        return context.cacheResult(PyObjTool::buildNone());
    }
public:
    PyCppFunc     cppFunc;
    std::vector<ExprASTPtr>        funcdata;
};
class PyCppFuncWrapArgName: public PyCppFunc{
public:
    typedef PyObjPtr  (*PyCppFunc)(PyContext& , std::vector<ArgTypeInfo>& , std::vector<PyObjPtr>& );
    
    PyCppFuncWrapArgName(PyCppFunc f):cppFunc(f){
    }
    virtual PyObjPtr& exeFunc(PyContext& context, PyObjPtr& self, std::vector<ArgTypeInfo>& allArgsVal, std::vector<PyObjPtr>& argAssignVal){
        if (cppFunc){
            PyObjPtr v = (*cppFunc)(context, allArgsVal, argAssignVal);
            return context.cacheResult(v);
        }
        return context.cacheResult(PyObjTool::buildNone());
    }
public:
    PyCppFunc     cppFunc;
};

class PyCppClassFuncWrap: public PyCppFunc{
public:
    typedef PyObjPtr  (*PyCppFunc)(PyContext& , PyObjPtr& , std::vector<PyObjPtr>& );
    
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
class PyCppClassFuncWrapArgName: public PyCppFunc{
public:
    typedef PyObjPtr  (*PyCppFunc)(PyContext& , PyObjPtr& , std::vector<ArgTypeInfo>& , std::vector<PyObjPtr>& );
    
    PyCppClassFuncWrapArgName(PyCppFunc f):cppFunc(f){
    }
    virtual PyObjPtr& exeFunc(PyContext& context, PyObjPtr& self, std::vector<ArgTypeInfo>& allArgsVal, std::vector<PyObjPtr>& argAssignVal){
        if (cppFunc){
            PyObjPtr& selfobj = self.cast<PyObjFuncDef>()->classInstance;
            if (!selfobj){
                throw PyException::buildException("arg self not assigned");
            }
            PyObjPtr v = (*cppFunc)(context, selfobj, allArgsVal, argAssignVal);
            return context.cacheResult(v);
        }
        return context.cacheResult(PyObjTool::buildNone());
    }
public:
    PyCppFunc     cppFunc;
};

#define PyCheckNone(x) (x->getType() == PY_NONE)
#define PyCheckInt(x) (x->getType() == PY_INT)
#define PyAssertInt(x) PyCppUtil::pyAssert(x, PY_INT)
#define PyCheckFloat(x) (x->getType() == PY_FLOAT)
#define PyAssertFloat(x) PyCppUtil::pyAssert(x, PY_FLOAT)
#define PyCheckStr(x) (x->getType() == PY_STR)
#define PyAssertStr(x) PyCppUtil::pyAssert(x, PY_STR)
#define PyCheckBool(x) (x->getType() == PY_BOOL)
#define PyAssertBool(x) PyCppUtil::pyAssert(x, PY_BOOL)

#define PyCheckFunc(x) (x->getType() == PY_FUNC_DEF)
#define PyAsserFunc(x) PyCppUtil::pyAssert(x, PY_FUNC_DEF)
#define PyCheckCallable(x) (x->getType() == PY_FUNC_DEF || x->getType() == PY_CLASS_DEF)

#define PyCheckModule(x) (x->getType() == PY_MOD)
#define PyAsserModule(x) PyCppUtil::pyAssert(x, PY_MOD)

#define PyCheckTuple(x) (x->getType() == PY_TUPLE)
#define PyAssertTuple(x) PyCppUtil::pyAssert(x, PY_TUPLE)
#define PyCheckList(x) (x->getType() == PY_LIST)
#define PyAssertList(x) PyCppUtil::pyAssert(x, PY_LIST)
#define PyCheckDict(x) (x->getType() == PY_DICT)
#define PyAssertDict(x) PyCppUtil::pyAssert(x, PY_DICT)

#define PyCheckClass(x) (x->getType() == PY_CLASS_DEF)
#define PyCheckInstance(x) (x->getType() == PY_CLASS_INST)
#define PyAssertInstance(x) PyCppUtil::pyAssert(x, PY_CLASS_INST)

#define PY_RAISE_STR(context, v) context.cacheResult(PyCppUtil::genStr(v)); throw PyExceptionSignal()
#define PY_ASSERT_ARG_SIZE(context, given, need, funcname) \
    do{ if(given != need){ \
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: %s() takes exactly %d argument (%u given)", std::string(funcname).c_str(), need, given)); \
        } \
    }while(0)


struct PyCppUtil{
    static std::string strFormat(const char * format, ...);
    static void pyAssert(PyObjPtr& v, int nType){
        if (v->getType() != nType){
            throw PyException::buildException("%d instance needed, given:%d", nType, v->getType());
        }
    }
    static PyInt toInt(PyObjPtr v){
        if (PyCheckInt(v)){
            return v.cast<PyObjInt>()->value;
        }
        else if (PyCheckFloat(v)){
            return PyInt(v.cast<PyObjFloat>()->value);
        }
        PyAssertInt(v);
        return 0;
    }
    static PyFloat toFloat(PyObjPtr v){
        if (PyCheckInt(v)){
            return PyFloat(v.cast<PyObjInt>()->value);
        }
        else if (PyCheckFloat(v)){
            return PyFloat(v.cast<PyObjFloat>()->value);
        }
        PyAssertFloat(v);
        return 0.0;
    }
    static std::string toStr(PyObjPtr v){
        if (PyCheckStr(v)){
            return v.cast<PyObjStr>()->value;
        }
        PyAssertStr(v);
        return "";
    }
    static bool toBool(PyObjPtr v){
        if (PyCheckBool(v)){
            return v.cast<PyObjBool>()->value;
        }
        return false;
    }
    static PyObjPtr genInt(PyInt n){
        return new PyObjInt(n);
    }
    static PyObjPtr genFloat(PyFloat n){
        return new PyObjFloat(n);
    }
    static PyObjPtr genStr(const std::string& s){
        return new PyObjStr(s);
    }
    static std::string int2str(PyInt value){
        std::ostringstream  ostr;
        ostr << value;
        return ostr.str();
    }
    
    static PyObjPtr genFunc(PyCppFuncWrapWithData::PyCppFunc f, std::vector<ExprASTPtr>& data, std::string n = ""){
        return new PyObjFuncDef(n, NULL, NULL, new PyCppFuncWrapWithData(f, data));
    }
    static PyObjPtr genFunc(PyCppFuncWrap::PyCppFunc f, std::string n = ""){
        return new PyObjFuncDef(n, NULL, NULL, new PyCppFuncWrap(f));
    }
    static PyObjPtr genFunc(PyCppFuncWrapArgName::PyCppFunc f, std::string n = ""){
        return new PyObjFuncDef(n, NULL, NULL, new PyCppFuncWrapArgName(f));
    }
    static PyObjPtr genFunc(PyCppClassFuncWrap::PyCppFunc f, std::string n = ""){
        return new PyObjFuncDef(n, NULL, NULL, new PyCppClassFuncWrap(f));
    }
    static PyObjPtr genFunc(PyCppClassFuncWrapArgName::PyCppFunc f, std::string n = ""){
        return new PyObjFuncDef(n, NULL, NULL, new PyCppClassFuncWrapArgName(f));
    }
    
    static PyObjPtr getAttr(PyContext& context, PyObjPtr& obj, const std::string& filedname);
    static bool hasAttr(PyContext& context, PyObjPtr& obj, const std::string& filedname);
    static void setAttr(PyContext& context, PyObjPtr& obj, const std::string& fieldName, PyObjPtr v);
    
    static std::map<std::string, PyObjPtr> getAllFieldData(PyObjPtr obj);
    static PyObjPtr& callPyfunc(PyContext& context, PyObjPtr& obj, std::vector<PyObjPtr>& args);
    static PyObjPtr& callPyObjfunc(PyContext& context, PyObjPtr& func, const std::string& funName, std::vector<PyObjPtr>& args);
    static PyObjPtr getArgVal(std::vector<ArgTypeInfo>& allArgsVal, std::vector<PyObjPtr>& argAssignVal, size_t index,
                              const std::string& argName);
                              
    static std::string hexstr(const std::string& src);
};
struct IterUtil{
    IterUtil(PyContext& context, PyObjPtr v);
    PyObjPtr next();
    
    PyContext& context;
    PyObjPtr  obj;
    int       index;
    PyObjPtr  funcNext;
    std::vector<PyObjPtr> funcagsTmp;
};

}
#endif


