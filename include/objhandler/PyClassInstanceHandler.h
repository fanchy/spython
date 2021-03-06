#ifndef _PY_CLASS_INSTANCE_HANDLER_H_
#define _PY_CLASS_INSTANCE_HANDLER_H_

#include <iostream>
#include <string>
#include <vector>
#include <map>
#include <vector>
#include <stdexcept>

#include "Base.h"
#include "Singleton.h"
#include "objhandler/PyCommonHandler.h"

namespace ff {

class PyClassInstanceHandler: public PyCommonHandler{
public:
    PyClassInstanceHandler();
    
    virtual int getType() const {
        return PY_CLASS_INST;
    }
    virtual std::string handleStr(PyContext& context, const PyObjPtr& self) const;
    virtual bool handleBool(PyContext& context, const PyObjPtr& self) const;
    virtual PyObjPtr& handleCall(PyContext& context, PyObjPtr& self, std::vector<ArgTypeInfo>& allArgsVal, std::vector<PyObjPtr>& argAssignVal);
    
    ExprASTPtr __call__;
};


}
#endif


