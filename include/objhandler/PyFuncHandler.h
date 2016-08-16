#ifndef _PY_FUNC_HANDLER_H_
#define _PY_FUNC_HANDLER_H_

#include <iostream>
#include <string>
#include <vector>
#include <map>
#include <vector>
#include <stdexcept>

#include "Base.h"
#include "singleton.h"

namespace ff {

class PyFuncHandler: public PyObjHandler{
public:
    virtual int getType() {
        return EXPR_FUNCDEF;
    }
    virtual std::string handleStr(PyObjPtr& self);
    virtual bool handleBool(PyContext& context, PyObjPtr& self);
    virtual bool handleEqual(PyContext& context, PyObjPtr& self, PyObjPtr& val);
    
};


}
#endif


