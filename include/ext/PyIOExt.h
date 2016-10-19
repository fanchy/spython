#ifndef _PY_IO_EXT_H_
#define _PY_IO_EXT_H_

#include "ExprAST.h"
#include "PyObj.h"

#include "StrTool.h"
#include <stdio.h>

namespace ff {
class PyIOData:public SafeTypeHelper<PyIOData, PyInstanceData>{
public:
    PyIOData():fp(NULL){
    }
    ~PyIOData(){
        closeFile();
    }
    void closeFile(){
        if (fp){
            ::fclose(fp);
            fp = NULL;
        }
    }
    FILE* fp;
    std::string filename;
    std::string mode;
};
struct PyIOExt{
    static void assertFileOpen(PyContext& context, PyIOData* p){
        if (!p->fp){
            PY_RAISE_STR(context, PyCppUtil::strFormat("ValueError: I/O operation on closed file"));
        }
    }
    static PyObjPtr file__init__(PyContext& context, std::vector<PyObjPtr>& argAssignVal){
        if (argAssignVal.size() < 2){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: file__init__() takes exactly >=1 argument (%u given)", argAssignVal.size()));
        }
        PyObjPtr& self = argAssignVal[0];
        PyAssertInstance(self);
        
        std::string filename = PyCppUtil::toStr(argAssignVal[1]);
        
        std::string openArgs;
        if (argAssignVal.size() >= 3){
            openArgs = PyCppUtil::toStr(argAssignVal[2]);
        }
        if (openArgs.empty()){
            openArgs = "r";
        }
        FILE* f = ::fopen(filename.c_str(), openArgs.c_str());
        if (f){
            PyIOData* instanceData = new PyIOData();
            instanceData->fp = f;
            instanceData->filename = filename;
            instanceData->mode = openArgs;
            self.cast<PyObjClassInstance>()->instanceData = instanceData;
        }
        return PyObjTool::buildTrue();
    }
    static PyObjPtr file__str__(PyContext& context, PyObjPtr& self, std::vector<PyObjPtr>& argAssignVal){
        if (argAssignVal.size() != 0){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: file__str__() takes exactly 0 argument (%u given)", argAssignVal.size()));
        }
        PyAssertInstance(self);
        PyIOData* instanceData = self.cast<PyObjClassInstance>()->instanceData->cast<PyIOData>();
        char buff[512];
        if (instanceData->fp){
            snprintf(buff, sizeof(buff), "<open file '%s', mode '%s' at %p>", 
                    instanceData->filename.c_str(), instanceData->mode.c_str(), self.get());
        }
        else{
            snprintf(buff, sizeof(buff), "<closed file '%s', mode '%s' at %p>", 
                    instanceData->filename.c_str(), instanceData->mode.c_str(), self.get());
        }
        
        return PyCppUtil::genStr(buff);
    }
    static PyObjPtr file_open(PyContext& context, std::vector<PyObjPtr>& argAssignVal){
        if (argAssignVal.size() < 1){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: file_open() takes exactly >=1 argument (%u given)", argAssignVal.size()));
        }
        PyObjPtr classObj = context.getBuiltin("file");
        std::vector<PyObjPtr> args = argAssignVal;
        PyObjPtr ret = PyCppUtil::callPyfunc(context, classObj, args);
        if (!ret.cast<PyObjClassInstance>()->instanceData){
            PY_RAISE_STR(context, PyCppUtil::strFormat("IOError: [Errno 2] No such file or directory: '%s'", 
                                    PyCppUtil::toStr(argAssignVal[0]).c_str()));
        }
        return ret;
    }
    static PyObjPtr file_close(PyContext& context, PyObjPtr& self, std::vector<PyObjPtr>& argAssignVal){
        if (argAssignVal.size() != 0){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: close() takes exactly 0 argument (%u given)", argAssignVal.size()));
        }
        PyAssertInstance(self);
        self.cast<PyObjClassInstance>()->instanceData->cast<PyIOData>()->closeFile();
        return PyObjTool::buildTrue();
    }
    static PyObjPtr file_read(PyContext& context, PyObjPtr& self, std::vector<PyObjPtr>& argAssignVal){
        if (argAssignVal.size() != 0 && argAssignVal.size() != 1){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: read() takes exactly 1 argument (%u given)", argAssignVal.size()));
        }
        PyAssertInstance(self);
        PyIOData* instanceData = self.cast<PyObjClassInstance>()->instanceData->cast<PyIOData>();
        assertFileOpen(context, instanceData);
        
        char buff[512] = {0};
        PyObjPtr ret = PyCppUtil::genStr("");
        if (argAssignVal.empty()){
            while (!::feof(instanceData->fp)){
                size_t n = ::fread(buff, 1, sizeof(buff), instanceData->fp);
                ret.cast<PyObjStr>()->append(buff, n);
            }
        }
        else{
            PyInt size = PyCppUtil::toInt(argAssignVal[0]);
            
            while (size > 0 && !::feof(instanceData->fp)){
                PyInt readSize = sizeof(buff);
                if (readSize > size){
                    readSize = size;
                }
                size -= readSize;
                size_t n = ::fread(buff, 1, readSize, instanceData->fp);
                ret.cast<PyObjStr>()->append(buff, n);
            }
        }
        return ret;
    }
    static PyObjPtr file_readline(PyContext& context, PyObjPtr& self, std::vector<PyObjPtr>& argAssignVal){
        if (argAssignVal.size() != 0){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: readline() takes exactly 0 argument (%u given)", argAssignVal.size()));
        }
        PyAssertInstance(self);
        PyIOData* instanceData = self.cast<PyObjClassInstance>()->instanceData->cast<PyIOData>();
        assertFileOpen(context, instanceData);

        char buff[512] = {0};
        PyObjPtr ret = PyCppUtil::genStr("");
        if (!::feof(instanceData->fp)){
            if (::fgets(buff, sizeof(buff) - 1, instanceData->fp)){
               std::string s = buff;
               ret.cast<PyObjStr>()->append(s);
            }
        }
        return ret;
    }
    static PyObjPtr file_readlines(PyContext& context, PyObjPtr& self, std::vector<PyObjPtr>& argAssignVal){
        if (argAssignVal.size() != 0){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: readlines() takes exactly 0 argument (%u given)", argAssignVal.size()));
        }
        PyAssertInstance(self);
        PyIOData* instanceData = self.cast<PyObjClassInstance>()->instanceData->cast<PyIOData>();
        assertFileOpen(context, instanceData);

        char buff[512] = {0};
        PyObjPtr ret = new PyObjList();
        
        std::string s;
        while (!::feof(instanceData->fp)){
            if (::fgets(buff, sizeof(buff) - 1, instanceData->fp)){
               s = buff;
               ret.cast<PyObjList>()->append(PyCppUtil::genStr(s));
            }
        }
        return ret;
    }
    
