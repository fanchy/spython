#ifndef _PY_SPYTHON_H_
#define _PY_SPYTHON_H_

#include "Base.h"
namespace ff {

class SPython
{
public:
    SPython();
    PyContext& getPyContext() {
        return pycontext;
    }
    
    PyObjPtr importFile(const std::string& modname);
public:
    PyContext     pycontext;
};

}
#endif

