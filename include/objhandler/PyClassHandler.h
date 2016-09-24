#ifndef _PY_CLASS_HANDLER_H_
#define _PY_CLASS_HANDLER_H_

#include <iostream>
#include <string>
#include <vector>
#include <map>
#include <vector>
#include <stdexcept>

#include "Base.h"
#include "singleton.h"
#include "objhandler/PyCommonHandler.h"

namespace ff {

class PyClassHandler: public PyCommonHandler{
public:
    PyClassHandler();
    
    virtual int getType() const {
        return PY_CLASS_DEF;
    }
    virtual std::string handleStr(PyContext& context, const PyObjPtr& self) const;
    virtual bool handleBool(PyContext& context, const PyObjPtr& self) const;
    virtual bool handleEqual(PyContext& context, const PyObjPtr& self, const PyObjPtr& val) const;
    virtual PyObjPtr& handleCall(PyContext& context, PyObjPtr& self, std::vector<ArgTypeInfo>& allArgsVal, std::vector<PyObjPtr>& argAssignVal);
    virtual bool handleIsInstance(PyContext& context, PyObjPtr& self, PyObjPtr& val);
    ExprASTPtr __init__;
};


}
#endif


