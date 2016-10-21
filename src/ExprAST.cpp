
#include "Base.h"
#include "PyObj.h"
#include "ExprAST.h"
#include <map>
#include <cstdlib>

#include "Scanner.h"
#include "Parser.h"
#include "StrTool.h"
#include "Util.h"
#include <limits.h> 
using namespace std;
using namespace ff;

NumberExprAST::NumberExprAST(PyInt v) : Val(v) {
    char msg[64];
    snprintf(msg, sizeof(msg), "%ld(int)", long(Val));
    this->name = msg;
    obj = new PyObjInt(Val);
}
FloatExprAST::FloatExprAST(PyFloat v) : Val(v) {
    char msg[64];
    snprintf(msg, sizeof(msg), "%g(float)", Val);
    this->name = msg;
    obj = new PyObjFloat(Val);
}
PyObjPtr& VariableExprAST::eval(PyContext& context) {
    PyObjPtr& ret = this->getFieldVal(context);
    
    if (!ret){
        PyObjPtr ret2 = context.getBuiltin(this->name);
        if (ret2){
            return context.cacheResult(ret2);
        }

        if (IsFuncCallStack(context.curstack)){
            PyContextBackUp backup(context);
            context.curstack = context.curstack.cast<PyCallTmpStack>()->modBelong;
            PyObjPtr& ret3 = this->getFieldVal(context);
            if (ret3){
                return ret3;
            }
        }
        else if (PyCheckClass(context.curstack)){ //!get global var
            PyObjPtr mod = context.curstack.cast<PyObjClassDef>()->getMod(context);
            if (mod){
                PyObjPtr& ret4 = mod->getVar(context, mod, this);
                if (ret4){
                    return ret4;
                }
            }
        }
//        if (IsFuncCallStack(context.curstack)){
//            printf("!!!!!!!!\n");
//            string strObj = PyObj::dump(context, context.curstack);
//            printf("%s\n", strObj.c_str());
//        }
//        else{
//            string strObj = PyObj::dump(context, context.curstack);
//            printf("##%s\n", strObj.c_str());
//        }
        PY_RAISE_STR(context, 
            PyCppUtil::strFormat("NameError: global name '%s' is not defined %d", this->name.c_str(), context.curstack->getType()));
    }
    return ret;
}
PyObjPtr& VariableExprAST::assignVal(PyContext& context, PyObjPtr& v){
    
    if (IsFuncCallStack(context.curstack) && context.curstack.cast<PyCallTmpStack>()->isGlobalVar(this)){
        PyContextBackUp backup(context);
        context.curstack = context.curstack.cast<PyCallTmpStack>()->modBelong;
        PyObjPtr& ret3 = this->getFieldVal(context);
        ret3 = v;
        return ret3;
    }
    
    PyObjPtr& lval = this->getFieldVal(context);
    lval = v;
    return lval;
}

PyObjPtr& PowerAST::eval(PyContext& context){TRACE_EXPR();
    return merge->eval(context);
}
string PowerAST::dump(int nDepth){
    string ret;
    for (int i = 0; i < nDepth; ++i){
        ret += "-";
    }
    ret += "PowerAST";
    ret += "\n" + merge->dump(nDepth+1);
    //for (unsigned int i = 0; i < trailer.size(); ++i){
    //    ret += "\n" + trailer[i]->dump(nDepth+1);
    //}
    return ret;
}

PyObjPtr& StmtAST::eval(PyContext& context){TRACE_EXPR();
    if (exprs.empty()){
        return context.cacheResult(PyObjTool::buildNone());
    }
    unsigned int i = 0;
    for (; i < exprs.size() - 1; ++i){
        exprs[i]->eval(context);
    }
    return exprs[i]->eval(context);
}
string StmtAST::dump(int nDepth){
    string ret;
    for (int i = 0; i < nDepth; ++i){
        ret += "-";
    }
    ret += "StmtAST";
    for (unsigned int i = 0; i < exprs.size(); ++i){
        ret += "\n" + exprs[i]->dump(nDepth+1);
    }
    return ret;
}

PyObjPtr& PrintAST::eval(PyContext& context){TRACE_EXPR();
    for (unsigned int i = 0; i < exprs.size(); ++i){
        PyObjPtr v = exprs[i]->eval(context);
        string   s = v->getHandler()->handleStr(context, v);
        if (PyCheckStr(v)){
            s = s.substr(1, s.size() - 2);
        }
        if (i == 0){
            printf("%s", s.c_str());
        }
        else{
            printf(" %s", s.c_str());
        }
    }
    printf("\n");
    return context.cacheResult(PyObjTool::buildNone());
}

string PrintAST::dump(int nDepth){
    string ret;
    for (int i = 0; i < nDepth; ++i){
        ret += "-";
    }
    ret += "PrintAST";
    for (unsigned int i = 0; i < exprs.size(); ++i){
        ret += "\n" + exprs[i]->dump(nDepth+1);
    }
    return ret;
}

PyObjPtr& DelAST::eval(PyContext& context){TRACE_EXPR();
    exprlist->delVal(context);

    return context.cacheResult(PyObjTool::buildNone());
}
string DelAST::dump(int nDepth){
    string ret;
    for (int i = 0; i < nDepth; ++i){
        ret += "-";
    }
    ret += "DelAST";
    ret += "\n" + exprlist->dump(nDepth+1);
    return ret;
}

PyObjPtr& ReturnAST::eval(PyContext& context){TRACE_EXPR();
    if (!testlist){
        PY_RAISE_STR(context, 
            PyCppUtil::strFormat("NameError: global name '%s' is not defined %d", this->name.c_str(), context.curstack->getType()));
    }
    PyObjPtr& ret = testlist->eval(context);
    context.cacheResult(ret);
    throw ReturnSignal();
    return ret;
}
string ReturnAST::dump(int nDepth){
    string ret;
    for (int i = 0; i < nDepth; ++i){
        ret += "-";
    }
    ret += "ReturnAST";
    if (testlist)
        ret += "\n" + testlist->dump(nDepth+1);
    return ret;
}

PyObjPtr& RaiseAST::eval(PyContext& context){TRACE_EXPR();
    if (exprs.empty()){
        context.cacheResult(PyObjTool::buildNone());
        throw PyExceptionSignal();
    }
    PyObjPtr v = exprs[0]->eval(context);
    PY_RAISE(context, v);
    return context.cacheResult(PyObjTool::buildNone());
}
string RaiseAST::dump(int nDepth){
    string ret;
    for (int i = 0; i < nDepth; ++i){
        ret += "-";
    }
    ret += "RaiseAST";
    for (unsigned int i = 0; i < exprs.size(); ++i){
        ret += "\n" + exprs[i]->dump(nDepth+1);
    }
    return ret;
}

