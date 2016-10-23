#ifndef _PY_OS_EXT_H_
#define _PY_OS_EXT_H_

#include "ExprAST.h"
#include "PyObj.h"

#include "StrTool.h"
#include "Util.h"

#include <libgen.h>
#include <unistd.h>

namespace ff {
#ifdef linux
    #define LINE_SEP "\n"
    #define SEP "/"
#else
    #define LINE_SEP "\r\n"
    #define SEP "\\"
#endif
struct PyOsExt{
    static PyObjPtr path_getcwd(PyContext& context, std::vector<PyObjPtr>& argAssignVal){
        if (argAssignVal.size() != 0){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: getcwd() takes exactly 0 argument (%u given)", argAssignVal.size()));
        }
        std::string ret;
        char buffer[1024];
        const char* rets = ::getcwd(buffer, sizeof(buffer) - 1);
        if (rets){
            ret = rets;
        }
        return PyCppUtil::genStr(ret);
    }
    static PyObjPtr path_listdir(PyContext& context, std::vector<PyObjPtr>& argAssignVal){
        if (argAssignVal.size() != 1){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: listdir() takes exactly 1 argument (%u given)", argAssignVal.size()));
        }
        std::string path = PyCppUtil::toStr(argAssignVal[0]);
        
        std::vector<std::string> allFiles;
        if (!Util::getAllFileInDir(path, allFiles)){
        }
        PyObjPtr ret = new PyObjTuple();
        
        for (size_t i = 2; i < allFiles.size(); ++i){
            ret.cast<PyObjTuple>()->append(PyCppUtil::genStr(allFiles[i]));
        }
        return ret;
    }
    static PyObjPtr path_remove(PyContext& context, std::vector<PyObjPtr>& argAssignVal){
        if (argAssignVal.size() != 1){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: remove() takes exactly 1 argument (%u given)", argAssignVal.size()));
        }
        std::string path = PyCppUtil::toStr(argAssignVal[0]);
        int nRet = ::remove(path.c_str());
        return PyCppUtil::genInt(nRet);
    }
    static PyObjPtr path_system(PyContext& context, std::vector<PyObjPtr>& argAssignVal){
        if (argAssignVal.size() != 1){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: system() takes exactly 1 argument (%u given)", argAssignVal.size()));
        }
        std::string path = PyCppUtil::toStr(argAssignVal[0]);
        
        int nRet = ::system(path.c_str());
        return PyCppUtil::genInt(nRet);
    }
    
    static PyObjPtr path_split(PyContext& context, std::vector<PyObjPtr>& argAssignVal){
        if (argAssignVal.size() != 1){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: split() takes exactly 1 argument (%u given)", argAssignVal.size()));
        }
        
        PyObjPtr ret = new PyObjTuple();
        std::string path = PyCppUtil::toStr(argAssignVal[0]);
        std::string::size_type pos = path.rfind(SEP);
        std::string s;
        if (pos != std::string::npos){
            s.assign(path.begin(), path.begin() + pos - 1);
            ret.cast<PyObjTuple>()->append(PyCppUtil::genStr(s));
            s.assign(path.begin() + pos + 1, path.end());
            ret.cast<PyObjTuple>()->append(PyCppUtil::genStr(s));
        }
        return ret;
    }
    static PyObjPtr path_isdir(PyContext& context, std::vector<PyObjPtr>& argAssignVal){
        if (argAssignVal.size() != 1){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: isdir() takes exactly 1 argument (%u given)", argAssignVal.size()));
        }
        
        std::string path = PyCppUtil::toStr(argAssignVal[0]);
        if (Util::isDir(path)){
            return PyObjTool::buildTrue();
        }
        return PyObjTool::buildFalse();
    }
    static PyObjPtr path_isfile(PyContext& context, std::vector<PyObjPtr>& argAssignVal){
        if (argAssignVal.size() != 1){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: isfile() takes exactly 1 argument (%u given)", argAssignVal.size()));
        }
        
        std::string path = PyCppUtil::toStr(argAssignVal[0]);
        if (Util::isFile(path)){
            return PyObjTool::buildTrue();
        }
        return PyObjTool::buildFalse();
    }
    static PyObjPtr path_exists(PyContext& context, std::vector<PyObjPtr>& argAssignVal){
        if (argAssignVal.size() != 1){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: exists() takes exactly 1 argument (%u given)", argAssignVal.size()));
        }
        
        std::string path = PyCppUtil::toStr(argAssignVal[0]);
        if (Util::isFile(path) || Util::isDir(path)){
            return PyObjTool::buildTrue();
        }
        return PyObjTool::buildFalse();
    }
    
