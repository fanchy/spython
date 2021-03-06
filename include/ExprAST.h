#ifndef _EXPRAST_H_
#define _EXPRAST_H_

#include <iostream>
#include <string>
#include <vector>
#include <map>
#include <stdexcept>
#include "Base.h"

namespace ff {


/// NumberExprAST - Expression class for numeric literals like "1.0".
class NumberExprAST : public ExprAST {
public:
    PyInt Val;
    PyObjPtr obj;
    NumberExprAST(PyInt v);
    virtual PyObjPtr& eval(PyContext& context) {
        return obj;
    }
    virtual int getType() {
        return EXPR_INT;
    }
};
class FloatExprAST : public ExprAST {
public:
    PyFloat Val;
    PyObjPtr obj;
    FloatExprAST(PyFloat v);
    virtual PyObjPtr& eval(PyContext& context) {
        return obj;
    }
    virtual int getType() {
        return EXPR_INT;
    }
};
class StrExprAST : public ExprAST {
public:
    std::string val;
    PyObjPtr obj;
    StrExprAST(const std::string& v) ;
    virtual PyObjPtr& eval(PyContext& context) {
        return obj;
    }
    virtual int getType() {
        return EXPR_STR;
    }
};

/// VariableExprAST - Expression class for referencing a variable, like "a".
class VariableExprAST : public ExprAST {
public:
    VariableExprAST(const std::string &n) {
        this->name = n;
        cache = NULL;
    }
    virtual PyObjPtr& eval(PyContext& context);
    virtual PyObjPtr& assignVal(PyContext& context, PyObjPtr& v);
    
    virtual int getType() {
        return EXPR_VAR;
    }
    PyObjPtr*   cache;
};

struct VariableExprAllocator{

    ExprASTPtr alloc(const std::string& name){
        if (name.empty()){
            return NULL;
        }
        ExprASTPtr& ret = allVar[name];
        if (!ret){
            ExprASTPtr p = new VariableExprAST(name);
            ret = p;
            //DMSG(("alloc field:%s\n", name.c_str()));
        }
        return ret;
    }
    
    template<typename T>
    ExprASTPtr allocIfNotExist(const std::string& name){
        ExprASTPtr& ret = allVar[name];
        if (!ret){
            ExprASTPtr p = new T();
            ret = p;
            //DMSG(("alloc field:%s\n", name.c_str()));
        }
        return ret;
    }
    std::map<std::string, ExprASTPtr> allVar;
};

class PowerAST : public ExprAST {
public:
    ExprASTPtr                  atom;
    std::vector<ExprASTPtr>     trailer;
    ExprASTPtr                  merge;
public:
    PowerAST() {
        this->name = "power";
    }
    virtual int getType() {
        return EXPR_POWER;
    }
    
    virtual PyObjPtr& eval(PyContext& context);
};
class StmtAST : public ExprAST {

public:
    StmtAST(){
        //DMSG(("build call %s\n", Callee->name.c_str()));
    }
    virtual int getType() {
        return EXPR_STMT;
    }
    
    virtual PyObjPtr& eval(PyContext& context);
public:
    std::vector<ExprASTPtr> exprs;
};
class PrintAST : public ExprAST {

public:
    PrintAST(){
    }
    virtual int getType() {
        return EXPR_PRINT_STMT;
    }
    
    virtual PyObjPtr& eval(PyContext& context);
public:
    std::vector<ExprASTPtr> exprs;
};
class DelAST : public ExprAST {

public:
    DelAST(ExprASTPtr& v):exprlist(v){
    }
    virtual int getType() {
        return EXPR_DEL_STMT;
    }
    