PyObjPtr& GlobalAST::eval(PyContext& context){TRACE_EXPR();
    if (IsFuncCallStack(context.curstack)){
        for (unsigned int i = 0; i < exprs.size(); ++i){
            context.curstack.cast<PyCallTmpStack>()->addGlobalVar(exprs[i].get());
        }
    }

    return context.cacheResult(PyObjTool::buildNone());
}
string GlobalAST::dump(int nDepth){
    string ret;
    for (int i = 0; i < nDepth; ++i){
        ret += "-";
    }
    ret += "GlobalAST";
    for (unsigned int i = 0; i < exprs.size(); ++i){
        ret += "\n" + exprs[i]->dump(nDepth+1);
    }
    return ret;
}

PyObjPtr& ExecAST::eval(PyContext& context){TRACE_EXPR();
    for (unsigned int i = 0; i < exprs.size(); ++i){
        exprs[i]->eval(context);
    }
    return context.cacheResult(PyObjTool::buildNone());
}
string ExecAST::dump(int nDepth){
    string ret;
    for (int i = 0; i < nDepth; ++i){
        ret += "-";
    }
    ret += "ExecAST";
    for (unsigned int i = 0; i < exprs.size(); ++i){
        ret += "\n" + exprs[i]->dump(nDepth+1);
    }
    return ret;
}

PyObjPtr& AssertAST::eval(PyContext& context){TRACE_EXPR();
    if (exprs.empty()){
        return context.cacheResult(PyObjTool::buildNone());
    }
    unsigned int i = 0;
    for (; i < exprs.size(); ++i){
        exprs[i]->eval(context);
    }
    return exprs[i]->eval(context);
}
string AssertAST::dump(int nDepth){
    string ret;
    for (int i = 0; i < nDepth; ++i){
        ret += "-";
    }
    ret += "AssertAST";
    for (unsigned int i = 0; i < exprs.size(); ++i){
        ret += "\n" + exprs[i]->dump(nDepth+1);
    }
    return ret;
}

StrExprAST::StrExprAST(const string& v) : val(v) {
    this->name = v;
    this->name += "(str)";
    obj = new PyObjStr(val);
}

string IfExprAST::dump(int nDepth){
    string ret;
    for (int i = 0; i < nDepth; ++i){
        ret += "-";
    }
    ret += "IfExprAST";
    for (unsigned int i = 0; i < ifTest.size(); ++i){
        ret += "\niftest\n" + ifTest[i]->dump(nDepth+1);
        ret += "\nifsuit\n" + ifSuite[i]->dump(nDepth+1);
    }
    if (elseSuite){
        ret += "\nelse\n" + elseSuite->dump(nDepth+1);
    }
    return ret;
}

PyObjPtr& IfExprAST::eval(PyContext& context){TRACE_EXPR();
    for (unsigned int i = 0; i < ifTest.size(); ++i){
        PyObjPtr& caseBool = ifTest[i]->eval(context);
        if (caseBool->getHandler()->handleBool(context, caseBool)){
            ifSuite[i]->eval(context);
            return context.cacheResult(PyObjTool::buildNone());
        }
    }
    if (elseSuite){
        elseSuite->eval(context);
        return context.cacheResult(PyObjTool::buildNone());
    }
    return context.cacheResult(PyObjTool::buildNone());
}

string WhileExprAST::dump(int nDepth){
    string ret;
    for (int i = 0; i < nDepth; ++i){
        ret += "-";
    }
    ret += "WhileExprAST";
    ret += "\ntest\n" + test->dump(nDepth+1);
    ret += "\nsuite\n" + suite->dump(nDepth+1);
    if (elseSuite){
        ret += "\nelse\n" + elseSuite->dump(nDepth+1);
    }
    return ret;
}

PyObjPtr& WhileExprAST::eval(PyContext& context){TRACE_EXPR();
    bool doElse = true;
    while (true){
        try{
            PyObjPtr& caseBool = test->eval(context);
            if (caseBool->getHandler()->handleBool(context, caseBool)){
                doElse = false;
                suite->eval(context);
            }
            else{
                break;
            }
        }
        catch(FlowCtrlSignal& s){
            if (s.nSignal == FlowCtrlSignal::CONTINUE){
                continue;
            }
            else if (s.nSignal == FlowCtrlSignal::BREAK){
                break;
            }
        }
    }
    if (doElse && elseSuite){
        elseSuite->eval(context);
    }
    return context.cacheResult(PyObjTool::buildNone());
}

string ForExprAST::dump(int nDepth){
    string ret;
    for (int i = 0; i < nDepth; ++i){
        ret += "-";
    }
    ret += "ForExprAST";
    ret += "\nexprlist\n" + exprlist->dump(nDepth+1);
    ret += "\ntestlist\n" + testlist->dump(nDepth+1);
    ret += "\nsuite\n" + suite->dump(nDepth+1);
    if (elseSuite){
        ret += "\nelse\n" + elseSuite->dump(nDepth+1);
    }
    return ret;
}

PyObjPtr& ForExprAST::eval(PyContext& context){TRACE_EXPR();
    bool doElse = true;
    PyObjPtr allVal = testlist->eval(context);
    IterUtil iterUtil(context, allVal);
    while (true){
        try{
            PyObjPtr v = iterUtil.next();
            if (!v){
                break;
            }
            doElse = false;
            exprlist->assignVal(context, v);
            suite->eval(context);
        }
        catch(FlowCtrlSignal& s){
            if (s.nSignal == FlowCtrlSignal::CONTINUE){
                continue;
            }
            else if (s.nSignal == FlowCtrlSignal::BREAK){
                break;
            }
        }
    }
    if (doElse && elseSuite){
        elseSuite->eval(context);
    }
    return context.cacheResult(PyObjTool::buildNone());
}

string ListMakerExprAST::dump(int nDepth){
    string ret;
    for (int i = 0; i < nDepth; ++i){
        ret += "-";
    }
    ret += "list";
    for (unsigned int i = 0; i < test.size(); ++i){
        ret += "\ntest\n" + test[i]->dump(nDepth+1);
    }
    if (list_for_exprlist){
        ret += "\nlist_for\n" + list_for_exprlist->dump(nDepth+1);
    }
    return ret;
}

PyObjPtr& ListMakerExprAST::eval(PyContext& context){TRACE_EXPR();
    PyObjPtr ret = new PyObjList();
    if (!list_for_exprlist){
        for (unsigned int i = 0; i < test.size(); ++i){
            ret.cast<PyObjList>()->value.push_back(test[i]->eval(context));
        }
    }
    else{
        PyObjPtr allVal = list_for_testlist_safe->eval(context);
        IterUtil iterUtil(context, allVal);
        ExprASTPtr& elemExpr = test[0];
        while (true){
            PyObjPtr v = iterUtil.next();
            if (!v){
                break;
            }
            list_for_exprlist->assignVal(context, v);
            ret.cast<PyObjList>()->value.push_back(elemExpr->eval(context));
        }
    }
    return context.cacheResult(ret);
}

