
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
bool PyListHandler::handleContains(PyContext& context, const PyObjPtr& self, const PyObjPtr& val) const{
    const vector<PyObjPtr>& s = self.cast<PyObjList>()->value;
    for (size_t i = 0; i < s.size(); ++i){
        if (val->getHandler()->handleEqual(context, val, s[i])){
            return true;
        }
    }
    return false;
}
PyObjPtr& PyListHandler::handleSlice(PyContext& context, PyObjPtr& self, PyObjPtr& startVal, int* stop, int step){
    PyAssertInt(startVal);
    int start = startVal.cast<PyObjInt>()->value;
    vector<PyObjPtr>& s = self.cast<PyObjList>()->value;
    PyObjPtr newVal;
    if (NULL == stop){
        if (start < 0){
            start = int(s.size()) + start;
        }
        if (start >= 0 && start < (int)s.size()){
            return s[start];
        }
        else{
            THROW_EVAL_ERROR("IndexError: tuple index out of range");
        }
    }
    
    if (step > 0){
        if (start < 0){
            start += (int)s.size();
        }
        if (*stop <= start){
            THROW_EVAL_ERROR("IndexError: tuple index out of range");
        }
        newVal = new PyObjList();
        for (int i = start; i < *stop && i < (int)s.size(); i += step){
            newVal.cast<PyObjList>()->value.push_back(s[i]);
        }
    }
    else{
        newVal = new PyObjList();
        for (int i = start; i > *stop; i += step){
            int index = i;
            if (index < 0){
                index = int(s.size()) + index;
            }
            if (index < 0 || index >= (int)s.size()){
                break;
            }
            newVal.cast<PyObjList>()->value.push_back(s[index]);
        }
    }
    return context.cacheResult(newVal);
}
void PyListHandler::handleSliceDel(PyContext& context, PyObjPtr& self, PyObjPtr& startVal){
    PyAssertInt(startVal);
    long start = startVal.cast<PyObjInt>()->value;
    if (start < 0 || start > (long)self.cast<PyObjList>()->value.size()){
        THROW_EVAL_ERROR("IndexError: list assignment index out of range");
    }
    self.cast<PyObjList>()->value.erase(self.cast<PyObjList>()->value.begin() + start);
}
