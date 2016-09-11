#include <cstdlib>
#include <string.h>

#include "Scanner.h"
#include "Parser.h"
#include "PyObj.h"
#include "StrTool.h"

using namespace std;
using namespace ff;

int main(int argc, char** argv) {
    PyContext context;
    Scanner scanner;
    string path = "./test.py";
    int nFileId = context.allocFileIdByPath(path);
    scanner.tokenizeFile(path, nFileId);
    
    
    Parser parser;
    ExprASTPtr rootExpr;
    try{
        rootExpr = parser.parse(scanner);
    
        if (rootExpr){
            //printf("%s\n", rootExpr->dump(0).c_str());

            context.curstack = new PyObjModule("__main__");
            
            PyObjPtr ret = rootExpr->eval(context);
            if (!ret){
                printf("eval Ê§°Ü£¡\n");
                return 0;
            }
            //string strObj = PyObj::dump(context.curstack);
            //printf("ret:\n %s", strObj.c_str());
        }else{
            printf("parser.parse Ê§°Ü£¡\n");
        }
    }
    catch(exception& e){
        printf("Traceback (most recent call last):\n");
        for (list<ExprAST*>::iterator it = context.exprTrace.begin(); it != context.exprTrace.end(); ++it){
            ExprAST* e = *it;
            if (!e)
                continue;
            printf("  File \"%s\", line %d\n", context.getFileId2Path(e->lineInfo.fileId).c_str(), e->lineInfo.nLine);
            string lineCode = StrTool::trim(scanner.getLineCode(e->lineInfo.nLine));
            printf("    %s\n", lineCode.c_str());
        }
        printf("%s\n", e.what());
    }
    
    return 0;
}