string DictorsetMakerExprAST::dump(int nDepth){
    string ret;
    for (int i = 0; i < nDepth; ++i){
        ret += "-";
    }
    ret += "dict";
    ret += "\ntest Key,Val";
    for (unsigned int i = 0; i < testKey.size(); ++i){
        ret += "\n"+ testKey[i]->dump(nDepth+1);
        ret += "\n"+ testVal[i]->dump(nDepth+1);
    }
    /*for (unsigned int i = 0; i < test.size(); ++i){
        ret += "\ntest\n" + test[i]->dump(nDepth+1);
    }*/
    if (comp_for_exprlist){
        ret += "\ncomp_for\n" + comp_for_exprlist->dump(nDepth+1);
    }
    return ret;
}

PyObjPtr& DictorsetMakerExprAST::eval(PyContext& context){TRACE_EXPR();
    PyObjPtr ret = new PyObjDict();
    if (!comp_for_exprlist){
        for (unsigned int i = 0; i < testKey.size(); ++i){
            PyObjPtr pObjKey = testKey[i]->eval(context);
            ret.cast<PyObjDict>()->set(context, pObjKey, testVal[i]->eval(context));
            
        }
    }
    else{
        if (testKey.size() != 1 || testVal.size() != 1){
            PY_RAISE_STR(context, PyCppUtil::strFormat("Decorator key:val for ... in ... invalid"));
        }

        PyObjPtr allVal = comp_for_or_test->eval(context);
        IterUtil iterUtil(context, allVal);
        while (true){
            try{
                PyObjPtr v = iterUtil.next();
                if (!v){
                    break;
                }
                comp_for_exprlist->assignVal(context, v);
                
                PyObjPtr pObjKey = testKey[0]->eval(context);
                ret.cast<PyObjDict>()->set(context, pObjKey, testVal[0]->eval(context));
            }
            catch(FlowCtrlSignal& s){
                if (s.nSignal == FlowCtrlSignal::CONTINUE){
                    continue;
                }
                else if (s.nSignal == FlowCtrlSignal::BREAK){
                    break;
                }
            }
        }
    }
    
    return context.cacheResult(ret);
}

string ParametersExprAST::dump(int nDepth){
    string ret;
    for (int i = 0; i < nDepth; ++i){
        ret += "-";
    }
    ret += "parameters:fpdef,test";
    for (unsigned int i = 0; i < allParam.size(); ++i){
        ret += "\n"+ allParam[i].paramKey->dump(nDepth+1);
        if (allParam[i].paramDefault){
            ret += "\n"+ allParam[i].paramDefault->dump(nDepth+1);
        }
    }
    
    return ret;
}

PyObjPtr& ParametersExprAST::eval(PyContext& context){TRACE_EXPR();
    //!TODO
    return context.curstack;
}

string FuncDefExprAST::dump(int nDepth){
    string ret;
    for (int i = 0; i < nDepth; ++i){
        ret += "-";
    }
    ret += "funcdef:name,parameters,suite:";
    ret += "\n" + funcname->dump(nDepth+1);
    ret += "\n" + parameters->dump(nDepth+1);
    ret += "\n" + suite->dump(nDepth+1);
    
    return ret;
}

PyObjPtr& FuncDefExprAST::eval(PyContext& context){TRACE_EXPR();
    PyObjPtr rval = new PyObjFuncDef(funcname.cast<VariableExprAST>()->name, parameters, suite);
    if (IsFuncCallStack(context.curstack)){ //!closure
       rval.cast<PyObjFuncDef>()->closureStack = context.curstack;
    }
    
    PyCppUtil::setAttr(context, rval, "__doc__", PyCppUtil::genStr(doc));

    PyObjPtr& lval = funcname->assignVal(context, rval);
    return lval;
}

string ClassDefExprAST::dump(int nDepth){
    string ret;
    for (int i = 0; i < nDepth; ++i){
        ret += "-";
    }
    ret += "classdef:name,testlist,suite:";
    ret += "\n" + classname->dump(nDepth+1);
    if (testlist)
        ret += "\n" + testlist->dump(nDepth+1);
    ret += "\n" + suite->dump(nDepth+1);
    
    return ret;
}

PyObjPtr& ClassDefExprAST::eval(PyContext& context){TRACE_EXPR();
    vector<PyObjPtr> parentClass;

    if (testlist){
        PyObjPtr inheritClass = testlist->eval(context);
        if (PyCheckTuple(inheritClass)){
            parentClass = inheritClass.cast<PyObjTuple>()->value;
        }
        else{
            parentClass.push_back(inheritClass);
        }
    }
    int modFileid = context.getFileIdByMod(context.curstack);
    PyObjPtr rval = PyObjClassDef::build(context, classname.cast<VariableExprAST>()->name, parentClass, modFileid);

    PyObjPtr& lval = classname->assignVal(context, rval);

    if (suite){
        PyContextBackUp backup(context);
        context.curstack = rval;
        
        suite->eval(context);
    }
    return lval;
}

