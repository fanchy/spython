#ifndef _PY_OS_EXT_H_
#define _PY_OS_EXT_H_

#include "ExprAST.h"
#include "PyObj.h"

#include "StrTool.h"

#include <libgen.h>

namespace ff {
struct PyOsExt{
    static PyObjPtr path_dirname(PyContext& context, std::vector<PyObjPtr>& argAssignVal){
        if (argAssignVal.size() != 1){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: dirname() takes exactly 1 argument (%u given)", argAssignVal.size()));
        }
        std::string ret;
       
        std::string filename = PyCppUtil::toStr(argAssignVal[0]);
        std::vector<char> tmpBuff;
        tmpBuff.insert(tmpBuff.begin(), filename.begin(), filename.end());

        const char* rets = ::dirname((char*)(&tmpBuff[0]));
        
        if (rets){
            ret = rets;
        }
        return PyCppUtil::genStr(ret);
    }
    static bool init(PyContext& pycontext){
        {
            PyObjPtr mod = PyObjModule::BuildModule(pycontext, "os", "built-in");
            {
                PyObjPtr path = PyObjClassDef::build(pycontext, "path");
                PyCppUtil::setAttr(pycontext, path, "dirname", PyCppUtil::genFunc(PyOsExt::path_dirname, "dirname"));
                PyCppUtil::setAttr(pycontext, mod, "path", path);
            }
            pycontext.addModule("os", mod);
        }
        return true;
    }
};
    
}
#endif

