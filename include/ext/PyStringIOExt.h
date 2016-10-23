#ifndef _PY_STRING_IO_EXT_H_
#define _PY_STRING_IO_EXT_H_

#include "ExprAST.h"
#include "PyObj.h"

#include "StrTool.h"

namespace ff {
class PyStringIOData:public SafeTypeHelper<PyStringIOData, PyInstanceData>{
public:
    PyStringIOData():nIndex(0){
    }
    int nIndex;
    std::string buff;
};

struct PyStringIOExt{
    static PyObjPtr StringIO__init__(PyContext& context, std::vector<PyObjPtr>& argAssignVal){
        if (argAssignVal.size() < 1){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: StringIO__init__() takes exactly 1 argument (%u given)", argAssignVal.size()));
        }
        PyObjPtr& iterself = argAssignVal[0];
        PyAssertInstance(iterself);

        PyStringIOData* instanceData = new PyStringIOData();
        iterself.cast<PyObjClassInstance>()->instanceData = instanceData;
        if (argAssignVal.size() >= 2){
            PyObjPtr& src = argAssignVal[1];
            if (PyCheckStr(src)){
                instanceData->buff += PyCppUtil::toStr(argAssignVal[1]);
            }
            else{
                std::vector<PyObjPtr> argsnew;
                //std::string dumps = src->getHandler()->handleStr(context, src);
                PyObjPtr data = PyCppUtil::callPyObjfunc(context, src, "getvalue", argsnew);
                instanceData->buff += PyCppUtil::toStr(data);
            }
        }
        return PyObjTool::buildTrue();
    }
    static PyObjPtr StringIO_write(PyContext& context, PyObjPtr& self, std::vector<PyObjPtr>& argAssignVal){
        if (argAssignVal.size() < 1){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: StringIO__init__() takes exactly 1 argument (%u given)", argAssignVal.size()));
        }
        PyAssertInstance(self);
        PyObjPtr& param = argAssignVal[0];
        

        PyStringIOData* instanceData = self.cast<PyObjClassInstance>()->instanceData->cast<PyStringIOData>();
        std::string paramStr = PyCppUtil::toStr(param);
        instanceData->buff.append(paramStr.c_str(), paramStr.size());
        //printf("StringIO_write %d\n", int(instanceData->buff.size()));
        return self;
    }
    static PyObjPtr StringIO_getvalue(PyContext& context, PyObjPtr& self, std::vector<PyObjPtr>& argAssignVal){
        if (argAssignVal.size() != 0){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: StringIO__init__() takes exactly 0 argument (%u given)", argAssignVal.size()));
        }
        PyAssertInstance(self);

        PyStringIOData* instanceData = self.cast<PyObjClassInstance>()->instanceData->cast<PyStringIOData>();
        //printf("getvalue %s\n", PyCppUtil::hexstr(instanceData->buff).c_str());
        return PyCppUtil::genStr(instanceData->buff);
    }
    static PyObjPtr StringIO_read(PyContext& context, PyObjPtr& self, std::vector<PyObjPtr>& argAssignVal){
        if (argAssignVal.size() > 1){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: read() takes exactly 0/1 argument (%u given)", argAssignVal.size()));
        }
        PyAssertInstance(self);
        PyStringIOData* instanceData = self.cast<PyObjClassInstance>()->instanceData->cast<PyStringIOData>();
        
        PyInt n = instanceData->buff.size();
        if (argAssignVal.size() >= 1){
            n = PyCppUtil::toInt(argAssignVal[0]);
            if (n < 0){
                PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: read() size argument (%d given)", n));
            }
        }
        std::string ret;
        
        if (instanceData->nIndex < 0){
            instanceData->nIndex = 0;
        }
        if (instanceData->nIndex < (int)instanceData->buff.size()){
            if (instanceData->nIndex + n > (int)instanceData->buff.size()){
                n = (int)instanceData->buff.size() - instanceData->nIndex;
            }
            ret.assign(instanceData->buff.begin() + instanceData->nIndex, instanceData->buff.begin() + instanceData->nIndex + n);
            instanceData->nIndex += n;
            if (instanceData->nIndex > (int)instanceData->buff.size()){
                instanceData->nIndex = instanceData->buff.size();
            }
        }
        
        //printf("stringio.read %d %d %d %s\n", instanceData->nIndex, int(n), int(ret.size()), PyCppUtil::hexstr(ret).c_str());

        return PyCppUtil::genStr(ret);
    }
    static PyObjPtr StringIO_close(PyContext& context, PyObjPtr& self, std::vector<PyObjPtr>& argAssignVal){
        if (argAssignVal.size() != 0){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: StringIO_close() takes exactly 0 argument (%u given)", argAssignVal.size()));
        }
        PyAssertInstance(self);

        PyStringIOData* instanceData = self.cast<PyObjClassInstance>()->instanceData->cast<PyStringIOData>();
        instanceData->buff.clear();
        return PyObjTool::buildTrue();
    }
    static PyObjPtr StringIO_truncate(PyContext& context, PyObjPtr& self, std::vector<PyObjPtr>& argAssignVal){
        if (argAssignVal.size() != 0){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: StringIO_truncate() takes exactly 0 argument (%u given)", argAssignVal.size()));
        }
        PyAssertInstance(self);

        PyStringIOData* instanceData = self.cast<PyObjClassInstance>()->instanceData->cast<PyStringIOData>();
        instanceData->buff.clear();
        return PyObjTool::buildTrue();
    }
    static PyObjPtr StringIO_seek(PyContext& context, PyObjPtr& self, std::vector<PyObjPtr>& argAssignVal){
        if (argAssignVal.size() != 1){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: StringIO_seek() takes exactly 1 argument (%u given)", argAssignVal.size()));
        }
        PyAssertInstance(self);
        int offset = PyCppUtil::toInt(argAssignVal[0]);
        int whence = 0;//0代表从文件开头开始算起，1代表从当前位置开始算起，2代表从文件末尾算起。
        if (argAssignVal.size() >= 2){
            whence = PyCppUtil::toInt(argAssignVal[1]);
        }
        PyStringIOData* instanceData = self.cast<PyObjClassInstance>()->instanceData->cast<PyStringIOData>();
        if (whence == 0){
            instanceData->nIndex = offset;
        }
        else if (whence == 1){
            instanceData->nIndex += offset;
        }
        else{
            instanceData->nIndex = instanceData->buff.size() - 1;
            instanceData->nIndex += offset;
        }
        return PyObjTool::buildTrue();
    }
    
