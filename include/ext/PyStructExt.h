#ifndef _PY_STRUCT_EXT_H_
#define _PY_STRUCT_EXT_H_

#include "ExprAST.h"
#include "PyObj.h"

#include "StrTool.h"
#include <stdio.h>

namespace ff {

struct PyStructExt{
    static PyObjPtr struct_pack(PyContext& context, std::vector<PyObjPtr>& argAssignVal){
        if (argAssignVal.size() < 2){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: pack() takes exactly >=2 argument (%u given)", argAssignVal.size()));
        }
        std::string ret;
        std::string fmt = PyCppUtil::toStr(argAssignVal[0]);
        size_t hasPopNum = 1;
        bool useNetworkEndian = false;
        std::string numArg;
        for (size_t i = 0; i < fmt.size(); ++i){
            switch (fmt[i]){
                case '@':
                case '=':
                case '<':
                    {
                        
                    }
                    break;
                case '>':
                case '!':
                    {
                        useNetworkEndian = true;
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
                        uint8_t v = (uint8_t)PyCppUtil::toInt(val);
                        ret.append((const char*)(&v), sizeof(v));
                    }
                    break;
                case 'h':
                case 'H':
                    {
                        uint16_t v = (uint16_t)PyCppUtil::toInt(val);
                        ret.append((const char*)(&v), sizeof(v));
                    }
                    break;
                case 'i':
                case 'I':
                case 'l':
                case 'L':
                    {
                        uint32_t v = (uint32_t)PyCppUtil::toInt(val);
                        ret.append((const char*)(&v), sizeof(v));
                    }
                    break;
                case 'q':
                case 'Q':
                case 'P':
                    {
                        PyInt v = (PyInt)PyCppUtil::toInt(val);
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
                        double v = (double)PyCppUtil::toFloat(val);
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
    static bool init(PyContext& pycontext){
        
        PyObjPtr mod = PyObjModule::BuildModule(pycontext, "struct", "built-in");
        PyCppUtil::setAttr(pycontext, mod, "pack", PyCppUtil::genFunc(PyStructExt::struct_pack, "pack"));

        pycontext.addModule("struct", mod);
        return true;
    }
};
    
}
#endif

