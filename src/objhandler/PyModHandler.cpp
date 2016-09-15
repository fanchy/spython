
#include "PyObj.h"
#include "ExprAST.h"
#include "objhandler/PyModHandler.h"

using namespace std;
using namespace ff;

string PyModHandler::handleStr(const PyObjPtr& self) const {
    char msg[128] = {0};
    snprintf(msg, sizeof(msg), "<module %s at %s>", self.cast<PyObjModule>()->moduleName.c_str(), self.cast<PyObjModule>()->path.c_str());
    return string(msg);
}
bool PyModHandler::handleBool(PyContext& context, const PyObjPtr& self) const{
    return true;
}
bool PyModHandler::handleEqual(PyContext& context, const PyObjPtr& self, const PyObjPtr& val) const{
    if (self.get() == val.get()){
        return true;
    }
    return false;
}
PyObjPtr& PyModHandler::handleCall(PyContext& context, PyObjPtr& self, std::vector<ArgTypeInfo>& allArgsVal, std::vector<PyObjPtr>& argAssignVal){
    return self.cast<PyObjFuncDef>()->exeFunc(context, self, allArgsVal, argAssignVal);
}

