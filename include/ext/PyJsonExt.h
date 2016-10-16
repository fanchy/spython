#ifndef _PY_JSON_EXT_H_
#define _PY_JSON_EXT_H_

#include "ExprAST.h"
#include "PyObj.h"

#include "StrTool.h"

namespace ff {
struct PyJsonExt{
    static bool init(PyContext& pycontext){
        {
            PyObjPtr mod = PyObjModule::BuildModule(pycontext, "json", "built-in");
            
            pycontext.addModule("json", mod);
        }
        return true;
    }
};
    
}
#endif

