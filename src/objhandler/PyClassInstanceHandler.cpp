
#include "PyObj.h"
#include "ExprAST.h"
#include "objhandler/PyClassInstanceHandler.h"

using namespace std;
using namespace ff;
PyClassInstanceHandler::PyClassInstanceHandler(){
    __init__ = singleton_t<VariableExprAllocator>::instance_ptr()->alloc("__init__");
}
string PyClassInstanceHandler::handleStr(const PyObjPtr& self) const {
    char msg[128] = {0};
    snprintf(msg, sizeof(msg), "<__main__.%s instance at %p>", self.cast<PyObjClassInstance>()->classDefPtr.cast<PyObjClassDef>()->name.c_str(), self.get());
    return string(msg);
}
bool PyClassInstanceHandler::handleBool(PyContext& context, const PyObjPtr& self) const{
    return true;
}
bool PyClassInstanceHandler::handleEqual(PyContext& context, const PyObjPtr& self, const PyObjPtr& val) const{
    if (val->getType() == EXPR_CLASSDEF && self.get() == val.get()){
        return true;
    }
    return false;
}
PyObjPtr& PyClassInstanceHandler::handleCall(PyContext& context, PyObjPtr& self, std::vector<ArgTypeInfo>& allArgsVal, std::vector<PyObjPtr>& argAssignVal){
    PyContextBackUp backup(context);
    
    PyObjPtr tmp = context.curstack;
    context.curstack = self;

    PyObjPtr __init__func = __init__->getFieldVal(context);
    context.curstack      = tmp;

    PyObjPtr ret = new PyObjClassInstance(self);

    if (__init__func && __init__func->getType() == PY_FUNC_DEF){
        //DMSG(("__init__func =%d", __init__func->getType()));
        __init__func->getHandler()->handleCall(context, __init__func, allArgsVal, argAssignVal);
    }
    
    return context.cacheResult(ret);
}

