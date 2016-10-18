#ifndef _PY_RANDOM_EXT_H_
#define _PY_RANDOM_EXT_H_

#include "ExprAST.h"
#include "PyObj.h"

#include "StrTool.h"

#include <libgen.h>

namespace ff {
struct PyRandomExt{
    static PyInt randint(PyInt nMin, PyInt nMax){
        ::srand((unsigned)::time(NULL));
        return rand() % (nMax + 1 - nMin) + nMin;
    }
    static PyObjPtr random_random(PyContext& context, std::vector<PyObjPtr>& argAssignVal){
        if (argAssignVal.size() != 0){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: random() takes exactly 0 argument (%u given)", argAssignVal.size()));
        }
        ::srand(::time(NULL));
        PyFloat ret = (PyFloat)rand() / (RAND_MAX + 1.0);
        return PyCppUtil::genFloat(ret);
    }
    static PyObjPtr random_uniform(PyContext& context, std::vector<PyObjPtr>& argAssignVal){
        if (argAssignVal.size() != 2){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: uniform() takes exactly 2 argument (%u given)", argAssignVal.size()));
        }
        ::srand(::time(NULL));
        PyFloat minVal = PyCppUtil::toFloat(argAssignVal[0]);
        PyFloat maxVal = PyCppUtil::toFloat(argAssignVal[1]);
        
        if (minVal > maxVal){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: uniform() takes exactly arg invalid"));
        }
        
        PyFloat ret = (PyFloat)rand() / (RAND_MAX);
        ret = minVal + (maxVal - minVal) * ret;
        return PyCppUtil::genFloat(ret);
    }
    static PyObjPtr random_randint(PyContext& context, std::vector<PyObjPtr>& argAssignVal){
        if (argAssignVal.size() != 2){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: randint() takes exactly 2 argument (%u given)", argAssignVal.size()));
        }
        PyInt minVal = PyCppUtil::toInt(argAssignVal[0]);
        PyInt maxVal = PyCppUtil::toInt(argAssignVal[1]);
        
        if (minVal > maxVal){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: uniform() takes exactly arg invalid"));
        }
        return PyCppUtil::genInt(randint(minVal, maxVal));
    }
    static bool init(PyContext& pycontext){
        {
            PyObjPtr mod = PyObjModule::BuildModule(pycontext, "random", "built-in");
            PyCppUtil::setAttr(pycontext, mod, "random", PyCppUtil::genFunc(PyRandomExt::random_random, "random"));
            PyCppUtil::setAttr(pycontext, mod, "uniform", PyCppUtil::genFunc(PyRandomExt::random_uniform, "uniform"));
            PyCppUtil::setAttr(pycontext, mod, "uniform", PyCppUtil::genFunc(PyRandomExt::random_uniform, "uniform"));
            PyCppUtil::setAttr(pycontext, mod, "randint", PyCppUtil::genFunc(PyRandomExt::random_randint, "randint"));
            pycontext.addModule("random", mod);
        }
        return true;
    }
};
    
}
#endif