string ImportAST::dump(int nDepth){
    string ret;
    for (int i = 0; i < nDepth; ++i){
        ret += "-";
    }
    ret += "import";
    //ret += "\n" + param->dump(nDepth+1);
    return ret;
}
BinaryExprAST::BinaryExprAST(const std::string& o, ExprASTPtr& l, ExprASTPtr& r) : op(o), left(l), right(r),funcImpl(NULL) {
    this->name = op;

    if (op == "="){
        funcImpl = &BinaryExprAST::eval_OP_ASSIGN;
    }
    else if (op == "+"){
        funcImpl = &BinaryExprAST::eval_OP_ADD;
    }
    else if (op == "-"){
        funcImpl = &BinaryExprAST::eval_OP_SUB;
    }
    else if (op == "*"){
        funcImpl = &BinaryExprAST::eval_OP_MUL;
    }
    else if (op == "/"){
        funcImpl = &BinaryExprAST::eval_OP_DIV;
    }
    else if (op == "%"){
        funcImpl = &BinaryExprAST::eval_OP_MOD;
    }
    else if (op == "==" || op == "is"){
        funcImpl = &BinaryExprAST::eval_OP_EQ;
    }
    else if (op == "!=" or op == "not" or op == "<>"){
        funcImpl = &BinaryExprAST::eval_OP_NOTEQ;
    }
    else if (op == "<"){
        funcImpl = &BinaryExprAST::eval_OP_LESS;
    }
    else if (op == ">"){
        funcImpl = &BinaryExprAST::eval_OP_GREAT;
    }
    else if (op == "<="){
        funcImpl = &BinaryExprAST::eval_OP_LESSEQ;
    }
    else if (op == ">="){
        funcImpl = &BinaryExprAST::eval_OP_GREATEQ;
    }
    else if (op == "in" || op == "is in"){
        funcImpl = &BinaryExprAST::eval_OP_IN;
    }
    else if (op == "not in"){
        funcImpl = &BinaryExprAST::eval_OP_NOTIN;
    }
    else if (op == "or"){
        funcImpl = &BinaryExprAST::eval_OP_OR;
    }
    else if (op == "and"){
        funcImpl = &BinaryExprAST::eval_OP_AND;
    }
    else if (op == "&"){
        funcImpl = &BinaryExprAST::eval_OP_BIT_AND;
    }
    else if (op == "|"){
        funcImpl = &BinaryExprAST::eval_OP_BIT_OR;
    }
    else if (op == "^"){
        funcImpl = &BinaryExprAST::eval_OP_BIT_XOR;
    }
    else if (op == "~"){
        funcImpl = &BinaryExprAST::eval_OP_BIT_INVERT;
    }
    else if (op == "<<"){
        funcImpl = &BinaryExprAST::eval_OP_BIT_SHIFT;
    }
    else if (op == ">>"){
        funcImpl = &BinaryExprAST::eval_OP_BIT_RSHIFT;
    }
}
PyObjPtr& BinaryExprAST::eval_OP_ASSIGN(PyContext& context){
    PyObjPtr rval = right->eval(context);
    if (!rval){
        PY_RAISE_STR(context, "var is not defined");
    }
    PyObjPtr& lval = left->assignVal(context, rval);
    return lval;
}
PyObjPtr& BinaryExprAST::eval_OP_ADD(PyContext& context){
    PyObjPtr rval = right->eval(context);
    PyObjPtr lval = left->eval(context);
    return lval->getHandler()->handleAdd(context, lval, rval);
}
PyObjPtr& BinaryExprAST::eval_OP_SUB(PyContext& context){
    PyObjPtr rval = right->eval(context);
    PyObjPtr lval = left->eval(context);
    return lval->getHandler()->handleSub(context, lval, rval);
}
PyObjPtr& BinaryExprAST::eval_OP_MUL(PyContext& context){
    PyObjPtr rval = right->eval(context);
    PyObjPtr lval = left->eval(context);
    return lval->getHandler()->handleMul(context, lval, rval);
}
PyObjPtr& BinaryExprAST::eval_OP_DIV(PyContext& context){
    PyObjPtr rval = right->eval(context);
    PyObjPtr lval = left->eval(context);
    return lval->getHandler()->handleDiv(context, lval, rval);
}
PyObjPtr& BinaryExprAST::eval_OP_MOD(PyContext& context){
    PyObjPtr rval = right->eval(context);
    PyObjPtr& lval = left->eval(context);
    return lval->getHandler()->handleMod(context, lval, rval);
}
PyObjPtr& BinaryExprAST::eval_OP_EQ(PyContext& context){
    PyObjPtr rval = right->eval(context);
    PyObjPtr lval = left->eval(context);
    if (lval->getHandler()->handleEqual(context, lval, rval)){
        return context.cacheResult(PyObjTool::buildTrue());
    }
    return context.cacheResult(PyObjTool::buildFalse());
}
PyObjPtr& BinaryExprAST::eval_OP_NOTEQ(PyContext& context){
    PyObjPtr rval = right->eval(context);
    PyObjPtr lval = left->eval(context);
    if (lval->getHandler()->handleEqual(context, lval, rval)){
        return context.cacheResult(PyObjTool::buildFalse());
    }
    return context.cacheResult(PyObjTool::buildTrue());
} //!= not
PyObjPtr& BinaryExprAST::eval_OP_LESS(PyContext& context){
    PyObjPtr rval = right->eval(context);
    PyObjPtr lval = left->eval(context);
    if (lval->getHandler()->handleLess(context, lval, rval)){
        return context.cacheResult(PyObjTool::buildFalse());
    }
    return context.cacheResult(PyObjTool::buildFalse());
}//<
PyObjPtr& BinaryExprAST::eval_OP_GREAT(PyContext& context){
    PyObjPtr rval = right->eval(context);
    PyObjPtr lval = left->eval(context);
    if (lval->getHandler()->handleGreat(context, lval, rval)){
        return context.cacheResult(PyObjTool::buildTrue());
    }
    return context.cacheResult(PyObjTool::buildFalse());
}//>
PyObjPtr& BinaryExprAST::eval_OP_LESSEQ(PyContext& context){
    PyObjPtr rval = right->eval(context);
    PyObjPtr lval = left->eval(context);
    if (lval->getHandler()->handleLessEqual(context, lval, rval)){
        return context.cacheResult(PyObjTool::buildTrue());
    }
    return context.cacheResult(PyObjTool::buildFalse());
} //<=
PyObjPtr& BinaryExprAST::eval_OP_GREATEQ(PyContext& context){
    PyObjPtr rval = right->eval(context);
    PyObjPtr lval = left->eval(context);
    if (lval->getHandler()->handleGreatEqual(context, lval, rval)){
        return context.cacheResult(PyObjTool::buildTrue());
    }
    return context.cacheResult(PyObjTool::buildFalse());
} //>=
PyObjPtr& BinaryExprAST::eval_OP_IN(PyContext& context){
    PyObjPtr rval = right->eval(context);
    PyObjPtr lval = left->eval(context);
    if (lval->getHandler()->handleContains(context, lval, rval)){
        return context.cacheResult(PyObjTool::buildTrue());
    }
    return context.cacheResult(PyObjTool::buildFalse());
}
PyObjPtr& BinaryExprAST::eval_OP_NOTIN(PyContext& context){
    PyObjPtr rval = right->eval(context);
    PyObjPtr lval = left->eval(context);
    if (lval->getHandler()->handleContains(context, lval, rval)){
        return context.cacheResult(PyObjTool::buildFalse());
    }
    return context.cacheResult(PyObjTool::buildTrue());
}
PyObjPtr& BinaryExprAST::eval_OP_OR(PyContext& context){
    PyObjPtr lval = left->eval(context);
    if (lval->getHandler()->handleBool(context, lval)){
        return context.cacheResult(PyObjTool::buildTrue());
    }
    
    PyObjPtr rval = right->eval(context);
    if (rval->getHandler()->handleBool(context, rval)){
        return context.cacheResult(PyObjTool::buildTrue());
    }
    return context.cacheResult(PyObjTool::buildFalse());
} //! or 
PyObjPtr& BinaryExprAST::eval_OP_AND(PyContext& context){
    PyObjPtr lval = left->eval(context);
    PyObjPtr rval = right->eval(context);
    if (lval->getHandler()->handleBool(context, lval) && rval->getHandler()->handleBool(context, rval)){
        return context.cacheResult(PyObjTool::buildTrue());
    }
    return context.cacheResult(PyObjTool::buildFalse());
} //! and
PyObjPtr& BinaryExprAST::eval_OP_BIT_AND(PyContext& context){
    PyObjPtr lval = left->eval(context);
    PyObjPtr rval = right->eval(context);
    PyObjPtr ret = PyCppUtil::genInt(PyCppUtil::toInt(lval) & PyCppUtil::toInt(rval));
    return context.cacheResult(ret);
} //! &
PyObjPtr& BinaryExprAST::eval_OP_BIT_OR(PyContext& context){
    PyObjPtr lval = left->eval(context);
    PyObjPtr rval = right->eval(context);
    PyObjPtr ret = PyCppUtil::genInt(PyCppUtil::toInt(lval) | PyCppUtil::toInt(rval));
    return context.cacheResult(ret);
} //! |
PyObjPtr& BinaryExprAST::eval_OP_BIT_XOR(PyContext& context){
    PyObjPtr lval = left->eval(context);
    PyObjPtr rval = right->eval(context);
    PyObjPtr ret = PyCppUtil::genInt(PyCppUtil::toInt(lval) ^ PyCppUtil::toInt(rval));
    return context.cacheResult(ret);
} //! ^
PyObjPtr& BinaryExprAST::eval_OP_BIT_INVERT(PyContext& context){
    PyObjPtr lval = left->eval(context);
    PyObjPtr ret = PyCppUtil::genInt(~PyCppUtil::toInt(lval));
    return context.cacheResult(ret);
} //! ~
PyObjPtr& BinaryExprAST::eval_OP_BIT_SHIFT(PyContext& context){
    PyObjPtr lval = left->eval(context);
    PyObjPtr rval = right->eval(context);
    PyObjPtr ret = PyCppUtil::genInt(PyCppUtil::toInt(lval) << PyCppUtil::toInt(rval));
    return context.cacheResult(ret);
} //! <<
PyObjPtr& BinaryExprAST::eval_OP_BIT_RSHIFT(PyContext& context){
    PyObjPtr lval = left->eval(context);
    PyObjPtr rval = right->eval(context);
    PyObjPtr ret = PyCppUtil::genInt(PyCppUtil::toInt(lval) >> PyCppUtil::toInt(rval));
    return context.cacheResult(ret);
} //! >>
PyObjPtr& BinaryExprAST::eval(PyContext& context){TRACE_EXPR();
    if (funcImpl){
        return (this->*funcImpl)(context);
    }
    return context.cacheResult(PyObjTool::buildNone());
}

