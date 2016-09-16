
#include "Base.h"
#include "PyObj.h"
#include "ExprAST.h"
#include <map>
#include <cstdlib>

#include "Scanner.h"
#include "Parser.h"
#include "StrTool.h"
#include "Util.h"

using namespace std;
using namespace ff;

NumberExprAST::NumberExprAST(long v) : Val(v) {
    char msg[64];
    snprintf(msg, sizeof(msg), "%ld(int)", Val);
    this->name = msg;
    obj = new PyObjInt(Val);
}
FloatExprAST::FloatExprAST(double v) : Val(v) {
    char msg[64];
    snprintf(msg, sizeof(msg), "%g(float)", Val);
    this->name = msg;
    obj = new PyObjFloat(Val);
}
PyObjPtr& VariableExprAST::eval(PyContext& context) {
    PyObjPtr& ret = this->getFieldVal(context);
    if (!ret){
        throw PyException::buildException("NameError: global name '%s' is not defined", this->name.c_str());
    }
    return ret;
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
        string   s = v->handler->handleStr(v);
        
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
    PyObjPtr& ret = exprlist->eval(context);
    return ret;
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
        return context.cacheResult(PyObjTool::buildNone());
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
        return context.cacheResult(PyObjTool::buildNone());
    }

    unsigned int i = 0;
    for (; i < exprs.size(); ++i){
        exprs[i]->eval(context);
    }
    return exprs[i]->eval(context);
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
    if (exprs.empty()){
        return context.cacheResult(PyObjTool::buildNone());
    }
    unsigned int i = 0;
    for (; i < exprs.size(); ++i){
        exprs[i]->eval(context);
    }
    return exprs[i]->eval(context);
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
    if (exprs.empty()){
        return context.cacheResult(PyObjTool::buildNone());
    }
    unsigned int i = 0;
    for (; i < exprs.size(); ++i){
        exprs[i]->eval(context);
    }
    return exprs[i]->eval(context);
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
        if (caseBool->handler->handleBool(context, caseBool)){
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
            if (caseBool->handler->handleBool(context, caseBool)){
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
    while (true){
        PyObjPtr& caseBool = exprlist->eval(context);
        if (PyObjTool::handleBool(caseBool)){
            suite->eval(context);
        }
        else{
            break;
        }
    }
    if (elseSuite){
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
    if (list_for){
        ret += "\nlist_for\n" + list_for->dump(nDepth+1);
    }
    return ret;
}

PyObjPtr& ListMakerExprAST::eval(PyContext& context){TRACE_EXPR();
    for (unsigned int i = 0; i < test.size(); ++i){
        test[i]->eval(context);
    }
    if (list_for){
        list_for->eval(context);
    }
    return context.cacheResult(PyObjTool::buildNone());
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
    if (comp_for){
        ret += "\ncomp_for\n" + comp_for->dump(nDepth+1);
    }
    return ret;
}

PyObjPtr& DictorsetMakerExprAST::eval(PyContext& context){TRACE_EXPR();
    PyObjPtr ret = new PyObjDict();
    for (unsigned int i = 0; i < testKey.size(); ++i){
        PyObjPtr pObjKey = testKey[i]->eval(context);
        ret.cast<PyObjDict>()->value[pObjKey] = testVal[i]->eval(context);
        
    }
    if (comp_for){
        comp_for->eval(context);
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
        if (inheritClass->getType() == PY_TUPLE){
            parentClass = inheritClass.cast<PyObjTuple>()->value;
        }
        else{
            parentClass.push_back(inheritClass);
        }
    }
    PyObjPtr rval = new PyObjClassDef(classname.cast<VariableExprAST>()->name, parentClass, suite);
    rval.cast<PyObjClassDef>()->processInheritInfo(context, rval);
    
    PyObjPtr& lval = classname->assignVal(context, rval);

    if (suite){
        PyContextBackUp backup(context);
        context.curstack = rval;
        
        suite->eval(context);
    }
    return lval;
}



PyObjPtr& ForExprASTOld::eval(PyContext& context){TRACE_EXPR();
    PyObjPtr& iterObj = iterFunc->eval(context);
    if (!iterObj)
    {
        return context.curstack;
    }
    //DMSG(("\n"));
    ForBreakContinueFlag* pFlag =  singleton_t<ForBreakContinueFlag>::instance_ptr();
    pFlag->flagContinue = false;
    pFlag->flagBreak = false;
    
    switch (iterObj->getType())
    {
        case PY_TUPLE:
        {
            if (this->iterTuple->getType() != EXPR_VAR){
                throw PyException::buildException("for key nust be var");
            }
            PyObjTuple* pTuple = iterObj.cast<PyObjTuple>();

            for (unsigned int i = 0; i < pTuple->value.size(); ++i){
                
                //TODO this->iterTuple->handleAssign(context, pTuple->values[i]);
                
                //DMSG((" -------- ForExprAST::eval ------")); 
                //pTuple->values[i]->dump();
                //this->iterTuple->eval(context)->dump();
                //DMSG(("\n"));
                for (unsigned int j = 0; j < forBody.size(); ++j){
                    //DMSG((" -------- ForExprAST::eval ------\n")); 
                    forBody[j]->eval(context);
                    if (pFlag->flagContinue || pFlag->flagBreak){
                        break;
                    }
                }
                if (pFlag->flagContinue){
                    pFlag->flagContinue = false;
                    continue;
                }
                else if (pFlag->flagBreak){
                    pFlag->flagBreak = false;
                    break;
                }
            }
            return context.curstack;
        }
        break;
        default:
            break;
    }

    for (unsigned int i = 0; i < forBody.size(); ++i){
        forBody[i]->eval(context);
    }
    return context.curstack;
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

PyObjPtr& BinaryExprAST::eval(PyContext& context){TRACE_EXPR();
    switch (optype){
        case OP_ASSIGN:{
            //DMSG(("BinaryExprAST file:%d line %d", this->lineInfo.fileId, this->lineInfo.nLine));
            PyObjPtr rval = right->eval(context);
            if (!rval){
                throw PyException::buildException("var is not defined");
            }
            
            if (left->getType() == EXPR_DOT_GET_FIELD){ //!special process class instance filed assign
                return left.cast<DotGetFieldExprAST>()->assignToField(context, rval);
            }
            else if (left->getType() == EXPR_TUPLE){ //!special process assign for tuple
                return left.cast<TupleExprAST>()->assignToField(context, rval);
            }
            else if (left->getType() == EXPR_VAR){ //!special process assign for var
                PyObjPtr& lval = left->assignVal(context, rval);
                return lval;
            }
            //DMSG(("assign %s\n%s,%s\n", left->dump(0).c_str(), right->dump(0).c_str(), rval->handler->handleStr(rval).c_str()));

            PyObjPtr& lval = left->eval(context);
            lval = rval;
            return lval;
        }break;
        case OP_ADD:{
            PyObjPtr rval = right->eval(context);
            PyObjPtr& lval = left->eval(context);
            return lval->handler->handleAdd(context, lval, rval);
        }break;
        case OP_SUB:{
            PyObjPtr rval = right->eval(context);
            PyObjPtr& lval = left->eval(context);
            return lval->handler->handleSub(context, lval, rval);
        }break;
        case OP_MUL:{
            PyObjPtr rval = right->eval(context);
            PyObjPtr& lval = left->eval(context);
            return lval->handler->handleMul(context, lval, rval);
        }break;
        case OP_DIV:{
            PyObjPtr rval = right->eval(context);
            PyObjPtr& lval = left->eval(context);
            return lval->handler->handleDiv(context, lval, rval);
        }break;
        case OP_MOD:{
            PyObjPtr rval = right->eval(context);
            PyObjPtr& lval = left->eval(context);
            return lval->handler->handleMod(context, lval, rval);
        }break;
        case OP_EQ:{
            PyObjPtr& rval = right->eval(context);
            PyObjPtr& lval = left->eval(context);
            if (lval->handler->handleEqual(context, lval, rval)){
                return context.cacheResult(PyObjTool::buildTrue());
            }
            return context.cacheResult(PyObjTool::buildFalse());
        }break;
        case OP_NOTEQ:{
            PyObjPtr rval = right->eval(context);
            PyObjPtr& lval = left->eval(context);
            if (lval->handler->handleEqual(context, lval, rval)){
                return context.cacheResult(PyObjTool::buildFalse());
            }
            return context.cacheResult(PyObjTool::buildTrue());
        }break;
        case OP_LESS:{
            PyObjPtr rval = right->eval(context);
            PyObjPtr& lval = left->eval(context);
            if (lval->handler->handleLess(context, lval, rval)){
                return context.cacheResult(PyObjTool::buildFalse());
            }
            return context.cacheResult(PyObjTool::buildFalse());
        }break;
        case OP_GREAT:{
            PyObjPtr rval = right->eval(context);
            PyObjPtr& lval = left->eval(context);
            if (lval->handler->handleGreat(context, lval, rval)){
                return context.cacheResult(PyObjTool::buildTrue());
            }
            return context.cacheResult(PyObjTool::buildFalse());
        }break;
        case OP_LESSEQ:{
            PyObjPtr rval = right->eval(context);
            PyObjPtr& lval = left->eval(context);
            if (lval->handler->handleLessEqual(context, lval, rval)){
                return context.cacheResult(PyObjTool::buildTrue());
            }
            return context.cacheResult(PyObjTool::buildFalse());
        }break;
        case OP_GREATEQ:{
            PyObjPtr rval = right->eval(context);
            PyObjPtr& lval = left->eval(context);
            if (lval->handler->handleGreatEqual(context, lval, rval)){
                return context.cacheResult(PyObjTool::buildTrue());
            }
            return context.cacheResult(PyObjTool::buildFalse());
        }break;
        case OP_IN:{
            PyObjPtr rval = right->eval(context);
            PyObjPtr& lval = left->eval(context);
            if (lval->handler->handleIn(context, lval, rval)){
                return context.cacheResult(PyObjTool::buildTrue());
            }
            return context.cacheResult(PyObjTool::buildFalse());
        }break;
        case OP_NOTIN:{
            PyObjPtr rval = right->eval(context);
            PyObjPtr& lval = left->eval(context);
            if (lval->handler->handleIn(context, lval, rval)){
                return context.cacheResult(PyObjTool::buildFalse());
            }
            return context.cacheResult(PyObjTool::buildTrue());
        }break;
        case OP_OR:{
            PyObjPtr& lval = left->eval(context);
            if (lval->handler->handleBool(context, lval)){
                return context.cacheResult(PyObjTool::buildTrue());
            }
            
            PyObjPtr& rval = right->eval(context);
            if (rval->handler->handleBool(context, rval)){
                return context.cacheResult(PyObjTool::buildTrue());
            }
            return context.cacheResult(PyObjTool::buildFalse());
        }break;
        case OP_AND:{
            PyObjPtr& lval = left->eval(context);
            PyObjPtr& rval = right->eval(context);
            if (lval->handler->handleBool(context, lval) && rval->handler->handleBool(context, rval)){
                return context.cacheResult(PyObjTool::buildTrue());
            }
            return context.cacheResult(PyObjTool::buildFalse());
        }break;
        default:
            return context.cacheResult(PyObjTool::buildNone());
    }
    
    return context.curstack;
}

string BinaryExprAST::dump(int nDepth){
    string ret;
    for (int i = 0; i < nDepth; ++i){
        ret += "-";
    }
    ret += left->dump(0) + this->name + right->dump(0);
    return ret;
}

PyObjPtr& AugassignAST::eval(PyContext& context){TRACE_EXPR();
    return context.cacheResult(PyObjTool::buildNone());//!TODO
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

PyObjPtr& TupleExprAST::assignToField(PyContext& context, PyObjPtr& v){
    if (v->getType() != PY_TUPLE){
        throw PyException::buildException("value must be tuple");
    }
    
    PyObjTuple* tuple = v.cast<PyObjTuple>();
    if (values.size() != tuple->value.size()){
        throw PyException::buildException("value size invalid");
    }
    
    for (unsigned int i = 0; i < values.size(); ++i){
        if (values[i]->getType() != EXPR_VAR){
            throw PyException::buildException("left tuple must be var");
        }
        PyObjPtr& ref = values[i]->eval(context);
        ref = tuple->value[i];
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
    //string strObj = PyObj::dump(obj);
    //printf("%p %s:obj:\n %s", obj.get(), fieldName.cast<VariableExprAST>()->name.c_str(), strObj.c_str());
    return fieldName->eval(context);
}

PyObjPtr& DotGetFieldExprAST::assignToField(PyContext& context, PyObjPtr& v){
    PyObjPtr obj = preExpr->eval(context);
    if (obj->getType() == PY_CLASS_INST){
        return obj.cast<PyObjClassInstance>()->assignToField(context, obj, fieldName, v);
    }
    
    PyContextBackUp backup(context);
    context.curstack = obj;
    //string strObj = PyObj::dump(obj);
    //printf("%s:obj:\n %s", fieldName.cast<VariableExprAST>()->name.c_str(), strObj.c_str());
    PyObjPtr& ref = fieldName->eval(context);
    ref = v;
    return ref;
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
            PyObjPtr& v = argInfo.argVal->eval(context);
            allValue.push_back(v);
        }
        
        PyObjPtr& ret = funcObj->handler->handleCall(context, funcObj, allArgsTypeInfo, allValue);
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
            if (pVal->getType() != PY_TUPLE){
                throw PyException::buildException("tuple needed after *");
            }
            
            for (unsigned int i = 0; i < pVal.cast<PyObjTuple>()->value.size(); ++i){
                newArgTypeInfo.push_back(tmpInfo);
            }
            allValue.insert(allValue.end(), pVal.cast<PyObjTuple>()->value.begin(), pVal.cast<PyObjTuple>()->value.end());
        }
        else if (argInfo.argType == "**"){
            PyObjPtr pVal = argInfo.argVal->eval(context);
            if (pVal->getType() != PY_DICT){
                throw PyException::buildException("dict needed after **");
            }
            
            PyObjDict::DictMap::iterator it = pVal.cast<PyObjDict>()->value.begin();
            
            for (; it != pVal.cast<PyObjDict>()->value.end(); ++it){
                const PyObjPtr& pKey = it->first;
                if (pKey->getType() != PY_STR){
                    throw PyException::buildException("dict key must string");
                }
                tmpInfo.argType = "=";
                tmpInfo.argKey = pKey.cast<PyObjStr>()->value;
                newArgTypeInfo.push_back(tmpInfo);
                
                PyObjPtr& v = it->second;
                allValue.push_back(v);
            }
        }
    }
    
    PyObjPtr& ret = funcObj->handler->handleCall(context, funcObj, newArgTypeInfo, allValue);
    TRACE_EXPR_POP();
    return ret;
}

PyObjPtr PyOpsUtil::importFile(PyContext& context, const std::string& modpath, std::string asName, bool assignFlag){
    string realpath = modpath + ".py";
    Scanner scanner;
    int nFileId = context.allocFileIdByPath(realpath);
    scanner.tokenizeFile(realpath, nFileId);
    
    std::map<int, std::string> line2Code = scanner.getAllLineCode();
    context.setFileIdLineInfo(nFileId, line2Code);

    Parser parser;
    ExprASTPtr rootExpr;
    rootExpr = parser.parse(scanner);

    string modname = asName;
    PyObjPtr mod = new PyObjModule(modname, realpath);
    PyContextBackUp backup(context);
    context.curstack = mod;
    rootExpr->eval(context);
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
PyObjPtr& ImportAST::eval(PyContext& context) {TRACE_EXPR();
    vector<string> sysdir;
    StrTool::split(context.syspath, sysdir, ";");
    
    for (size_t i = 0; i < importArgs.size(); ++i){
        ImportAST::ImportInfo& info = importArgs[i];

        string realpath;
        string path;
        if (sysdir.empty()){
            sysdir.push_back("./");
        }
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
                if (Util::isDir(path)){
                    continue;
                }
                else if (Util::isFile(path + ".py")){
                    realpath = path;
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
            throw PyException::buildException("ImportError: No module named %s", info.pathinfo[info.pathinfo.size() - 1].c_str());
        }
        
        if (allPyInDir.empty() == false){
            for (size_t t = 0; t < allPyInDir.size(); ++t){
                vector<string> modargs;
                StrTool::split(allPyInDir[t], modargs, ".py");
                string modName = modargs[0];
                PyObjPtr mod = PyOpsUtil::importFile(context, realpath + "/" + modName, modName);
                if (!mod){
                    throw PyException::buildException("ImportError: No module named %s", modName.c_str());
                }
            }
            continue;
        }
        
        string asMod; 
        if (info.asinfo.empty() || info.asinfo == "*"){
            asMod = info.pathinfo[info.pathinfo.size() - 1];
        }
        else{
            asMod = info.asinfo;
        }
        
        PyObjPtr mod = PyOpsUtil::importFile(context, realpath, asMod, importChildProp.empty());
        if (!mod){
            throw PyException::buildException("ImportError: No module named %s", info.pathinfo[info.pathinfo.size() - 1].c_str());
        }
        
        if (!importChildProp.empty() && mod){
            map<string, PyObjPtr> ret = mod.cast<PyObjModule>()->getAllFieldData();
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
                    throw PyException::buildException("ImportError: No module named %s", importChildProp.c_str());
                }
                ExprASTPtr asExpr = singleton_t<VariableExprAllocator>::instance_ptr()->alloc(it->first);
                asExpr->assignVal(context, it->second);
            }
            
        }
    }
    return context.cacheResult(PyObjTool::buildNone());
}

