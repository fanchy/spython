#ifndef _BASE_H_
#define _BASE_H_

#include <string>
#include <map>
#include <vector>
#include <list>
#include <set>
#include <stdexcept>

#include "SmartPtr.h"
#include "Singleton.h"
#include "TypeInfo.h"

#include <stdio.h>
#include <stdint.h>
#include <inttypes.h>

#define DTRACE(x) {}//printf x ; printf("\n")
#define DMSG(x) printf x ; printf("\n")

namespace ff {

enum PyObjType{
    PY_NONE = 1,
    PY_INT,
    PY_FLOAT,
    PY_STR,
    PY_BOOL,
    PY_FUNC_DEF,
    PY_CLASS_FUNC,
    PY_CLASS_DEF,
    PY_CLASS_INST,
    PY_MOD,
    PY_TUPLE,
    PY_LIST,
    PY_DICT,
    PY_BUILTIN_TYPE
};

typedef  int TokenType;
typedef  int64_t PyInt;
typedef  double PyFloat;

enum ETokenType {
    TOK_EOF = 0,
    //TOK_DEF = -2,
    TOK_VAR = -4,
    TOK_INT = -5,
    TOK_FLOAT = -6,
    TOK_STR = -7,
    TOK_CHAR = -8,
};

class PyMetaType{
public:
    inline int allocFieldId(const std::string& name){
        std::map<std::string, int>::iterator it = name2field.find(name);
        if (it != name2field.end()){
            return it->second;
        }
        int n = name2field.size();
        name2field[name] = n;
        return n;
    }
    inline std::string id2name(int nFieldId){
        for (std::map<std::string, int>::iterator it = name2field.begin(); it != name2field.end(); ++it){
            if (it->second == nFieldId){
                return it->first;
            }
        }
        return "";
    }

private:
    std::map<std::string, int> name2field;
};

class ParseHelper;

struct PyException {
    static std::runtime_error buildException(const char * format, ...);
};

struct PyHelper{
    PyHelper();
    bool isKeyword(const std::string& v);
    
    std::set<std::string>    m_allKeyword;
}; 

class PyContext;

class ExprAST;

struct ObjIdInfo{
    ObjIdInfo():nModuleId(0), nObjectId(0){}

    unsigned int nModuleId;
    unsigned int nObjectId;
    std::string strFieldName;
};


struct ObjFieldMetaData{
    ObjFieldMetaData():nCountMeta(0){
    }
    //!module id -> objectid -> fieldid -> fieldname
    std::map<int, std::map<int,  std::map<int, std::string> > >        module2object2fieldname;

    const std::string& getFieldName(int moduleid, int objectid, int nFieldId) {
        return module2object2fieldname[moduleid][objectid][nFieldId];
    }
    int allocObjId() {
        return nCountMeta++;
    }
    int nCountMeta;
};

template<typename T>
struct ObjIdTypeTraits{
    ObjIdTypeTraits(){
        objInfo.nModuleId = 0;
        objInfo.nObjectId = singleton_t<ObjFieldMetaData>::instance_ptr()->allocObjId();
    }

    ObjIdInfo objInfo;
};
class PyObjHandler;
class PyContext;
class ExprAST;
class PyObj {
public:
    typedef SmartPtr<PyObj> PyObjPtr;
    PyObj():m_pObjIdInfo(NULL), handler(NULL){}
    virtual ~PyObj() {}

    int getType() const;
    virtual int getFieldNum() const { return m_objStack.size(); }
    static std::string dump(PyContext& context, PyObjPtr& self, int preBlank = 0);

    virtual PyObjPtr& getVar(PyContext& c, PyObjPtr& self, ExprAST* e);
    virtual const ObjIdInfo& getObjIdInfo() = 0;