    virtual PyObjPtr& eval(PyContext& context);
public:
    ExprASTPtr exprlist;
};
class PassAST : public ExprAST {

public:
    PassAST(){
        this->name = "pass";
    }
    virtual int getType() {
        return EXPR_PASS_STMT;
    }
    virtual PyObjPtr& eval(PyContext& context) {
        return context.cacheResult(PyObjTool::buildNone());
    }
public:
};
class BreakAST : public ExprAST {
public:
    BreakAST(){
        this->name = "continue";
    }
    virtual int getType() {
        return EXPR_BREAK_STMT;
    }
    virtual PyObjPtr& eval(PyContext& context) {
        throw FlowCtrlSignal(FlowCtrlSignal::BREAK);
        return context.cacheResult(PyObjTool::buildNone());
    }
public:
};
class NotAST : public ExprAST {
public:
    NotAST(ExprASTPtr& e):expr(e){
        this->name = "not";
    }
    virtual int getType() {
        return EXPR_NOT_TEST;
    }
    virtual PyObjPtr& eval(PyContext& context) {
        PyObjPtr& val = expr->eval(context);
        if (val->getHandler()->handleBool(context, val)){
            return context.cacheResult(PyObjTool::buildFalse());
        }
        return context.cacheResult(PyObjTool::buildTrue());
    }
public:
    ExprASTPtr expr;
};
class ContinueAST : public ExprAST {
public:
    ContinueAST(){
        this->name = "break";
    }
    virtual int getType() {
        return EXPR_CONTINUE_STMT;
    }
    virtual PyObjPtr& eval(PyContext& context) {
        throw FlowCtrlSignal(FlowCtrlSignal::CONTINUE);
        return context.cacheResult(PyObjTool::buildNone());
    }
public:
};

struct PyOpsUtil{
    static PyObjPtr importFile(PyContext& context, const std::string& realpath, std::string asName = "", bool assignFlag = true);
    static std::string traceback(PyContext& context);
};
class ImportAST : public ExprAST {
public:
    struct ImportInfo{
        std::vector<std::string>  pathinfo; //! import a.b.c.d
        std::string               asinfo;   //! import a.b.c.d as abcd
    };
    ImportAST(){
        this->name = "import";
    }
    virtual int getType() {
        return EXPR_IMPORT_STMT;
    }
    virtual PyObjPtr& eval(PyContext& context);
    
public:
    std::vector<ImportInfo> importArgs;
};
/// BinaryExprAST - Expression class for a binary operator.
class BinaryExprAST : public ExprAST {
    typedef PyObjPtr& (BinaryExprAST::*ExprAstEvalFunc)(PyContext&);
    enum {
        OP_ASSIGN = 0,
        OP_ADD,
        OP_SUB,
        OP_MUL,
        OP_DIV,
        OP_MOD,
        
        OP_EQ,
        OP_NOTEQ, //!= not
        OP_LESS,//<
        OP_GREAT,//>
        OP_LESSEQ, //<=
        OP_GREATEQ, //>=
        OP_IN,
        OP_NOTIN,
        
        OP_OR, //! or 
        OP_AND, //! and
        
        OP_BIT_AND, //! &
        OP_BIT_OR, //! |
        OP_BIT_XOR, //! ^
        OP_BIT_INVERT, //! ~
        OP_BIT_SHIFT, //! <<
        OP_BIT_RSHIFT, //! >>
    };
public:
    BinaryExprAST(const std::string& o, ExprASTPtr& l, ExprASTPtr& r);
    virtual int getType() {
        return EXPR_BIN;
    }
    
    virtual PyObjPtr& eval(PyContext& context);
public://!implement
    PyObjPtr& eval_OP_ASSIGN(PyContext& context);
    PyObjPtr& eval_OP_ADD(PyContext& context);
    PyObjPtr& eval_OP_SUB(PyContext& context);
    PyObjPtr& eval_OP_MUL(PyContext& context);
    PyObjPtr& eval_OP_DIV(PyContext& context);
    PyObjPtr& eval_OP_MOD(PyContext& context);
    
    PyObjPtr& eval_OP_EQ(PyContext& context);
    PyObjPtr& eval_OP_NOTEQ(PyContext& context); //!= not
    PyObjPtr& eval_OP_LESS(PyContext& context);//<
    PyObjPtr& eval_OP_GREAT(PyContext& context);//>
    PyObjPtr& eval_OP_LESSEQ(PyContext& context); //<=
    PyObjPtr& eval_OP_GREATEQ(PyContext& context); //>=
    PyObjPtr& eval_OP_IN(PyContext& context);
    PyObjPtr& eval_OP_NOTIN(PyContext& context);
    
    PyObjPtr& eval_OP_OR(PyContext& context); //! or 
    PyObjPtr& eval_OP_AND(PyContext& context); //! and
    
    PyObjPtr& eval_OP_BIT_AND(PyContext& context); //! &
    PyObjPtr& eval_OP_BIT_OR(PyContext& context); //! |
    PyObjPtr& eval_OP_BIT_XOR(PyContext& context); //! ^
    PyObjPtr& eval_OP_BIT_INVERT(PyContext& context); //! ~
    PyObjPtr& eval_OP_BIT_SHIFT(PyContext& context); //! <<
    PyObjPtr& eval_OP_BIT_RSHIFT(PyContext& context); //! >>
    
public:
    std::string op;
    ExprASTPtr left, right;
    //int optype;
    ExprAstEvalFunc funcImpl;
};

class AugassignAST : public ExprAST {
    typedef PyObjPtr& (AugassignAST::*ExprAstEvalFunc)(PyContext&);
public:
    std::string op;
    ExprASTPtr left, right;
    ExprAstEvalFunc funcImpl;
public:
    AugassignAST(const std::string& o, ExprASTPtr l, ExprASTPtr r);
    virtual int getType() {
        return EXPR_AUGASSIGN;
    }
    
