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

#include <stdio.h>
#define DTRACE(x) {}//printf x ; printf("\n")
#define DMSG(x) printf x ; printf("\n")

namespace ff {
/*
enum ExprType{
    EXPR_CALL = 1,
    EXPR_FUNC = 2,
    EXPR_IF   = 3,
    EXPR_INT  = 4,
    EXPR_FLOAT  = 5,
    EXPR_STR,
    EXPR_VAR,
    EXPR_STMT,
    EXPR_TUPLE,
    EXPR_FOR,
    EXPR_CLASS,
    EXPR_BREAK,
    EXPR_CONTINUE,
    EXPR_ASSIGN,
    EXPR_AUGASSIGN,
    EXPR_PRINT,
};
*/
enum PyObjType{
    PY_NONE = 1,
    PY_INT,
    PY_FLOAT,
    PY_STR,
    PY_FUNC_DEF,
    PY_CLASS_FUNC,
    PY_CLASS_DEF,
    PY_CLASS_OBJ,
    PY_MOD,
    PY_BOOL,
    PY_TUPLE,
    PY_DICT,
};

typedef  int TokenType;

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
        std::map<std::string, int>::iterator it = name2filed.find(name);
        if (it != name2filed.end()){
            return it->second;
        }
        int n = name2filed.size();
        name2filed[name] = n;
        return n;
    }
    inline std::string id2name(int nFieldId){
        for (std::map<std::string, int>::iterator it = name2filed.begin(); it != name2filed.end(); ++it){
            if (it->second == nFieldId){
                return it->first;
            }
        }
        return "";
    }

private:
    std::map<std::string, int> name2filed;
};

class ParseHelper;

struct PyException {
    static std::runtime_error buildIndentException(ParseHelper& parseHelper, int nNeedIndent, std::string err = "") ;
    static std::runtime_error buildException(ParseHelper& parseHelper, const std::string& err);
    static std::runtime_error buildException(const std::string& err);
};

struct PyHelper{
    PyHelper();
    bool isKeyword(const std::string& v);
    
    std::set<std::string>    m_allKeyword;
}; 

class PyContext;

