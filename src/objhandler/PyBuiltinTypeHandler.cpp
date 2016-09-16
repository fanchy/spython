
#include "PyObj.h"
#include "ExprAST.h"
#include "objhandler/PyBuiltinTypeHandler.h"

using namespace std;
using namespace ff;

string PyBuiltinTypeHandler::handleStr(const PyObjPtr& self) const {
    char msg[128] = {0};
    snprintf(msg, sizeof(msg), "<type '%d'>", self.cast<PyBuiltinTypeInfo>()->nType);
    return string(msg);
}
bool PyBuiltinTypeHandler::handleBool(PyContext& context, const PyObjPtr& self) const{
    return true;
}
bool PyBuiltinTypeHandler::handleEqual(PyContext& context, const PyObjPtr& self, const PyObjPtr& val) const{
    if (self.get() == val.get()){
        return true;
    }
    return false;
}
PyObjPtr& PyBuiltinTypeHandler::handleCall(PyContext& context, PyObjPtr& self, std::vector<ArgTypeInfo>& allArgsVal, std::vector<PyObjPtr>& argAssignVal){
    //return self.cast<PyObjFuncDef>()->exeFunc(context, self, allArgsVal, argAssignVal);
    return context.cacheResult(PyObjTool::buildNone());
}
bool PyBuiltinTypeHandler::handleIsInstance(PyContext& context, PyObjPtr& self, PyObjPtr& val){
    if (val->getType() == self.cast<PyBuiltinTypeInfo>()->nType){
        return true;
    }
    return false;
}

