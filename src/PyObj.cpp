
#include <stdio.h>
#include <stdarg.h>

#include "PyObj.h"
#include "ExprAST.h"

using namespace std;
using namespace ff;
PyObjPtr PyObjDict::build(){
    return new PyObjDict();
}
PyObjDict::PyObjDict():version(0), versionCache(0){
    this->handler = singleton_t<PyDictHandler>::instance_ptr();
    cacheAsList = new PyObjList();
}
PyObjDict& PyObjDict::set(PyContext& context, PyObjPtr &k, PyObjPtr &v){
    PyObjDict::Key keyInfo;
    keyInfo.key = k;
    keyInfo.context = &context;
    keyInfo.hash= k->getHandler()->handleHash(context, k);
    //pair<DictMap::iterator, bool> > ret = value.insert(make_pair(keyInfo, v));

    value[keyInfo] = v;
    ++version;
    return *this;
}
PyObjPtr PyObjDict::get(PyContext& context, const PyObjPtr &k){
    PyObjDict::Key keyInfo;
    keyInfo.key = k;
    keyInfo.context = &context;
    keyInfo.hash= k->getHandler()->handleHash(context, k);
    
    DictMap::iterator it = value.find(keyInfo);
    if (it != value.end()){
        return it->second;
    }
    return NULL;
}
bool PyObjDict::delByKey(PyContext& context, PyObjPtr &k){
    PyObjDict::Key keyInfo;
    keyInfo.key = k;
    keyInfo.context = &context;
    keyInfo.hash= k->getHandler()->handleHash(context, k);
    
    DictMap::iterator it = value.find(keyInfo);
    if (it != value.end()){
        value.erase(it);
        return true;
    }
    return false;
}
PyObjPtr PyObjDict::pop(PyContext& context, const PyObjPtr &k){
    PyObjDict::Key keyInfo;
    keyInfo.key = k;
    keyInfo.context = &context;
    keyInfo.hash= k->getHandler()->handleHash(context, k);
    
    DictMap::iterator it = value.find(keyInfo);
    if (it != value.end()){
        PyObjPtr ret = DICT_ITER_VAL(it);
        value.erase(it);
        ++version;
        return ret;
    }
    return NULL;
}
PyObjPtr PyObjDict::getValueAsList(){//!return all dict key and value as [(key, value), ....]
    if (versionCache != version){
        cacheAsList.cast<PyObjList>()->clear();
        DictMap::iterator it = value.begin();
        for (; it != value.end(); ++it){
            PyObjPtr t = new PyObjTuple();
            t.cast<PyObjTuple>()->append(DICT_ITER_KEY(it)).append(DICT_ITER_VAL(it));
            cacheAsList.cast<PyObjList>()->append(t);
        }
        versionCache = version;
    }
    return cacheAsList;
}
void PyObjDict::clear(){
    value.clear();
    ++version;
}
PyObjPtr PyObjDict::copy(){
    PyObjPtr ret = new PyObjDict();
    ret.cast<PyObjDict>()->value = value;
    ret.cast<PyObjDict>()->version++;
    return ret;
}

PyObjPtr PyObjDict::keys(){
    PyObjPtr ret = new PyObjList();
    DictMap::iterator it = value.begin();
    for (; it != value.end(); ++it){
        ret.cast<PyObjList>()->append(DICT_ITER_KEY(it));
    }
    return ret;
}
size_t PyObjDict::size(){
    return value.size();
}
PyObjPtr PyObjDict::popitem(){
    if (value.empty()){
        return NULL;
    }
    PyObjPtr ret = new PyObjTuple();
    DictMap::iterator it = value.begin();
    ret.cast<PyObjTuple>()->append(DICT_ITER_KEY(it));
    ret.cast<PyObjTuple>()->append(DICT_ITER_VAL(it));
    value.erase(it);
    ++version;
    return ret;
}

PyObjPtr PyObjDict::setdefault(PyContext& context, PyObjPtr &k, PyObjPtr &v){
    PyObjDict::Key keyInfo;
    keyInfo.key = k;
    keyInfo.context = &context;
    keyInfo.hash= k->getHandler()->handleHash(context, k);
    //pair<DictMap::iterator, bool> > ret = value.insert(make_pair(keyInfo, v));
    DictMap::iterator it = value.find(keyInfo);
    if (it != value.end()){
        return DICT_ITER_VAL(it);
    }
    it->second = v;
    ++version;
    return v;
}
void PyObjDict::update(PyContext& context, PyObjPtr& v){
    PyAssertDict(v);
    
    DictMap::iterator it = v.cast<PyObjDict>()->value.begin();
    for (; it != v.cast<PyObjDict>()->value.end(); ++it){
        value[it->first] = it->second;
    }
    ++version;
}

