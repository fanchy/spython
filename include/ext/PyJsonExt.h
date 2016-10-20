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
        else if (PyCheckBool(v)){
            bool b = PyCppUtil::toBool(v);
            jval.SetBool(b);
        }
        else if (PyCheckNone(v)){
            jval.SetNull();
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
    //json.dump(obj, fp, skipkeys=False, ensure_ascii=True, check_circular=True, allow_nan=True, cls=None, indent=None, separators=None, encoding="utf-8", default=None, sort_keys=False, **kw)
    //json.dumps(obj, skipkeys=False, ensure_ascii=True, check_circular=True, allow_nan=True, cls=None, indent=None, separators=None, encoding="utf-8", default=None, sort_keys=False, **kw)
    //json.load(fp[, encoding[, cls[, object_hook[, parse_float[, parse_int[, parse_constant[, object_pairs_hook[, **kw]]]]]]]])
    //json.loads(s[, encoding[, cls[, object_hook[, parse_float[, parse_int[, parse_constant[, object_pairs_hook[, **kw]]]]]]]])
    static PyObjPtr json_dumps(PyContext& context, std::vector<ArgTypeInfo>& allArgsVal, std::vector<PyObjPtr>& argAssignVal){
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
    static PyObjPtr json_dump(PyContext& context, std::vector<PyObjPtr>& argAssignVal){
        if (argAssignVal.size() < 2){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: json_dumps() can't encode json, file needed"));
        }
        PyObjPtr io = argAssignVal[1];
        std::vector<PyObjPtr> argAssignVal2 = argAssignVal;
        argAssignVal2.erase(argAssignVal2.begin()+1);
        std::vector<ArgTypeInfo> allArgsVal;
        PyObjPtr ret = json_dumps(context, allArgsVal, argAssignVal2);
        std::vector<PyObjPtr> tmpargs;
        tmpargs.push_back(ret);
        PyObjPtr func = PyCppUtil::getAttr(context, io, "write");
        PyCppUtil::callPyfunc(context, func, tmpargs);
        return PyObjTool::buildTrue();
    }
    
    static PyObjPtr json2PyObj(const rapidjson::Value& jval){
        if (jval.IsInt64()){
            return PyCppUtil::genInt(jval.GetInt64());
        }
        else if (jval.IsDouble()){
            return PyCppUtil::genFloat(jval.GetDouble());
        }
        else if (jval.IsBool()){
            return PyObjTool::buildBool(jval.GetBool());
        }
        else if (jval.IsNull()){
            return PyObjTool::buildNone();
        }
        else if (jval.IsString()){
            return PyCppUtil::genStr(jval.GetString());
        }
        return NULL;
    }
    static PyObjPtr jsonArrayObject2PyObj(PyContext& context, const rapidjson::Value& jval){
        if (jval.IsArray()){
            PyObjPtr ret = new PyObjList();
            for (rapidjson::Value::ConstValueIterator itr = jval.Begin(); itr != jval.End(); ++itr){
                PyObjPtr elem = json2PyObj(*itr);
                if (!elem){
                    elem = jsonArrayObject2PyObj(context, *itr);
                    if (!elem){
                        PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: json_loads() can't convert json"));
                    }
                }
                ret.cast<PyObjList>()->append(elem);
            }
            return ret;
        }
        else if (jval.IsObject()){
            PyObjPtr ret = new PyObjDict();
            for (rapidjson::Value::ConstMemberIterator itr = jval.MemberBegin(); itr != jval.MemberEnd(); ++itr){
                PyObjPtr elem = json2PyObj(itr->value);
                if (!elem){
                    elem = jsonArrayObject2PyObj(context, itr->value);
                    if (!elem){
                        PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: json_loads() can't convert json object"));
                    }
                }
                PyObjPtr key = PyCppUtil::genStr(itr->name.GetString());
                ret.cast<PyObjDict>()->set(context, key, elem);
            }
            return ret;
        }
        else{
            return json2PyObj(jval);
        }
        return NULL;
    }
    static PyObjPtr json_loads(PyContext& context, std::vector<PyObjPtr>& argAssignVal){
        if (argAssignVal.size() < 1){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: json_loads() takes exactly >=1 argument (%u given)", argAssignVal.size()));
        }

        std::string jsonstr = PyCppUtil::toStr(argAssignVal[0]);
        
        using namespace rapidjson;
        Document d;
        d.Parse(jsonstr.c_str());
        
        if (d.IsArray() || d.IsObject()){
            return jsonArrayObject2PyObj(context, d);
        }
        else{
            return json2PyObj(d);
        }
        return PyObjTool::buildNone();
    }
    static PyObjPtr json_load(PyContext& context, std::vector<PyObjPtr>& argAssignVal){
        if (argAssignVal.size() < 1){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: json_loads() takes exactly >=1 argument (%u given)", argAssignVal.size()));
        }
        PyObjPtr io = argAssignVal[0];
        PyObjPtr func = PyCppUtil::getAttr(context, io, "read");
        std::vector<PyObjPtr> tmpargs;
        PyObjPtr pyStr= PyCppUtil::callPyfunc(context, func, tmpargs);
        argAssignVal[0] = pyStr;
        return json_loads(context, argAssignVal);
    }
    static bool init(PyContext& pycontext){
        {
            PyObjPtr mod = PyObjModule::BuildModule(pycontext, "json", "built-in");
            PyCppUtil::setAttr(pycontext, mod, "dumps", PyCppUtil::genFunc(PyJsonExt::json_dumps, "dumps"));
            PyCppUtil::setAttr(pycontext, mod, "dump", PyCppUtil::genFunc(PyJsonExt::json_dump, "dump"));
            PyCppUtil::setAttr(pycontext, mod, "loads", PyCppUtil::genFunc(PyJsonExt::json_loads, "loads"));
            PyCppUtil::setAttr(pycontext, mod, "load", PyCppUtil::genFunc(PyJsonExt::json_load, "load"));
            pycontext.addModule("json", mod);
        }
        return true;
    }
};
    
}
#endif

