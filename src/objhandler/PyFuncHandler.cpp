
#include "PyObj.h"
#include "ExprAST.h"
#include "objhandler/PyFuncHandler.h"

using namespace std;
using namespace ff;

string PyFuncHandler::handleStr(const PyObjPtr& self) const {
    char msg[128] = {0};
    snprintf(msg, sizeof(msg), "<function %s at 0x%p>", self.cast<PyObjFuncDef>()->name.c_str(), self.get());
    return string(msg);
}
bool PyFuncHandler::handleBool(PyContext& context, const PyObjPtr& self) const{
    return true;
}
bool PyFuncHandler::handleEqual(PyContext& context, const PyObjPtr& self, const PyObjPtr& val) const{
    if (val->getType() == EXPR_FUNCDEF && self.get() == val.get()){
        return true;
    }
    return false;
}
PyObjPtr& PyFuncHandler::handleCall(PyContext& context, PyObjPtr& self, std::vector<ArgTypeInfo>& allArgsVal, std::vector<PyObjPtr>& argAssignVal){
    return self.cast<PyObjFuncDef>()->exeFunc(context, self, allArgsVal, argAssignVal);
}

