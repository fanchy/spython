
#include "PyObj.h"
#include "ExprAST.h"
#include "objhandler/PyListHandler.h"

using namespace std;
using namespace ff;

string PyListHandler::handleStr(PyContext& context, const PyObjPtr& self) const {
    string ret;
    const PyObjList* pT = self.cast<PyObjList>();
    for (size_t i = 0; i < pT->value.size(); ++i){
        if (ret.empty())
            ret += "["+pT->value[i]->getHandler()->handleStr(context, pT->value[i]);
        else
            ret += ", " + pT->value[i]->getHandler()->handleStr(context, pT->value[i]);
    }
    if (ret.empty()){
        ret = "[]";
    }
    else{
        ret += "]";
    }
    return ret;
}
bool PyListHandler::handleBool(PyContext& context, const PyObjPtr& self) const{
    return self.cast<PyObjList>()->value.empty() == false;
}
bool PyListHandler::handleEqual(PyContext& context, const PyObjPtr& self, const PyObjPtr& val) const{
    if (val->getType() != self->getType()){
        return false;
    }
    const PyObjList* pT = self.cast<PyObjList>();
    const PyObjList* pV = val.cast<PyObjList>();
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
bool PyListHandler::handleLessEqual(PyContext& context, const PyObjPtr& self, const PyObjPtr& val) const{
    if (val->getType() != self->getType()){
        return true;
    }
    const PyObjList* pT = self.cast<PyObjList>();
    const PyObjList* pV = val.cast<PyObjList>();

    for (size_t i = 0; i < pT->value.size(); ++i){
        if (pT->value[i]->getHandler()->handleLessEqual(context, pT->value[i], pV->value[i])){
            return true;
        }
    }
    return false;
}
bool PyListHandler::handleGreatEqual(PyContext& context, const PyObjPtr& self, const PyObjPtr& val) const{
    if (val->getType() != self->getType()){
        return true;
    }
    const PyObjList* pT = self.cast<PyObjList>();
    const PyObjList* pV = val.cast<PyObjList>();

    for (size_t i = 0; i < pT->value.size(); ++i){
        if (pT->value[i]->getHandler()->handleGreatEqual(context, pT->value[i], pV->value[i])){
            return true;
        }
    }
    return false;
}

PyObjPtr& PyListHandler::handleAdd(PyContext& context, PyObjPtr& self, PyObjPtr& val){
    if (val->getType() != self->getType()){
        THROW_EVAL_ERROR("can only concatenate list to list");
    }

    PyObjPtr ret   = new PyObjList();
    
    ret.cast<PyObjList>()->value = self.cast<PyObjList>()->value;
    ret.cast<PyObjList>()->value.insert(ret.cast<PyObjList>()->value.end(),
                                            val.cast<PyObjList>()->value.begin(),
                                            val.cast<PyObjList>()->value.end());
    return context.cacheResult(ret);
}
PyObjPtr& PyListHandler::handleSub(PyContext& context, PyObjPtr& self, PyObjPtr& val){
    THROW_EVAL_ERROR("unsupported operand type(s) for -: 'list' and 'list'");
    return self;
}
PyObjPtr& PyListHandler::handleMul(PyContext& context, PyObjPtr& self, PyObjPtr& val){
    if (PyCheckInt(val)){
        PyObjPtr ret   = new PyObjList();
        long newVal = self.cast<PyObjInt>()->value * val.cast<PyObjInt>()->value;
        
        for (long i = 0; i < newVal; ++i){
            ret.cast<PyObjList>()->value.insert(ret.cast<PyObjList>()->value.end(),
                                                    self.cast<PyObjList>()->value.begin(),
                                                    self.cast<PyObjList>()->value.end());
        }

        return context.cacheResult(ret);
    }
    else{
        THROW_EVAL_ERROR(" can't multiply sequence by non-int");
    }
    return self;
}
PyObjPtr& PyListHandler::handleDiv(PyContext& context, PyObjPtr& self, PyObjPtr& val){
    THROW_EVAL_ERROR("unsupported operand type(s) for /: 'list' and other value");
    return self;
}
PyObjPtr& PyListHandler::handleMod(PyContext& context, PyObjPtr& self, PyObjPtr& val){
    THROW_EVAL_ERROR("unsupported operand type(s) for %: 'list' and other value");
    return self;
}
long PyListHandler::handleLen(PyContext& context, PyObjPtr& self){
    return self.cast<PyObjList>()->value.size();
}

