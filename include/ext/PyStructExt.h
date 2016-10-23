#ifndef _PY_STRUCT_EXT_H_
#define _PY_STRUCT_EXT_H_

#include "ExprAST.h"
#include "PyObj.h"

#include "StrTool.h"
#include <stdio.h>

namespace ff {

#define BIG_HIG_LOW_SWAP16(A)  ((((uint16_t)(A) & 0xff00) >> 8) | \
                        (((uint16_t)(A) & 0x00ff) << 8))

#define BIG_HIG_LOW_SWAP32(A)  ((((uint32_t)(A) & 0xff000000) >> 24) | \
                            (((uint32_t)(A) & 0x00ff0000) >> 8) | \
                            (((uint32_t)(A) & 0x0000ff00) << 8) | \
                            (((uint32_t)(A) & 0x000000ff) << 24))
struct PyStructExt{
    
     // 本机大端返回1，小端返回0
    static int IsBigendian()
    {
       union{
              uint32_t i;
              unsigned char s[4];
       }c;
    
       c.i = 0x12345678;
       return (0x12 == c.s[0]);
    }
    static int64_t myhton64(int64_t h)
    {
       int32_t* p = (int32_t*)(&h);
       int32_t* p2 = p + 1;

       if (!IsBigendian()){
           int32_t v = BIG_HIG_LOW_SWAP32(*p);
           int32_t v2 = BIG_HIG_LOW_SWAP32(*p2);
           *p2 = v;
           *p  = v2;
       }
       return h;
    }
    static int64_t myntoh64(int64_t h)
    {
       int32_t* p = (int32_t*)(&h);
       int32_t* p2 = p + 1;

       if (!IsBigendian()){
           int32_t v = BIG_HIG_LOW_SWAP32(*p);
           int32_t v2 = BIG_HIG_LOW_SWAP32(*p2);
           *p2 = v;
           *p  = v2;
       }
       return h;
    }
    static uint32_t myhtonl(int32_t h)
    {
       return IsBigendian() ? h : BIG_HIG_LOW_SWAP32(h);
    }
     
    static uint32_t myntohl(int32_t n)
    {
       return IsBigendian() ? n : BIG_HIG_LOW_SWAP32(n);
    }
    
