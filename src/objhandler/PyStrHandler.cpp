
#include "PyObj.h"
#include "ExprAST.h"
#include "objhandler/PyStrHandler.h"

using namespace std;
using namespace ff;

string PyStrHandler::handleStr(const PyObjPtr& self) const {
    string ret = "'";
    ret += self.cast<PyObjStr>()->value + "'";
    return ret;
}
bool PyStrHandler::handleBool(PyContext& context, const PyObjPtr& self) const{
    return self.cast<PyObjStr>()->value.empty() == false;
}
bool PyStrHandler::handleEqual(PyContext& context, const PyObjPtr& self, const PyObjPtr& val) const{
    if (val->getType() == self->getType() && self.cast<PyObjStr>()->value == val.cast<PyObjStr>()->value){
        return true;
    }
    return false;
}
bool PyStrHandler::handleLessEqual(PyContext& context, const PyObjPtr& self, const PyObjPtr& val) const{
    if (val->getType() == self->getType()){
        return self.cast<PyObjStr>()->value <= val.cast<PyObjStr>()->value;
    }
    else{
        THROW_EVAL_ERROR("can't compare to str");
    }
    return false;
}
bool PyStrHandler::handleGreatEqual(PyContext& context, const PyObjPtr& self, const PyObjPtr& val) const{
    if (val->getType() == self->getType()){
        return self.cast<PyObjStr>()->value >= val.cast<PyObjStr>()->value;
    }
    else{
        THROW_EVAL_ERROR("can't compare to str");
    }
    return false;
}

PyObjPtr& PyStrHandler::handleAdd(PyContext& context, PyObjPtr& self, PyObjPtr& val){
    if (val->getType() == self->getType()){
        string newVal = self.cast<PyObjStr>()->value += val.cast<PyObjStr>()->value;
        return context.cacheResult(new PyObjStr(newVal));
    }
    else{
        THROW_EVAL_ERROR("can't add to str");
    }
    return self;
}
PyObjPtr& PyStrHandler::handleSub(PyContext& context, PyObjPtr& self, PyObjPtr& val){
    THROW_EVAL_ERROR("can't sub to str");
    return self;
}
PyObjPtr& PyStrHandler::handleMul(PyContext& context, PyObjPtr& self, PyObjPtr& val){
    int nType   = val->getType();

    if (nType == PY_INT){
        long times = val.cast<PyObjInt>()->value;
        string newVal;
        for (long i = 0; i < times; ++i){
            newVal += self.cast<PyObjStr>()->value;
        }
        return context.cacheResult(new PyObjStr(newVal));
    }
    else{
        THROW_EVAL_ERROR("can't mul to str");
    }
    return self;
}
PyObjPtr& PyStrHandler::handleDiv(PyContext& context, PyObjPtr& self, PyObjPtr& val){
    THROW_EVAL_ERROR("can't div to str");
    return self;
}
PyObjPtr& PyStrHandler::handleMod(PyContext& context, PyObjPtr& self, PyObjPtr& val){
    THROW_EVAL_ERROR("can't mod to str");
    return self;
}

