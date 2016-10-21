#include <cstdlib>
#include <string.h>

#include "SPython.h"
#include "ExprAST.h"
#include "PyObj.h"

using namespace std;
using namespace ff;

int main(int argc, char** argv) {
    SPython spython;
    
    try{
        if (argc <= 1){
            printf("usage spython xx.py\n");
            return 0;
        }
        PyObjPtr sys = spython.pycontext.getModule("sys");
        PyObjPtr sysargv = PyCppUtil::getAttr(spython.pycontext, sys, "argv");
        if (PyCheckTuple(sysargv)){
            for (int i = 1; i < argc; ++i){
                sysargv.cast<PyObjTuple>()->append(PyCppUtil::genStr(argv[i]));
            }
        }
        
        PyObjPtr ret = spython.importFile(argv[1], "__main__");
        if (!ret){
            printf("eval Ê§°Ü£¡\n");
            return 0;
        }
        if (argc >= 3 && string(argv[2]) == "-dump"){
            string strObj = PyObj::dump(spython.getPyContext(), spython.getPyContext().curstack);
            printf("%s", strObj.c_str());
        }
        
    }
    catch(PyExceptionSignal& e){
        printf("Traceback (most recent call last):\n");
        string traceback = PyOpsUtil::traceback(spython.getPyContext());
        printf("%s", traceback.c_str());
        PyObjPtr v = spython.getPyContext().getCacheResult();
        if (v){
            string info = v->getHandler()->handleStr(spython.getPyContext(), v);
            printf("%s\n", info.c_str());
        }
    }
    catch(exception& e){
        printf("Traceback (most recent call last):\n");
        string traceback = PyOpsUtil::traceback(spython.getPyContext());
        printf("%s", traceback.c_str());
        printf("%s\n", e.what());
    }
    
    return 0;
}
