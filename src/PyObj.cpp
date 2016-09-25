
#include <stdio.h>
#include <stdarg.h>

#include "PyObj.h"
#include "ExprAST.h"

using namespace std;
using namespace ff;

PyObjDict& PyObjDict::set(PyContext& context, PyObjPtr &k, PyObjPtr &v){
    PyObjDict::Key keyInfo;
    keyInfo.key = k;
    keyInfo.context = &context;
    keyInfo.hash= k->getHandler()->handleHash(context, k);
    value[keyInfo] = v;
    return *this;
}

PyObjPtr& PyObjBuiltinTool::getVar(PyContext& context, PyObjPtr& self, unsigned int nFieldIndex, ExprAST* e, const string& strType)
{
    PyObjPtr& classObj = context.allBuiltin[strType];
    if (!classObj){
        return context.cacheResult(classObj);
    }
    PyObjPtr& ret = classObj->getVar(context, classObj, e->getFieldIndex(context, classObj), e);

    if (false == IS_NULL(ret)){
        if (PyCheckFunc(ret)){
            return context.cacheResult(ret.cast<PyObjFuncDef>()->forkClassFunc(self));
        }
        return ret;
    }
    vector<PyObjPtr>& m_objStack = self->m_objStack;
    for (unsigned int i = m_objStack.size(); i <= nFieldIndex; ++i){
        m_objStack.push_back(PyObjTool::buildNULL());
    }
    
    ret = m_objStack[nFieldIndex];

    return ret;
}


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
PyObjPtr& PyObjClassInstance::assignToField(PyContext& context, PyObjPtr& self, ExprASTPtr& fieldName, PyObjPtr& v){
    unsigned int nFieldIndex = fieldName->getFieldIndex(context, self);

    for (unsigned int i = m_objStack.size(); i <= nFieldIndex; ++i){
        m_objStack.push_back(PyObjTool::buildNULL());
    }
    
    PyObjPtr& ret = m_objStack[nFieldIndex];
    ret = v;
    return ret;
}
PyObjPtr& PyObjClassInstance::getVar(PyContext& context, PyObjPtr& self, unsigned int nFieldIndex, ExprAST* e)
{
    if (nFieldIndex < m_objStack.size()) {
        PyObjPtr& ret = m_objStack[nFieldIndex];
        //DMSG(("PyObjClassInstance::getVar...%u %d, %ds", nFieldIndex, ret->getType(), ret->getHandler()->handleStr(ret).c_str()));
        if (false == IS_NULL(ret)){
            if (PyCheckFunc(ret)){
                return context.cacheResult(ret.cast<PyObjFuncDef>()->forkClassFunc(self));
            }
            return ret;
        }
    }
  
    PyObjPtr& ret = classDefPtr->getVar(context, classDefPtr, e->getFieldIndex(context, classDefPtr), e);

    if (false == IS_NULL(ret)){
        if (PyCheckFunc(ret)){
            return context.cacheResult(ret.cast<PyObjFuncDef>()->forkClassFunc(self));
        }
        return ret;
    }

    for (unsigned int i = m_objStack.size(); i <= nFieldIndex; ++i){
        m_objStack.push_back(PyObjTool::buildNULL());
    }
    
    ret = m_objStack[nFieldIndex];

    return ret;
}
void PyObjFuncDef::processParam(PyContext& context, PyObjPtr& self, std::vector<ArgTypeInfo>& allArgsVal, std::vector<PyObjPtr>& argAssignVal){
    ParametersExprAST* pParametersExprAST = parameters.cast<ParametersExprAST>();
    unsigned int hasConsumeArg = 0;
    unsigned int hasAssignArgNum = 0;
    
    if (classInstance){//!self param
        if (pParametersExprAST->allParam.empty()){
            PY_RAISE_STR(context, "too many arg num");
        }
        ParametersExprAST::ParameterInfo& paramInfo = pParametersExprAST->allParam[0];
        
        //PyObjPtr& ref = paramInfo.paramKey->eval(context);
        //ref = classInstance;
        paramInfo.paramKey->assignVal(context, classInstance);
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
                paramInfo.paramKey->assignVal(context, v);

                ++hasAssignArgNum;
            }
            else{
                PY_RAISE_STR(context, "need more arg num");
            }
            continue;
        }
        else if (allArgsVal[hasConsumeArg].argType.empty()){//!普通赋值过来的参数 f(1, 2, 3)
            paramInfo.paramKey->assignVal(context, argAssignVal[hasConsumeArg]);

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
                    PY_RAISE_STR(context, "got an unexpected keyword argument");
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
                        //PyObjPtr& ref = paramInfo.paramKey->eval(context);
                        //ref = argAssignVal[n];
                        paramInfo.paramKey->assignVal(context, argAssignVal[n]);
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
                    paramInfo.paramKey->assignVal(context, v);

                    ++hasAssignArgNum;
                }
                else{
                    PY_RAISE_STR(context, "need more arg num");
                }
            }
            break;
        }
        else{
            PY_RAISE_STR(context, "arg not assign value");
        }
    }
    
    //!处理* **的情况 
    for (; hasAssignArgNum < pParametersExprAST->allParam.size(); ++hasAssignArgNum){
        unsigned int j = hasAssignArgNum;
        ParametersExprAST::ParameterInfo& paramInfo = pParametersExprAST->allParam[j];
        
        const string& strVarName = paramInfo.paramKey.cast<VariableExprAST>()->name;
        if (paramInfo.paramType == "*"){
            PyObjPtr pVal = new PyObjTuple();
            paramInfo.paramKey->assignVal(context, pVal);

            
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
            paramInfo.paramKey->assignVal(context, pVal);

            
            for (unsigned int m = hasConsumeArg; m < allArgsVal.size(); ++m){
                ArgTypeInfo& argInfo = allArgsVal[m];
                if (argInfo.argType != "="){
                    PY_RAISE_STR(context, "given more arg");
                }
                const string& keyName = argInfo.argKey;
                PyObjPtr tmpKey = new PyObjStr(keyName);
                pVal.cast<PyObjDict>()->set(context, tmpKey, argAssignVal[m]);
            }
            continue;
        }
    }
}
PyObjPtr& PyObjFuncDef::exeFunc(PyContext& context, PyObjPtr& self, std::vector<ArgTypeInfo>& allArgsVal, std::vector<PyObjPtr>& argAssignVal){
    try
    {
        PyContextBackUp backup(context);

        if (pyCppfunc){//!this is cpp func wrap
            context.curstack = new PyCallTmpStack(this->getObjIdInfo(), NULL);
            return pyCppfunc->exeFunc(context, self, allArgsVal, argAssignVal);
        }
        else{
            context.curstack = new PyCallTmpStack(this->getObjIdInfo(), context.getFileIdModCache(this->suite->lineInfo.fileId));
        }

        processParam(context, self, allArgsVal, argAssignVal);
        
        if (suite){
            suite->eval(context);
        }
    }
    catch(ReturnSignal& s){
        return context.getCacheResult();
    }
    
    return context.cacheResult(PyObjTool::buildNone());
}
PyObjPtr PyObjClassDef::build(PyContext& context, const std::string& s, ObjIdInfo* p)
{
    PyObjPtr ret = new PyObjClassDef(s, p);
    return ret;
}
PyObjPtr PyObjClassDef::build(PyContext& context, const std::string& s, std::vector<PyObjPtr>& parentClass){
    PyObjPtr ret = PyObjClassDef::build(context, s);
    ret.cast<PyObjClassDef>()->parentClass = parentClass;
    ret.cast<PyObjClassDef>()->processInheritInfo(context, ret);
    PyCppUtil::setAttr(context, ret, "__module__", context.curstack);
    PyCppUtil::setAttr(context, ret, "__name__", PyCppUtil::genStr(s));
    return ret;
}

