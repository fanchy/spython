
#include "PyObj.h"
#include "ExprAST.h"

using namespace std;
using namespace ff;

bool PyObjFuncDef::hasSelfParam(){
    ParametersExprAST* pParametersExprAST = parameters.cast<ParametersExprAST>();
    if (pParametersExprAST->allParam.empty() == false){
        ParametersExprAST::ParameterInfo& paramInfo = pParametersExprAST->allParam[0];
        if (paramInfo.paramKey->getType() == EXPR_VAR && paramInfo.paramKey.cast<VariableExprAST>()->name == "self"){
            return true;
        }
    }
    return false;
}

PyObjPtr& PyObjClassInstance::getVar(PyContext& context, PyObjPtr& self, unsigned int nFieldIndex)
{
    PyObjPtr& ret = classDefPtr->getVar(context, classDefPtr, nFieldIndex);

    if (false == IS_NULL(ret)){
        if (ret->getType() == EXPR_FUNCDEF && ret.cast<PyObjFuncDef>()->hasSelfParam()){
            return context.cacheResult(ret.cast<PyObjFuncDef>()->forkClassFunc(self));
        }
        return ret;
    }

    if (nFieldIndex < m_objStack.size()) {
        ret = this->PyObj::getVar(context, self, nFieldIndex);
    }

    for (unsigned int i = m_objStack.size(); i <= nFieldIndex; ++i){
        m_objStack.push_back(PyObjTool::buildNULL());
    }
    
    ret = m_objStack[nFieldIndex];

    return ret;
}

