
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
    snprintf(msg, sizeof(msg), "%f(float)", Val);
    this->name = msg;
    obj = new PyObjFloat(Val);
}

PyObjPtr StmtAST::eval(PyObjPtr context){
    PyObjPtr ret;
    for (unsigned int i = 0; i < exprs.size(); ++i){
        ret = exprs[i]->eval(context);
    }
    return ret;
}

StrExprAST::StrExprAST(const string& v) : val(v) {
    this->name = v;
    this->name += "(str)";
    obj = new PyObjStr(val);
}

PyObjPtr IfExprAST::eval(PyObjPtr context) {
    for (unsigned int i = 0; i < conditions.size(); ++i){
        PyObjPtr caseBool = conditions[i]->eval(context);
        if (PyObjTool::handleBool(caseBool)){
            vector<ExprASTPtr>& bodys = ifbody[i];
            for (unsigned int m = 0; m < bodys.size(); ++m){
                bodys[m]->eval(context);
            }
            return context;
        }
    }
    return context;
}

PyObjPtr ForExprAST::eval(PyObjPtr context) {
    PyObjPtr iterObj = iterFunc->eval(context);
    if (!iterObj)
    {
        return context;
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
                
                this->iterTuple->handleAssign(context, pTuple->values[i]);
                
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
            return context;
        }
        break;
        default:
            break;
    }

    for (unsigned int i = 0; i < forBody.size(); ++i){
        forBody[i]->eval(context);
    }
    return context;
}

PyObjPtr BinaryExprAST::eval(PyObjPtr context) {
    switch (op){
        case TOK_ASSIGN:{
            //DMSG()("TOK_ASSIGN Op:%s %s %s begin\n", this->name.c_str(), LHS->name.c_str(), RHS->name.c_str());

            if (LHS->getType() == EXPR_INT || LHS->getType() == EXPR_STR){
                throw PyException::buildException("can not assign to const value");
            }
            PyObjPtr rval = RHS->eval(context);
            
            if (LHS->getType() == EXPR_TUPLE)
            {
                PyObjPtr ret = LHS.cast<TupleExprAST>()->handleAssign(context, rval);
                return ret;
            }
            PyObjPtr& v = LHS->getFieldVal(context);
            v = rval;
            return rval;
        }break;
        case TOK_EQ:{
            PyObjPtr lval = LHS->eval(context);
            PyObjPtr rval = RHS->eval(context);
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
            PyObjPtr lval = LHS->eval(context);
            PyObjPtr rval = RHS->eval(context);
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
            PyObjPtr lval = LHS->eval(context);
            PyObjPtr rval = RHS->eval(context);
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
            PyObjPtr lval = LHS->eval(context);
            //DMSG(("BinaryExprAST TOK_FIELD Op:%s %s %s begin\n", this->name.c_str(), LHS->name.c_str(), RHS->name.c_str()));
            PyObjPtr& v = RHS->getFieldVal(lval);
            
            return v;
        }break;
        default:
            return context;
    }
    return context;
}

PyObjPtr& BinaryExprAST::getFieldVal(PyObjPtr& context){
    switch (op){
        case TOK_FIELD:{
            PyObjPtr lval = LHS->eval(context);
            PyObjPtr& v = RHS->getFieldVal(lval);
            return v;
        }
        break;
        default:
            return context;
    }
    return context;
}

PyObjPtr TupleExprAST::eval(PyObjPtr context){
    PyObjTuple* tuple = new PyObjTuple();
    PyObjPtr ret = tuple;
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
        PyObjPtr& v =  this->values[i]->getFieldVal(context); 
        v = tuple->values[i];
    }
    return val;
}

PyObjPtr FunctionAST::eval(PyObjPtr context) {
    PyObjPtr obj = new PyObjFuncDef(codeImplptr);
    PyObjPtr& v = this->codeImplptr.cast<FuncCodeImpl>()->varAstforName->getFieldVal(context);
    v = obj;
    return obj;
}

PyObjPtr FuncCodeImpl::exeCode(PyObjPtr context, list<PyObjPtr>&  tmpArgsInput) {
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
    return context;
}

PyObjPtr ClassAST::eval(PyObjPtr context){
    //DMSG(("ClassAST::eval...%d\n", classFieldCode.size()));
    PyObjPtr obj = new PyObjClassDef(codeImplptr);
    PyObjPtr& v = this->codeImplptr.cast<ClassCodeImpl>()->varAstforName->getFieldVal(context);
    v = obj;
    
    for (unsigned int i = 0; i < classFieldCode.size(); ++i){
        classFieldCode[i]->eval(obj);
    }
    //obj->PyObj::dump();DMSG(("\n"));
    //DMSG(("ClassAST::eval...end\n"));
    return obj;
}

PyObjPtr CallExprAST::eval(PyObjPtr context) {
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
    
    PyObjPtr ret = e->handleCall(e, argsObj);
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
}
