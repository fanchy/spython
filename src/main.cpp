#include "OldParser.h"

#include <cstdlib>
#include <string.h>
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
