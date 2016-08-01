#ifndef _EXPRAST_H_
#define _EXPRAST_H_

#include <iostream>
#include <string>
#include <vector>
#include <map>
#include <stdexcept>
#include "Base.h"
using namespace std;

namespace ff {


/// NumberExprAST - Expression class for numeric literals like "1.0".
class NumberExprAST : public ExprAST {
public:
    int Val;
    PyObjPtr obj;
    NumberExprAST(int v);
    virtual PyObjPtr eval(PyObjPtr context) {
        return obj;
    }
    virtual int getType() {
        return EXPR_INT;
    }
};
class StrExprAST : public ExprAST {
public:
    string val;
    PyObjPtr obj;
    StrExprAST(const string& v) ;
    virtual PyObjPtr eval(PyObjPtr context) {
        return obj;
    }
    virtual int getType() {
        return EXPR_STR;
    }
};

/// VariableExprAST - Expression class for referencing a variable, like "a".
class VariableExprAST : public ExprAST {
public:
    VariableExprAST(const string &n) {
        this->name = n;
    }
    virtual PyObjPtr eval(PyObjPtr context) {
        return this->getFieldVal(context);
    }
    PyObjPtr handleAssign(PyObjPtr context, PyObjPtr val){
        PyObjPtr& v = this->getFieldVal(context);
        v = val;
        return val;
    }
    virtual int getType() {
        return EXPR_VAR;
    }
};

struct VariableExprAllocator{

    ExprASTPtr alloc(const string& name){
        ExprASTPtr& ret = allVar[name];
        if (!ret){
            ExprASTPtr p = new VariableExprAST(name);
            ret = p;
            //DMSG(("alloc field:%s\n", name.c_str()));
        }
        return ret;
    }
    
    template<typename T>
    ExprASTPtr allocIfNotExist(const string& name){
        ExprASTPtr& ret = allVar[name];
        if (!ret){
            ExprASTPtr p = new T();
            ret = p;
            //DMSG(("alloc field:%s\n", name.c_str()));
        }
        return ret;
    }
    map<string, ExprASTPtr> allVar;
};

/// BinaryExprAST - Expression class for a binary operator.
class BinaryExprAST : public ExprAST {
    TokenType op;
    ExprASTPtr LHS, RHS;

public:
    BinaryExprAST(TokenType o, ExprASTPtr l, ExprASTPtr r)
        : op(o), LHS(l), RHS(r) {
        
        this->name = PyHelper::token2name(op);
        //DMSG(("BinaryExprAST Op:%s,lhs=%s,rhs=%s\n", this->name.c_str(), LHS->name.c_str(), RHS->name.c_str()));
    }
    virtual PyObjPtr eval(PyObjPtr context);
    virtual PyObjPtr& getFieldVal(PyObjPtr& context);
};

class FuncCodeImpl: public ExprAST{
public:
    ExprASTPtr         varAstforName;
    vector<ExprASTPtr> argsDef;
    vector<ExprASTPtr> body;
public:
    FuncCodeImpl(){
        //this->varAstforName = singleton_t<VariableExprAllocator>::instance_ptr()->alloc(p->name);
        //DMSG(("FunctionAST Proto.name=%s\n", proto->name.c_str()));
    }
    virtual PyObjPtr exeCode(PyObjPtr context, list<PyObjPtr>&  tmpArgsInput);
    virtual int getType() {
        return EXPR_FUNC;
    }
};

/// FunctionAST - This class represents a function definition itself.
class FunctionAST: public ExprAST {
public:
    ExprASTPtr codeImplptr;
public:
    FunctionAST():codeImplptr(new FuncCodeImpl()){
        
        //this->varAstforName = singleton_t<VariableExprAllocator>::instance_ptr()->alloc(p->name);
        //DMSG(("FunctionAST Proto.name=%s\n", proto->name.c_str()));
    }
    virtual int getType() {
        return EXPR_FUNC;
    }

    virtual PyObjPtr eval(PyObjPtr context);
};

class  ClassCodeImpl: public ExprAST{
public:
    ExprASTPtr         varAstforName;
public:
    ClassCodeImpl(){
        //this->varAstforName = singleton_t<VariableExprAllocator>::instance_ptr()->alloc(p->name);
        //DMSG(("FunctionAST Proto.name=%s\n", proto->name.c_str()));
    }

    virtual int getType() {
        return EXPR_CLASS;
    }
};

/// ClassAST - This class represents a class definition itself.
class ClassAST: public ExprAST {
public:
    ExprASTPtr codeImplptr;
    vector<ExprASTPtr> classFieldCode;
public:
    ClassAST():codeImplptr(new ClassCodeImpl()){
        
        //this->varAstforName = singleton_t<VariableExprAllocator>::instance_ptr()->alloc(p->name);
        //DMSG(("FunctionAST Proto.name=%s\n", proto->name.c_str()));
    }
    virtual int getType() {
        return EXPR_CLASS;
    }

    virtual PyObjPtr eval(PyObjPtr context);
};

class IfExprAST: public ExprAST {
public:
    vector<ExprASTPtr>          conditions;
    vector<vector<ExprASTPtr> > ifbody;

public:
    IfExprAST(){
        this->name = "if";
        //DMSG(("FunctionAST Proto.name=%s\n", proto->name.c_str()));
    }
    virtual int getType() {
        return EXPR_IF;
    }
    virtual PyObjPtr eval(PyObjPtr context);
    
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
    virtual PyObjPtr eval(PyObjPtr context) {
        //DMSG(("continue expr eval---------\n"));
        singleton_t<ForBreakContinueFlag>::instance_ptr()->flagContinue = true;
        return context;
    }
    virtual int getType() {
        return EXPR_CONTINUE;
    }
};

class BreakExprAST : public ExprAST {
public:
    BreakExprAST(){
    }
    virtual PyObjPtr eval(PyObjPtr context) {
        //DMSG(("break expr eval---------\n"));
        singleton_t<ForBreakContinueFlag>::instance_ptr()->flagBreak = true;
        return context;
    }
    virtual int getType() {
        return EXPR_BREAK;
    }
};
class ForExprAST: public ExprAST {
public:
    ExprASTPtr                  iterTuple;
    ExprASTPtr                  iterFunc;
    vector<ExprASTPtr>          forBody;
public:
    ForExprAST(){
        this->name = "for";
        //DMSG(("FunctionAST Proto.name=%s\n", proto->name.c_str()));
    }
    virtual int getType() {
        return EXPR_FOR;
    }
    virtual PyObjPtr eval(PyObjPtr context);
};


class TupleExprAST: public ExprAST {
public:
    vector<ExprASTPtr>    values;

public:
    TupleExprAST(){
        this->name = "tuple";
        //DMSG(("FunctionAST Proto.name=%s\n", proto->name.c_str()));
    }
    virtual int getType() {
        return EXPR_TUPLE;
    }
    virtual PyObjPtr eval(PyObjPtr context);
    
    PyObjPtr handleAssign(PyObjPtr context, PyObjPtr value);
};

/// CallExprAST - Expression class for function calls.
class CallExprAST : public ExprAST {

public:
    CallExprAST(ExprASTPtr& c, ExprASTPtr& a)
        : varFuncName(c), argsTuple(a) {
        //DMSG(("build call %s\n", Callee->name.c_str()));
    }
    virtual int getType() {
        return EXPR_CALL;
    }
    virtual PyObjPtr eval(PyObjPtr context);
public:
    ExprASTPtr varFuncName;
    ExprASTPtr argsTuple;
};


}
#endif


