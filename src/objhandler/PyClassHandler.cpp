
#include "PyObj.h"
#include "ExprAST.h"
#include "objhandler/PyClassHandler.h"

using namespace std;
using namespace ff;
PyClassHandler::PyClassHandler(){
    __init__ = singleton_t<VariableExprAllocator>::instance_ptr()->alloc("__init__");
}
string PyClassHandler::handleStr(PyContext& context, const PyObjPtr& self) const {
    string ret;
    char msg[128] = {0};
    snprintf(msg, sizeof(msg), "%s.%s", 
                               self.cast<PyObjClassDef>()->getModName(context).c_str(), 
                               self.cast<PyObjClassDef>()->name.c_str());
    ret = msg;
    return ret;
}
bool PyClassHandler::handleBool(PyContext& context, const PyObjPtr& self) const{
    return true;
}
bool PyClassHandler::handleEqual(PyContext& context, const PyObjPtr& self, const PyObjPtr& val) const{
    if (val->getType() == PY_CLASS_DEF && self.get() == val.get()){
        return true;
    }
    return false;
}
PyObjPtr& PyClassHandler::handleCall(PyContext& context, PyObjPtr& self, std::vector<ArgTypeInfo>& allArgsVal, std::vector<PyObjPtr>& argAssignVal){
    PyContextBackUp backup(context);
    context.curstack = self;

    PyObjPtr __init__func = __init__->getFieldVal(context);
    backup.rollback();

    PyObjPtr ret = new PyObjClassInstance(self);

    if (__init__func && PyCheckFunc(__init__func)){
        std::vector<ArgTypeInfo> allArgsVal2 = allArgsVal;
        ArgTypeInfo tmp;
        allArgsVal2.push_back(tmp);
        argAssignVal.insert(argAssignVal.begin(), ret);
        __init__func->getHandler()->handleCall(context, __init__func, allArgsVal2, argAssignVal);
    }
    
    return context.cacheResult(ret);
}
bool PyClassHandler::handleIsInstance(PyContext& context, PyObjPtr& self, PyObjPtr& val){
    if (val->getType() == PY_CLASS_INST){
        PyObjPtr& classDef = val.cast<PyObjClassInstance>()->classDefPtr;
        if (classDef.get() == self.get()){
            return true;
        }
        vector<PyObjPtr>& allParentDef = classDef.cast<PyObjClassDef>()->parentClass;
        for (size_t i = 0; i < allParentDef.size(); ++i){
            if (allParentDef[i].get() == self.get()){
                return true;
            }
        }
    }
    else{
        PyContextBackUp backup(context);
        context.curstack = val;
        
        ExprASTPtr expr = singleton_t<VariableExprAllocator>::instance_ptr()->alloc("__class__");
        PyObjPtr classDef = expr->eval(context);
        if (classDef.get() == self.get()){
            return true;
        }
        
    }
    return false;
}