    static PyObjPtr file_write(PyContext& context, PyObjPtr& self, std::vector<PyObjPtr>& argAssignVal){
        if (argAssignVal.size() != 1 && argAssignVal.size() != 2){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: write() takes exactly 1 argument (%u given)", argAssignVal.size()));
        }
        PyAssertInstance(self);
        PyIOData* instanceData = self.cast<PyObjClassInstance>()->instanceData->cast<PyIOData>();
        assertFileOpen(context, instanceData);
        
        std::string data = PyCppUtil::toStr(argAssignVal[0]);
        PyInt nSize = (PyInt)data.size();
        if (argAssignVal.size() >= 2){
            nSize = PyCppUtil::toInt(argAssignVal[1]);
            if (nSize < 0){
                nSize = 0;
            }
        }
        ::fwrite(data.c_str(), nSize, 1, instanceData->fp);
        return PyObjTool::buildTrue();
    }
    
    static bool init(PyContext& pycontext){
        {
            PyObjPtr strClass = PyObjClassDef::build(pycontext, "file");
            
            PyCppUtil::setAttr(pycontext, strClass, "__init__", PyCppUtil::genFunc(PyIOExt::file__init__, "__init__"));
            PyCppUtil::setAttr(pycontext, strClass, "__str__", PyCppUtil::genFunc(PyIOExt::file__str__, "__str__"));
            PyCppUtil::setAttr(pycontext, strClass, "close", PyCppUtil::genFunc(PyIOExt::file_close, "close"));
            PyCppUtil::setAttr(pycontext, strClass, "read", PyCppUtil::genFunc(PyIOExt::file_read, "read"));
            PyCppUtil::setAttr(pycontext, strClass, "write", PyCppUtil::genFunc(PyIOExt::file_write, "write"));
            PyCppUtil::setAttr(pycontext, strClass, "readline", PyCppUtil::genFunc(PyIOExt::file_readline, "readline"));
            PyCppUtil::setAttr(pycontext, strClass, "readlines", PyCppUtil::genFunc(PyIOExt::file_readlines, "readlines"));
            pycontext.addBuiltin("file", strClass);
        }
        pycontext.addBuiltin("open", PyCppUtil::genFunc(PyIOExt::file_open, "open"));
        return true;
    }
};
    
}
#endif