PyObjClassDef::PyObjClassDef(const std::string& s, ObjIdInfo* p):name(s){
    if (p){
        selfObjInfo = *p;
    }
    else{
        selfObjInfo = singleton_t<ObjIdTypeTraits<PyObjFuncDef> >::instance_ptr()->objInfo;
    }
    
    //!different function has different object id 
    selfObjInfo.nObjectId = singleton_t<ObjFieldMetaData>::instance_ptr()->allocObjId();
    this->handler = singleton_t<PyClassHandler>::instance_ptr();
    expr__class__ = singleton_t<VariableExprAllocator>::instance_ptr()->alloc("__class__").get();
}

PyObjPtr& PyObjClassDef::getVar(PyContext& context, PyObjPtr& self, unsigned int nFieldIndex, ExprAST* e) {
    if (e == expr__class__){//! return __class__
        return context.cacheResult(self);
    }
    PyObjPtr& ret = PyObj::getVar(context, self, e->getFieldIndex(context, self), e);
    return ret;
}
PyObjPtr PyObjModule::BuildModule(PyContext& context, const std::string& s, const std::string& p){
    PyObjPtr ret = new PyObjModule(s, p);
    PyCppUtil::setAttr(context, ret, "__name__", PyCppUtil::genStr(s));
    return ret;
}

