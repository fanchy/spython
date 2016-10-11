#ifndef _PY_TIME_EXT_H_
#define _PY_TIME_EXT_H_

#include <time.h>
#include<sys/time.h>

#include "ExprAST.h"
#include "PyObj.h"

#include "StrTool.h"

namespace ff {
struct PyTimeExt{
    static PyObjPtr time_impl(PyContext& context, std::vector<PyObjPtr>& argAssignVal){
        if (argAssignVal.size() != 0){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: WeakRef__init__() takes exactly 0 argument (%u given)", argAssignVal.size()));
        }
        
        struct timeval curtm;
	    ::gettimeofday(&curtm, NULL);
	
	    double ret = curtm.tv_sec + double(curtm.tv_usec) / (1000 * 1000);
	    return PyCppUtil::genFloat(ret);
    }
    static bool init(PyContext& pycontext){
        {
            PyObjPtr mod = PyObjModule::BuildModule(pycontext, "time", "built-in");
            
            /*
            PyObjPtr objClass = PyObjClassDef::build(pycontext, "weakref");
            PyCppUtil::setAttr(pycontext, objClass, "__init__", PyCppUtil::genFunc(PyWeakExt::WeakRef__init__, "__init__"));
            PyCppUtil::setAttr(pycontext, objClass, "__call__", PyCppUtil::genFunc(PyWeakExt::weak__call__, "__call__"));
            
            PyCppUtil::setAttr(pycontext, mod, "time", objClass);
            */
            
            PyCppUtil::setAttr(pycontext, mod, "time", PyCppUtil::genFunc(PyTimeExt::time_impl, "time"));
            pycontext.addModule("time", mod);
        }
        return true;
    }
};
    
}
#endif

