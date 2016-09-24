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
            printf("eval Ê§°Ü£¡\n");
            return 0;
        }
        string strObj = PyObj::dump(spython.getPyContext(), spython.getPyContext().curstack);
        printf("%s", strObj.c_str());
    }
    catch(exception& e){
        printf("Traceback (most recent call last):\n");
        string traceback = PyOpsUtil::traceback(spython.getPyContext());
        printf("%s", traceback.c_str());
        printf("%s\n", e.what());
    }
    
    return 0;
}