    static uint16_t myhtons(int16_t h)
    {
       return IsBigendian() ? h : BIG_HIG_LOW_SWAP16(h);
    }
    static uint16_t myntohs(int16_t n)
    {
       return IsBigendian() ? n : BIG_HIG_LOW_SWAP16(n);
    }
    static PyObjPtr struct_pack(PyContext& context, std::vector<PyObjPtr>& argAssignVal){
        if (argAssignVal.size() < 2){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: pack() takes exactly >=2 argument (%u given)", argAssignVal.size()));
        }
        std::string ret;
        std::string fmt = PyCppUtil::toStr(argAssignVal[0]);
        size_t hasPopNum = 1;
        bool useNetworkEndian = false;
        std::string numArg;
        
        //printf("struct_pack %s %s\n", fmt.c_str(), argAssignVal[1]->getHandler()->handleStr(context, argAssignVal[1]).c_str());
        for (size_t i = 0; i < fmt.size(); ++i){
            switch (fmt[i]){
                case '@':
                case '=':
                case '<':
                    {
                        continue;
                    }
                    break;
                case '>':
                case '!':
                    {
                        useNetworkEndian = true;
                        continue;
                    }
                    break;
                default:
                    {
                        if (::isdigit(fmt[i])){
                            numArg += fmt[i];
                            continue;
                        }
                    }
                    break;
            }
            if (hasPopNum >= argAssignVal.size()){
                PY_RAISE_STR(context, PyCppUtil::strFormat("arg num not enough"));
            }
            PyObjPtr& val = argAssignVal[hasPopNum++];
            switch (fmt[i]){
                case 'x':
                case 'c':
                case 'b':
                case 'B':
                    {
                        int8_t v = (int8_t)PyCppUtil::toInt(val);
                        ret.append((const char*)(&v), sizeof(v));
                    }
                    break;
                case 'h':
                case 'H':
                    {
                        int16_t v = (int16_t)PyCppUtil::toInt(val);
                        if (useNetworkEndian){
                            v = (int16_t)myhtons(v);
                        }
                        ret.append((const char*)(&v), sizeof(v));
                    }
                    break;
                case 'i':
                case 'I':
                case 'l':
                case 'L':
                    {
                        int32_t v = (int32_t)PyCppUtil::toInt(val);
                        if (useNetworkEndian){
                            v = (int32_t)myhtonl(v);
                        }
                        ret.append((const char*)(&v), sizeof(v));
                    }
                    break;
                case 'q':
                case 'Q':
                case 'P':
                    {
                        PyInt v = (PyInt)PyCppUtil::toInt(val);
                        if (useNetworkEndian){
                            v = (PyInt)myhton64((uint64_t)v);
                        }
                        ret.append((const char*)(&v), sizeof(v));
                    }
                    break;
                case 'f':
                    {
                        float v = (float)PyCppUtil::toFloat(val);
                        ret.append((const char*)(&v), sizeof(v));
                    }
                    break;
                case 'd':
                    {
                        PyFloat v = (PyFloat)PyCppUtil::toFloat(val);
                        ret.append((const char*)(&v), sizeof(v));
                    }
                    break;
                case 's':
                    {
                        int n = 1;
                        if (numArg.empty() == false){
                            n = ::atoi(numArg.c_str());
                            if (n < 0){
                                n = 0;
                            }
                        }
                        std::string v = PyCppUtil::toStr(val);
                        if (n > (int)v.size()){
                            n = v.size();
                        }
                        ret.append(v.begin(), v.begin()+n);
                    }
                    break;
                default:
                    {
                        PY_RAISE_STR(context, PyCppUtil::strFormat("not support `%c`", fmt[i]));
                    }
                    break;
            }
        }
        return PyCppUtil::genStr(ret);
    }
    