    void clear(){
        m_objStack.clear();
    }
    inline PyObjHandler* getHandler() { return handler; }
    inline const PyObjHandler* getHandler() const { return handler; }
public:
    std::vector<PyObjPtr>    m_objStack;
    ObjIdInfo*               m_pObjIdInfo;
    PyObjHandler*            handler;
};
typedef PyObj::PyObjPtr PyObjPtr;


struct PyObjTool{
    static PyObjPtr  buildNULL();
    static PyObjPtr& buildNone();
    static PyObjPtr& buildBool(bool b);
    static PyObjPtr& buildTrue();
    static PyObjPtr& buildFalse();
    static bool handleBool(PyObjPtr b);
}; 

struct ExprLine{
    ExprLine():fileId(0), nLine(0){
    }
    int         fileId;
    int         nLine;
};

class ExprAST {
public:
    //int    nFieldId;
    std::string name;
    ExprLine    lineInfo;
    ExprAST(){
    }
    virtual ~ExprAST() {}
    virtual PyObjPtr& eval(PyContext& context) = 0;

    unsigned int getFieldIndex(PyContext& context, PyObjPtr& obj);
    
    virtual PyObjPtr& getFieldVal(PyContext& context);
    virtual PyObjPtr& assignVal(PyContext& context, PyObjPtr& v){
        PyObjPtr& lval = this->eval(context);
        lval = v;
        return lval;
    }
    virtual void delVal(PyContext& context){
        PyObjPtr& lval = this->eval(context);
        lval = NULL;
    }
    
    virtual int getType() {
        return 0;
    }

    virtual std::string dump(int nDepth){
        std::string ret;
        for (int i = 0; i < nDepth; ++i){
            ret += "-";
        }
        char tmp[64] = {0};
        snprintf(tmp, sizeof(tmp), "%s", name.c_str());
        ret += tmp;
        return ret;
    }
    //std::vector<std::vector<int> >  module2objcet2fieldIndex;
    std::vector<int>                  module2objcet2fieldIndex;
};

typedef SmartPtr<ExprAST> ExprASTPtr;

struct ArgTypeInfo{
    std::string      argType; //! epmpty = * **
    std::string      argKey;
    ArgTypeInfo(){
    }
    ArgTypeInfo(const ArgTypeInfo& src){
        argType = src.argType;
        argKey  = src.argKey;
    }
};

class PyObjHandler{
public:
    virtual ~PyObjHandler(){}
    
    virtual int getType() const = 0;

    virtual std::string handleStr(PyContext& context, const PyObjPtr& self) const{
        return "";
    }
    virtual std::string handleRepr(PyContext& context, const PyObjPtr& self) const{
        return "";
    }
    virtual int handleCmp(PyContext& context, const PyObjPtr& self, const PyObjPtr& val) const;
    virtual bool handleBool(PyContext& context, const PyObjPtr& self) const;
    virtual bool handleEqual(PyContext& context, const PyObjPtr& self, const PyObjPtr& val) const;
    virtual bool handleLessEqual(PyContext& context, const PyObjPtr& self, const PyObjPtr& val) const;
    virtual bool handleGreatEqual(PyContext& context, const PyObjPtr& self, const PyObjPtr& val) const;
    virtual bool handleContains(PyContext& context, const PyObjPtr& self, const PyObjPtr& val) const;
    
    virtual bool handleLess(PyContext& context, const PyObjPtr& self, const PyObjPtr& val) const{
        if (self->getHandler()->handleGreatEqual(context, self, val) == false){
            return true;
        }
        return false;
    }
    virtual bool handleGreat(PyContext& context, const PyObjPtr& self, const PyObjPtr& val) const{
        if (self->getHandler()->handleLessEqual(context, self, val) == false){
            return true;
        }
        return false;
    }
    
