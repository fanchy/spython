
#include "PyObj.h"
#include "ExprAST.h"
#include "objhandler/PyBoolHandler.h"

using namespace std;
using namespace ff;

string PyBoolHandler::handleStr(const PyObjPtr& self) const {
    if (self.cast<PyObjBool>()->value){
        return "True";
    }
    return "False";
}
bool PyBoolHandler::handleBool(PyContext& context, const PyObjPtr& self) const{
    return self.cast<PyObjBool>()->value;
}
bool PyBoolHandler::handleEqual(PyContext& context, const PyObjPtr& self, const PyObjPtr& val) const{
    if (val->getType() == PY_BOOL && self.cast<PyObjBool>()->value == val.cast<PyObjBool>()->value){
        return true;
    }
    return false;
}


