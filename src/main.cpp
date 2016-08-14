#include <cstdlib>
#include <string.h>

#include "Scanner.h"
#include "Parser.h"
#include "PyObj.h"

using namespace std;
using namespace ff;

int main(int argc, char** argv) {
    string strCode;
    FILE* fp = ::fopen("./test.py", "r");
    if(NULL != fp)
    {
        char buf[2048];
        int n = fread(buf, 1, sizeof(buf), fp);
        ::fclose(fp);
        strCode.assign(buf, n);
        //printf("¶ÁÈ¡:\n%s\n", strCode.c_str());
    }
    else{
        printf("¶ÁÈ¡Ê§°Ü£¡\n");
    }

    Scanner scanner;
    scanner.tokenize(strCode);
    
    
    Parser parser;
    try{
        ExprASTPtr rootExpr = parser.parse(scanner);
    
        if (rootExpr){
            printf("%s\n", rootExpr->dump(0).c_str());

            PyContext context;
            context.curstack = new PyObjModule("__main__");
            
            PyObjPtr ret = rootExpr->eval(context);
            if (!ret){
                printf("eval Ê§°Ü£¡\n");
                return 0;
            }
            string strObj = context.curstack->dump();
            printf("ret:\n %s", strObj.c_str());
        }else{
            printf("parser.parse Ê§°Ü£¡\n");
        }
    }
    catch(exception& e){
        printf("%s\n", e.what());
    }
    
    return 0;
}