    virtual PyObjPtr& handleAdd(PyContext& context, PyObjPtr& self, PyObjPtr& val);
    virtual PyObjPtr& handleSub(PyContext& context, PyObjPtr& self, PyObjPtr& val);
    virtual PyObjPtr& handleMul(PyContext& context, PyObjPtr& self, PyObjPtr& val);
    virtual PyObjPtr& handleDiv(PyContext& context, PyObjPtr& self, PyObjPtr& val);
    virtual PyObjPtr& handleMod(PyContext& context, PyObjPtr& self, PyObjPtr& val);
    
    
    virtual PyObjPtr& handleIAdd(PyContext& context, PyObjPtr& self, PyObjPtr& val);
    virtual PyObjPtr& handleISub(PyContext& context, PyObjPtr& self, PyObjPtr& val);
    virtual PyObjPtr& handleIMul(PyContext& context, PyObjPtr& self, PyObjPtr& val);
    virtual PyObjPtr& handleIDiv(PyContext& context, PyObjPtr& self, PyObjPtr& val);
    virtual PyObjPtr& handleIMod(PyContext& context, PyObjPtr& self, PyObjPtr& val);
    
    virtual PyObjPtr& handleCall(PyContext& context, PyObjPtr& self, std::vector<ArgTypeInfo>& allArgsVal, 
                                 std::vector<PyObjPtr>& argAssignVal);
    virtual size_t    handleHash(PyContext& context, const PyObjPtr& self) const;
    virtual bool handleIsInstance(PyContext& context, PyObjPtr& self, PyObjPtr& val);
    virtual long handleLen(PyContext& context, PyObjPtr& self);
    virtual std::string dump(PyObjPtr& self) {
        return "";
    }
    virtual PyObjPtr& handleSlice(PyContext& context, PyObjPtr& self, PyObjPtr& startVal, int* stop, int step);
    virtual PyObjPtr& handleSliceAssign(PyContext& context, PyObjPtr& self, PyObjPtr& k, PyObjPtr& v);
    virtual void handleSliceDel(PyContext& context, PyObjPtr& self, PyObjPtr& k){}
};

class PyNoneHandler: public PyObjHandler{
public:
    virtual int getType() const{
        return PY_NONE;
    }
    virtual std::string handleStr(PyContext& context, const PyObjPtr& self) const{
        return "None";
    }
    bool handleBool(PyContext& context, const PyObjPtr& self){
        return false;
    }
    bool handleEqual(PyContext& context, const PyObjPtr& self, const PyObjPtr& val){
        return val->getType() == PY_NONE;
    }
};
class PyObjNone:public PyObj {
public:
    PyObjNone(bool b = false):isNull(b){
        this->handler = singleton_t<PyNoneHandler>::instance_ptr();
        selfObjInfo   = singleton_t<ObjIdTypeTraits<PyObjNone> >::instance_ptr()->objInfo;
    }
    /*
    PyObjNone(const ObjIdInfo& m, PyObjPtr v):modBelong(v){
        this->handler = singleton_t<PyNoneHandler>::instance_ptr();
        selfObjInfo   = m;
    }*/
    virtual const ObjIdInfo& getObjIdInfo(){
        return selfObjInfo;
    }
    ObjIdInfo       selfObjInfo;
    bool            isNull;
    //PyObjPtr        modBelong;
};
//typedef PyObjNone PyCallTmpStack;

#define IS_NULL(o) (o.get() == NULL)
//#define IsFuncCallStack(o) (o->getType() == PY_NONE && o.cast<PyObjNone>()->modBelong)


class PyContext{
public:
    struct FileInfo{
        FileInfo(){
        }
        FileInfo(const FileInfo& src){
            path = src.path;
            line2Code = src.line2Code;
            modCache = src.modCache;
        }
        std::string                 path;
        std::map<int, std::string>  line2Code;
        PyObjPtr                    modCache;
    };
public:
    ~PyContext(){
        {
            std::map<std::string, PyObjPtr>::iterator it = allBuiltin.begin();
            for (; it != allBuiltin.end(); ++it){
                if (it->second){
                    it->second->clear();
                }
            }
            allBuiltin.clear();
        }
        
        {
            std::map<int, FileInfo>::iterator it = fileId2Info.begin();
            for (; it != fileId2Info.end(); ++it){
                if (it->second.modCache){
                    it->second.modCache->clear();
                }
            }
            fileId2Info.clear();
        }
    }
    PyObjPtr& cacheResult(PyObjPtr v){
        evalResult = v;
        return evalResult;
    }
    PyObjPtr& getCacheResult(){
        return evalResult;
    }

