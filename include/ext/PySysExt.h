#ifndef _PY_SYS_EXT_H_
#define _PY_SYS_EXT_H_

#include "ExprAST.h"
#include "PyObj.h"

#include "StrTool.h"

namespace ff {
struct PySysExt{
    static bool init(PyContext& pycontext){
        {
            PyObjPtr mod = PyObjModule::BuildModule(pycontext, "sys", "built-in");
            PyCppUtil::setAttr(pycontext, mod, "path", pycontext.syspath);
            PyCppUtil::setAttr(pycontext, mod, "argv", new PyObjTuple());
            PyCppUtil::setAttr(pycontext, mod, "version_info", new PyObjTuple());
            pycontext.addModule("sys", mod);
        }
        return true;
    }
};
    
}
#endif

