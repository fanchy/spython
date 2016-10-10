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
        PyObjPtr ret = spython.importFile("test");
        if (!ret){
            printf("eval ʧ�ܣ�\n");
            return 0;
        }
        if (argc >= 1){
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
