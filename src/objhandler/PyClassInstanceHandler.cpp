
#include "PyObj.h"
#include "ExprAST.h"
#include "objhandler/PyClassInstanceHandler.h"

using namespace std;
using namespace ff;
PyClassInstanceHandler::PyClassInstanceHandler(){
    __call__ = singleton_t<VariableExprAllocator>::instance_ptr()->alloc("__call__");
}
string PyClassInstanceHandler::handleStr(PyContext& context, const PyObjPtr& self) const {
    string ret = this->PyCommonHandler::handleStr(context, self);
    if (!ret.empty()){
        return ret;
    }
    
    char msg[128] = {0};
    snprintf(msg, sizeof(msg), "<%s.%s instance at %p>", 
                               self.cast<PyObjClassInstance>()->classDefPtr.cast<PyObjClassDef>()->getModName(context).c_str(), 
                               self.cast<PyObjClassInstance>()->classDefPtr.cast<PyObjClassDef>()->name.c_str(), 
                               self.get());
    return string(msg);
}
bool PyClassInstanceHandler::handleBool(PyContext& context, const PyObjPtr& self) const{
    return true;
}

PyObjPtr& PyClassInstanceHandler::handleCall(PyContext& context, PyObjPtr& self, std::vector<ArgTypeInfo>& allArgsVal, std::vector<PyObjPtr>& argAssignVal){
    PyContextBackUp backup(context);
    
    PyObjPtr tmp = context.curstack;
    context.curstack = self;

    PyObjPtr obj__call__ = __call__->getFieldVal(context);
    context.curstack      = tmp;

    PyObjPtr ret = PyCppUtil::callPyfunc(context, obj__call__, argAssignVal);
    return context.cacheResult(ret);
}

