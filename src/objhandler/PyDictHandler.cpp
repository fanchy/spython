
#include "PyObj.h"
#include "ExprAST.h"
#include "objhandler/PyDictHandler.h"

using namespace std;
using namespace ff;

string PyDictHandler::handleStr(const PyObjPtr& self) const {
    string ret;
    const PyObjDict* pD = self.cast<PyObjDict>();
    for (PyObjDict::DictMap::const_iterator it = pD->value.begin(); it != pD->value.end(); ++it){
        if (ret.empty())
            ret += "{"+it->first->getHandler()->handleStr(it->first) + ": " + it->second->getHandler()->handleStr(it->second);
        else
            ret += ", "+it->first->getHandler()->handleStr(it->first) + ": " + it->second->getHandler()->handleStr(it->second);
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
        if (it->first->getHandler()->handleEqual(context, it->first, it2->first) == false){
            return false;
        }
        if (it->second->getHandler()->handleEqual(context, it->second, it2->second) == false){
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
        if (it->first->getHandler()->handleLessEqual(context, it->first, it2->first) == false){
            return false;
        }
        if (it->second->getHandler()->handleLessEqual(context, it->second, it2->second) == false){
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
        if (it->first->getHandler()->handleGreatEqual(context, it->first, it2->first) == false){
            return false;
        }
        if (it->second->getHandler()->handleGreatEqual(context, it->second, it2->second) == false){
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

