#ifndef _PY_BUILTIN_TYPE_HANDLER_H_
#define _PY_BUILTIN_TYPE_HANDLER_H_

#include <iostream>
#include <string>
#include <vector>
#include <map>
#include <vector>
#include <stdexcept>

#include "Base.h"
#include "singleton.h"

namespace ff {

class PyBuiltinTypeHandler: public PyObjHandler{
public:
    virtual int getType() const {
        return PY_BUILTIN_TYPE;
    }
    virtual std::string handleStr(PyContext& context, const PyObjPtr& self) const;
    virtual bool handleBool(PyContext& context, const PyObjPtr& self) const;
    virtual bool handleEqual(PyContext& context, const PyObjPtr& self, const PyObjPtr& val) const;
    virtual PyObjPtr& handleCall(PyContext& context, PyObjPtr& self, std::vector<ArgTypeInfo>& allArgsVal, std::vector<PyObjPtr>& argAssignVal);
    virtual bool handleIsInstance(PyContext& context, PyObjPtr& self, PyObjPtr& val);
};


}
#endif


