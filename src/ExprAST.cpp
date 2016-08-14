
#include "Base.h"
#include "PyObj.h"
#include "ExprAST.h"
#include <map>
#include <cstdlib>

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

PyObjPtr& PowerAST::eval(PyContext& context){
    PyObjPtr& ret = atom->eval(context);
    //!TODO
    return ret;
}
string PowerAST::dump(int nDepth){
    string ret;
    for (int i = 0; i < nDepth; ++i){
        ret += "-";
    }
    ret += "PowerAST";
    ret += "\n" + atom->dump(nDepth+1);
    for (unsigned int i = 0; i < trailer.size(); ++i){
        ret += "\n" + trailer[i]->dump(nDepth+1);
    }
    return ret;
}

PyObjPtr& StmtAST::eval(PyContext& context){
    PyObjPtr& ret = PyObjTool::buildNone();
    for (unsigned int i = 0; i < exprs.size(); ++i){
        ret = exprs[i]->eval(context);
    }
    return ret;
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

PyObjPtr& PrintAST::eval(PyContext& context){
    PyObjPtr& ret = PyObjTool::buildNone();
    for (unsigned int i = 0; i < exprs.size(); ++i){
        ret = exprs[i]->eval(context);
    }
    return ret;
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

PyObjPtr& DelAST::eval(PyContext& context){
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

PyObjPtr& ReturnAST::eval(PyContext& context){
    if (!testlist){
        return PyObjTool::buildNone();
    }
    PyObjPtr& ret = testlist->eval(context);
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

PyObjPtr& RaiseAST::eval(PyContext& context){
    PyObjPtr& ret = PyObjTool::buildNone();
    for (unsigned int i = 0; i < exprs.size(); ++i){
        ret = exprs[i]->eval(context);
    }
    return ret;
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

PyObjPtr& GlobalAST::eval(PyContext& context){
    PyObjPtr& ret = PyObjTool::buildNone();
    for (unsigned int i = 0; i < exprs.size(); ++i){
        ret = exprs[i]->eval(context);
    }
    return ret;
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

PyObjPtr& ExecAST::eval(PyContext& context){
    PyObjPtr& ret = PyObjTool::buildNone();
    for (unsigned int i = 0; i < exprs.size(); ++i){
        ret = exprs[i]->eval(context);
    }
    return ret;
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

PyObjPtr& AssertAST::eval(PyContext& context){
    PyObjPtr& ret = PyObjTool::buildNone();
    for (unsigned int i = 0; i < exprs.size(); ++i){
        ret = exprs[i]->eval(context);
    }
    return ret;
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

PyObjPtr& IfExprAST::eval(PyContext& context) {
    for (unsigned int i = 0; i < ifTest.size(); ++i){
        PyObjPtr& caseBool = ifTest[i]->eval(context);
        if (caseBool->handler->handleBool(context, caseBool)){
            ifSuite[i]->eval(context);
            return PyObjTool::buildNone();
        }
    }
    if (elseSuite){
        elseSuite->eval(context);
        return PyObjTool::buildNone();
    }
    return PyObjTool::buildNone();
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

PyObjPtr& WhileExprAST::eval(PyContext& context) {
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
    return context.curstack;
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

PyObjPtr& ForExprAST::eval(PyContext& context) {
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
    return context.curstack;
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

PyObjPtr& ListMakerExprAST::eval(PyContext& context) {
    for (unsigned int i = 0; i < test.size(); ++i){
        test[i]->eval(context);
    }
    if (list_for){
        list_for->eval(context);
    }
    return context.curstack;
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
    for (unsigned int i = 0; i < test.size(); ++i){
        ret += "\ntest\n" + test[i]->dump(nDepth+1);
    }
    if (comp_for){
        ret += "\ncomp_for\n" + comp_for->dump(nDepth+1);
    }
    return ret;
}

PyObjPtr& DictorsetMakerExprAST::eval(PyContext& context) {
    for (unsigned int i = 0; i < test.size(); ++i){
        test[i]->eval(context);
    }
    if (comp_for){
        comp_for->eval(context);
    }
    return context.curstack;
}

string ParametersExprAST::dump(int nDepth){
    string ret;
    for (int i = 0; i < nDepth; ++i){
        ret += "-";
    }
    ret += "parameters:fpdef,test";
    for (unsigned int i = 0; i < fpdef.size(); ++i){
        ret += "\n"+ fpdef[i]->dump(nDepth+1);
    }
    for (unsigned int i = 0; i < test.size(); ++i){
        ret += "\n" + test[i]->dump(nDepth+1);
    }

    return ret;
}

PyObjPtr& ParametersExprAST::eval(PyContext& context) {
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

PyObjPtr& FuncDefExprAST::eval(PyContext& context) {
    //!TODO

    return context.curstack;
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

PyObjPtr& ClassDefExprAST::eval(PyContext& context) {
    //!TODO

    return context.curstack;
}



PyObjPtr& ForExprASTOld::eval(PyContext& context) {
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

            for (unsigned int i = 0; i < pTuple->values.size(); ++i){
                
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
    ret += "\n" + param->dump(nDepth+1);
    return ret;
}

PyObjPtr& BinaryExprAST::eval(PyContext& context) {
    switch (optype){
        case OP_ASSIGN:{
            PyObjPtr& rval = right->eval(context);
            PyObjPtr& lval = left->eval(context);
            lval = rval;
            return lval;
        }break;
        case OP_ADD:{
            PyObjPtr& rval = right->eval(context);
            PyObjPtr& lval = left->eval(context);
            return lval->handler->handleAdd(context, lval, rval);
        }break;
        case OP_SUB:{
            PyObjPtr& rval = right->eval(context);
            PyObjPtr& lval = left->eval(context);
            return lval->handler->handleSub(context, lval, rval);
        }break;
        case OP_MUL:{
            PyObjPtr& rval = right->eval(context);
            PyObjPtr& lval = left->eval(context);
            return lval->handler->handleMul(context, lval, rval);
        }break;
        case OP_DIV:{
            PyObjPtr& rval = right->eval(context);
            PyObjPtr& lval = left->eval(context);
            return lval->handler->handleDiv(context, lval, rval);
        }break;
        case OP_MOD:{
            PyObjPtr& rval = right->eval(context);
            PyObjPtr& lval = left->eval(context);
            return lval->handler->handleMod(context, lval, rval);
        }break;
        /*
        case TOK_EQ:{
            PyObjPtr lval = left->eval(context);
            PyObjPtr rval = right->eval(context);
            //DMSG(("BinaryExprAST Op:%s begin\n", this->name.c_str()));
            //lval->dump();
            //rval->dump();
            //DMSG(("BinaryExprAST Op:%s begin\n", this->name.c_str()));
            if (lval && rval && lval->handleEQ(rval)){
                return PyObjTool::buildBool(true);
            }
            return PyObjTool::buildBool(false);
        }break;
        case TOK_AND:{
            PyObjPtr lval = left->eval(context);
            PyObjPtr rval = right->eval(context);
            //DMSG(("BinaryExprAST TOK_AND Op:%s begin\n", this->name.c_str()));
            //lval->dump();
            //rval->dump();
            //DMSG(("BinaryExprAST TOK_AND Op:%s begin\n", this->name.c_str()));
            if (PyObjTool::handleBool(lval) && PyObjTool::handleBool(rval)){
                return PyObjTool::buildBool(true);
            }
            return PyObjTool::buildBool(false);
        }break;
        case TOK_OR:{
            PyObjPtr lval = left->eval(context);
            PyObjPtr rval = right->eval(context);
            //DMSG(("BinaryExprAST TOK_OR Op:%s begin\n", this->name.c_str()));
            //lval->dump();
            //rval->dump();
            //DMSG(("BinaryExprAST TOK_OR Op:%s end\n", this->name.c_str()));
            if (PyObjTool::handleBool(lval) || PyObjTool::handleBool(rval)){
                return PyObjTool::buildBool(true);
            }
            return PyObjTool::buildBool(false);
        }break;
        case TOK_FIELD:{
            PyObjPtr lval = left->eval(context);
            //DMSG(("BinaryExprAST TOK_FIELD Op:%s %s %s begin\n", this->name.c_str(), left->name.c_str(), right->name.c_str()));
            PyObjPtr& v = right->getFieldVal(lval);
            
            return v;
        }break;*/
        default:
            return PyObjTool::buildNone();
    }
    
    return context.curstack;
}

PyObjPtr& BinaryExprAST::getFieldVal(PyObjPtr& context){
    /*
    switch (op){
        case TOK_FIELD:{
            PyObjPtr lval = left->eval(context);
            PyObjPtr& v = right->getFieldVal(lval);
            return v;
        }
        break;
        default:
            return context;
    }
    */
    return context;
}
string BinaryExprAST::dump(int nDepth){
    string ret;
    for (int i = 0; i < nDepth; ++i){
        ret += "-";
    }
    ret += left->dump(0) + this->name + right->dump(0);
    return ret;
}

PyObjPtr& AugassignAST::eval(PyContext& context){
    return  PyObjTool::buildNone();//!TODO
}
PyObjPtr& AugassignAST::getFieldVal(PyContext& context){
    /*
    PyObjPtr lval = left->eval(context);
    PyObjPtr& v = right->getFieldVal(lval);
    return v;*/
    return context.curstack;
}
string AugassignAST::dump(int nDepth){
    string ret;
    for (int i = 0; i < nDepth; ++i){
        ret += "-";
    }
    ret += left->dump(0) + this->name + right->dump(0);
    return ret;
}

PyObjPtr& TupleExprAST::eval(PyContext& context){
    PyObjTuple* tuple = new PyObjTuple();
    context.tmpcache.push_back(tuple);
    PyObjPtr& ret = context.tmpcache.back();
    for (unsigned int i = 0; i < values.size(); ++i){
        PyObjPtr v = values[i]->eval(context);
        tuple->values.push_back(v);
    }
    return ret;
}


PyObjPtr TupleExprAST::handleAssign(PyObjPtr context, PyObjPtr val)
{
    if (val->getType() != PY_TUPLE){
        throw PyException::buildException("tuple assign invalid");
    }
    
    PyObjTuple* tuple = val.cast<PyObjTuple>();

    if (this->values.size() != tuple->values.size()){
        throw PyException::buildException("tuple size not equal");
    }
    for (unsigned int i = 0; i < tuple->values.size(); ++i){
        //!TODO PyObjPtr& v =  this->values[i]->getFieldVal(context); 
        //v = tuple->values[i];
    }
    return val;
}

PyObjPtr& FunctionAST::eval(PyContext& context) {
    context.tmpcache.push_back(new PyObjFuncDef(codeImplptr));
    PyObjPtr& obj = context.tmpcache.back();
    
    PyObjPtr& v = this->codeImplptr.cast<FuncCodeImpl>()->varAstforName->getFieldVal(context);
    v = obj;
    return obj;
}

PyObjPtr FuncCodeImpl::exeCode(PyObjPtr context, list<PyObjPtr>&  tmpArgsInput) {
    /*TODO
    //DMSG(("FunctionAST::exeCode...\n"));
    list<PyObjPtr>::iterator it = tmpArgsInput.begin();
    for (unsigned int i = 0; i < argsDef.size() && it != tmpArgsInput.end(); ++i){
        argsDef[i]->handleAssign(context, *it);
        ++it;
    }

    for (unsigned int i = 0; i < body.size(); ++i){
        body[i]->eval(context);
    }
    //DMSG(("FunctionAST eval name=%s\n", proto->name.c_str()));
    */
    return context;
}

PyObjPtr& ClassAST::eval(PyContext& context){
    /*TODO
    //DMSG(("ClassAST::eval...%d\n", classFieldCode.size()));
    PyObjPtr obj = new PyObjClassDef(codeImplptr);
    PyObjPtr& v = this->codeImplptr.cast<ClassCodeImpl>()->varAstforName->getFieldVal(context);
    v = obj;
    
    for (unsigned int i = 0; i < classFieldCode.size(); ++i){
        classFieldCode[i]->eval(obj);
    }
    //obj->PyObj::dump();DMSG(("\n"));
    //DMSG(("ClassAST::eval...end\n"));
    
    return obj;*/
    return context.curstack;
}

PyObjPtr& CallExprAST::eval(PyContext& context) {
    /*
    PyObjPtr e = varFuncName->eval(context);
    if (!e){
        throw PyException::buildException("null can't be called");
        return NULL;
    }
    //DMSG(("CallExprAST eval...%s %s %d\n", varFuncName->name.c_str(), argsTuple->name.c_str(), e->getType()));
    
    vector<ExprASTPtr>& args = argsTuple.cast<TupleExprAST>()->values;
    list<PyObjPtr>    argsObj;

    for (unsigned int  i = 0; i < args.size(); ++i){
        argsObj.push_back(args[i]->eval(context));
    }
    
    PyObjPtr ret = e->handler->handleCall(e, argsObj);
    if (!ret){
        char msg[256] = {0};
        snprintf(msg, sizeof(msg), "[%d] can't be called", e->getType());
        throw PyException::buildException(msg);
        return NULL;
    }
    //DMSG(("CallExprAST dump begin..\n"));
    //e->PyObj::dump();
    //DMSG(("CallExprAST dump end..\n"));
    return ret;
    */
    return context.curstack;
}
