
#include "PyObj.h"
#include "ExprAST.h"
#include "objhandler/PyIntHandler.h"

using namespace std;
using namespace ff;

string PyIntHandler::handleStr(PyContext& context, const PyObjPtr& self) const {
    std::ostringstream  ostr;
    ostr << self.cast<PyObjInt>()->value;
    
    return ostr.str();
}
bool PyIntHandler::handleBool(PyContext& context, const PyObjPtr& self) const{
    return self.cast<PyObjInt>()->value != 0;
}
bool PyIntHandler::handleEqual(PyContext& context, const PyObjPtr& self, const PyObjPtr& val) const{
    if (PyCheckInt(val) && self.cast<PyObjInt>()->value == val.cast<PyObjInt>()->value){
        return true;
    }
    return false;
}
bool PyIntHandler::handleLessEqual(PyContext& context, const PyObjPtr& self, const PyObjPtr& val) const{
    int nType   = val->getType();

    if (nType == PY_INT){
        return self.cast<PyObjInt>()->value <= val.cast<PyObjInt>()->value;
    }
    else if (nType == PY_FLOAT){
        return PyFloat(self.cast<PyObjInt>()->value) <= val.cast<PyObjFloat>()->value;
    }
    else{
        THROW_EVAL_ERROR("can't compare to int");
    }
    return false;
}
bool PyIntHandler::handleGreatEqual(PyContext& context, const PyObjPtr& self, const PyObjPtr& val) const{
    int nType   = val->getType();

    if (nType == PY_INT){
        return self.cast<PyObjInt>()->value >= val.cast<PyObjInt>()->value;
    }
    else if (nType == PY_FLOAT){
        return PyFloat(self.cast<PyObjInt>()->value) >= val.cast<PyObjFloat>()->value;
    }
    else{
        THROW_EVAL_ERROR("can't compare to int");
    }
    return false;
}

PyObjPtr& PyIntHandler::handleAdd(PyContext& context, PyObjPtr& self, PyObjPtr& val){
    int nType   = val->getType();

    if (nType == PY_INT){
        long newVal = self.cast<PyObjInt>()->value + val.cast<PyObjInt>()->value;
        return context.cacheResult(PyCppUtil::genInt(context, newVal));
    }
    else if (nType == PY_FLOAT){
        PyFloat newVal = self.cast<PyObjInt>()->value + val.cast<PyObjFloat>()->value;
        return context.cacheResult(new PyObjFloat(newVal));
    }
    else{
        THROW_EVAL_ERROR("can't add to int");
    }
    return self;
}
PyObjPtr& PyIntHandler::handleSub(PyContext& context, PyObjPtr& self, PyObjPtr& val){
    int nType   = val->getType();

    if (nType == PY_INT){
        long newVal = self.cast<PyObjInt>()->value - val.cast<PyObjInt>()->value;
        return context.cacheResult(PyCppUtil::genInt(context, newVal));
    }
    else if (nType == PY_FLOAT){
        PyFloat newVal = self.cast<PyObjInt>()->value - val.cast<PyObjFloat>()->value;
        return context.cacheResult(new PyObjFloat(newVal));
    }
    else{
        THROW_EVAL_ERROR("can't sub to int");
    }
    return self;
}
PyObjPtr& PyIntHandler::handleMul(PyContext& context, PyObjPtr& self, PyObjPtr& val){
    int nType   = val->getType();

    if (nType == PY_INT){
        long newVal = self.cast<PyObjInt>()->value * val.cast<PyObjInt>()->value;
        return context.cacheResult(PyCppUtil::genInt(context, newVal));
    }
    else if (nType == PY_FLOAT){
        PyFloat newVal = self.cast<PyObjInt>()->value * val.cast<PyObjFloat>()->value;
        return context.cacheResult(new PyObjFloat(newVal));
    }
    else{
        THROW_EVAL_ERROR("can't mul to int");
    }
    return self;
}
PyObjPtr& PyIntHandler::handleDiv(PyContext& context, PyObjPtr& self, PyObjPtr& val){
    int nType   = val->getType();

    if (nType == PY_INT){
        long rval = val.cast<PyObjInt>()->value;
        if (rval == 0){
            THROW_EVAL_ERROR("div by zero");
        }
        long newVal = self.cast<PyObjInt>()->value / rval;
        return context.cacheResult(PyCppUtil::genInt(context, newVal));
    }
    else if (nType == PY_FLOAT){
        PyFloat rval = val.cast<PyObjFloat>()->value;
        if (rval == 0.0){
            THROW_EVAL_ERROR("div by zero");
        }
        PyFloat newVal = long(self.cast<PyObjInt>()->value / rval);
        return context.cacheResult(new PyObjFloat(newVal));
    }
    else{
        THROW_EVAL_ERROR("can't div to int");
    }
    return self;
}
PyObjPtr& PyIntHandler::handleMod(PyContext& context, PyObjPtr& self, PyObjPtr& val){
    int nType   = val->getType();

    if (nType == PY_INT){
        long rval = val.cast<PyObjInt>()->value;
        if (rval == 0){
            THROW_EVAL_ERROR("div by zero");
        }
        long newVal = self.cast<PyObjInt>()->value % rval;
        return context.cacheResult(PyCppUtil::genInt(context, newVal));
    }
    else if (nType == PY_FLOAT){
        long rval = long(val.cast<PyObjFloat>()->value);
        if (rval == 0){
            THROW_EVAL_ERROR("div by zero");
        }
        long newVal = self.cast<PyObjInt>()->value % rval;
        return context.cacheResult(PyCppUtil::genInt(context, newVal));
    }
    else{
        THROW_EVAL_ERROR("can't mod to int");
    }
    return self;
}
size_t PyIntHandler::handleHash(PyContext& context, const PyObjPtr& self) const{
    return self.cast<PyObjInt>()->value;
}
void PyIntHandler::handleRelese(PyObj* data){
    singleton_t<PyObjAllocator<PyObjInt> >::instance_ptr()->release((PyObjInt*)data);
}