class ExprAST;
class PyIter;
typedef SmartPtr<PyIter> PyIterPtr;

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

    const std::string& getFiledName(int moduleid, int objectid, int nFieldId) {
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
class PyObj {
public:
    typedef SmartPtr<PyObj> PyObjPtr;
    PyObj():m_pObjIdInfo(NULL), handler(NULL){}
    virtual ~PyObj() {}

    int getType() const;
    int getFieldNum() const { return m_objStack.size(); }
    static std::string dump(PyObjPtr& self);

    virtual PyObjPtr& getVar(PyContext& c, PyObjPtr& self, unsigned int nFieldIndex);
    virtual const ObjIdInfo& getObjIdInfo() = 0;

public:
    std::vector<PyObjPtr>    m_objStack;
    ObjIdInfo*               m_pObjIdInfo;
    PyObjHandler*            handler;
};
typedef PyObj::PyObjPtr PyObjPtr;


class PyIter{
public:
    virtual PyObjPtr next() {
        return NULL;
    }
    virtual ~PyIter(){}
};

struct PyObjTool{
    static PyObjPtr  buildNULL();
    static PyObjPtr& buildNone();
    static PyObjPtr& buildBool(bool b);
    static PyObjPtr& buildTrue();
    static PyObjPtr& buildFalse();
    static bool handleBool(PyObjPtr b);
}; 

struct ExprLine{
    ExprLine():nLine(0), nIndent(0){
    }
    std::string file;
    int         nLine;
    int         nIndent;
};
class ExprAST {
public:
    int    nFieldId;
    std::string name;
    ExprLine    lineInfo;
    ExprAST():nFieldId(-1){
    }
    virtual ~ExprAST() {}
    virtual PyObjPtr& eval(PyContext& context) = 0;

    virtual PyObjPtr& getFieldVal(PyContext& context);
    virtual int getType() {
        return 0;
    }
    virtual PyObjPtr handleAssign(PyObjPtr context, PyObjPtr val) { return NULL; }
    
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
    std::vector<std::vector<int> >  module2objcet2fieldIndex;
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
    
    virtual int getType() const {
        return 0;
    }

    //!比较是否相等 
    virtual bool handleEQ(PyObjPtr& self, PyObjPtr& args){
        return false;
    }
    virtual PyIterPtr getIter(){
        return NULL;
    }
    virtual PyObjPtr handleCall(PyObjPtr context, std::list<PyObjPtr>& args){
        return NULL;
    }
    virtual std::string handleStr(const PyObjPtr& self) const{
        return "";
    }
    virtual PyObjPtr& handleAssign(PyContext& context, PyObjPtr& self, PyObjPtr& val){
        self = val;
        return self;
    }

    virtual bool handleBool(PyContext& context, const PyObjPtr& self) const;
    virtual bool handleEqual(PyContext& context, const PyObjPtr& self, const PyObjPtr& val) const;
    virtual bool handleLessEqual(PyContext& context, const PyObjPtr& self, const PyObjPtr& val) const;
    virtual bool handleGreatEqual(PyContext& context, const PyObjPtr& self, const PyObjPtr& val) const;
    virtual bool handleIn(PyContext& context, const PyObjPtr& self, const PyObjPtr& val) const;
    
    virtual bool handleLess(PyContext& context, const PyObjPtr& self, const PyObjPtr& val) const{
        if (self->handler->handleGreatEqual(context, self, val) == false){
            return true;
        }
        return false;
    }
    virtual bool handleGreat(PyContext& context, const PyObjPtr& self, const PyObjPtr& val) const{
        if (self->handler->handleLessEqual(context, self, val) == false){
            return true;
        }
        return false;
    }
    
    virtual PyObjPtr& handleAdd(PyContext& context, PyObjPtr& self, PyObjPtr& val);
    virtual PyObjPtr& handleSub(PyContext& context, PyObjPtr& self, PyObjPtr& val);
    virtual PyObjPtr& handleMul(PyContext& context, PyObjPtr& self, PyObjPtr& val);
    virtual PyObjPtr& handleDiv(PyContext& context, PyObjPtr& self, PyObjPtr& val);
    virtual PyObjPtr& handleMod(PyContext& context, PyObjPtr& self, PyObjPtr& val);
    virtual PyObjPtr& handleCall(PyContext& context, PyObjPtr& self, std::vector<ArgTypeInfo>& allArgsVal, 
                                 std::vector<PyObjPtr>& argAssignVal);
    virtual std::size_t    handleHash(const PyObjPtr& self) const;

    virtual std::string dump(PyObjPtr& self) {
        return "";
    }
};

class PyNoneHandler: public PyObjHandler{
public:
    virtual int getType() {
        return PY_NONE;
    }
    virtual std::string handleStr(const PyObjPtr& self) const{
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
    PyObjNone(const ObjIdInfo& m){
        this->handler = singleton_t<PyNoneHandler>::instance_ptr();
        selfObjInfo   = m;
    }
    virtual const ObjIdInfo& getObjIdInfo(){
        return selfObjInfo;
    }
    ObjIdInfo       selfObjInfo;
    bool            isNull;
};
#define IS_NULL(o) ((o)->getType() == PY_NONE && (o).cast<PyObjNone>()->isNull)

typedef PyObjNone PyCallTmpStack;

class PyContext{
public:
    PyObjPtr& cacheResult(PyObjPtr v){
        evalResult = v;
        return evalResult;
    }
    PyObjPtr& getCacheResult(){
        return evalResult;
    }
    //std::vector<PyObjPtr>   tmpcache;
    
    PyObjPtr evalResult;
    PyObjPtr curstack;//!cur using context
};

struct PyContextBackUp{
    PyContextBackUp(PyContext& c):context(c), curstack(c.curstack){
    }
    ~PyContextBackUp(){
        rollback();
    }
    void rollback(){
        context.curstack = curstack;
    }
    PyObjPtr   curstack;
    PyContext& context;
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
    EXPR_DOT_GET_FIELD
};


}
#endif

