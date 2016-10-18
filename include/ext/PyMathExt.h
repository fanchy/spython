#ifndef _PY_MATH_EXT_H_
#define _PY_MATH_EXT_H_

#include "ExprAST.h"
#include "PyObj.h"

#include "StrTool.h"
#include <math.h>

namespace ff {
#define DECALIRE_MATH_FUNC_FLOAT(X) \
    static PyObjPtr math_##X(PyContext& context, std::vector<PyObjPtr>& argAssignVal){ \
        if (argAssignVal.size() != 1){ \
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: #X() takes exactly 1 argument (%u given)", argAssignVal.size())); \
        } \
        PyObjPtr& param = argAssignVal[0]; \
        PyFloat nRet = :: X(PyCppUtil::toFloat(param)); \
        return PyCppUtil::genFloat(nRet); \
    }

struct PyMathExt{
    DECALIRE_MATH_FUNC_FLOAT(acos);
    DECALIRE_MATH_FUNC_FLOAT(acosh);
    DECALIRE_MATH_FUNC_FLOAT(asin);
    DECALIRE_MATH_FUNC_FLOAT(asinh);
    DECALIRE_MATH_FUNC_FLOAT(atan);
    //DECALIRE_MATH_FUNC_FLOAT(atan2);
    DECALIRE_MATH_FUNC_FLOAT(atanh);
    
    DECALIRE_MATH_FUNC_FLOAT(ceil);
    DECALIRE_MATH_FUNC_FLOAT(cos);
    DECALIRE_MATH_FUNC_FLOAT(cosh);
    //DECALIRE_MATH_FUNC_FLOAT(degrees);
    
    
    
    
    //常数 e = 2.7128...	math.e
    //exp 
    DECALIRE_MATH_FUNC_FLOAT(fabs);
    DECALIRE_MATH_FUNC_FLOAT(floor);
    //DECALIRE_MATH_FUNC_FLOAT(fmod);
    //frexp
    //fsum
    //hypot
    //isinf
    //isnan
    //ldexp
    //log
    //DECALIRE_MATH_FUNC_FLOAT(log);
    //log10
    DECALIRE_MATH_FUNC_FLOAT(log10);
    //loglp
    //modf
    //返回常数 π (3.14159...)	math.pi
    //返回 xy	math.pow(x,y)
    //將 x(角度) 转成弧长，与 degrees 为反函数	math.radians(d)
    //math.sin(x)
    //	math.sinh(x)
    //	math.sqrt(x)
    //	math.tan(x)
    //math.tanh(x)
    //	math.trunc(x)
    DECALIRE_MATH_FUNC_FLOAT(sin);
    DECALIRE_MATH_FUNC_FLOAT(sinh);
    DECALIRE_MATH_FUNC_FLOAT(sqrt);
    DECALIRE_MATH_FUNC_FLOAT(tan);
    DECALIRE_MATH_FUNC_FLOAT(tanh);
    DECALIRE_MATH_FUNC_FLOAT(trunc);
    
    static bool init(PyContext& pycontext){
        {
            PyObjPtr mod = PyObjModule::BuildModule(pycontext, "math", "built-in");
            PyCppUtil::setAttr(pycontext, mod, "e", PyCppUtil::genFloat(2.718281828459045));
            PyCppUtil::setAttr(pycontext, mod, "pi", PyCppUtil::genFloat(3.141592653589793));
            PyCppUtil::setAttr(pycontext, mod, "acos", PyCppUtil::genFunc(PyMathExt::math_acos, "acos"));
            PyCppUtil::setAttr(pycontext, mod, "acosh", PyCppUtil::genFunc(PyMathExt::math_acosh, "acosh"));
            PyCppUtil::setAttr(pycontext, mod, "asin", PyCppUtil::genFunc(PyMathExt::math_asin, "asin"));
            PyCppUtil::setAttr(pycontext, mod, "asinh", PyCppUtil::genFunc(PyMathExt::math_asinh, "asinh"));
            
            PyCppUtil::setAttr(pycontext, mod, "atan", PyCppUtil::genFunc(PyMathExt::math_atan, "atan"));
            PyCppUtil::setAttr(pycontext, mod, "atanh", PyCppUtil::genFunc(PyMathExt::math_atanh, "atanh"));
            PyCppUtil::setAttr(pycontext, mod, "ceil", PyCppUtil::genFunc(PyMathExt::math_ceil, "ceil"));
            PyCppUtil::setAttr(pycontext, mod, "cos", PyCppUtil::genFunc(PyMathExt::math_cos, "cos"));
            PyCppUtil::setAttr(pycontext, mod, "cosh", PyCppUtil::genFunc(PyMathExt::math_cosh, "cosh"));
            PyCppUtil::setAttr(pycontext, mod, "fabs", PyCppUtil::genFunc(PyMathExt::math_fabs, "fabs"));
            PyCppUtil::setAttr(pycontext, mod, "floor", PyCppUtil::genFunc(PyMathExt::math_floor, "floor"));
            PyCppUtil::setAttr(pycontext, mod, "log10", PyCppUtil::genFunc(PyMathExt::math_log10, "log10"));
            PyCppUtil::setAttr(pycontext, mod, "sin", PyCppUtil::genFunc(PyMathExt::math_sin, "sin"));
            PyCppUtil::setAttr(pycontext, mod, "sinh", PyCppUtil::genFunc(PyMathExt::math_sinh, "sinh"));
            PyCppUtil::setAttr(pycontext, mod, "sqrt", PyCppUtil::genFunc(PyMathExt::math_sqrt, "sqrt"));
            PyCppUtil::setAttr(pycontext, mod, "tanh", PyCppUtil::genFunc(PyMathExt::math_tanh, "tanh"));
            PyCppUtil::setAttr(pycontext, mod, "trunc", PyCppUtil::genFunc(PyMathExt::math_trunc, "trunc"));
    
            pycontext.addModule("math", mod);
        }
        return true;
    }
};
    
}
#endif