    virtual PyObjPtr& eval(PyContext& context);
public:
    PyObjPtr& eval_IAdd(PyContext& context);
    PyObjPtr& eval_ISub(PyContext& context);
    PyObjPtr& eval_IMul(PyContext& context);
    PyObjPtr& eval_IDiv(PyContext& context);
    PyObjPtr& eval_IMod(PyContext& context);
};

class ReturnAST : public ExprAST {

public:
    ReturnAST(ExprASTPtr& v):testlist(v){
    }
    virtual int getType() {
        return EXPR_RETURN_STMT;
    }
    
    virtual PyObjPtr& eval(PyContext& context);
public:
    ExprASTPtr testlist;
};
class RaiseAST : public ExprAST {

public:
    RaiseAST(){
    }
    virtual int getType() {
        return EXPR_RAISE_STMT;
    }
    
    virtual PyObjPtr& eval(PyContext& context);
public:
    std::vector<ExprASTPtr> exprs;
};
class GlobalAST : public ExprAST {

public:
    GlobalAST(){
    }
    virtual int getType() {
        return EXPR_GLOBAL_STMT;
    }
    
    virtual PyObjPtr& eval(PyContext& context);
public:
    std::vector<ExprASTPtr> exprs;
};
class ExecAST : public ExprAST {

public:
    ExecAST(){
    }
    virtual int getType() {
        return EXPR_EXEC_STMT;
    }
    
    virtual PyObjPtr& eval(PyContext& context);
public:
    std::vector<ExprASTPtr> exprs;
};
class AssertAST : public ExprAST {

public:
    AssertAST(){
    }
    virtual int getType() {
        return EXPR_ASSERT_STMT;
    }
    
    virtual PyObjPtr& eval(PyContext& context);
public:
    std::vector<ExprASTPtr> exprs;
};

//! if_stmt: 'if' test ':' suite ('elif' test ':' suite)* ['else' ':' suite]
class IfExprAST: public ExprAST {
public:
    std::vector<ExprASTPtr>          ifTest;
    std::vector<ExprASTPtr>          ifSuite;
    ExprASTPtr                       elseSuite;

public:
    IfExprAST(){
        this->name = "if";
    }
    virtual int getType() {
        return EXPR_IF_STMT;
    }
    
    virtual PyObjPtr& eval(PyContext& context);
    
};

//! while_stmt: 'while' test ':' suite ['else' ':' suite]
class WhileExprAST: public ExprAST {
public:
    ExprASTPtr          test;
    ExprASTPtr          suite;
    ExprASTPtr          elseSuite;

public:
    WhileExprAST(){
        this->name = "while";
    }
    virtual int getType() {
        return EXPR_WHILE_STMT;
    }
    
    virtual PyObjPtr& eval(PyContext& context);
    
};

//! for_stmt: 'for' exprlist 'in' testlist ':' suite ['else' ':' suite]
class ForExprAST: public ExprAST {
public:
    ExprASTPtr          exprlist;
    ExprASTPtr          testlist;
    ExprASTPtr          suite;
    ExprASTPtr          elseSuite;

public:
    ForExprAST(){
        this->name = "for";
    }
    virtual int getType() {
        return EXPR_FOR_STMT;
    }
    
    virtual PyObjPtr& eval(PyContext& context);
    
};
//! listmaker: test ( list_for | (',' test)* [','] )
//! list_for: 'for' exprlist 'in' testlist_safe [list_iter]
class ListMakerExprAST: public ExprAST {
public:
    std::vector<ExprASTPtr>  test;
    ExprASTPtr               list_for_exprlist;
    ExprASTPtr               list_for_testlist_safe;

public:
    ListMakerExprAST(){
        this->name = "list";
    }
    virtual int getType() {
        return EXPR_LISTMAKER;
    }
    
    virtual PyObjPtr& eval(PyContext& context);
    
};

class DictorsetMakerExprAST: public ExprAST {
public:
    std::vector<ExprASTPtr>  testKey;
    std::vector<ExprASTPtr>  testVal;
    
