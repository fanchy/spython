
#include "PyObj.h"
#include "ExprAST.h"

using namespace std;
using namespace ff;

PyObjPtr& PyObjFuncDef::exeFunc(PyContext& context, PyObjPtr& self, ExprASTPtr& arglist){
    DMSG(("PyObjFuncDef::exeFunc...\n"));
    try
    {
        vector<PyObjPtr> allValue;
        FuncArglist* parg = NULL;
        map<string, PyObjPtr> nameArg2Index;//!是否有具名参数 
        if (arglist){
            parg = arglist.cast<FuncArglist>();
            for (unsigned int i = 0; i < parg->allArgs.size(); ++i){
                FuncArglist::ArgInfo& argInfo = parg->allArgs[i];
                DMSG(("PyObjFuncDef::argType...%s\n", argInfo.argType.c_str()));
                if (argInfo.argType.empty()){
                    PyObjPtr v = argInfo.argVal->eval(context);
                    allValue.push_back(v);
                }
                else if (argInfo.argType == "="){
                    PyObjPtr v = argInfo.argVal->eval(context);
                    if (argInfo.argKey->getType() == EXPR_VAR)
                    {
                        nameArg2Index[argInfo.argKey.cast<VariableExprAST>()->name] = v;
                    }
                } 
            }
        }
        DMSG(("PyObjFuncDef::exeFunc...%u\n", allValue.size()));
        PyContextBackUp backup(context);
        context.curstack = self;
        
        ParametersExprAST* pParametersExprAST = parameters.cast<ParametersExprAST>();
        unsigned int hasConsumeArg = 0;
        for (unsigned j = 0; j < pParametersExprAST->allParam.size(); ++j){
            ParametersExprAST::ParameterInfo& paramInfo = pParametersExprAST->allParam[j];
            
            const string& strVarName = paramInfo.paramKey.cast<VariableExprAST>()->name;
            map<string, PyObjPtr>::iterator it = nameArg2Index.find(strVarName);
            if (it != nameArg2Index.end()){
                //!命中具名参数, 检测是否有重复赋值
                if (allValue.size() > hasConsumeArg){
                    throw PyException::buildException("got multiple values for keyword argument");
                }
                
                PyObjPtr& ref = paramInfo.paramKey->eval(context);
                ref = it->second;
                nameArg2Index.erase(it);
            }
            else{
                if (allValue.size() > hasConsumeArg){
                    //!如果这个参数是具名参数，那么要跳过
                    PyObjPtr& ref = paramInfo.paramKey->eval(context);
                    ref = allValue[hasConsumeArg];
                    ++hasConsumeArg;
                }
                else if (paramInfo.paramDefault){
                    PyObjPtr v = paramInfo.paramDefault->eval(context);
                    PyObjPtr& ref = paramInfo.paramKey->eval(context);
                    ref = v;
                }
                else{
                    throw PyException::buildException("need more arg num");
                }
            }
        }
        suite->eval(context);
    }
    catch(ReturnSignal& s){
        self->m_objStack.clear();
        return context.getCacheResult();
    }
    
    self->m_objStack.clear();
    return context.cacheResult(PyObjTool::buildNone());
}

PyObjPtr PyObjClassDef::handleCall(PyObjPtr self, list<PyObjPtr>& args){
    //DMSG(("PyObjFuncDef::handleCall...\n"));
    //DMSG(("PyObjFuncDef::handleCall2...\n"));
    //return funcASTPtr.cast<FuncCodeImpl>()->exeCode(context, args);
    PyObjPtr ret = new PyObjClassObj(self);
    return ret;
}
void PyObjClassDef::dump() {
    DMSG(("%s(class)", classASTPtr->name.c_str()));
}

PyObjPtr PyObjClassFunc::handleCall(PyObjPtr context, list<PyObjPtr>& args){
    //DMSG(("PyObjClassFunc::handleCall...\n"));
    //args.insert(args.begin(), classSelf);
    args.push_front(classSelf);
    return NULL;//funcDefPtr.cast<PyObjFuncDef>()->handleCall(context, args);
}

void PyObjClassObj::dump() {
    DMSG(("%s(classobj)", classDefPtr.cast<PyObjClassDef>()->classASTPtr->name.c_str()));
}

PyObjPtr& PyObjClassObj::getVar(PyObjPtr& self, unsigned int nFieldIndex)
{
    if (nFieldIndex < m_objStack.size()) {
        return this->PyObj::getVar(self, nFieldIndex);
    }

    for (unsigned int i = m_objStack.size(); i <= nFieldIndex; ++i){
        m_objStack.push_back(PyObjTool::buildNULL());
    }
    
    PyObjPtr& ret = m_objStack[nFieldIndex];
    ret = classDefPtr->getVar(classDefPtr, nFieldIndex);
    if (PY_FUNC_DEF == ret->getType()){
        ret = new PyObjClassFunc(self, ret);
    }
    
    return ret;
}