string BinaryExprAST::dump(int nDepth){
    string ret;
    for (int i = 0; i < nDepth; ++i){
        ret += "-";
    }
    if (left){
        ret += left->dump(0);
    }
    ret +=  this->name;
    
    if (right){
        ret += right->dump(0);
    }
    return ret;
}

AugassignAST::AugassignAST(const std::string& o, ExprASTPtr l, ExprASTPtr r): op(o), left(l), right(r), funcImpl(NULL) {
    this->name = op;
    
    if (op == "+="){
        funcImpl = &AugassignAST::eval_IAdd;
    }
    else if (op == "-="){
        funcImpl = &AugassignAST::eval_ISub;
    }
    else if (op == "*="){
        funcImpl = &AugassignAST::eval_IMul;
    }
    else if (op == "/="){
        funcImpl = &AugassignAST::eval_IDiv;
    }
    else if (op == "%="){
        funcImpl = &AugassignAST::eval_IMod;
    }
}
PyObjPtr& AugassignAST::eval_IAdd(PyContext& context){
    PyObjPtr rval = right->eval(context);
    PyObjPtr lval = left->eval(context);
    PyObjPtr& ret = lval->getHandler()->handleIAdd(context, lval, rval);
    if (ret.get() != lval.get()){
        PyObjPtr& newret = left->assignVal(context, ret);
        return newret;
    }
    return ret;
}
PyObjPtr& AugassignAST::eval_ISub(PyContext& context){
    PyObjPtr rval = right->eval(context);
    PyObjPtr lval = left->eval(context);
    PyObjPtr& ret = lval->getHandler()->handleISub(context, lval, rval);
    if (ret.get() != lval.get()){
        PyObjPtr& newret = left->assignVal(context, ret);
        return newret;
    }
    return ret;
}
PyObjPtr& AugassignAST::eval_IMul(PyContext& context){
    PyObjPtr rval = right->eval(context);
    PyObjPtr lval = left->eval(context);
    PyObjPtr& ret = lval->getHandler()->handleIMul(context, lval, rval);
    if (ret.get() != lval.get()){
        PyObjPtr& newret = left->assignVal(context, ret);
        return newret;
    }
    return ret;
}
PyObjPtr& AugassignAST::eval_IDiv(PyContext& context){
    PyObjPtr rval = right->eval(context);
    PyObjPtr lval = left->eval(context);
    PyObjPtr& ret = lval->getHandler()->handleIDiv(context, lval, rval);
    if (ret.get() != lval.get()){
        PyObjPtr& newret = left->assignVal(context, ret);
        return newret;
    }
    return ret;
}
PyObjPtr& AugassignAST::eval_IMod(PyContext& context){
    PyObjPtr rval = right->eval(context);
    PyObjPtr lval = left->eval(context);
    PyObjPtr& ret = lval->getHandler()->handleIMod(context, lval, rval);
    if (ret.get() != lval.get()){
        PyObjPtr& newret = left->assignVal(context, ret);
        return newret;
    }
    return ret;
}
PyObjPtr& AugassignAST::eval(PyContext& context){TRACE_EXPR();
    if (funcImpl){
        return (this->*funcImpl)(context);
    }
    return context.cacheResult(PyObjTool::buildNone());
}

string AugassignAST::dump(int nDepth){
    string ret;
    for (int i = 0; i < nDepth; ++i){
        ret += "-";
    }
    ret += left->dump(0) + this->name + right->dump(0);
    return ret;
}

PyObjPtr& TupleExprAST::eval(PyContext& context){TRACE_EXPR();
    PyObjTuple* tuple = new PyObjTuple();
    PyObjPtr ret = tuple;
    for (unsigned int i = 0; i < values.size(); ++i){
        PyObjPtr v = values[i]->eval(context);
        tuple->value.push_back(v);
    }
    return context.cacheResult(ret);
}
void TupleExprAST::delVal(PyContext& context){
    for (unsigned int i = 0; i < values.size(); ++i){
        values[i]->delVal(context);
    }
}
PyObjPtr& TupleExprAST::assignVal(PyContext& context, PyObjPtr& v){
    if (values.size() != (size_t)v->getHandler()->handleLen(context, v)){
        PY_RAISE_STR(context, "value size not equal");
    }
    
    IterUtil iterUtil(context, v);

    for (unsigned int i = 0; i < values.size(); ++i){
        PyObjPtr key = iterUtil.next();
        if (!key){
            PY_RAISE_STR(context, "iter value size not equal");
        }
        if (values[i]->getType() != EXPR_VAR){
            PY_RAISE_STR(context, "left tuple must be var");
        }
        values[i]->assignVal(context, key);
    }
    return v;
}
//!dot get 
string DotGetFieldExprAST::dump(int nDepth){
    string ret;
    for (int i = 0; i < nDepth; ++i){
        ret += "-";
    }
    ret += preExpr->dump(0) + "." + fieldName->dump(0);
    return ret;
}

PyObjPtr& DotGetFieldExprAST::eval(PyContext& context){TRACE_EXPR();
    PyObjPtr obj = preExpr->eval(context);
    PyContextBackUp backup(context);
    context.curstack = obj;
    //string strObj = PyObj::dump(context, obj);
    //printf("%p %s %s:obj:\n %s", obj.get(), preExpr.cast<VariableExprAST>()->name.c_str(), fieldName.cast<VariableExprAST>()->name.c_str(), strObj.c_str());
    PyObjPtr& ret = fieldName->eval(context);

    return ret;
}

