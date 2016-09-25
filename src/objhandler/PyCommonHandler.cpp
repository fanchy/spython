
#include "PyObj.h"
#include "ExprAST.h"
#include "objhandler/PyCommonHandler.h"

using namespace std;
using namespace ff;
PyCommonHandler::PyCommonHandler(){
    expr__str__ = singleton_t<VariableExprAllocator>::instance_ptr()->alloc("__str__");
    expr__lt__  = singleton_t<VariableExprAllocator>::instance_ptr()->alloc("__lt__");
    expr__le__  = singleton_t<VariableExprAllocator>::instance_ptr()->alloc("__le__");
    expr__eq__  = singleton_t<VariableExprAllocator>::instance_ptr()->alloc("__eq__");
    expr__gt__  = singleton_t<VariableExprAllocator>::instance_ptr()->alloc("__gt__");
    expr__ge__  = singleton_t<VariableExprAllocator>::instance_ptr()->alloc("__ge__");
    expr__cmp__ = singleton_t<VariableExprAllocator>::instance_ptr()->alloc("__cmp__");
    expr__len__ = singleton_t<VariableExprAllocator>::instance_ptr()->alloc("__len__");
    expr__contains__ = singleton_t<VariableExprAllocator>::instance_ptr()->alloc("__contains__");
    
    expr__add__ = singleton_t<VariableExprAllocator>::instance_ptr()->alloc("__add__");
    expr__sub__ = singleton_t<VariableExprAllocator>::instance_ptr()->alloc("__sub__");
    expr__mul__ = singleton_t<VariableExprAllocator>::instance_ptr()->alloc("__mul__");
    //expr__floordiv__ = singleton_t<VariableExprAllocator>::instance_ptr()->alloc("");
    expr__mod__ = singleton_t<VariableExprAllocator>::instance_ptr()->alloc("__mod__");
    
    expr__divmod__ = singleton_t<VariableExprAllocator>::instance_ptr()->alloc("__divmod__");
    //expr__pow__ = singleton_t<VariableExprAllocator>::instance_ptr()->alloc("");
    expr__lshift__ = singleton_t<VariableExprAllocator>::instance_ptr()->alloc("__lshift__");
    expr__rshift__ = singleton_t<VariableExprAllocator>::instance_ptr()->alloc("__rshift__");
    //expr__and__ = singleton_t<VariableExprAllocator>::instance_ptr()->alloc("");
    //expr__xor__ = singleton_t<VariableExprAllocator>::instance_ptr()->alloc("");
    //expr__or__ = singleton_t<VariableExprAllocator>::instance_ptr()->alloc("");
    expr__div__ = singleton_t<VariableExprAllocator>::instance_ptr()->alloc("__div__");
    //expr__truediv__ = singleton_t<VariableExprAllocator>::instance_ptr()->alloc("");
    //expr__radd__
    //expr__rsub__
    //expr__rmul__
    //expr__rdiv__
    //expr__rtruediv__
    //expr__rfloordiv__
    /*
    object.__rmod__(self, other)
    object.__rdivmod__(self, other)
    object.__rpow__(self, other)
    object.__rlshift__(self, other)?
    object.__rrshift__(self, other)
    object.__rand__(self, other)
    object.__rxor__(self, other)
    object.__ror__(self, other)
    */
    expr__iadd__ = singleton_t<VariableExprAllocator>::instance_ptr()->alloc("__iadd__");
    expr__isub__ = singleton_t<VariableExprAllocator>::instance_ptr()->alloc("__isub__");
    expr__imul__ = singleton_t<VariableExprAllocator>::instance_ptr()->alloc("__imul__");
    expr__idiv__ = singleton_t<VariableExprAllocator>::instance_ptr()->alloc("__idiv__");
    expr__itruediv__ = singleton_t<VariableExprAllocator>::instance_ptr()->alloc("__idiv__");
    expr__ifloordiv__ = singleton_t<VariableExprAllocator>::instance_ptr()->alloc("r__itruediv__");
    expr__imod__ = singleton_t<VariableExprAllocator>::instance_ptr()->alloc("__ifloordiv__");
    expr__ipow__ = singleton_t<VariableExprAllocator>::instance_ptr()->alloc("__imod__");
    expr__ilshift__ = singleton_t<VariableExprAllocator>::instance_ptr()->alloc("__ipow__");
    expr__irshift__ = singleton_t<VariableExprAllocator>::instance_ptr()->alloc("__irshift__");
    expr__iand__ = singleton_t<VariableExprAllocator>::instance_ptr()->alloc("__iand__");
    expr__ixor__ = singleton_t<VariableExprAllocator>::instance_ptr()->alloc("__ixor__");
    expr__ior__ = singleton_t<VariableExprAllocator>::instance_ptr()->alloc("__ior__");
    expr__long__ = singleton_t<VariableExprAllocator>::instance_ptr()->alloc("__long__");
    expr__enter__ = singleton_t<VariableExprAllocator>::instance_ptr()->alloc("__enter__");
    expr__exit__ = singleton_t<VariableExprAllocator>::instance_ptr()->alloc("__exit__");
    
    expr__call__ = singleton_t<VariableExprAllocator>::instance_ptr()->alloc("__call__");
}
string PyCommonHandler::handleStr(PyContext& context, const PyObjPtr& self) const {
    PyContextBackUp backup(context);
    context.curstack = self;
    
    ExprASTPtr  expr  = expr__str__;
    PyObjPtr func = expr->getFieldVal(context);
    backup.rollback();
    
    if (func && PyCheckFunc(func)){
        vector<PyObjPtr> argAssignVal;
        PyObjPtr ret = PyCppUtil::callPyfunc(context, func, argAssignVal);
        if (PyCheckStr(ret)){
            return ret.cast<PyObjStr>()->value;
        }
    }
    return "";
}
bool PyCommonHandler::handleBool(PyContext& context, const PyObjPtr& self) const{
    return false;
}
bool PyCommonHandler::handleCompare(PyContext& context, const PyObjPtr& self, const PyObjPtr& val, ExprASTPtr expr, int flag) const{
    PyContextBackUp backup(context);
    context.curstack = self;
    
    PyObjPtr func = expr->getFieldVal(context);
    backup.rollback();
    
    if (func && PyCheckFunc(func)){
        vector<PyObjPtr> argAssignVal;
        argAssignVal.push_back(val);
        PyObjPtr ret = PyCppUtil::callPyfunc(context, func, argAssignVal);
        return ret->getHandler()->handleBool(context, ret);
    }
    else if (flag == 0){
        PyContextBackUp backup2(context);
        context.curstack = self;
        ExprASTPtr expr2 = expr__cmp__;
        func = expr2->getFieldVal(context);
        backup.rollback();
        
        if (func && PyCheckFunc(func)){
            vector<PyObjPtr> argAssignVal;
            argAssignVal.push_back(val);
            PyObjPtr ret = PyCppUtil::callPyfunc(context, func, argAssignVal);
            if (PyCheckInt(ret)){
                // return a negative integer if self < other, zero if self == other, a positive integer if self > other.
                int n = ret.cast<PyObjInt>()->value;
                if (expr.get() == expr__lt__.get()){
                    return n < 0;
                }
                else if (expr.get() == expr__le__.get()){
                    return n <= 0;
                }
                else if (expr.get() == expr__eq__.get()){
                    return n == 0;
                }
                else if (expr.get() == expr__gt__.get()){
                    return n > 0;
                }
                else if (expr.get() == expr__ge__.get()){
                    return n >= 0;
                }
            }
        }
    }
    return false;
}
long PyCommonHandler::handleLen(PyContext& context, PyObjPtr& self){
    PyContextBackUp backup(context);
    context.curstack = self;
    
    ExprASTPtr  expr  = expr__len__;
    PyObjPtr func = expr->getFieldVal(context);
    backup.rollback();
    
    if (func && PyCheckFunc(func)){
        vector<PyObjPtr> argAssignVal;
        PyObjPtr ret = PyCppUtil::callPyfunc(context, func, argAssignVal);
        if (PyCheckInt(ret)){
            return ret.cast<PyObjInt>()->value;
        }
    }
    return 0;
}

