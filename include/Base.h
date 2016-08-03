#ifndef _BASE_H_
#define _BASE_H_

#include <string>
#include <map>
#include <vector>
#include <list>
#include <stdexcept>
using namespace std;

#include "SmartPtr.h"
#include "Singleton.h"

#include <stdio.h>
#define DMSG(x) printf x

namespace ff {

enum ExprType{
    EXPR_CALL = 1,
    EXPR_FUNC = 2,
    EXPR_IF   = 3,
    EXPR_INT  = 4,
    EXPR_STR  = 5,
    EXPR_VAR,
    EXPR_TUPLE,
    EXPR_FOR,
    EXPR_CLASS,
    EXPR_BREAK,
    EXPR_CONTINUE
};

enum PyObjType{
    PY_NONE = 1,
    PY_INT,
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

enum Token {
    TOK_EOF = -1,
    //TOK_DEF = -2,
    TOK_VAR = -4,
    TOK_NUM = -5,
    TOK_STR = -6,
    TOK_CALL= -7,
    TOK_FIELD = -7, // .

    TOK_LS  = -21, //<
    TOK_LE  = -22, //<=
    TOK_GT  = -23, //>
    TOK_GE  = -24, //>=
    TOK_EQ  = -25, //==
    TOK_NE  = -26, //!=
    
    TOK_ASSIGN= -27, // = 
    TOK_PLUS= -28, // +
    TOK_SUB = -29, // -
    TOK_MUT = -30, // *
    TOK_DIV = -31, // /
    
    TOK_AND = -32, // && and
    TOK_OR  = -33, // || or
    TOK_YU  = -34, // &
    TOK_HUO = -35, // |
    TOK_FAN = -36, // ! 
    
};

class PyMetaType{
public:
    inline int allocFieldId(const string& name){
        map<string, int>::iterator it = name2filed.find(name);
        if (it != name2filed.end()){
            return it->second;
        }
        int n = name2filed.size();
        name2filed[name] = n;
        return n;
    }
    inline string id2name(int nFieldId){
        for (map<string, int>::iterator it = name2filed.begin(); it != name2filed.end(); ++it){
            if (it->second == nFieldId){
                return it->first;
            }
        }
        return "";
    }

private:
    map<string, int> name2filed;
};

class ParseHelper;

struct PyException {
    static runtime_error buildIndentException(ParseHelper& parseHelper, int nNeedIndent, string err = "") ;
    static runtime_error buildException(ParseHelper& parseHelper, const string& err);
    static runtime_error buildException(const string& err);
};

struct PyHelper{    
    static string token2name(TokenType token);
}; 

class ExprAST;
class PyIter;
typedef SmartPtr<PyIter> PyIterPtr;

struct ObjIdInfo{
    ObjIdInfo():nModuleId(0), nObjectId(0){}

    unsigned int nModuleId;
    unsigned int nObjectId;
    string strFieldName;
};


struct ObjFieldMetaData{
    ObjFieldMetaData():nCountMeta(0){
    }
    //!module id -> objectid -> fieldid -> fieldname
    map<int, map<int,  map<int, string> > >        module2object2fieldname;

    const string& getFiledName(int moduleid, int objectid, int nFieldId) {
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
    virtual PyObjPtr handleCall(PyObjPtr context, list<PyObjPtr>& args){
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
    vector<PyObjPtr>    m_objStack;
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
    string name;
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
    
    vector<vector<int> >  module2objcet2fieldIndex;
};

typedef SmartPtr<ExprAST> ExprASTPtr;



}
#endif

