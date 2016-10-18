
#include "PyObj.h"
#include "ExprAST.h"

#include "objhandler/PyFloatHandler.h"

using namespace std;
using namespace ff;


string PyFloatHandler::handleStr(PyContext& context, const PyObjPtr& self)  const{
    char msg[64] = {0};
    snprintf(msg, sizeof(msg), "%g", self.cast<PyObjFloat>()->value);
    string ret = msg;
    if (ret.find("e") != string::npos){
        snprintf(msg, sizeof(msg), "%f", self.cast<PyObjFloat>()->value);
        ret = msg;
    }
    return ret;
}

bool PyFloatHandler::handleBool(PyContext& context, const PyObjPtr& self) const{
    return self.cast<PyObjFloat>()->value != 0.0;
}
bool PyFloatHandler::handleEqual(PyContext& context, const PyObjPtr& self, const PyObjPtr& val) const{
    if (PyCheckInt(val) && self.cast<PyObjInt>()->value == val.cast<PyObjInt>()->value){
        return true;
    }
    return false;
}


PyObjPtr& PyFloatHandler::handleAdd(PyContext& context, PyObjPtr& self, PyObjPtr& val){
    int nType   = val->getType();

    if (nType == PY_INT){
        PyFloat newVal = self.cast<PyObjFloat>()->value + val.cast<PyObjInt>()->value;
        return context.cacheResult(new PyObjFloat(newVal));
    }
    else if (nType == PY_FLOAT){
        PyFloat newVal = self.cast<PyObjFloat>()->value + val.cast<PyObjFloat>()->value;
        return context.cacheResult(new PyObjFloat(newVal));
    }
    else{
        THROW_EVAL_ERROR("can't add to float");
    }
    return self;
}
PyObjPtr& PyFloatHandler::handleSub(PyContext& context, PyObjPtr& self, PyObjPtr& val){
    int nType   = val->getType();

    if (nType == PY_INT){
        PyFloat newVal = self.cast<PyObjFloat>()->value - val.cast<PyObjInt>()->value;
        return context.cacheResult(new PyObjFloat(newVal));
    }
    else if (nType == PY_FLOAT){
        PyFloat newVal = self.cast<PyObjFloat>()->value - val.cast<PyObjFloat>()->value;
        return context.cacheResult(new PyObjFloat(newVal));
    }
    else{
        THROW_EVAL_ERROR("can't sub to int");
    }
    return self;
}
PyObjPtr& PyFloatHandler::handleMul(PyContext& context, PyObjPtr& self, PyObjPtr& val){
    int nType   = val->getType();

    if (nType == PY_INT){
        PyFloat newVal = self.cast<PyObjFloat>()->value * val.cast<PyObjInt>()->value;
        return context.cacheResult(new PyObjFloat(newVal));
    }
    else if (nType == PY_FLOAT){
        PyFloat newVal = self.cast<PyObjFloat>()->value * val.cast<PyObjFloat>()->value;
        return context.cacheResult(new PyObjFloat(newVal));
    }
    else{
        THROW_EVAL_ERROR("can't mul to int");
    }
    return self;
}
PyObjPtr& PyFloatHandler::handleDiv(PyContext& context, PyObjPtr& self, PyObjPtr& val){
    int nType   = val->getType();

    if (nType == PY_INT){
        long rval = val.cast<PyObjInt>()->value;
        if (rval == 0){
            THROW_EVAL_ERROR("div by zero");
        }
        PyFloat newVal = self.cast<PyObjFloat>()->value / rval;
        return context.cacheResult(new PyObjFloat(newVal));
    }
    else if (nType == PY_FLOAT){
        PyFloat rval = val.cast<PyObjFloat>()->value;
        if (rval == 0.0){
            THROW_EVAL_ERROR("div by zero");
        }
        PyFloat newVal = self.cast<PyObjFloat>()->value / rval;
        return context.cacheResult(new PyObjFloat(newVal));
    }
    else{
        THROW_EVAL_ERROR("can't div to int");
    }
    return self;
}
PyObjPtr& PyFloatHandler::handleMod(PyContext& context, PyObjPtr& self, PyObjPtr& val){
    int nType   = val->getType();

    if (nType == PY_INT){
        long rval = val.cast<PyObjInt>()->value;
        if (rval == 0){
            THROW_EVAL_ERROR("div by zero");
        }
        long newVal = long(self.cast<PyObjFloat>()->value) % long(rval);
        return context.cacheResult(new PyObjInt(newVal));
    }
    else if (nType == PY_FLOAT){
        PyFloat rval = val.cast<PyObjFloat>()->value;
        if (rval == 0.0){
            THROW_EVAL_ERROR("div by zero");
        }
        long newVal = long(self.cast<PyObjFloat>()->value) % long(rval);
        return context.cacheResult(new PyObjInt(newVal));
    }
    else{
        THROW_EVAL_ERROR("can't mod to int");
    }
    return self;
}

size_t PyFloatHandler::handleHash(PyContext& context, const PyObjPtr& self) const{
    return size_t(self.cast<PyObjFloat>()->value);
}

