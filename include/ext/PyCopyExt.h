#ifndef _PY_COPY_EXT_H_
#define _PY_COPY_EXT_H_

#include "ExprAST.h"
#include "PyObj.h"

#include "StrTool.h"
#include "Util.h"
namespace ff {
struct PyCopyExt{
    static PyObjPtr copy_copy(PyContext& context, std::vector<PyObjPtr>& argAssignVal){
        if (argAssignVal.size() != 1){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: copy() takes exactly 1 argument (%u given)", argAssignVal.size()));
        }
        return argAssignVal[0];
    }
    static PyObjPtr copy_deepcopy(PyContext& context, std::vector<PyObjPtr>& argAssignVal){
        if (argAssignVal.size() != 1){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: deepcopy() takes exactly 1 argument (%u given)", argAssignVal.size()));
        }
        return argAssignVal[0];
    }
    static bool init(PyContext& pycontext){
        {
            PyObjPtr mod = PyObjModule::BuildModule(pycontext, "copy", "built-in");
            PyCppUtil::setAttr(pycontext, mod, "copy", PyCppUtil::genFunc(PyCopyExt::copy_copy, "copy"));
            PyCppUtil::setAttr(pycontext, mod, "deepcopy", PyCppUtil::genFunc(PyCopyExt::copy_deepcopy, "deepcopy"));
            pycontext.addModule("copy", mod);
        }
        return true;
    }
};
    
}
#endif