PyObjPtr& PyObjFuncDef::exeFunc(PyContext& context, PyObjPtr& self, std::vector<ArgTypeInfo>& allArgsVal, std::vector<PyObjPtr>& argAssignVal){
    //DMSG(("PyObjFuncDef::exeFunc...\n"));
    try
    {
        //DMSG(("PyObjFuncDef::exeFunc...%u\n", allArgsVal.size()));
        PyContextBackUp backup(context);
        context.curstack = new PyCallTmpStack(this->getObjIdInfo());

        ParametersExprAST* pParametersExprAST = parameters.cast<ParametersExprAST>();
        unsigned int hasConsumeArg = 0;
        unsigned int hasAssignArgNum = 0;
        
        if (classInstance){//!self param
            if (pParametersExprAST->allParam.empty()){
                throw PyException::buildException("too many arg num");
            }
            ParametersExprAST::ParameterInfo& paramInfo = pParametersExprAST->allParam[0];
            
            PyObjPtr& ref = paramInfo.paramKey->eval(context);
            ref = classInstance;
            ++hasAssignArgNum;
        }
        
        for (; hasAssignArgNum < pParametersExprAST->allParam.size(); ++hasAssignArgNum){
            unsigned int j = hasAssignArgNum;
            ParametersExprAST::ParameterInfo& paramInfo = pParametersExprAST->allParam[j];
            
            const string& strVarName = paramInfo.paramKey.cast<VariableExprAST>()->name;
            if (paramInfo.paramType.empty() == false){ //!非普通参数, *a, **b  在后边统一处理 
                break;
            }
            else if (allArgsVal.size() <= hasConsumeArg){
                if (paramInfo.paramDefault){
                    PyObjPtr v = paramInfo.paramDefault->eval(context);
                    PyObjPtr& ref = paramInfo.paramKey->eval(context);
                    ref = v;
                    ++hasAssignArgNum;
                }
                else{
                    throw PyException::buildException("need more arg num");
                }
                continue;
            }
            else if (allArgsVal[hasConsumeArg].argType.empty()){//!普通赋值过来的参数 f(1, 2, 3)
                PyObjPtr& ref = paramInfo.paramKey->eval(context);
                ref = argAssignVal[hasConsumeArg];
                ++hasConsumeArg;
                ++hasAssignArgNum;
            }
            else if (allArgsVal[hasConsumeArg].argType == "="){//!具名参数  f(a=1, b=2, c=3)
                //!如果这个参数是具名参数，后边的全部都是具名参数了
                unsigned int fromIndex = hasConsumeArg;
                //!先检查一遍，如果有具名参数，没有定义报个错
                for (unsigned int n = fromIndex; n < allArgsVal.size(); ++n){
                    ArgTypeInfo& argInfo = allArgsVal[n];
                    if (argInfo.argType == "="){
                        bool bFind = false;
                        for (unsigned int m = j; m < pParametersExprAST->allParam.size(); ++m){
                            const string& strArgName = pParametersExprAST->allParam[m].paramKey.cast<VariableExprAST>()->name;
                            if (strArgName == argInfo.argKey){
                                bFind = true;
                                break;
                            }
                        }
                        if (bFind){
                            continue;
                        }
                        throw PyException::buildException("got an unexpected keyword argument");
                        break;
                    }
                }
                
                for (unsigned int m = j; m < pParametersExprAST->allParam.size(); ++m){
                    paramInfo = pParametersExprAST->allParam[m];
                    if (paramInfo.paramType.empty() == false){ //!非普通参数, *a, **b  在后边统一处理 
                        break;
                    }
                    const string& strArgName = paramInfo.paramKey.cast<VariableExprAST>()->name;
                    
                    bool hitFlag = false;
                    for (unsigned int n = fromIndex; n < allArgsVal.size(); ++n){
                        ArgTypeInfo& argInfo = allArgsVal[n];
                        if (argInfo.argKey == strArgName){//!hit
                            PyObjPtr& ref = paramInfo.paramKey->eval(context);
                            ref = argAssignVal[n];
                            hitFlag = true;
                            ++hasAssignArgNum;
                            break;
                        }
                    }
                    if (hitFlag){
                        continue;
                    }
                    else if(paramInfo.paramDefault){//!如果有默认值 
                        PyObjPtr v = paramInfo.paramDefault->eval(context);
                        PyObjPtr& ref = paramInfo.paramKey->eval(context);
                        ref = v;
                        ++hasAssignArgNum;
                    }
                    else{
                        throw PyException::buildException("need more arg num");
                    }
                }
                break;
            }
            else{
                throw PyException::buildException("arg not assign value");
            }
        }
        
        //!处理* **的情况 
        for (; hasAssignArgNum < pParametersExprAST->allParam.size(); ++hasAssignArgNum){
            unsigned int j = hasAssignArgNum;
            ParametersExprAST::ParameterInfo& paramInfo = pParametersExprAST->allParam[j];
            
            const string& strVarName = paramInfo.paramKey.cast<VariableExprAST>()->name;
            if (paramInfo.paramType == "*"){
                PyObjPtr pVal = new PyObjTuple();
                PyObjPtr& ref = paramInfo.paramKey->eval(context);
                ref = pVal;
                
                for (unsigned int m = hasConsumeArg; m < allArgsVal.size(); ++m){
                    ArgTypeInfo& argInfo = allArgsVal[m];
                    if (argInfo.argType == "=" || argInfo.argType == "**"){
                        break;
                    }
                    pVal.cast<PyObjTuple>()->value.push_back(argAssignVal[m]);
                }
                continue;
            }
            else if (paramInfo.paramType == "**"){
                PyObjPtr pVal = new PyObjDict();
                PyObjPtr& ref = paramInfo.paramKey->eval(context);
                ref = pVal;
                
                for (unsigned int m = hasConsumeArg; m < allArgsVal.size(); ++m){
                    ArgTypeInfo& argInfo = allArgsVal[m];
                    if (argInfo.argType != "="){
                        throw PyException::buildException("given more arg");
                    }
                    const string& keyName = argInfo.argKey;
                    PyObjPtr tmpKey = new PyObjStr(keyName);
                    pVal.cast<PyObjDict>()->value[tmpKey] = argAssignVal[m];
                }
                continue;
            }
        }
        suite->eval(context);
    }
    catch(ReturnSignal& s){
        return context.getCacheResult();
    }
    
    return context.cacheResult(PyObjTool::buildNone());
}

