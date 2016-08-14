
#include "PyObj.h"
#include "ExprAST.h"
#include "objhandler/PyBoolHandler.h"

using namespace std;
using namespace ff;

string PyBoolHandler::handleStr(PyObjPtr& self) {
    if (self.cast<PyObjBool>()->value){
        return "True";
    }
    return "False";
}
bool PyBoolHandler::handleBool(PyContext& context, PyObjPtr& self){
    return self.cast<PyObjBool>()->value;
}
bool PyBoolHandler::handleEqual(PyContext& context, PyObjPtr& self, PyObjPtr& val){
    if (val->getType() == PY_BOOL && self.cast<PyObjBool>()->value == val.cast<PyObjBool>()->value){
        return true;
    }
    return false;
}


