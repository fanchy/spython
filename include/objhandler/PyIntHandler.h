#ifndef _PY_INT_HANDLER_H_
#define _PY_INT_HANDLER_H_

#include <iostream>
#include <string>
#include <vector>
#include <map>
#include <vector>
#include <stdexcept>

#include "Base.h"
#include "singleton.h"

namespace ff {

class PyIntHandler: public PyObjHandler{
public:
    virtual int getType() {
        return PY_INT;
    }
    virtual std::string handleStr(PyObjPtr& self);
    virtual bool handleBool(PyContext& context, PyObjPtr& self);
    virtual bool handleEqual(PyContext& context, PyObjPtr& self, PyObjPtr& val);
    virtual bool handleLessEqual(PyContext& context, PyObjPtr& self, PyObjPtr& val);
    virtual bool handleGreatEqual(PyContext& context, PyObjPtr& self, PyObjPtr& val);
    
    virtual PyObjPtr& handleAdd(PyContext& context, PyObjPtr& self, PyObjPtr& val);
    virtual PyObjPtr& handleSub(PyContext& context, PyObjPtr& self, PyObjPtr& val);
    virtual PyObjPtr& handleMul(PyContext& context, PyObjPtr& self, PyObjPtr& val);
    virtual PyObjPtr& handleDiv(PyContext& context, PyObjPtr& self, PyObjPtr& val);
    virtual PyObjPtr& handleMod(PyContext& context, PyObjPtr& self, PyObjPtr& val);
    
};


}
#endif