PyObjPtr& DotGetFieldExprAST::assignVal(PyContext& context, PyObjPtr& v){
    PyObjPtr obj = preExpr->eval(context);
    if (obj->getType() == PY_CLASS_INST){
        return obj.cast<PyObjClassInstance>()->assignToField(context, obj, fieldName, v);
    }
    
    PyContextBackUp backup(context);
    context.curstack = obj;
    //string strObj = PyObj::dump(obj);
    //printf("%s:obj:\n %s", fieldName.cast<VariableExprAST>()->name.c_str(), strObj.c_str());
    PyObjPtr& ret = fieldName->eval(context);

    ret = v;
    return ret;
}
void DotGetFieldExprAST::delVal(PyContext& context){
   PyObjPtr obj = preExpr->eval(context);
    if (obj->getType() == PY_CLASS_INST){
        return obj.cast<PyObjClassInstance>()->delField(context, obj, fieldName);
    } 
}
string SliceExprAST::dump(int nDepth){
    string ret;
    for (int i = 0; i < nDepth; ++i){
        ret += "-";
    }
    ret += preExpr->dump(0);
    return ret;
}

PyObjPtr& SliceExprAST::eval(PyContext& context){TRACE_EXPR();
    PyObjPtr obj = preExpr->eval(context);
    
    
    PyObjPtr startVal = start->eval(context);

    int nStep  = 1;
    int nStop  = 0;
    if (step){
        PyObjPtr stepVal = step->eval(context);
        if (!PyCheckInt(stepVal)){
            PY_RAISE_STR(context, "slice arg3 must be int");
        }
        nStep = stepVal.cast<PyObjInt>()->value;
        if (nStep == 0){
            PY_RAISE_STR(context, "slice arg3 can't' be zero");
        }
    }
    
    int *pStop = NULL;
    if (stop){
        PyObjPtr stopVal = stop->eval(context);
        if (!PyCheckInt(stopVal)){
            PY_RAISE_STR(context, "slice arg2 must be int");
        }
        nStop = stopVal.cast<PyObjInt>()->value;
        pStop = &nStop;
    }
    else if (stopFlag == FLAG_END){
        if (nStep > 0){
            nStop = INT_MAX;
            pStop = &nStop;
        }
        else if (nStep < 0){
            nStop = 0;
            pStop = &nStop;
        }
    }

    return obj->getHandler()->handleSlice(context, obj, startVal, pStop, nStep);
}
PyObjPtr& SliceExprAST::assignVal(PyContext& context, PyObjPtr& v){
    
    PyObjPtr lval = preExpr->eval(context);
    PyObjPtr startVal = start->eval(context);
    return lval->getHandler()->handleSliceAssign(context, lval, startVal, v);
}
void SliceExprAST::delVal(PyContext& context){
    PyObjPtr lval = preExpr->eval(context);
    PyObjPtr startVal = start->eval(context);
    return lval->getHandler()->handleSliceDel(context, lval, startVal);
}

std::string CallExprAST::dump(int nDepth){
    string ret;
    for (int i = 0; i < nDepth; ++i){
        ret += "-";
    }
    ret += this->name + "(call)" + preExpr->dump(nDepth+1);
    return ret;
}


PyObjPtr& CallExprAST::eval(PyContext& context){TRACE_EXPR_PUSH();
    
    PyObjPtr funcObj = preExpr->eval(context);

    FuncArglist* parg = arglist.cast<FuncArglist>();
    vector<ArgTypeInfo>& allArgsTypeInfo = parg->allArgsTypeInfo;

    vector<PyObjPtr> allValue;

    if (false == parg->bNeedRerangeArgs){
        for (unsigned int i = 0; i < parg->allArgs.size(); ++i){
            FuncArglist::ArgInfo& argInfo = parg->allArgs[i];
            //DMSG(("PyObjFuncDef::argType...%s\n", argInfo.argType.c_str()));
            if (!argInfo.argVal){
                break;
            }
            PyObjPtr& v = argInfo.argVal->eval(context);
            allValue.push_back(v);
        }
        
        PyObjPtr& ret = funcObj->getHandler()->handleCall(context, funcObj, allArgsTypeInfo, allValue);
        TRACE_EXPR_POP();
        return ret;
    }
    
    vector<ArgTypeInfo>    newArgTypeInfo;
    
    for (unsigned int i = 0; i < parg->allArgs.size(); ++i){
        FuncArglist::ArgInfo& argInfo = parg->allArgs[i];
        //DMSG(("PyObjFuncDef::argType...%s\n", argInfo.argType.c_str()));
        ArgTypeInfo tmpInfo;
        if (argInfo.argType.empty()){
            newArgTypeInfo.push_back(tmpInfo);
            PyObjPtr& v = argInfo.argVal->eval(context);
            allValue.push_back(v);
        }
        else if (argInfo.argType == "="){
            tmpInfo.argType = "=";
            tmpInfo.argKey = argInfo.argKey;
            newArgTypeInfo.push_back(tmpInfo);
            PyObjPtr& v = argInfo.argVal->eval(context);
            allValue.push_back(v);
        }
        else if (argInfo.argType == "*"){
            PyObjPtr pVal = argInfo.argVal->eval(context);
            if (!PyCheckTuple(pVal)){
                PY_RAISE_STR(context, "tuple needed after *");
            }
            
            for (unsigned int i = 0; i < pVal.cast<PyObjTuple>()->value.size(); ++i){
                newArgTypeInfo.push_back(tmpInfo);
            }
            allValue.insert(allValue.end(), pVal.cast<PyObjTuple>()->value.begin(), pVal.cast<PyObjTuple>()->value.end());
        }
        else if (argInfo.argType == "**"){
            PyObjPtr pVal = argInfo.argVal->eval(context);
            if (!PyCheckDict(pVal)){
                PY_RAISE_STR(context, "dict needed after **");
            }
            
            PyObjDict::DictMap::iterator it = pVal.cast<PyObjDict>()->value.begin();
            
            for (; it != pVal.cast<PyObjDict>()->value.end(); ++it){
                const PyObjPtr& pKey = DICT_ITER_KEY(it);
                if (!PyCheckStr(pKey)){
                    PY_RAISE_STR(context, "dict key must string");
                }
                tmpInfo.argType = "=";
                tmpInfo.argKey = pKey.cast<PyObjStr>()->value;
                newArgTypeInfo.push_back(tmpInfo);
                
                PyObjPtr& v = DICT_ITER_VAL(it);
                allValue.push_back(v);
            }
        }
    }
    
    PyObjPtr& ret = funcObj->getHandler()->handleCall(context, funcObj, newArgTypeInfo, allValue);
    TRACE_EXPR_POP();
    return ret;
}