void PyObjClassDef::processInheritInfo(PyContext& context, PyObjPtr& self){
    PyContextBackUp backup(context);
    context.curstack = self;

    for (unsigned int i = 0; i < parentClass.size(); ++i){
        PyObjPtr& v = parentClass[i];
        if (v->getType() != PY_CLASS_DEF)
           continue;

        std::map<std::string, PyObjPtr> fieldData = PyCppUtil::getAllFieldData(v);
        std::map<std::string, PyObjPtr>::iterator it = fieldData.begin();
        for (; it != fieldData.end(); ++it){
            ExprASTPtr expr = singleton_t<VariableExprAllocator>::instance_ptr()->alloc(it->first);
            
            //DMSG(("PyObjClassDef::processInheritInfo %s", it->first.c_str()));
            
            //PyObjPtr& ref = expr->eval(context);
            //ref = it->second;
            expr->assignVal(context, it->second);
        }
    }
}
string PyCppUtil::strFormat(const char * format, ...) {
    char msg[512];
      
    va_list vl;  
    va_start(vl, format);  
  
    vsprintf(msg, format, vl);  
    return string(msg);
}

PyObjPtr PyCppUtil::getAttr(PyContext& context, PyObjPtr& obj, const std::string& filedname){
    PyContextBackUp backup(context);
    context.curstack = obj;
    
    ExprASTPtr expr = singleton_t<VariableExprAllocator>::instance_ptr()->alloc(filedname);
    return expr->eval(context);
}
void PyCppUtil::setAttr(PyContext& context, PyObjPtr& obj, const std::string& fieldName, PyObjPtr v){
    PyContextBackUp backup(context);
    context.curstack = obj;
    
    ExprASTPtr expr = singleton_t<VariableExprAllocator>::instance_ptr()->alloc(fieldName);
    expr->assignVal(context, v);
}

std::map<std::string, PyObjPtr> PyCppUtil::getAllFieldData(PyObjPtr obj){
    std::map<std::string, PyObjPtr> ret;

    const ObjIdInfo& p = obj->getObjIdInfo();
    for (unsigned int i = 0; i < obj->m_objStack.size(); ++i) {
        if (!obj->m_objStack[i]){//!ignore __init__
            continue;
        }
        string n = singleton_t<ObjFieldMetaData>::instance_ptr()->getFieldName(p.nModuleId, p.nObjectId, i);
        ret[n]   = obj->m_objStack[i];
    }

    return ret;
}

PyObjPtr& PyCppUtil::callPyfunc(PyContext& context, PyObjPtr& func, std::vector<PyObjPtr>& argAssignVal){
    if (func && PyCheckFunc(func)){
        vector<ArgTypeInfo> allArgsVal;
        for (size_t i = 0; i < argAssignVal.size(); ++i){
            ArgTypeInfo info;
            allArgsVal.push_back(info);
        }
        return func->getHandler()->handleCall(context, func, allArgsVal, argAssignVal);
    }
    return context.cacheResult(PyObjTool::buildNone());
}

