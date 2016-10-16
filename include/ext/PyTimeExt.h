#ifndef _PY_TIME_EXT_H_
#define _PY_TIME_EXT_H_

#include <time.h>
#include<sys/time.h>

#include "ExprAST.h"
#include "PyObj.h"

#include "StrTool.h"

namespace ff {
struct PyTimeExt{
    static PyObjPtr time_impl(PyContext& context, std::vector<PyObjPtr>& argAssignVal){
        if (argAssignVal.size() != 0){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: time() takes exactly 0 argument (%u given)", argAssignVal.size()));
        }
        
        struct timeval curtm;
	    ::gettimeofday(&curtm, NULL);
	
	    double ret = curtm.tv_sec + double(curtm.tv_usec) / (1000 * 1000);
	    return PyCppUtil::genFloat(ret);
    }
    static PyObjPtr struct_time__init__(PyContext& context, std::vector<PyObjPtr>& argAssignVal){
        if (argAssignVal.size() == 0){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: struct_time() takes exactly 1/2 argument (%u given)", argAssignVal.size()));
        }
        PyObjPtr& self = argAssignVal[0];
        PyAssertInstance(self);
        
        time_t rawtime = 0;
        bool useLocalTime = true;
        
        if (argAssignVal.size() >= 2){
            PyObjPtr& destself = argAssignVal[1];
            rawtime = PyCppUtil::toInt(destself);
            
            if (argAssignVal.size() >= 3 && PyCppUtil::toInt(argAssignVal[2]) != 0){
                useLocalTime = false;
            }
        }
        else{
            ::time(&rawtime);
        }
        
        struct tm *info = NULL;
        if (useLocalTime){
            info = ::localtime(&rawtime);
        }
        else{
            info = ::gmtime(&rawtime);
        }
        
	    PyCppUtil::setAttr(context, self, "tm_sec", PyCppUtil::genInt(info->tm_sec));         /* seconds,  range 0 to 59          */
        PyCppUtil::setAttr(context, self, "tm_min", PyCppUtil::genInt(info->tm_min));         /* minutes, range 0 to 59           */
        PyCppUtil::setAttr(context, self, "tm_hour", PyCppUtil::genInt(info->tm_hour));        /* hours, range 0 to 23             */
        PyCppUtil::setAttr(context, self, "tm_mday", PyCppUtil::genInt(info->tm_mday));        /* day of the month, range 1 to 31  */
        PyCppUtil::setAttr(context, self, "tm_mon", PyCppUtil::genInt(info->tm_mon));         /* month, range 0 to 11             */
        PyCppUtil::setAttr(context, self, "tm_year", PyCppUtil::genInt(info->tm_year));        /* The number of years since 1900   */
        PyCppUtil::setAttr(context, self, "tm_wday", PyCppUtil::genInt(info->tm_wday));        /* day of the week, range 0 to 6    */
        PyCppUtil::setAttr(context, self, "tm_yday", PyCppUtil::genInt(info->tm_yday));        /* day in the year, range 0 to 365  */
        PyCppUtil::setAttr(context, self, "tm_isdst", PyCppUtil::genInt(info->tm_isdst));       /* daylight saving time             */
	    return PyObjTool::buildNone();
    }
    //
    static PyObjPtr struct_time__str__(PyContext& context, PyObjPtr& self, std::vector<PyObjPtr>& argAssignVal){
        PyAssertInstance(self);
        char buff[512] = {0};
        snprintf(buff, sizeof(buff), "time.struct_time(tm_year=%ld, tm_mon=%ld, tm_mday=%ld, tm_hour=%ld, tm_min=%ld, tm_sec=%ld, tm_wday=%ld, tm_yday=%ld, tm_isdst=%ld)",
                       1900 + long(PyCppUtil::toInt(PyCppUtil::getAttr(context, self, "tm_year"))),
                       1 + long(PyCppUtil::toInt(PyCppUtil::getAttr(context, self, "tm_mon"))),
                       long(PyCppUtil::toInt(PyCppUtil::getAttr(context, self, "tm_mday"))),
                       long(PyCppUtil::toInt(PyCppUtil::getAttr(context, self, "tm_hour"))),
                       long(PyCppUtil::toInt(PyCppUtil::getAttr(context, self, "tm_min"))),
                       long(PyCppUtil::toInt(PyCppUtil::getAttr(context, self, "tm_sec"))),
                       long(PyCppUtil::toInt(PyCppUtil::getAttr(context, self, "tm_wday"))) - 1,
                       long(PyCppUtil::toInt(PyCppUtil::getAttr(context, self, "tm_yday"))) + 1,
                       long(PyCppUtil::toInt(PyCppUtil::getAttr(context, self, "tm_isdst")))
                       );

        PyObjPtr ret = PyCppUtil::genStr(std::string(buff));
        return ret;
    }
    static PyObjPtr time_localtime(PyContext& context, std::vector<PyObjPtr>& argAssignVal){
        if (argAssignVal.size() != 0 && argAssignVal.size() != 1){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: localtime() takes exactly 0/1 argument (%u given)", argAssignVal.size()));
        }
        
        PyObjPtr mod = context.getModule("time");
        PyObjPtr objClass = PyCppUtil::getAttr(context, mod, "struct_time");

        return PyCppUtil::callPyfunc(context, objClass, argAssignVal);
    }
    static PyObjPtr time_gmtime(PyContext& context, std::vector<PyObjPtr>& argAssignVal){
        if (argAssignVal.size() != 0 && argAssignVal.size() != 1){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: localtime() takes exactly 0/1 argument (%u given)", argAssignVal.size()));
        }
        
        PyObjPtr mod = context.getModule("time");
        PyObjPtr objClass = PyCppUtil::getAttr(context, mod, "struct_time");
        argAssignVal.push_back(PyCppUtil::genInt(1));
        return PyCppUtil::callPyfunc(context, objClass, argAssignVal);
    }
    static PyObjPtr time_mktime(PyContext& context, std::vector<PyObjPtr>& argAssignVal){
        if (argAssignVal.size() != 1){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: mktime() takes exactly 1 argument (%u given)", argAssignVal.size()));
        }
        
        PyObjPtr& self = argAssignVal[0];
        PyAssertInstance(self);
        
        struct tm info;
        info.tm_year = PyCppUtil::toInt(PyCppUtil::getAttr(context, self, "tm_year"));
        info.tm_mon  = PyCppUtil::toInt(PyCppUtil::getAttr(context, self, "tm_mon")) ;
        info.tm_mday =  PyCppUtil::toInt(PyCppUtil::getAttr(context, self, "tm_mday"));
        info.tm_hour = PyCppUtil::toInt(PyCppUtil::getAttr(context, self, "tm_hour"));
        info.tm_min = PyCppUtil::toInt(PyCppUtil::getAttr(context, self, "tm_min"));
        info.tm_sec = PyCppUtil::toInt(PyCppUtil::getAttr(context, self, "tm_sec"));
        info.tm_wday = PyCppUtil::toInt(PyCppUtil::getAttr(context, self, "tm_wday"));
        info.tm_yday = PyCppUtil::toInt(PyCppUtil::getAttr(context, self, "tm_yday"));
        info.tm_isdst = PyCppUtil::toInt(PyCppUtil::getAttr(context, self, "tm_isdst"));

        time_t ret = ::mktime(&info);
        return PyCppUtil::genFloat(double(ret));
    }
    static bool init(PyContext& pycontext){
        {
            PyObjPtr mod = PyObjModule::BuildModule(pycontext, "time", "built-in");

            {
                PyObjPtr objClass = PyObjClassDef::build(pycontext, "struct_time");
                PyCppUtil::setAttr(pycontext, objClass, "__init__", PyCppUtil::genFunc(PyTimeExt::struct_time__init__, "__init__"));
                PyCppUtil::setAttr(pycontext, objClass, "__str__", PyCppUtil::genFunc(PyTimeExt::struct_time__str__, "__str__"));
                PyCppUtil::setAttr(pycontext, mod, "struct_time", objClass);
            }
                        
            PyCppUtil::setAttr(pycontext, mod, "time", PyCppUtil::genFunc(PyTimeExt::time_impl, "time"));
            PyCppUtil::setAttr(pycontext, mod, "localtime", PyCppUtil::genFunc(PyTimeExt::time_localtime, "localtime"));
            PyCppUtil::setAttr(pycontext, mod, "gmtime", PyCppUtil::genFunc(PyTimeExt::time_gmtime, "gmtime"));
            PyCppUtil::setAttr(pycontext, mod, "mktime", PyCppUtil::genFunc(PyTimeExt::time_mktime, "mktime"));
            pycontext.addModule("time", mod);
        }
        return true;
    }
};
    
}
#endif