struct TmpImportCacheGuard{
    TmpImportCacheGuard(PyContext& c, int n):context(c),nFileId(n) {
    }
    ~TmpImportCacheGuard(){
        PyObjPtr modCache = context.getFileIdModCache(nFileId);
        if (modCache){
            if (modCache.cast<PyObjModule>()->loadFlag == PyObjModule::MOD_LOADING){
                context.setFileIdModCache(nFileId, NULL);
            }
        }
    }
    PyContext& context;
    int nFileId;
};
static void PyList2Vector(PyContext& context, PyObjPtr obj, vector<string>& ret){
    IterUtil iterUtil(context, obj);
    while (true){
        PyObjPtr v = iterUtil.next();
        if (!v){
            break;
        }
        ret.push_back(PyCppUtil::toStr(v));
    }
}
PyObjPtr PyOpsUtil::importFile(PyContext& context, const std::string& modpath, std::string asName, bool assignFlag){
    PyObjPtr cacheMod = context.getModule(modpath);
    if (cacheMod){
        if (assignFlag){
            ExprASTPtr asExpr = singleton_t<VariableExprAllocator>::instance_ptr()->alloc(asName);
            asExpr->assignVal(context, cacheMod);
        }
        return cacheMod;
    }
    string realpath;
    if (modpath.find(".py") != string::npos){
        realpath = modpath;
    }
    else{
        vector<string> sysdir;
        PyList2Vector(context, context.syspath, sysdir);//StrTool::split(context.syspath, sysdir, ";");
        if (sysdir.empty()){
            sysdir.push_back("./");
        }
        string path;
        for (size_t n = 0; n < sysdir.size(); ++n){
            path = sysdir[n];
            if (path.empty() == false && path[path.size() - 1] != '/'){
                path += '/';
            }
            path += modpath + ".py";
            if (Util::isFile(path)){
                realpath = path;
                break;
            }
        }
    }
    if (realpath.empty()){
        PY_RAISE_STR(context, PyCppUtil::strFormat("ImportError: No module named %s", modpath.c_str()));
    }
    Scanner scanner;
    int nFileId = context.allocFileIdByPath(realpath);
    
    PyObjPtr modCache = context.getFileIdModCache(nFileId);
    if (modCache){
        if (modCache.cast<PyObjModule>()->loadFlag == PyObjModule::MOD_LOADING){
            PY_RAISE_STR(context, PyCppUtil::strFormat("ImportError: loop import %s", modpath.c_str()));
        }
        if (assignFlag){
            ExprASTPtr asExpr = singleton_t<VariableExprAllocator>::instance_ptr()->alloc(asName);
            asExpr->assignVal(context, modCache);
        }
        return modCache;
    }
    
    scanner.tokenizeFile(realpath, nFileId);
    
    std::map<int, std::string> line2Code = scanner.getAllLineCode();
    context.setFileIdLineInfo(nFileId, line2Code);

    Parser parser;
    ExprASTPtr rootExpr;
    rootExpr = parser.parse(scanner);

    string modname = asName;
    PyObjPtr mod = PyObjModule::BuildModule(context, modname, realpath);
    context.setFileIdModCache(nFileId, mod);
    TmpImportCacheGuard guardCache(context, nFileId);
    
    PyContextBackUp backup(context);
    context.curstack = mod;
    
    if (EXPR_STMT == rootExpr->getType() && rootExpr.cast<StmtAST>()->exprs.size() >= 1){
        ExprASTPtr doc = rootExpr.cast<StmtAST>()->exprs[0];
        if (doc->getType() == EXPR_STR){
            PyCppUtil::setAttr(context, mod, "__doc__", PyCppUtil::genStr(doc.cast<StrExprAST>()->val));
            
            rootExpr.cast<StmtAST>()->exprs.erase(rootExpr.cast<StmtAST>()->exprs.begin());
        }
    }
    
    rootExpr->eval(context);
    mod.cast<PyObjModule>()->loadFlag = PyObjModule::MOD_LOADOK;
    backup.rollback();

    if (asName.empty()){
        asName = modname;
    }
    if (assignFlag){
        ExprASTPtr asExpr = singleton_t<VariableExprAllocator>::instance_ptr()->alloc(asName);
        asExpr->assignVal(context, mod);
    }
    return mod;
}
std::string PyOpsUtil::traceback(PyContext& context){
    string ret;
    char msg[512] = {0};
    for (list<ExprAST*>::iterator it = context.exprTrace.begin(); it != context.exprTrace.end(); ++it){
        ExprAST* e = *it;
        if (!e)
            continue;
        snprintf(msg, sizeof(msg), "  File \"%s\", line %d\n", context.getFileId2Path(e->lineInfo.fileId).c_str(), e->lineInfo.nLine);
        ret += msg;
        string lineCode = StrTool::trim(context.getLine2Code(e->lineInfo.fileId, e->lineInfo.nLine));
        snprintf(msg, sizeof(msg), "    %s\n", lineCode.c_str());
        ret += msg;
    }
    return ret;
}
PyObjPtr& ImportAST::eval(PyContext& context) {
    TRACE_EXPR_PUSH();
    vector<string> sysdir;
    PyList2Vector(context, context.syspath, sysdir);//StrTool::split(context.syspath, sysdir, ";");
    sysdir.push_back("");
    
    for (size_t i = 0; i < importArgs.size(); ++i){
        ImportAST::ImportInfo& info = importArgs[i];
        
        string realpath;
        string path;
        
        string importChildProp; //! from a import b
        vector<string> allPyInDir; //!each file in dir
        
        for (size_t n = 0; n < sysdir.size(); ++n){
            path = sysdir[n];
            if (path.empty() == false && path[path.size() - 1] != '/'){
                path += '/';
            }
            bool hit = false;
            for (size_t j = 0; j < info.pathinfo.size(); ++j){
                if (info.pathinfo[j] == "*" && Util::isDir(path)){
                    Util::getAllFileInDir(path, allPyInDir, ".py");
                    realpath = path;
                    hit = true;
                    break;
                }
                if (j == 0){
                    path += info.pathinfo[j];
                }
                else{
                    path += "/" + info.pathinfo[j];
                }
                
                if (context.getModule(path)){
                    realpath = path;
                    hit = true;
                    if (j < info.pathinfo.size() - 1){
                        importChildProp = info.pathinfo[info.pathinfo.size() - 1];
                    }
                    break;
                }
                
                if (Util::isDir(path)){
                    continue;
                }
                else if (Util::isFile(path + ".py")){
                    realpath = path + ".py";
                    hit = true;
                    
                    if (j < info.pathinfo.size() - 1){
                        importChildProp = info.pathinfo[info.pathinfo.size() - 1];
                    }
                    break;
                }
                else{
                    break;
                }
            }
            if (hit){
                break;
            }
        }
        
        if (realpath.empty()){
            PY_RAISE_STR(context, PyCppUtil::strFormat("ImportError: No module named %s", info.pathinfo[info.pathinfo.size() - 1].c_str()));
        }
        
        if (allPyInDir.empty() == false){
            for (size_t t = 0; t < allPyInDir.size(); ++t){
                string& modName = allPyInDir[t];
                PyObjPtr mod = PyOpsUtil::importFile(context, realpath + "/" + modName, modName);
                if (!mod){
                    PY_RAISE_STR(context, PyCppUtil::strFormat("ImportError: No module named %s", modName.c_str()));
                }
            }
            continue;
        }
        
        string asMod; 
        if (info.asinfo.empty() || info.asinfo == "*"){
            asMod = info.pathinfo[info.pathinfo.size() - 1];
            if (importChildProp.empty() && info.asinfo == "*"){
                importChildProp = info.asinfo;
            }
        }
        else{
            asMod = info.asinfo;
        }
        
        PyObjPtr mod = PyOpsUtil::importFile(context, realpath, asMod, importChildProp.empty());
        if (!mod){
            PY_RAISE_STR(context, PyCppUtil::strFormat("ImportError: No module named %s", info.pathinfo[info.pathinfo.size() - 1].c_str()));
        }

        if (!importChildProp.empty() && mod){
            map<string, PyObjPtr> ret = PyCppUtil::getAllFieldData(mod);
            if (importChildProp == "*"){
                map<string, PyObjPtr>::iterator it = ret.begin();
                for (; it != ret.end(); ++it){
                    ExprASTPtr asExpr = singleton_t<VariableExprAllocator>::instance_ptr()->alloc(it->first);
                    asExpr->assignVal(context, it->second);
                }
            }
            else{
                map<string, PyObjPtr>::iterator it = ret.find(importChildProp);
                if (it == ret.end()){
                    PY_RAISE_STR(context, PyCppUtil::strFormat("ImportError: No module named %s", importChildProp.c_str()));
                }
                ExprASTPtr asExpr = singleton_t<VariableExprAllocator>::instance_ptr()->alloc(asMod);
                asExpr->assignVal(context, it->second);
            }
            
        }
    }
    TRACE_EXPR_POP();
    return context.cacheResult(PyObjTool::buildNone());
}

