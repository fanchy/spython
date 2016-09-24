
#include "PyObj.h"
#include "ExprAST.h"
#include "objhandler/PyCommonHandler.h"

using namespace std;
using namespace ff;

string PyCommonHandler::handleStr(const PyObjPtr& self) const {
    if (self.cast<PyObjBool>()->value){
        return "True";
    }
    return "False";
}
bool PyCommonHandler::handleBool(PyContext& context, const PyObjPtr& self) const{
    return self.cast<PyObjBool>()->value;
}
bool PyCommonHandler::handleEqual(PyContext& context, const PyObjPtr& self, const PyObjPtr& val) const{
    if (PyCheckBool(val) && self.cast<PyObjBool>()->value == val.cast<PyObjBool>()->value){
        return true;
    }
    return false;
}