    static PyObjPtr path_dirname(PyContext& context, std::vector<PyObjPtr>& argAssignVal){
        if (argAssignVal.size() != 1){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: dirname() takes exactly 1 argument (%u given)", argAssignVal.size()));
        }
        std::string ret;
       
        std::string filename = PyCppUtil::toStr(argAssignVal[0]);
        std::vector<char> tmpBuff;
        tmpBuff.insert(tmpBuff.begin(), filename.begin(), filename.end());
        tmpBuff.push_back(0);
        const char* rets = ::dirname((char*)(&tmpBuff[0]));
        
        if (rets){
            ret = rets;
        }
        return PyCppUtil::genStr(ret);
    }
    static PyObjPtr path_basename(PyContext& context, std::vector<PyObjPtr>& argAssignVal){
        if (argAssignVal.size() != 1){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: basename() takes exactly 1 argument (%u given)", argAssignVal.size()));
        }
        std::string ret;
       
        std::string filename = PyCppUtil::toStr(argAssignVal[0]);
        std::vector<char> tmpBuff;
        tmpBuff.insert(tmpBuff.begin(), filename.begin(), filename.end());
        tmpBuff.push_back(0);
        const char* rets = ::basename((char*)(&tmpBuff[0]));
        
        if (rets){
            ret = rets;
        }
        return PyCppUtil::genStr(ret);
    }
    static bool init(PyContext& pycontext){
        {
            PyObjPtr mod = PyObjModule::BuildModule(pycontext, "os", "built-in");
            PyCppUtil::setAttr(pycontext, mod, "getcwd", PyCppUtil::genFunc(PyOsExt::path_getcwd, "getcwd"));
            PyCppUtil::setAttr(pycontext, mod, "listdir", PyCppUtil::genFunc(PyOsExt::path_listdir, "listdir"));
            PyCppUtil::setAttr(pycontext, mod, "remove", PyCppUtil::genFunc(PyOsExt::path_remove, "remove"));
            PyCppUtil::setAttr(pycontext, mod, "system", PyCppUtil::genFunc(PyOsExt::path_system, "system"));
            PyCppUtil::setAttr(pycontext, mod, "linesep", PyCppUtil::genStr(LINE_SEP));
            PyCppUtil::setAttr(pycontext, mod, "sep", PyCppUtil::genStr(SEP));
            
            {
                PyObjPtr path = PyObjClassDef::build(pycontext, "path");
                PyCppUtil::setAttr(pycontext, path, "split", PyCppUtil::genFunc(PyOsExt::path_split, "split"));
                PyCppUtil::setAttr(pycontext, path, "isdir", PyCppUtil::genFunc(PyOsExt::path_isdir, "isdir"));
                PyCppUtil::setAttr(pycontext, path, "isfile", PyCppUtil::genFunc(PyOsExt::path_isfile, "isfile"));
                PyCppUtil::setAttr(pycontext, path, "exists", PyCppUtil::genFunc(PyOsExt::path_exists, "exists"));
                PyCppUtil::setAttr(pycontext, path, "dirname", PyCppUtil::genFunc(PyOsExt::path_dirname, "dirname"));
                PyCppUtil::setAttr(pycontext, path, "basename", PyCppUtil::genFunc(PyOsExt::path_basename, "basename"));
                PyCppUtil::setAttr(pycontext, mod, "path", path);
            }
            pycontext.addModule("os", mod);
        }
        return true;
    }
};
    
}
#endif