    void setTraceExpr(ExprAST* e){
        if (e->lineInfo.fileId == 0){
            return;
        }
        if (exprTrace.empty()){
            exprTrace.push_back(e);
        }
        else{
            exprTrace.back() = e;
        }
    }
    void pushTraceExpr(ExprAST* e){
        setTraceExpr(e);
        exprTrace.push_back(NULL);
    }
    void popTraceExpr(){
        exprTrace.pop_back();
    }
    int getCurExprFileId() {
        if (!exprTrace.empty()){
            exprTrace.back()->lineInfo.fileId;
        }
        return 0;
    }
    std::string getFileId2Path(int n){
        std::map<int, FileInfo>::iterator it = fileId2Info.find(n);
        if (it != fileId2Info.end()){
            return it->second.path;
        }
        
        char msg[128] = {0};
        snprintf(msg, sizeof(msg), "fileid:%d", n);
        return std::string(msg);
    }
    int allocFileIdByPath(const std::string& f){
        std::map<int, FileInfo>::iterator it = fileId2Info.begin();
        for (; it != fileId2Info.end(); ++it){
            if (it->second.path == f){
                return it->first;
            }
        }
        int n = fileId2Info.size() + 1;
        fileId2Info[n].path = f;
        return n;
    }
    void setFileIdLineInfo(int nFiledId, std::map<int, std::string>& line2Code){
        fileId2Info[nFiledId].line2Code = line2Code;
    }
    void setFileIdModCache(int nFiledId, PyObjPtr v){
        fileId2Info[nFiledId].modCache = v;
    }
    
    PyObjPtr getFileIdModCache(int nFiledId){
        std::map<int, FileInfo>::iterator it = fileId2Info.find(nFiledId);
        if (it != fileId2Info.end()){
            return it->second.modCache;
        }
        return NULL;
    }
    int getFileIdByMod(PyObjPtr mod){
        std::map<int, FileInfo>::iterator it = fileId2Info.begin();
        for (; it != fileId2Info.end(); ++it){
            if (it->second.modCache == mod){
                return it->first;
            }
        }
        return 0;
    }
    std::string getLine2Code(int nFiledId, int n){
        std::map<int, FileInfo>::iterator it = fileId2Info.find(nFiledId);
        if (it != fileId2Info.end()){
            return it->second.line2Code[n];
        }
        return "";
    }
    
    int allocFieldIndex(int m, int o);
    
    PyContext& addBuiltin(const std::string& name, PyObjPtr v);
    PyObjPtr&  getBuiltin(const std::string& name);
    PyContext& addModule(const std::string& name, PyObjPtr v);
    PyObjPtr   getModule(const std::string& name);
public:
    std::list<ExprAST*> exprTrace;//! for trace back
    std::map<int, FileInfo> fileId2Info;
    std::string             syspath;
    PyObjPtr evalResult;
    PyObjPtr curstack;//!cur using context
    
    std::map<std::string, PyObjPtr>  allBuiltin;
    
