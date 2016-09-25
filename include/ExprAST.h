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
    long Val;
    PyObjPtr obj;
    NumberExprAST(long v);
    virtual PyObjPtr& eval(PyContext& context) {
        return obj;
    }
    virtual int getType() {
        return EXPR_INT;
    }
};
class FloatExprAST : public ExprAST {
public:
    double Val;
    PyObjPtr obj;
    FloatExprAST(double v);
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
    }
    virtual PyObjPtr& eval(PyContext& context);
    virtual PyObjPtr& assignVal(PyContext& context, PyObjPtr& v){
        PyObjPtr& lval = this->getFieldVal(context);
        lval = v;
        return lval;
    }
    
    virtual int getType() {
        return EXPR_VAR;
    }
};

struct VariableExprAllocator{

    ExprASTPtr alloc(const std::string& name){
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
    virtual std::string dump(int nDepth);
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
    virtual std::string dump(int nDepth);
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
    virtual std::string dump(int nDepth);
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
    virtual std::string dump(int nDepth);
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
    virtual std::string dump(int nDepth);
public:
    std::vector<ImportInfo> importArgs;
};
/// BinaryExprAST - Expression class for a binary operator.
class BinaryExprAST : public ExprAST {
    enum {
        OP_ASSIGN = 0,
        OP_ADD,
        OP_SUB,
        OP_MUL,
        OP_DIV,
        OP_MOD,
        
        OP_EQ,
        OP_LESS,//<
        OP_GREAT,//>
        OP_LESSEQ, //<=
        OP_GREATEQ, //>=
        OP_NOTEQ, //!= not
        OP_IN,
        OP_NOTIN,
        
        OP_OR,
        OP_AND,
    };
    std::string op;
    ExprASTPtr left, right;
    int optype;
public:
    BinaryExprAST(const std::string& o, ExprASTPtr& l, ExprASTPtr& r)
        : op(o), left(l), right(r),optype(-1) {
        this->name = op;

        if (op == "="){
            optype = OP_ASSIGN;
        }
        else if (op == "+"){
            optype = OP_ADD;
        }
        else if (op == "-"){
            optype = OP_SUB;
        }
        else if (op == "*"){
            optype = OP_MUL;
        }
        else if (op == "/"){
            optype = OP_DIV;
        }
        else if (op == "%"){
            optype = OP_MOD;
        }
        else if (op == "==" || op == "is"){
            optype = OP_EQ;
        }
        else if (op == "!=" or op == "not" or op == "<>"){
            optype = OP_NOTEQ;
        }
        else if (op == "<"){
            optype = OP_LESS;
        }
        else if (op == ">"){
            optype = OP_GREAT;
        }
        else if (op == "<="){
            optype = OP_LESSEQ;
        }
        else if (op == ">="){
            optype = OP_GREATEQ;
        }
        else if (op == "in" || op == "is in"){
            optype = OP_IN;
        }
        else if (op == "not in"){
            optype = OP_NOTIN;
        }
        else if (op == "or"){
            optype = OP_OR;
        }
        else if (op == "and"){
            optype = OP_AND;
        }
    }
    virtual int getType() {
        return EXPR_BIN;
    }
    virtual std::string dump(int nDepth);
    virtual PyObjPtr& eval(PyContext& context);
};

class ReturnAST : public ExprAST {

public:
    ReturnAST(ExprASTPtr& v):testlist(v){
    }
    virtual int getType() {
        return EXPR_DEL_STMT;
    }
    virtual std::string dump(int nDepth);
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
    virtual std::string dump(int nDepth);
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
    virtual std::string dump(int nDepth);
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
    virtual std::string dump(int nDepth);
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
    virtual std::string dump(int nDepth);
    virtual PyObjPtr& eval(PyContext& context);
public:
    std::vector<ExprASTPtr> exprs;
};

class AugassignAST : public ExprAST {
public:
    std::string op;
    ExprASTPtr left, right;

public:
    AugassignAST(const std::string& o, ExprASTPtr l, ExprASTPtr r)
        : op(o), left(l), right(r) {
        
        this->name = op;
    }
    virtual int getType() {
        return EXPR_AUGASSIGN;
    }
    virtual std::string dump(int nDepth);
    virtual PyObjPtr& eval(PyContext& context);
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
    virtual std::string dump(int nDepth);
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
    virtual std::string dump(int nDepth);
    virtual PyObjPtr& eval(PyContext& context);
    
};
struct IterUtil{
    IterUtil(PyObjPtr v);
    PyObjPtr next();
    
    PyObjPtr  obj;
    int       objType;
    int       index;
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
    virtual std::string dump(int nDepth);
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
    virtual std::string dump(int nDepth);
    virtual PyObjPtr& eval(PyContext& context);
    
};

class DictorsetMakerExprAST: public ExprAST {
public:
    std::vector<ExprASTPtr>  testKey;
    std::vector<ExprASTPtr>  testVal;
    
    //std::vector<ExprASTPtr>  test;
    ExprASTPtr               comp_for;

public:
    DictorsetMakerExprAST(){
        this->name = "dict";
    }
    virtual int getType() {
        return EXPR_DICTORSETMAKER;
    }
    virtual std::string dump(int nDepth);
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
    virtual std::string dump(int nDepth);
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

public:
    FuncDefExprAST(){
        this->name = "funcdef";
    }

    virtual std::string dump(int nDepth);
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
    virtual std::string dump(int nDepth);
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
    virtual std::string dump(int nDepth);
    virtual PyObjPtr& eval(PyContext& context);
    
    PyObjPtr& assignVal(PyContext& context, PyObjPtr& v);
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
    virtual std::string dump(int nDepth);
    virtual PyObjPtr& eval(PyContext& context);
    
    //PyObjPtr& assignToField(PyContext& context, PyObjPtr& v);
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
    virtual std::string dump(int nDepth);
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

}
#endif