bool PyCommonHandler::handleLess(PyContext& context, const PyObjPtr& self, const PyObjPtr& val) const{
    return handleCompare(context, self, val, expr__lt__);
}
bool PyCommonHandler::handleLessEqual(PyContext& context, const PyObjPtr& self, const PyObjPtr& val) const{
    return handleCompare(context, self, val, expr__le__);
}
bool PyCommonHandler::handleEqual(PyContext& context, const PyObjPtr& self, const PyObjPtr& val) const{
    if (self.get() == val.get()){
        return true;
    }
    return handleCompare(context, self, val, expr__eq__);
}
bool PyCommonHandler::handleGreat(PyContext& context, const PyObjPtr& self, const PyObjPtr& val) const{
    return handleCompare(context, self, val, expr__gt__);
}
bool PyCommonHandler::handleGreatEqual(PyContext& context, const PyObjPtr& self, const PyObjPtr& val) const{
    return handleCompare(context, self, val, expr__ge__);
}
bool PyCommonHandler::handleContains(PyContext& context, const PyObjPtr& self, const PyObjPtr& val) const{
    return handleCompare(context, self, val, expr__contains__, 1);
}
PyObjPtr& PyCommonHandler::handleBinOps(PyContext& context, PyObjPtr& self, PyObjPtr& val, ExprASTPtr expr){
    PyContextBackUp backup(context);
    context.curstack = self;
    
    PyObjPtr func = expr->getFieldVal(context);
    backup.rollback();
    
    if (func && PyCheckFunc(func)){
        vector<PyObjPtr> argAssignVal;
        argAssignVal.push_back(val);
        PyObjPtr ret = PyCppUtil::callPyfunc(context, func, argAssignVal);
        return context.cacheResult(ret);
    }
    PY_RAISE_STR(context, PyCppUtil::strFormat("no %s defined", expr.cast<VariableExprAST>()->name.c_str()));
    return context.cacheResult(PyObjTool::buildNone());
}
PyObjPtr& PyCommonHandler::handleAdd(PyContext& context, PyObjPtr& self, PyObjPtr& val){
    return handleBinOps(context, self, val, expr__add__);
}
PyObjPtr& PyCommonHandler::handleSub(PyContext& context, PyObjPtr& self, PyObjPtr& val){
    return handleBinOps(context, self, val, expr__sub__);
}
PyObjPtr& PyCommonHandler::handleMul(PyContext& context, PyObjPtr& self, PyObjPtr& val){
    return handleBinOps(context, self, val, expr__mul__);
}
PyObjPtr& PyCommonHandler::handleDiv(PyContext& context, PyObjPtr& self, PyObjPtr& val){
    return handleBinOps(context, self, val, expr__div__);
}
PyObjPtr& PyCommonHandler::handleMod(PyContext& context, PyObjPtr& self, PyObjPtr& val){
    return handleBinOps(context, self, val, expr__mod__);
}
PyObjPtr& PyCommonHandler::handleCall(PyContext& context, PyObjPtr& self, std::vector<ArgTypeInfo>& allArgsVal, 
                                 std::vector<PyObjPtr>& argAssignVal){
    PyContextBackUp backup(context);
    context.curstack = self;
    ExprASTPtr expr = expr__call__;
    PyObjPtr func = expr->getFieldVal(context);
    backup.rollback();
    
    if (func && PyCheckFunc(func) && func.get() != self.get()){
        return func->getHandler()->handleCall(context, func, allArgsVal, argAssignVal);
    }
    PY_RAISE_STR(context, PyCppUtil::strFormat("no %s defined", expr.cast<VariableExprAST>()->name.c_str()));
    return self;
}
std::size_t PyCommonHandler::handleHash(PyContext& context, const PyObjPtr& self) const{
    PyContextBackUp backup(context);
    context.curstack = self;
    
    ExprASTPtr  expr  = expr__hash__;
    PyObjPtr func = expr->getFieldVal(context);
    backup.rollback();
    
    if (func && PyCheckFunc(func)){
        vector<PyObjPtr> argAssignVal;
        PyObjPtr ret = PyCppUtil::callPyfunc(context, func, argAssignVal);
        if (PyCheckInt(ret)){
            return ret.cast<PyObjInt>()->value;
        }
    }
    PY_RAISE_STR(context, PyCppUtil::strFormat("no %s defined", expr.cast<VariableExprAST>()->name.c_str()));
    return 0;
}
bool PyCommonHandler::handleIsInstance(PyContext& context, PyObjPtr& self, PyObjPtr& val){
    return 0;
}

PyObjPtr& PyCommonHandler::handleSlice(PyContext& context, PyObjPtr& self, int start, int* stop, int step){
    return self;
}