    ExprASTPtr               comp_for_exprlist;
    ExprASTPtr               comp_for_or_test;

public:
    DictorsetMakerExprAST(){
        this->name = "dict";
    }
    virtual int getType() {
        return EXPR_DICTORSETMAKER;
    }
    
    virtual PyObjPtr& eval(PyContext& context);
    
};

class ParametersExprAST: public ExprAST {
public:
    struct ParameterInfo{
        ParameterInfo(){
        }
        ParameterInfo(const ParameterInfo& src){
            paramKey     = src.paramKey;
            paramDefault = src.paramDefault;
            paramType    = src.paramType;
        }
        ExprASTPtr  paramKey;
        ExprASTPtr  paramDefault;
        std::string paramType; //!* **
    };
    //std::vector<ExprASTPtr>  fpdef;
    //std::vector<ExprASTPtr>  test;
    std::vector<ParameterInfo> allParam;
public:
    ParametersExprAST(){
        this->name = "parameters";
    }
    virtual int getType() {
        return EXPR_PARAMETERS;
    }
    
    virtual PyObjPtr& eval(PyContext& context);
    void addParam(ExprASTPtr k, ExprASTPtr v, std::string strType){
        ParameterInfo info;
        info.paramKey = k;
        info.paramDefault = v;
        info.paramType = strType;
        allParam.push_back(info);
    }
};


class FuncDefExprAST: public ExprAST {
public:
    ExprASTPtr              funcname;
    ExprASTPtr              parameters;
    ExprASTPtr              suite;
    std::string             doc;

public:
    FuncDefExprAST(){
        this->name = "funcdef";
    }

    
    virtual PyObjPtr& eval(PyContext& context);
    virtual int getType() {
        return EXPR_FUNCDEF;
    }
};


class ClassDefExprAST: public ExprAST {
public:
    ExprASTPtr              classname;
    ExprASTPtr              testlist;//! inherit parent class
    ExprASTPtr              suite;

public:
    ClassDefExprAST(){
        this->name = "classdef";
    }
    virtual int getType() {
        return EXPR_CLASSDEF;
    }
    
    virtual PyObjPtr& eval(PyContext& context);
    
};

struct ForBreakContinueFlag{
    ForBreakContinueFlag():flagContinue(false), flagBreak(false){
    }
    bool flagContinue;
    bool flagBreak;
};
class ContinueExprAST : public ExprAST {
public:
    ContinueExprAST(){
    }
    virtual PyObjPtr& eval(PyContext& context) {
        //DMSG(("continue expr eval---------\n"));
        singleton_t<ForBreakContinueFlag>::instance_ptr()->flagContinue = true;
        return context.curstack;
    }
    virtual int getType() {
        return EXPR_CONTINUE_STMT;
    }
};

class BreakExprAST : public ExprAST {
public:
    BreakExprAST(){
    }
    virtual PyObjPtr& eval(PyContext& context) {
        //DMSG(("break expr eval---------\n"));
        singleton_t<ForBreakContinueFlag>::instance_ptr()->flagBreak = true;
        return context.curstack;
    }
    virtual int getType() {
        return EXPR_BREAK_STMT;
    }
};

class TupleExprAST: public ExprAST {
public:
    std::vector<ExprASTPtr>    values;

public:
    TupleExprAST(){
        this->name = "tuple";
    }
    virtual int getType() {
        return EXPR_TUPLE;
    }
    virtual PyObjPtr& eval(PyContext& context);
    PyObjPtr& assignVal(PyContext& context, PyObjPtr& v);
    TupleExprAST& append(ExprASTPtr& v){
        values.push_back(v);
        return *this;
    }
    void delVal(PyContext& context);
};

class FuncArglist : public ExprAST {
public:
    struct ArgInfo{
        ArgInfo(const ArgInfo& src){
            argType    = src.argType;
            argKey     = src.argKey;
            argVal     = src.argVal;
        }
        ArgInfo(){
        }
        std::string      argType; //! epmpty = * **
        ExprASTPtr       argKey, argVal; //! k = 10
    };
    FuncArglist():bNeedRerangeArgs(false) {
    }
    virtual int getType() {
        return EXPR_ARGLIST;
    }
    virtual PyObjPtr& eval(PyContext& context){
        return context.cacheResult(PyObjTool::buildNone());
    }
    void addArg(ExprASTPtr k, ExprASTPtr v, const std::string& s){
        if (!v){
            return;
        }
        ArgInfo info;
        info.argType = s;
        info.argKey  = k;
        info.argVal  = v;
        allArgs.push_back(info);
        
        ArgTypeInfo info2;
        info2.argType = s;
        if (k)
            info2.argKey  = k.cast<VariableExprAST>()->name;
        allArgsTypeInfo.push_back(info2);
        
        if (s == "*" || s == "**"){
            bNeedRerangeArgs = true;
        }
    }
public:
    std::vector<ArgInfo>        allArgs;
    std::vector<ArgTypeInfo>    allArgsTypeInfo;
    bool                        bNeedRerangeArgs;//!是否有* 和 ** 参数有的话，顺序需要重新整理 
};

class TrailerExprAST : public ExprAST {
public:
    ExprASTPtr preExpr;
};
class DotGetFieldExprAST : public TrailerExprAST {
public:
    DotGetFieldExprAST(ExprASTPtr &n):fieldName(n) {
    }
    virtual int getType() {
        return EXPR_DOT_GET_FIELD;
    }
    