    static bool init(PyContext& pycontext){
        {
            PyObjPtr mod = PyObjModule::BuildModule(pycontext, "StringIO", "built-in");
            {
                PyObjPtr objClass = PyObjClassDef::build(pycontext, "StringIO");
                PyCppUtil::setAttr(pycontext, objClass, "__init__", PyCppUtil::genFunc(PyStringIOExt::StringIO__init__, "__init__"));
                PyCppUtil::setAttr(pycontext, objClass, "write", PyCppUtil::genFunc(PyStringIOExt::StringIO_write, "write"));
                PyCppUtil::setAttr(pycontext, objClass, "getvalue", PyCppUtil::genFunc(PyStringIOExt::StringIO_getvalue, "getvalue"));
                PyCppUtil::setAttr(pycontext, objClass, "read", PyCppUtil::genFunc(PyStringIOExt::StringIO_read, "read"));
                PyCppUtil::setAttr(pycontext, objClass, "close", PyCppUtil::genFunc(PyStringIOExt::StringIO_close, "close"));
                PyCppUtil::setAttr(pycontext, objClass, "truncate", PyCppUtil::genFunc(PyStringIOExt::StringIO_truncate, "truncate"));
                PyCppUtil::setAttr(pycontext, objClass, "seek", PyCppUtil::genFunc(PyStringIOExt::StringIO_seek, "seek"));
                PyCppUtil::setAttr(pycontext, mod, "StringIO", objClass);
            }
            
            pycontext.addModule("StringIO", mod);
            pycontext.addModule("cStringIO", mod);
        }
        return true;
    }
};
    
}
#endif