PyObjPtr& PyObjBuiltinTool::getVar(PyContext& context, PyObjPtr& self, ExprAST* e, const string& strType)
{
    PyObjPtr& classObj = context.getBuiltin(strType);
    if (!classObj){
        return context.cacheResult(classObj);
    }
    PyObjPtr& ret = classObj->getVar(context, classObj, e);

    if (false == IS_NULL(ret)){
        if (PyCheckFunc(ret)){
            return context.cacheResult(ret.cast<PyObjFuncDef>()->forkClassFunc(self));
        }
        return ret;
    }
    unsigned int nFieldIndex = e->getFieldIndex(context, self);
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
PyObjPtr& PyObjFuncDef::getClosureStack(){
    if (hasCopyClosure || !closureStack){
        return closureStack;
    }
    closureStack = closureStack.cast<PyCallTmpStack>()->copy();
    hasCopyClosure = true;
    return closureStack;
}
PyObjPtr PyCallTmpStack::copy(){
    PyObjPtr ret = new PyCallTmpStack(selfObjInfo, modBelong, closureStack);
    ret->m_objStack = this->m_objStack;
    ret.cast<PyCallTmpStack>()->globalVar  = this->globalVar;
    return ret;
}
PyObjPtr& PyCallTmpStack::getVar(PyContext& context, PyObjPtr& self, ExprAST* e){
    PyObjPtr& ret = PyObj::getVar(context, self, e);
    if (!ret && closureStack){
        return closureStack->getVar(context, closureStack, e);
    }
    return ret;
}
bool PyCallTmpStack::isGlobalVar(ExprAST* e){
    return globalVar.empty() == false && globalVar.find(e) != globalVar.end();
}
void PyCallTmpStack::addGlobalVar(ExprAST* e){
    globalVar.insert(e);
}
PyObjPtr& PyObjClassInstance::assignToField(PyContext& context, PyObjPtr& self, ExprASTPtr& fieldName, PyObjPtr& v){
    unsigned int nFieldIndex = fieldName->getFieldIndex(context, self);

    for (unsigned int i = m_objStack.size(); i <= nFieldIndex; ++i){
        m_objStack.push_back(PyObjTool::buildNULL());
    }
    
    PyObjPtr& ret = m_objStack[nFieldIndex];
    
    if (!ret){ //!property check
        PyObjPtr& ret2 = classDefPtr->getVar(context, classDefPtr, fieldName.get());
        if (ret2 && IS_PROPERTY_OBJ(context, ret2) && PyCheckInstance(self)){//!special for property getter
            PyObjPtr func = PyCppUtil::getAttr(context, ret2, "fset");
            if (PyCheckFunc(func)){
                PyObjPtr classFunc = func.cast<PyObjFuncDef>()->forkClassFunc(self);
                vector<PyObjPtr> allValue;
                allValue.push_back(v);
                PyCppUtil::callPyfunc(context, classFunc, allValue);
                return v;
            }
            return context.cacheResult(PyObjTool::buildNULL());
        }
    }

    ret = v;
    return ret;
}
PyObjPtr& PyObjClassInstance::getVar(PyContext& context, PyObjPtr& self, ExprAST* e)
{
    unsigned int nFieldIndex = e->getFieldIndex(context, self);
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
  
    PyObjPtr& ret = classDefPtr->getVar(context, classDefPtr, e);

    if (false == IS_NULL(ret)){
        if (PyCheckFunc(ret)){
            return context.cacheResult(ret.cast<PyObjFuncDef>()->forkClassFunc(self));
        }
        else if (IS_PROPERTY_OBJ(context, ret)){//!special for property getter
            PyObjPtr func = PyCppUtil::getAttr(context, ret, "fget");
            if (PyCheckFunc(func)){
                PyObjPtr classFunc = func.cast<PyObjFuncDef>()->forkClassFunc(self);
                vector<PyObjPtr> allValue;
                PyObjPtr getterRet = PyCppUtil::callPyfunc(context, classFunc, allValue);
                return context.cacheResult(getterRet);
            }
            return context.cacheResult(PyObjTool::buildNULL());
        }
        return ret;
    }

    for (unsigned int i = m_objStack.size(); i <= nFieldIndex; ++i){
        m_objStack.push_back(PyObjTool::buildNULL());
    }
    
    ret = m_objStack[nFieldIndex];

    return ret;
}
void PyObjClassInstance::delField(PyContext& context, PyObjPtr& self, ExprASTPtr& fieldName){
    unsigned int nFieldIndex = fieldName->getFieldIndex(context, self);

    if (nFieldIndex < m_objStack.size()){
        m_objStack[nFieldIndex] = NULL;
    }
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
    
    for (; hasAssignArgNum < pParametersExprAST->allParam.size(); ){
        unsigned int j = hasAssignArgNum;
        ParametersExprAST::ParameterInfo& paramInfo = pParametersExprAST->allParam[j];
        
        //const string& strVarName = paramInfo.paramKey.cast<VariableExprAST>()->name;
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
        
        //const string& strVarName = paramInfo.paramKey.cast<VariableExprAST>()->name;
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
            context.curstack = new PyCallTmpStack(this->getObjIdInfo(), NULL, getClosureStack());
            return pyCppfunc->exeFunc(context, self, allArgsVal, argAssignVal);
        }
        else{
            context.curstack = new PyCallTmpStack(this->getObjIdInfo(), context.getFileIdModCache(this->suite->lineInfo.fileId), getClosureStack());
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
        selfObjInfo = singleton_t<ObjIdTypeTraits<PyObjClassDef> >::instance_ptr()->objInfo;
        //!different function has different object id 
        selfObjInfo.nObjectId = singleton_t<ObjFieldMetaData>::instance_ptr()->allocObjId();
    }
    
    this->handler = singleton_t<PyClassHandler>::instance_ptr();
    expr__class__ = singleton_t<VariableExprAllocator>::instance_ptr()->alloc("__class__").get();
}

PyObjPtr& PyObjClassDef::getVar(PyContext& context, PyObjPtr& self, ExprAST* e) {
    if (e == expr__class__){//! return __class__
        return context.cacheResult(self);
    }
    PyObjPtr& ret = PyObj::getVar(context, self, e);
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

bool PyCppUtil::hasAttr(PyContext& context, PyObjPtr& obj, const std::string& filedname){
    PyContextBackUp backup(context);
    context.curstack = obj;
    
    ExprASTPtr expr = singleton_t<VariableExprAllocator>::instance_ptr()->alloc(filedname);
    PyObjPtr   ret  = expr->getFieldVal(context);
    if (ret){
        return true;
    }
    return false;
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
    if (func && PyCheckCallable(func)){
        vector<ArgTypeInfo> allArgsVal;
        for (size_t i = 0; i < argAssignVal.size(); ++i){
            ArgTypeInfo info;
            allArgsVal.push_back(info);
        }
        return func->getHandler()->handleCall(context, func, allArgsVal, argAssignVal);
    }
    return context.cacheResult(PyObjTool::buildNone());
}
PyObjPtr PyCppUtil::getArgVal(std::vector<ArgTypeInfo>& allArgsVal, std::vector<PyObjPtr>& argAssignVal, 
                                size_t index, const std::string& argName){
    for (size_t i = 0; i < allArgsVal.size() && i < argAssignVal.size(); ++i){
        if (allArgsVal[i].argKey == argName){
            return argAssignVal[i];
        }
    }
    
    if (index < argAssignVal.size()){
        return argAssignVal[index];
    }
    return NULL;
}

IterUtil::IterUtil(PyContext& c, PyObjPtr v):context(c), obj(v), index(0){
    if (PyCheckInstance(obj) && PyCppUtil::hasAttr(context, obj, "next")){
        funcNext = PyCppUtil::getAttr(context, obj, "next");
    }
}
PyObjPtr IterUtil::next(){
    if (PyCheckTuple(obj)){
        if ((size_t)index >= obj.cast<PyObjTuple>()->value.size()){
            return NULL;
        }
        return obj.cast<PyObjTuple>()->value[index++];
    }
    else if (PyCheckList(obj)){
        if ((size_t)index >= obj.cast<PyObjList>()->value.size()){
            return NULL;
        }
        return obj.cast<PyObjList>()->value[index++];
    }
    else if (PyCheckDict(obj)){
        PyObjPtr listCache = obj.cast<PyObjDict>()->getValueAsList();
        PyAssertList(listCache);
        
        if ((size_t)index >= listCache.cast<PyObjList>()->size()){
            return NULL;
        }
        PyObjPtr ret = listCache.cast<PyObjList>()->value[index++];
        PyAssertTuple(ret);
        if (ret.cast<PyObjTuple>()->value.size() == 2){
            return ret.cast<PyObjTuple>()->value[0];
        }
        return NULL;
    }
    else if (funcNext){//!使用迭代器 
        try{
            PyObjPtr ret = PyCppUtil::callPyfunc(context, funcNext, funcagsTmp);
            return ret;
        }
        catch(PyExceptionSignal& e){
            return NULL;
        }
    }
    return NULL;
}

