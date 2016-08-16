
#include "PyObj.h"
#include "ExprAST.h"
#include "objhandler/PyFuncHandler.h"

using namespace std;
using namespace ff;

string PyFuncHandler::handleStr(PyObjPtr& self) {
    return self.cast<PyObjFuncDef>()->name;
}
bool PyFuncHandler::handleBool(PyContext& context, PyObjPtr& self){
    return self.cast<PyObjInt>()->value != 0;
}
bool PyFuncHandler::handleEqual(PyContext& context, PyObjPtr& self, PyObjPtr& val){
    if (val->getType() == PY_INT && self.cast<PyObjInt>()->value == val.cast<PyObjInt>()->value){
        return true;
    }
    return false;
}
