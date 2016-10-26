#ifndef _PY_RANDOM_EXT_H_
#define _PY_RANDOM_EXT_H_

#include "ExprAST.h"
#include "PyObj.h"

#include "StrTool.h"

#include <libgen.h>
#include <algorithm>

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
        return PyCppUtil::genInt(context, randint(minVal, maxVal));
    }
    static PyObjPtr random_choice(PyContext& context, std::vector<PyObjPtr>& argAssignVal){
        if (argAssignVal.size() != 1){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: choice() takes exactly 1 argument (%u given)", argAssignVal.size()));
        }
        PyObjPtr& sequence = argAssignVal[0];
        PyInt size = sequence->getHandler()->handleLen(context, sequence);
        if (size <= 0){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: choice() sequence can't be empty"));
        }
        PyInt nIndex = randint(0, size - 1);
        IterUtil iterUtil(context, sequence);

        for (PyInt i = 0; i < size; ++i){
            PyObjPtr key = iterUtil.next();
            if (i < nIndex){
                continue;
            }
            return key;
        }
        return NULL;
    }
    static PyObjPtr pyrandom_shuffle(PyContext& context, std::vector<PyObjPtr>& argAssignVal){
        if (argAssignVal.size() != 1){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: shuffle() takes exactly 1 argument (%u given)", argAssignVal.size()));
        }
        PyObjPtr& sequence = argAssignVal[0];
        PyAssertList(sequence);
        
        sequence.cast<PyObjList>()->randShuffle();
        return sequence;
    }
    static PyObjPtr random_sample(PyContext& context, std::vector<PyObjPtr>& argAssignVal){
        if (argAssignVal.size() != 2){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: sample() takes exactly 2 argument (%u given)", argAssignVal.size()));
        }
        PyObjPtr& sequence = argAssignVal[0];
        PyInt n = PyCppUtil::toInt(argAssignVal[1]);
        PyObjPtr ret = new PyObjList();
        
        PyInt size = sequence->getHandler()->handleLen(context, sequence);
        if (size < n){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: sample() sequence size not enough"));
        }
        std::vector<PyObjPtr> seqVal;
        if (PyCheckTuple(sequence)){
            seqVal = sequence.cast<PyObjTuple>()->getValue();
        }
        else if(PyCheckList(sequence)){
            seqVal = sequence.cast<PyObjList>()->getValue();
        }
        else{
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: sample() sequence list/tuple needed"));
        }
        std::random_shuffle(seqVal.begin(), seqVal.end());
        seqVal.erase(seqVal.begin() + n, seqVal.end());
        ret.cast<PyObjList>()->getValue() = seqVal;
        return ret;
    }
    static bool init(PyContext& pycontext){
        {
            PyObjPtr mod = PyObjModule::BuildModule(pycontext, "random", "built-in");
            PyCppUtil::setAttr(pycontext, mod, "random", PyCppUtil::genFunc(PyRandomExt::random_random, "random"));
            PyCppUtil::setAttr(pycontext, mod, "uniform", PyCppUtil::genFunc(PyRandomExt::random_uniform, "uniform"));
            PyCppUtil::setAttr(pycontext, mod, "uniform", PyCppUtil::genFunc(PyRandomExt::random_uniform, "uniform"));
            PyCppUtil::setAttr(pycontext, mod, "randint", PyCppUtil::genFunc(PyRandomExt::random_randint, "randint"));
            PyCppUtil::setAttr(pycontext, mod, "choice", PyCppUtil::genFunc(PyRandomExt::random_choice, "choice"));
            PyCppUtil::setAttr(pycontext, mod, "shuffle", PyCppUtil::genFunc(PyRandomExt::pyrandom_shuffle, "shuffle"));
            PyCppUtil::setAttr(pycontext, mod, "sample", PyCppUtil::genFunc(PyRandomExt::random_sample, "sample"));
            pycontext.addModule("random", mod);
        }
        return true;
    }
};
    
}
#endif

