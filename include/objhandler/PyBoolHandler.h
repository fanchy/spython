#ifndef _PY_BOOL_HANDLER_H_
#define _PY_BOOL_HANDLER_H_

#include <iostream>
#include <string>
#include <vector>
#include <map>
#include <vector>
#include <stdexcept>

#include "Base.h"
#include "singleton.h"

namespace ff {

class PyBoolHandler: public PyObjHandler{
public:
    virtual int getType() const {
        return PY_BOOL;
    }
    virtual std::string handleStr(const PyObjPtr& self) const;
    virtual bool handleBool(PyContext& context, const PyObjPtr& self) const;
    virtual bool handleEqual(PyContext& context, const PyObjPtr& self, const PyObjPtr& val) const;
    
    
};


}
#endif


