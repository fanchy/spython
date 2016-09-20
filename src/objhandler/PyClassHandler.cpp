
#include "PyObj.h"
#include "ExprAST.h"
#include "objhandler/PyClassHandler.h"

using namespace std;
using namespace ff;
PyClassHandler::PyClassHandler(){
    __init__ = singleton_t<VariableExprAllocator>::instance_ptr()->alloc("__init__");
}
string PyClassHandler::handleStr(const PyObjPtr& self) const {
    char msg[128] = {0};
    snprintf(msg, sizeof(msg), "__main__.%s", self.cast<PyObjClassDef>()->name.c_str());
    return string(msg);
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
    
    PyObjPtr tmp = context.curstack;
    context.curstack = self;

    PyObjPtr __init__func = __init__->getFieldVal(context);
    context.curstack      = tmp;

    PyObjPtr ret = new PyObjClassInstance(self);

    if (__init__func && __init__func->getType() == PY_FUNC_DEF){
        //DMSG(("__init__func =%d", __init__func->getType()));
        __init__func->handler->handleCall(context, __init__func, allArgsVal, argAssignVal);
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