    virtual PyObjPtr& eval(PyContext& context);
    
    PyObjPtr& assignVal(PyContext& context, PyObjPtr& v);
    virtual void delVal(PyContext& context);
public:
    ExprASTPtr fieldName;
};

class SliceExprAST : public TrailerExprAST {
public:
    enum SliceStopFlag{
        FLAG_NULL = 0,
        FLAG_END,
    };
    SliceExprAST():stopFlag(FLAG_NULL) {
    }
    virtual int getType() {
        return EXPR_SLICEOP;
    }
    
    virtual PyObjPtr& eval(PyContext& context);
    
    PyObjPtr& assignVal(PyContext& context, PyObjPtr& v);
    void delVal(PyContext& context);
public:
    ExprASTPtr start;
    ExprASTPtr stop;
    ExprASTPtr step;
    int        stopFlag;
};

/// CallExprAST - Expression class for function calls.
class CallExprAST : public TrailerExprAST {
public:
    CallExprAST() {
        arglist = new FuncArglist();
    }
    virtual int getType() {
        return EXPR_CALL;
    }
    
    virtual PyObjPtr& eval(PyContext& context);
    
public:
    ExprASTPtr func;
    ExprASTPtr arglist;
};

class TryAst : public ExprAST {
public:
    struct ExceptInfo{
        ExceptInfo(){
        }
        ExceptInfo(const ExceptInfo& src){
            exceptType = src.exceptType;
            exceptAsVal= src.exceptAsVal;
            exceptSuite= src.exceptSuite;
        }
        ExprASTPtr exceptType;
        ExprASTPtr exceptAsVal;
        ExprASTPtr exceptSuite;
    };
    virtual int getType() {
        return EXPR_TRY_STMT;
    }
    virtual PyObjPtr& eval(PyContext& context);
public:
    ExprASTPtr                  trySuite;
    std::vector<ExceptInfo>     exceptSuite;
    ExprASTPtr                  elseSuite;
    ExprASTPtr                  finallySuite;
};

class DecoratorAST : public ExprAST {
public:
    virtual PyObjPtr& eval(PyContext& context);
    virtual int getType() {
        return EXPR_DECORATOR;
    }
public:
    std::vector<ExprASTPtr>     allDecorators;
    ExprASTPtr                  funcDef;
};

class LambdaAST : public ExprAST {
public:
    virtual PyObjPtr& eval(PyContext& context);
    virtual int getType() {
        return EXPR_LAMBDEF;
    }
public:
    ExprASTPtr                  varargslist;
    ExprASTPtr                  test;
};
class RetAfterIfAST : public ExprAST {
public:
    virtual PyObjPtr& eval(PyContext& context);
    virtual int getType() {
        return EXPR_RET_AFTER_IF;
    }
public:
    ExprASTPtr                  ret;
    ExprASTPtr                  if_test;
    ExprASTPtr                  else_test;
};

class WithAST : public ExprAST {
public:
    struct with_item{
        ExprASTPtr test;
        ExprASTPtr asexpr;
        with_item(){
        }
        with_item(const with_item& src){
            test = src.test;
            asexpr = src.asexpr;
        }
    };
    virtual PyObjPtr& eval(PyContext& context);
    virtual int getType() {
        return EXPR_WITH_STMT;
    }
    void additem(ExprASTPtr test, ExprASTPtr asexpr){
        with_item a;
        a.test = test;
        a.asexpr = asexpr;
        with_items.push_back(a);
    }
public:
    std::vector<with_item>      with_items;
    ExprASTPtr                  suite;
};

class DumpAST : public ExprAST {
public:
    virtual PyObjPtr& eval(PyContext& context);
    virtual int getType() {
        return EXPR_DUMP;
    }
public:
    ExprASTPtr                  testlist1;
};

}
#endif


