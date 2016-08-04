#include "OldParser.h"

#include <cstdlib>
#include <string.h>

#include "Scanner.h"
#include "Parser.h"

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
    ExprASTPtr rootExpr = parser.parse(scanner);
    
    if (rootExpr){
        rootExpr->dump(0);
    }else{
        printf("parser.parse Ê§°Ü£¡\n");
    }
    
    return 0;
    PyObjPtr mainMod = new PyObjModule("__main__");
    ParseHelper parserHelper(strCode);
    ParseTool tool(mainMod);
    try{
        tool.MainLoop(parserHelper);
    }
    catch(exception& e){
        fprintf(stderr, "exception=%s\n", e.what());
    }
    
    if (argc >= 2 && string(argv[1]) == "-dump")
        mainMod->dump();
	return 0;
}
