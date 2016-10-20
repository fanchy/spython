#ifndef _PY_JSON_EXT_H_
#define _PY_JSON_EXT_H_

#include "ExprAST.h"
#include "PyObj.h"

#include "StrTool.h"

#include "rapidjson/document.h"
#include "rapidjson/writer.h"
#include "rapidjson/stringbuffer.h"

namespace ff {

struct PyJsonExt{
    static bool assignJVal(rapidjson::Document::AllocatorType& allocator, rapidjson::Value& jval, PyContext& context, PyObjPtr& v){
        if (PyCheckStr(v)){
            std::string s = PyCppUtil::toStr(v);
            jval.SetString(s.c_str(), s.size(), allocator);
        }
        else if (PyCheckInt(v)){
            PyInt n = PyCppUtil::toInt(v);
            jval.SetUint64(n);
        }
        else if (PyCheckFloat(v)){
            PyFloat n = PyCppUtil::toFloat(v);
            jval.SetDouble(n);
        }
        else{
            return false;
        }
        return true;
    }
    static bool encode_array_object(rapidjson::Document::AllocatorType& allocator, rapidjson::Value& dest, PyContext& context, PyObjPtr pyobj){
        bool isArray = true;
        if (PyCheckDict(pyobj)){
            isArray = false;
            std::vector<PyObjPtr> tmpargs;
            PyObjPtr func = PyCppUtil::getAttr(context, pyobj, "iteritems");
            pyobj = PyCppUtil::callPyfunc(context, func, tmpargs);
        }
        IterUtil iterUtil(context, pyobj);
        
        rapidjson::Value jval;
        rapidjson::Value jkey;
        while (true){
            PyObjPtr v = iterUtil.next();
            if (!v){
                break;
            }
            if (isArray){
                if (assignJVal(allocator, jval, context, v)){
                }
                else if (PyCheckTuple(v) || PyCheckList(v)){
                    jval.SetArray();
                    encode_array_object(allocator, jval, context, v);
                }
                else if (PyCheckDict(v)){
                    jval.SetObject();
                    encode_array_object(allocator, jval, context, v);
                }
                else{
                    PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: json_dumps() can't encode json"));
                }
                dest.PushBack(jval, allocator);
            }
            else{
                if (PyCheckTuple(v) && v.cast<PyObjTuple>()->size() == 2){
                    std::string key = PyCppUtil::toStr(v.cast<PyObjTuple>()->at(0));
                    
                    jkey.SetString(key.c_str(), key.size(), allocator);
                    PyObjPtr dictVal = v.cast<PyObjTuple>()->at(1);
                    if (assignJVal(allocator, jval, context, dictVal)){
                    }
                    else if (PyCheckTuple(v) || PyCheckList(v)){
                        jval.SetArray();
                        encode_array_object(allocator, jval, context, dictVal);
                    }
                    else if (PyCheckDict(v)){
                        jval.SetObject();
                        encode_array_object(allocator, jval, context, dictVal);
                    }
                    else{
                        PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: json_dumps() can't encode json"));
                    }
                    dest.AddMember(jkey, jval, allocator);
                }
            }
        }
        return true;
    }
    static bool encode_object(rapidjson::Document::AllocatorType& allocator, rapidjson::Value& dest, PyContext& context, PyObjPtr& pyobj){
        IterUtil iterUtil(context, pyobj);
        while (true){
            PyObjPtr v = iterUtil.next();
            if (!v){
                break;
            }
            
        }
        return true;
    }
    static PyObjPtr json_dumps(PyContext& context, std::vector<PyObjPtr>& argAssignVal){
        if (argAssignVal.size() < 1){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: json_dumps() takes exactly >=1 argument (%u given)", argAssignVal.size()));
        }
        PyObjPtr& obj = argAssignVal[0];
        
        using namespace rapidjson;
        Document d;
        if (PyCheckList(obj) || PyCheckTuple(obj)){
            d.SetArray();
            encode_array_object(d.GetAllocator(), d, context, obj);
        }
        else if (PyCheckDict(obj)){
            d.SetObject();
            encode_array_object(d.GetAllocator(), d, context, obj);
        }
        else if (assignJVal(d.GetAllocator(), d, context, obj)){
        }
        else{
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: json_dumps() can't encode json"));
        }
        StringBuffer buffer;
        Writer<StringBuffer> writer(buffer);
        d.Accept(writer);
        return PyCppUtil::genStr(buffer.GetString());
    }
    static bool init(PyContext& pycontext){
        {
            PyObjPtr mod = PyObjModule::BuildModule(pycontext, "json", "built-in");
            PyCppUtil::setAttr(pycontext, mod, "dumps", PyCppUtil::genFunc(PyJsonExt::json_dumps, "dumps"));
            pycontext.addModule("json", mod);
        }
        return true;
    }
};
    
}
#endif

