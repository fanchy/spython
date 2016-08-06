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

class PyObj {
public:
    typedef SmartPtr<PyObj> PyObjPtr;
    virtual ~PyObj() {
    }

    virtual PyObjPtr& getVar(PyObjPtr& self, unsigned int nFieldIndex);

    PyObj():m_pObjIdInfo(NULL){
    }
    virtual void dump();
    PyMetaType* getMetaType();

    virtual int getType() {
        return 0;
    }
    virtual PyObjPtr handleCall(PyObjPtr context, std::list<PyObjPtr>& args){
        return NULL;
    }

    virtual bool handleEQ(PyObjPtr args){
        return false;
    }

    virtual PyIterPtr getIter(){
        return NULL;
    }
    
    int getFieldNum() const { return m_objStack.size(); }
    
    virtual const ObjIdInfo& getObjIdInfo() = 0;
public:
    std::vector<PyObjPtr>    m_objStack;
    ObjIdInfo*          m_pObjIdInfo;
};
typedef PyObj::PyObjPtr PyObjPtr;

class PyObjNone:public PyObj {
public:
    virtual void dump() {
        DMSG(("None"));
    }
    virtual int getType() {
        return PY_NONE;
    }
    virtual bool handleEQ(PyObjPtr arg){
        if (arg && arg->getType() == this->getType()){
            return true;
        }
        return false;
    }
    virtual const ObjIdInfo& getObjIdInfo(){
        return singleton_t<ObjIdTypeTraits<PyObjNone> >::instance_ptr()->objInfo;
    }
};

class PyIter{
public:
    virtual PyObjPtr next() {
        return NULL;
    }
    virtual ~PyIter(){}
};

struct PyObjTool{
    static PyObjPtr& buildNone();
    static PyObjPtr& buildBool(bool b);
    static bool handleBool(PyObjPtr b);
}; 

class ExprAST {
public:
    int    nFieldId;
    std::string name;
    ExprAST():nFieldId(-1){
    }
    virtual ~ExprAST() {}
    virtual PyObjPtr eval(PyObjPtr context) {
        return NULL;
    }
    virtual PyObjPtr& getFieldVal(PyObjPtr& context);
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
    EXPR_CALL
};

}
#endif

