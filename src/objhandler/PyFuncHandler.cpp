
#include "PyObj.h"
#include "ExprAST.h"
#include "objhandler/PyFuncHandler.h"

using namespace std;
using namespace ff;

string PyFuncHandler::handleStr(PyObjPtr& self) {
    char msg[128] = {0};
    snprintf(msg, sizeof(msg), "<function %s at 0x%p>", self.cast<PyObjFuncDef>()->name.c_str(), self.get());
    return string(msg);
}
bool PyFuncHandler::handleBool(PyContext& context, PyObjPtr& self){
    return true;
}
bool PyFuncHandler::handleEqual(PyContext& context, PyObjPtr& self, PyObjPtr& val){
    if (val->getType() == EXPR_FUNCDEF && self.get() == val.get()){
        return true;
    }
    return false;
}
PyObjPtr& PyFuncHandler::handleCall(PyContext& context, PyObjPtr& self, ExprASTPtr& arglist){
    return self.cast<PyObjFuncDef>()->exeFunc(context, self, arglist);
}

