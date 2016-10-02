
#include "PyObj.h"
#include "ExprAST.h"
#include "objhandler/PyClassInstanceHandler.h"

using namespace std;
using namespace ff;
PyClassInstanceHandler::PyClassInstanceHandler(){
    __init__ = singleton_t<VariableExprAllocator>::instance_ptr()->alloc("__init__");
}
string PyClassInstanceHandler::handleStr(PyContext& context, const PyObjPtr& self) const {
    string ret = this->PyCommonHandler::handleStr(context, self);
    if (!ret.empty()){
        return ret;
    }
    
    char msg[128] = {0};
    snprintf(msg, sizeof(msg), "<__main__.%s instance at %p>", self.cast<PyObjClassInstance>()->classDefPtr.cast<PyObjClassDef>()->name.c_str(), self.get());
    return string(msg);
}
bool PyClassInstanceHandler::handleBool(PyContext& context, const PyObjPtr& self) const{
    return true;
}

PyObjPtr& PyClassInstanceHandler::handleCall(PyContext& context, PyObjPtr& self, std::vector<ArgTypeInfo>& allArgsVal, std::vector<PyObjPtr>& argAssignVal){
    PyContextBackUp backup(context);
    
    PyObjPtr tmp = context.curstack;
    context.curstack = self;

    PyObjPtr __init__func = __init__->getFieldVal(context);
    context.curstack      = tmp;

    PyObjPtr ret = new PyObjClassInstance(self);

    if (__init__func && PyCheckFunc(__init__func)){
        //DMSG(("__init__func =%d", __init__func->getType()));
        vector<ArgTypeInfo>  allArgsVal2 = allArgsVal;
        ArgTypeInfo tmp;
        allArgsVal2.insert(allArgsVal2.begin(), tmp);
        argAssignVal.insert(argAssignVal.begin(), self);
        __init__func->getHandler()->handleCall(context, __init__func, allArgsVal, argAssignVal);
    }
    
    return context.cacheResult(ret);
}

