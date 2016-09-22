
#include "PyObj.h"
#include "ExprAST.h"
#include "objhandler/PyTupleHandler.h"

using namespace std;
using namespace ff;

string PyTupleHandler::handleStr(const PyObjPtr& self) const {
    string ret;
    const PyObjTuple* pT = self.cast<PyObjTuple>();
    for (size_t i = 0; i < pT->value.size(); ++i){
        if (ret.empty())
            ret += "("+pT->value[i]->getHandler()->handleStr(pT->value[i]);
        else
            ret += ", " + pT->value[i]->getHandler()->handleStr(pT->value[i]);
    }
    if (ret.empty()){
        ret = "()";
    }
    else{
        ret += ")";
    }
    return ret;
}
bool PyTupleHandler::handleBool(PyContext& context, const PyObjPtr& self) const{
    return self.cast<PyObjTuple>()->value.empty() == false;
}
bool PyTupleHandler::handleEqual(PyContext& context, const PyObjPtr& self, const PyObjPtr& val) const{
    if (val->getType() != self->getType()){
        return false;
    }
    const PyObjTuple* pT = self.cast<PyObjTuple>();
    const PyObjTuple* pV = val.cast<PyObjTuple>();
    if (pT->value.size() != pV->value.size()){
        return false;
    }
    for (size_t i = 0; i < pT->value.size(); ++i){
        if (pT->value[i]->getHandler()->handleEqual(context, pT->value[i], pV->value[i]) == false){
            return false;
        }
    }
    return true;
}
bool PyTupleHandler::handleLessEqual(PyContext& context, const PyObjPtr& self, const PyObjPtr& val) const{
    if (val->getType() != self->getType()){
        return true;
    }
    const PyObjTuple* pT = self.cast<PyObjTuple>();
    const PyObjTuple* pV = val.cast<PyObjTuple>();

    for (size_t i = 0; i < pT->value.size(); ++i){
        if (pT->value[i]->getHandler()->handleLessEqual(context, pT->value[i], pV->value[i])){
            return true;
        }
    }
    return false;
}
bool PyTupleHandler::handleGreatEqual(PyContext& context, const PyObjPtr& self, const PyObjPtr& val) const{
    if (val->getType() != self->getType()){
        return true;
    }
    const PyObjTuple* pT = self.cast<PyObjTuple>();
    const PyObjTuple* pV = val.cast<PyObjTuple>();

    for (size_t i = 0; i < pT->value.size(); ++i){
        if (pT->value[i]->getHandler()->handleGreatEqual(context, pT->value[i], pV->value[i])){
            return true;
        }
    }
    return false;
}

PyObjPtr& PyTupleHandler::handleAdd(PyContext& context, PyObjPtr& self, PyObjPtr& val){
    if (val->getType() != self->getType()){
        THROW_EVAL_ERROR("can only concatenate tuple to tuple");
    }

    PyObjPtr ret   = new PyObjTuple();
    
    ret.cast<PyObjTuple>()->value = self.cast<PyObjTuple>()->value;
    ret.cast<PyObjTuple>()->value.insert(ret.cast<PyObjTuple>()->value.end(),
                                            val.cast<PyObjTuple>()->value.begin(),
                                            val.cast<PyObjTuple>()->value.end());
    return context.cacheResult(ret);
}
PyObjPtr& PyTupleHandler::handleSub(PyContext& context, PyObjPtr& self, PyObjPtr& val){
    THROW_EVAL_ERROR("unsupported operand type(s) for -: 'tuple' and 'tuple'");
    return self;
}
PyObjPtr& PyTupleHandler::handleMul(PyContext& context, PyObjPtr& self, PyObjPtr& val){
    if (PY_INT == val->getType()){
        PyObjPtr ret   = new PyObjTuple();
        long newVal = self.cast<PyObjInt>()->value * val.cast<PyObjInt>()->value;
        
        for (long i = 0; i < newVal; ++i){
            ret.cast<PyObjTuple>()->value.insert(ret.cast<PyObjTuple>()->value.end(),
                                                    self.cast<PyObjTuple>()->value.begin(),
                                                    self.cast<PyObjTuple>()->value.end());
        }

        return context.cacheResult(ret);
    }
    else{
        THROW_EVAL_ERROR(" can't multiply sequence by non-int");
    }
    return self;
}
PyObjPtr& PyTupleHandler::handleDiv(PyContext& context, PyObjPtr& self, PyObjPtr& val){
    THROW_EVAL_ERROR("unsupported operand type(s) for /: 'tuple' and other value");
    return self;
}
PyObjPtr& PyTupleHandler::handleMod(PyContext& context, PyObjPtr& self, PyObjPtr& val){
    THROW_EVAL_ERROR("unsupported operand type(s) for %: 'tuple' and other value");
    return self;
}
long PyTupleHandler::handleLen(PyContext& context, PyObjPtr& self){
    return self.cast<PyObjTuple>()->value.size();
}

