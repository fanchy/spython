
#include "PyObj.h"
#include "ExprAST.h"
#include "objhandler/PyDictHandler.h"

using namespace std;
using namespace ff;

string PyDictHandler::handleStr(PyContext& context, const PyObjPtr& self) const {
    string ret;
    const PyObjDict* pD = self.cast<PyObjDict>();
    for (PyObjDict::DictMap::const_iterator it = pD->value.begin(); it != pD->value.end(); ++it){
        if (ret.empty())
            ret += "{"+DICT_ITER_KEY(it)->getHandler()->handleStr(context, DICT_ITER_KEY(it)) + ": " + DICT_ITER_VAL(it)->getHandler()->handleStr(context, DICT_ITER_VAL(it));
        else
            ret += ", "+DICT_ITER_KEY(it)->getHandler()->handleStr(context, DICT_ITER_KEY(it)) + ": " + DICT_ITER_VAL(it)->getHandler()->handleStr(context, DICT_ITER_VAL(it));
    }
    if (ret.empty()){
        ret = "{}";
    }
    else{
        ret += "}";
    }
    return ret;
}
bool PyDictHandler::handleBool(PyContext& context, const PyObjPtr& self) const{
    return self.cast<PyObjDict>()->value.empty() == false;
}
bool PyDictHandler::handleEqual(PyContext& context, const PyObjPtr& self, const PyObjPtr& val) const{
    if (val->getType() != self->getType()){
        return false;
    }

    const PyObjDict* pD  = self.cast<PyObjDict>();
    const PyObjDict* pD2 = val.cast<PyObjDict>();
    if (pD->value.size() != pD2->value.size()){
        return false;
    }
    
    PyObjDict::DictMap::const_iterator it = pD->value.begin();
    PyObjDict::DictMap::const_iterator it2 = pD2->value.begin();
    for (; it != pD->value.end(); ++it){
        if (DICT_ITER_KEY(it)->getHandler()->handleEqual(context, DICT_ITER_KEY(it), DICT_ITER_KEY(it2)) == false){
            return false;
        }
        if (DICT_ITER_VAL(it)->getHandler()->handleEqual(context, DICT_ITER_VAL(it), DICT_ITER_VAL(it2)) == false){
            return false;
        }
        ++it2;
    }
    return true;
}
bool PyDictHandler::handleLessEqual(PyContext& context, const PyObjPtr& self, const PyObjPtr& val) const{
    if (val->getType() != self->getType()){
        return false;
    }

    const PyObjDict* pD  = self.cast<PyObjDict>();
    const PyObjDict* pD2 = val.cast<PyObjDict>();
    
    PyObjDict::DictMap::const_iterator it = pD->value.begin();
    PyObjDict::DictMap::const_iterator it2 = pD2->value.begin();
    for (; it != pD->value.end() && it2 != pD2->value.end(); ++it){
        if (DICT_ITER_KEY(it)->getHandler()->handleLessEqual(context, DICT_ITER_KEY(it), DICT_ITER_KEY(it2)) == false){
            return false;
        }
        if (DICT_ITER_VAL(it)->getHandler()->handleLessEqual(context, DICT_ITER_VAL(it), DICT_ITER_VAL(it2)) == false){
            return false;
        }
        ++it2;
    }
    if (it != pD->value.end()){
        return false;
    }
    return true;
}
bool PyDictHandler::handleGreatEqual(PyContext& context, const PyObjPtr& self, const PyObjPtr& val) const{
    if (val->getType() != self->getType()){
        return false;
    }

    const PyObjDict* pD  = self.cast<PyObjDict>();
    const PyObjDict* pD2 = val.cast<PyObjDict>();
    
    PyObjDict::DictMap::const_iterator it = pD->value.begin();
    PyObjDict::DictMap::const_iterator it2 = pD2->value.begin();
    for (; it != pD->value.end() && it2 != pD2->value.end(); ++it){
        if (DICT_ITER_KEY(it)->getHandler()->handleGreatEqual(context, DICT_ITER_KEY(it), DICT_ITER_KEY(it2)) == false){
            return false;
        }
        if (DICT_ITER_VAL(it)->getHandler()->handleGreatEqual(context, DICT_ITER_VAL(it), DICT_ITER_VAL(it2)) == false){
            return false;
        }
        ++it2;
    }
    if (it != pD->value.end()){
        return false;
    }
    return true;
}

PyObjPtr& PyDictHandler::handleAdd(PyContext& context, PyObjPtr& self, PyObjPtr& val){
    THROW_EVAL_ERROR("unsupported operand type(s) for +: 'dict'");
    return self;
}
PyObjPtr& PyDictHandler::handleSub(PyContext& context, PyObjPtr& self, PyObjPtr& val){
    THROW_EVAL_ERROR("unsupported operand type(s) for -: 'dict'");
    return self;
}
PyObjPtr& PyDictHandler::handleMul(PyContext& context, PyObjPtr& self, PyObjPtr& val){
    THROW_EVAL_ERROR("unsupported operand type(s) for *: 'dict'");
    return self;
}
PyObjPtr& PyDictHandler::handleDiv(PyContext& context, PyObjPtr& self, PyObjPtr& val){
    THROW_EVAL_ERROR("unsupported operand type(s) for /: 'dict'");
    return self;
}
PyObjPtr& PyDictHandler::handleMod(PyContext& context, PyObjPtr& self, PyObjPtr& val){
    THROW_EVAL_ERROR("unsupported operand type(s) for %: 'dict'");
    return self;
}

long PyDictHandler::handleLen(PyContext& context, PyObjPtr& self){
    return self.cast<PyObjDict>()->value.size();
}

PyObjPtr& PyDictHandler::handleSlice(PyContext& context, PyObjPtr& self, PyObjPtr& startVal, int* stop, int step){
    
    PyObjDict::DictMap& s = self.cast<PyObjDict>()->value;

    PyObjPtr ret = self.cast<PyObjDict>()->get(context, startVal);
    return context.cacheResult(ret);
}
PyObjPtr& PyDictHandler::handleSliceAssign(PyContext& context, PyObjPtr& self, PyObjPtr& k, PyObjPtr& v){
    PyObjDict::DictMap& s = self.cast<PyObjDict>()->value;

    self.cast<PyObjDict>()->set(context, k, v);
    
    return v;
}
void PyDictHandler::handleSliceDel(PyContext& context, PyObjPtr& self, PyObjPtr& k){
    PyObjDict::DictMap& s = self.cast<PyObjDict>()->value;
    if (!self.cast<PyObjDict>()->delByKey(context, k)){
        THROW_EVAL_ERROR("KeyError");
    }
    return;
}
