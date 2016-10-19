#ifndef _PY_IO_EXT_H_
#define _PY_IO_EXT_H_

#include "ExprAST.h"
#include "PyObj.h"

#include "StrTool.h"
#include <stdio.h>

namespace ff {
class PyIOData:public SafeTypeHelper<PyIOData, PyInstanceData>{
public:
    PyIOData():fp(NULL){
    }
    FILE* fp;
    std::string filename;
    std::string mode;
};
struct PyIOExt{
    static PyObjPtr file__init__(PyContext& context, std::vector<PyObjPtr>& argAssignVal){
        if (argAssignVal.size() < 2){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: file__init__() takes exactly >=1 argument (%u given)", argAssignVal.size()));
        }
        PyObjPtr& self = argAssignVal[0];
        PyAssertInstance(self);
        
        std::string filename = PyCppUtil::toStr(argAssignVal[1]);
        
        std::string openArgs;
        if (argAssignVal.size() >= 3){
            openArgs = PyCppUtil::toStr(argAssignVal[2]);
        }
        FILE* f = ::fopen(filename.c_str(), openArgs.c_str());
        if (f){
            PyIOData* instanceData = new PyIOData();
            instanceData->fp = f;
            instanceData->filename = filename;
            instanceData->mode = openArgs;
            self.cast<PyObjClassInstance>()->instanceData = instanceData;
        }
        return PyObjTool::buildTrue();
    }
    static PyObjPtr file__str__(PyContext& context, std::vector<PyObjPtr>& argAssignVal){
        if (argAssignVal.size() != 1){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: file__str__() takes exactly 1 argument (%u given)", argAssignVal.size()));
        }
        PyObjPtr& self = argAssignVal[0];
        PyAssertInstance(self);
        PyIOData* instanceData = self.cast<PyObjClassInstance>()->instanceData->cast<PyIOData>();
        char buff[512];
        snprintf(buff, sizeof(buff), "<open file '%s', mode '%s' at %p>", 
                    instanceData->filename.c_str(), instanceData->mode.c_str(), self.get());
        
        return PyCppUtil::genStr(buff);
    }
    static PyObjPtr file_open(PyContext& context, std::vector<PyObjPtr>& argAssignVal){
        if (argAssignVal.size() < 1){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: file_open() takes exactly >=1 argument (%u given)", argAssignVal.size()));
        }
        PyObjPtr classObj = context.getBuiltin("file");
        std::vector<PyObjPtr> args = argAssignVal;
        PyObjPtr ret = PyCppUtil::callPyfunc(context, classObj, args);
        if (!ret.cast<PyObjClassInstance>()->instanceData){
            PY_RAISE_STR(context, PyCppUtil::strFormat("IOError: [Errno 2] No such file or directory: '%s'", 
                                    PyCppUtil::toStr(argAssignVal[0]).c_str()));
        }
        return ret;
    }
    static bool init(PyContext& pycontext){
        {
            PyObjPtr strClass = PyObjClassDef::build(pycontext, "file");
            
            PyCppUtil::setAttr(pycontext, strClass, "__init__", PyCppUtil::genFunc(PyIOExt::file__init__, "__init__"));
            PyCppUtil::setAttr(pycontext, strClass, "__str__", PyCppUtil::genFunc(PyIOExt::file__str__, "__str__"));
            pycontext.addBuiltin("file", strClass);
        }
        pycontext.addBuiltin("open", PyCppUtil::genFunc(PyIOExt::file_open, "open"));
        return true;
    }
};
    
}
#endif