    //!record obj field id num
    std::map<int, std::map<int, int> >  recordAllFiledIndex;
    //!cache property class
    PyObjPtr                            propertyClass;
};
#define TRACE_EXPR() context.setTraceExpr(this)
#define TRACE_EXPR_PUSH() context.pushTraceExpr(this)
#define TRACE_EXPR_POP() context.popTraceExpr()

struct PyContextBackUp{
    PyContextBackUp(PyContext& c):bRollback(false),context(c), curstack(c.curstack){
    }
    ~PyContextBackUp(){
        rollback();
    }
    void rollback(){
        if (!bRollback){
            bRollback = true;
            context.curstack = curstack;
        }
    }
    bool       bRollback;
    PyContext& context;
    PyObjPtr   curstack;
};

class FlowCtrlSignal: public std::exception{
public:
    enum{
        CONTINUE=0,
        BREAK,
    };
    FlowCtrlSignal(int n = -1):nSignal(n) {}
    int nSignal;
};


class ReturnSignal: public std::exception{
public:
};
class PyExceptionSignal: public std::exception{
public:
};
#define PY_RAISE(context, v) context.cacheResult(v); throw PyExceptionSignal()

enum EEXPR_TYPE{ 
    EXPR_SINGLE_INPUT,
    EXPR_FILE_INPUT,
    EXPR_EVAL_INPUT,
    EXPR_DECORATOR,
    EXPR_DECORATORS,
    EXPR_DECORATED,
    EXPR_FUNCDEF,
    EXPR_PARAMETERS,
    EXPR_VARARGSLIST,
    EXPR_FPDEF,
    EXPR_FPLIST,
    EXPR_STMT,
    EXPR_SIMPLE_STMT,
    EXPR_SMALL_STMT,
    EXPR_EXPR_STMT,
    EXPR_AUGASSIGN,
    EXPR_PRINT_STMT,
    EXPR_DEL_STMT,
    EXPR_PASS_STMT,
    EXPR_FLOW_STMT,
    EXPR_BREAK_STMT,
    EXPR_CONTINUE_STMT,
    EXPR_RETURN_STMT,
    EXPR_YIELD_STMT,
    EXPR_RAISE_STMT,
    EXPR_IMPORT_STMT,
    EXPR_IMPORT_NAME,
    EXPR_IMPORT_FROM,
    EXPR_IMPORT_AS_NAME,
    EXPR_DOTTED_AS_NAME,
    EXPR_IMPORT_AS_NAMES,
    EXPR_DOTTED_AS_NAMES,
    EXPR_DOTTED_NAME,
    EXPR_GLOBAL_STMT,
    EXPR_EXEC_STMT,
    EXPR_ASSERT_STMT,
    EXPR_COMPOUND_STMT,
    EXPR_IF_STMT,
    EXPR_WHILE_STMT,
    EXPR_FOR_STMT,
    EXPR_TRY_STMT,
    EXPR_WITH_STMT,
    EXPR_WITH_ITEM,
    EXPR_EXCEPT_CLAUSE,
    EXPR_SUITE,
    EXPR_TESTLIST_SAFE,
    EXPR_OLD_TEST,
    EXPR_OLD_LAMBDEF,
    EXPR_TEST,
    EXPR_OR_TEST,
    EXPR_AND_TEST,
    EXPR_NOT_TEST,
    EXPR_COMPARISON,
    EXPR_COMP_OP,
    EXPR_EXPR,
    EXPR_XOR_EXPR,
    EXPR_AND_EXPR,
    EXPR_SHIFT_EXPR,
    EXPR_ARITH_EXPR,
    EXPR_TERM,
    EXPR_FACTOR,
    EXPR_POWER,
    EXPR_ATOM,
    EXPR_LISTMAKER,
    EXPR_TESTLIST_COMP,
    EXPR_LAMBDEF,
    EXPR_TRAILER,
    EXPR_SUBSCRIPTLIST,
    EXPR_SUBSCRIPT,
    EXPR_SLICEOP,
    EXPR_EXPRLIST,
    EXPR_TESTLIST,
    EXPR_DICTORSETMAKER,
    EXPR_CLASSDEF,
    EXPR_ARGLIST,
    EXPR_ARGUMENT,
    EXPR_LIST_ITER,
    EXPR_LIST_FOR,
    EXPR_LIST_IF,
    EXPR_COMP_ITER,
    EXPR_COMP_FOR,
    EXPR_COMP_IF,
    EXPR_TESTLIST1,
    EXPR_ENCODING_DECL,
    EXPR_YIELD_EXPR,
    
    //!self define
    EXPR_INT,
    EXPR_FLOAT,
    EXPR_STR,
    EXPR_VAR,
    EXPR_BIN,
    EXPR_TUPLE,
    EXPR_CALL,
    EXPR_DOT_GET_FIELD,
    EXPR_RET_AFTER_IF
};


}
#endif

