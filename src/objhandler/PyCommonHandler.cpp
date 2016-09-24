
#include "PyObj.h"
#include "ExprAST.h"
#include "objhandler/PyCommonHandler.h"

using namespace std;
using namespace ff;
PyCommonHandler::PyCommonHandler(){
    expr__str__ = singleton_t<VariableExprAllocator>::instance_ptr()->alloc("__str__");
    expr__eq__  = singleton_t<VariableExprAllocator>::instance_ptr()->alloc("__eq__");
}
string PyCommonHandler::handleStr(PyContext& context, const PyObjPtr& self) const {
    PyContextBackUp backup(context);
    context.curstack = self;
    
    ExprASTPtr  expr  = expr__str__;
    PyObjPtr __str__func = expr->getFieldVal(context);
    backup.rollback();
    
    if (__str__func && PyCheckFunc(__str__func)){
        vector<PyObjPtr> argAssignVal;
        PyCppUtil::callPyfunc(context, __str__func, argAssignVal);
    }
    return "";
}
bool PyCommonHandler::handleBool(PyContext& context, const PyObjPtr& self) const{
    return false;
}

bool PyCommonHandler::handleEqual(PyContext& context, const PyObjPtr& self, const PyObjPtr& val) const{
    return false;
}
bool PyCommonHandler::handleLessEqual(PyContext& context, const PyObjPtr& self, const PyObjPtr& val) const{
    return false;
}
bool PyCommonHandler::handleGreatEqual(PyContext& context, const PyObjPtr& self, const PyObjPtr& val) const{
    return false;
}
bool PyCommonHandler::handleIn(PyContext& context, const PyObjPtr& self, const PyObjPtr& val) const{
    return false;
}

PyObjPtr& PyCommonHandler::handleAdd(PyContext& context, PyObjPtr& self, PyObjPtr& val){
    return self;
}
PyObjPtr& PyCommonHandler::handleSub(PyContext& context, PyObjPtr& self, PyObjPtr& val){
    return self;
}
PyObjPtr& PyCommonHandler::handleMul(PyContext& context, PyObjPtr& self, PyObjPtr& val){
    return self;
}
PyObjPtr& PyCommonHandler::handleDiv(PyContext& context, PyObjPtr& self, PyObjPtr& val){
    return self;
}
PyObjPtr& PyCommonHandler::handleMod(PyContext& context, PyObjPtr& self, PyObjPtr& val){
    return self;
}
PyObjPtr& PyCommonHandler::handleCall(PyContext& context, PyObjPtr& self, std::vector<ArgTypeInfo>& allArgsVal, 
                                 std::vector<PyObjPtr>& argAssignVal){
    return self;
}
std::size_t PyCommonHandler::handleHash(const PyObjPtr& self) const{
    return 0;
}
bool PyCommonHandler::handleIsInstance(PyContext& context, PyObjPtr& self, PyObjPtr& val){
    return 0;
}
long PyCommonHandler::handleLen(PyContext& context, PyObjPtr& self){
    return 0;
}
PyObjPtr& PyCommonHandler::handleSlice(PyContext& context, PyObjPtr& self, int start, int* stop, int step){
    return self;
}