    static PyObjPtr struct_unpack(PyContext& context, std::vector<PyObjPtr>& argAssignValSrc){
        if (argAssignValSrc.size() < 2){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: unpack() takes exactly >=2 argument (%u given)", argAssignValSrc.size()));
        }
        PyObjPtr ret = new PyObjTuple();
        std::string fmt = PyCppUtil::toStr(argAssignValSrc[0]);
        std::string data= PyCppUtil::toStr(argAssignValSrc[1]);
        size_t hasPopNum = 0;
        bool useNetworkEndian = false;
        std::string numArg;
        
        //printf("struct_unpack %s %d %s\n", fmt.c_str(), int(data.size()), PyCppUtil::hexstr(data).c_str());
        for (size_t i = 0; i < fmt.size(); ++i){
            switch (fmt[i]){
                case '@':
                case '=':
                case '<':
                    {
                        continue;
                    }
                    break;
                case '>':
                case '!':
                    {
                        useNetworkEndian = true;
                        continue;
                    }
                    break;
                default:
                    {
                        if (::isdigit(fmt[i])){
                            numArg += fmt[i];
                            continue;
                        }
                    }
                    break;
            }
            
            switch (fmt[i]){
                case 'x':
                case 'c':
                case 'b':
                case 'B':
                    {
                        if (hasPopNum + sizeof(int8_t) > data.size()){
                            PY_RAISE_STR(context, PyCppUtil::strFormat("data num not enough"));
                        }
                        int8_t v = *((int8_t*)(data.c_str() + hasPopNum));
                        ret.cast<PyObjTuple>()->append(PyCppUtil::genInt(v));
                        hasPopNum += sizeof(int8_t);
                    }
                    break;
                case 'h':
                case 'H':
                    {
                        if (hasPopNum + sizeof(int16_t) > data.size()){
                            PY_RAISE_STR(context, PyCppUtil::strFormat("data num not enough"));
                        }
                        int16_t v = *((int16_t*)(data.c_str() + hasPopNum));
                        if (useNetworkEndian){
                            v = (int16_t)myntohs(v);
                        }
                        ret.cast<PyObjTuple>()->append(PyCppUtil::genInt(v));
                        hasPopNum += sizeof(int16_t);
                    }
                    break;
                case 'i':
                case 'I':
                case 'l':
                case 'L':
                    {
                        if (hasPopNum + sizeof(int32_t) > data.size()){
                            PY_RAISE_STR(context, PyCppUtil::strFormat("data num not enough"));
                        }
                        int32_t v = *((int32_t*)(data.c_str() + hasPopNum));
                        if (useNetworkEndian){
                            v = (int32_t)myntohl(v);
                        }
                        ret.cast<PyObjTuple>()->append(PyCppUtil::genInt(v));
                        hasPopNum += sizeof(int32_t);
                    }
                    break;
                case 'q':
                case 'Q':
                case 'P':
                    {
                        if (hasPopNum + sizeof(PyInt) > data.size()){
                            PY_RAISE_STR(context, PyCppUtil::strFormat("data num not enough"));
                        }
                        PyInt v = *((PyInt*)(data.c_str() + hasPopNum));
                        if (useNetworkEndian){
                            v = (uint64_t)myntoh64(v);
                        }
                        ret.cast<PyObjTuple>()->append(PyCppUtil::genInt(v));
                        hasPopNum += sizeof(PyInt);
                    }
                    break;
                case 'f':
                    {
                        if (hasPopNum + sizeof(float) > data.size()){
                            PY_RAISE_STR(context, PyCppUtil::strFormat("data num not enough"));
                        }
                        float v = *((float*)(data.c_str() + hasPopNum));
                        ret.cast<PyObjTuple>()->append(PyCppUtil::genFloat(v));
                        hasPopNum += sizeof(float);
                    }
                    break;
                case 'd':
                    {
                        if (hasPopNum + sizeof(PyFloat) > data.size()){
                            PY_RAISE_STR(context, PyCppUtil::strFormat("data num not enough"));
                        }
                        PyFloat v = *((PyFloat*)(data.c_str() + hasPopNum));
                        ret.cast<PyObjTuple>()->append(PyCppUtil::genFloat(v));
                        hasPopNum += sizeof(PyFloat);
                    }
                    break;
                case 's':
                    {
                        int n = 1;
                        if (numArg.empty() == false){
                            n = ::atoi(numArg.c_str());
                            if (n < 0){
                                n = 0;
                            }
                        }
                        
                        if (hasPopNum + n > data.size()){
                            PY_RAISE_STR(context, PyCppUtil::strFormat("data num not enough"));
                        }
                        std::string strV;
                        strV.append(data.c_str() + hasPopNum, n);
                        ret.cast<PyObjTuple>()->append(PyCppUtil::genStr(strV));
                        hasPopNum += n;
                    }
                    break;
                default:
                    {
                        PY_RAISE_STR(context, PyCppUtil::strFormat("not support `%c`", fmt[i]));
                    }
                    break;
            }
        }
        //printf("struct_unpack %s %s\n", fmt.c_str(), ret->getHandler()->handleStr(context, ret).c_str());
        
        return ret;
    }
    static bool init(PyContext& pycontext){
        
        PyObjPtr mod = PyObjModule::BuildModule(pycontext, "struct", "built-in");
        PyCppUtil::setAttr(pycontext, mod, "pack", PyCppUtil::genFunc(PyStructExt::struct_pack, "pack"));
        PyCppUtil::setAttr(pycontext, mod, "unpack", PyCppUtil::genFunc(PyStructExt::struct_unpack, "unpack"));

        pycontext.addModule("struct", mod);
        return true;
    }
};
    
}
#endif