PyObjPtr& TryAst::eval(PyContext& context){TRACE_EXPR();
    bool execptFlag = false;
    try{
        trySuite->eval(context);
    }
    catch(PyExceptionSignal& s){
        execptFlag = true;
        
        bool hit = false;
        PyObjPtr excepVal = context.getCacheResult();
        vector<ExceptInfo>::iterator it = exceptSuite.begin();
        for (; it != exceptSuite.end(); ++it){
            ExceptInfo& info = *it;
            if (!info.exceptType){ //!hit
                hit = true;
                info.exceptSuite->eval(context);
                break;
            }

            PyObjPtr exceptType = info.exceptType->eval(context);
            if (exceptType->getHandler()->handleIsInstance(context, exceptType, excepVal)){
                hit = true;
                info.exceptSuite->eval(context);
                break;
            }
        }
        
        if (!hit && !finallySuite){
            context.cacheResult(excepVal);
            throw PyExceptionSignal(); 
        }
    }

    if (!execptFlag && elseSuite){
        elseSuite->eval(context);
    }
    if (finallySuite){
        finallySuite->eval(context);
    }
    return context.cacheResult(PyObjTool::buildNone());
}

PyObjPtr& DecoratorAST::eval(PyContext& context){TRACE_EXPR();
    vector<PyObjPtr> funcDecorators;
    for (size_t i = 0; i < allDecorators.size(); ++i){
        ExprASTPtr& tmpExpr = allDecorators[allDecorators.size() - 1 - i];
        PyObjPtr funcObj = tmpExpr->eval(context);
        if (!funcObj || !PyCheckCallable(funcObj)){
            PY_RAISE_STR(context, PyCppUtil::strFormat("Decorator must be a func given:%d", funcObj->getType()));
        }
        funcDecorators.push_back(funcObj);
        
        
    }
    
    PyObjPtr objFunc = funcDef->eval(context);

    for (size_t i = 0; i < funcDecorators.size(); ++i){
        PyObjPtr& funcD = funcDecorators[i];
        
        vector<PyObjPtr> allValue;
        allValue.push_back(objFunc);
        
        objFunc = PyCppUtil::callPyfunc(context, funcD, allValue);
    }    
    funcDef.cast<FuncDefExprAST>()->funcname->assignVal(context, objFunc);
    return context.cacheResult(PyObjTool::buildNone());
}
static PyObjPtr lambdaFunc(PyContext& context, std::vector<PyObjPtr>& argAssignVal, std::vector<ExprASTPtr>& data){
    ExprASTPtr& varargslist = data[0];
    if (varargslist){
        ParametersExprAST* pParametersExprAST = varargslist.cast<ParametersExprAST>();
        if (pParametersExprAST->allParam.size() != argAssignVal.size()){
            PY_RAISE_STR(context, PyCppUtil::strFormat("arg num need %u given %u", 
                                pParametersExprAST->allParam.size(), argAssignVal.size()));
        }
        for (size_t i = 0; i < pParametersExprAST->allParam.size(); ++i){
            ParametersExprAST::ParameterInfo& paramInfo = pParametersExprAST->allParam[i];
            paramInfo.paramKey->assignVal(context, argAssignVal[i]);
        }
    }
    ExprASTPtr& test = data[1];
    PyObjPtr ret = test->eval(context);
    return ret;
}
PyObjPtr& LambdaAST::eval(PyContext& context){
    
    vector<ExprASTPtr> args;
    args.push_back(varargslist);
    args.push_back(test);
    PyObjPtr func = PyCppUtil::genFunc(lambdaFunc, args, "lambda");
    return context.cacheResult(func);
}

PyObjPtr& RetAfterIfAST::eval(PyContext& context){
    PyObjPtr iftestVal = if_test->eval(context);
    if (iftestVal->getHandler()->handleBool(context, iftestVal)){
        return ret->eval(context);
    }
    return else_test->eval(context);
}

struct WithGuard{
    WithGuard(PyContext& c):context(c){
    }
    ~WithGuard(){
        vector<PyObjPtr> tmpargs;
        for (size_t i = 0; i < waitExit.size(); ++i){
            PyObjPtr func = PyCppUtil::getAttr(context, waitExit[i], "__exit__");
            tmpargs.clear();
            tmpargs.push_back(PyObjTool::buildNone());
            tmpargs.push_back(PyObjTool::buildNone());
            tmpargs.push_back(PyObjTool::buildNone());
            PyCppUtil::callPyfunc(context, func, tmpargs);
        }
    }
    
    PyContext& context;
    vector<PyObjPtr> waitExit;
};

PyObjPtr& WithAST::eval(PyContext& context){
    WithGuard guard(context);
    vector<PyObjPtr> tmpargs;
    for (size_t i = 0; i < with_items.size(); ++i){
        with_item& item = with_items[i];
        PyObjPtr obj = item.test->eval(context);
        PyObjPtr func = PyCppUtil::getAttr(context, obj, "__enter__");
        tmpargs.clear();
        obj = PyCppUtil::callPyfunc(context, func, tmpargs);
        guard.waitExit.push_back(obj);
        
        if (item.asexpr){
            item.asexpr->assignVal(context, obj);
        }
    }
    suite->eval(context);
    return context.cacheResult(PyObjTool::buildNone());
}

