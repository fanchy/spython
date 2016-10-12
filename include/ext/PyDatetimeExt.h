#ifndef _PY_DATETIME_EXT_H_
#define _PY_DATETIME_EXT_H_

#include <time.h>
#include<sys/time.h>

#include "ExprAST.h"
#include "PyObj.h"

#include "StrTool.h"

namespace ff {
struct PyDatetimeExt{
    static PyObjPtr time_impl(PyContext& context, std::vector<PyObjPtr>& argAssignVal){
        if (argAssignVal.size() != 0){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: time() takes exactly 0 argument (%u given)", argAssignVal.size()));
        }
        
        struct timeval curtm;
	    ::gettimeofday(&curtm, NULL);
	
	    double ret = curtm.tv_sec + double(curtm.tv_usec) / (1000 * 1000);
	    return PyCppUtil::genFloat(ret);
    }
    static PyObjPtr datetime__init__(PyContext& context, std::vector<PyObjPtr>& argAssignVal){
        if (argAssignVal.size() < 4){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: datetime() takes exactly 4-6 argument (%u given)", argAssignVal.size()));
        }
        PyObjPtr& self = argAssignVal[0];
        PyAssertInstance(self);
        
        PyCppUtil::setAttr(context, self, "year", argAssignVal[1]);
        PyCppUtil::setAttr(context, self, "month", argAssignVal[2]);
        PyCppUtil::setAttr(context, self, "day", argAssignVal[3]);
        int hour = 0;
        int minute = 0;
        int second = 0;
        if (argAssignVal.size() >= 5){
            hour = PyCppUtil::toInt(argAssignVal[4]);
        }
        if (argAssignVal.size() >= 6){
            minute = PyCppUtil::toInt(argAssignVal[5]);
        }
        if (argAssignVal.size() >= 7){
            second = PyCppUtil::toInt(argAssignVal[6]);
        }
        PyCppUtil::setAttr(context, self, "hour", PyCppUtil::genInt(hour));
        PyCppUtil::setAttr(context, self, "minute", PyCppUtil::genInt(minute));
        PyCppUtil::setAttr(context, self, "second", PyCppUtil::genInt(second));
        return PyObjTool::buildNone();
    }
    //
    static PyObjPtr datetime__str__(PyContext& context, PyObjPtr& self, std::vector<PyObjPtr>& argAssignVal){
        PyAssertInstance(self);
        std::string ret;
        char buff[512] = {0};
        snprintf(buff, sizeof(buff), "%04ld-%02ld-%02ld %02ld:%02ld:%02ld",
                        PyCppUtil::toInt(PyCppUtil::getAttr(context, self, "year")),
                        PyCppUtil::toInt(PyCppUtil::getAttr(context, self, "month")),
                        PyCppUtil::toInt(PyCppUtil::getAttr(context, self, "day")),
                        PyCppUtil::toInt(PyCppUtil::getAttr(context, self, "hour")),
                        PyCppUtil::toInt(PyCppUtil::getAttr(context, self, "minute")),
                        PyCppUtil::toInt(PyCppUtil::getAttr(context, self, "second")));
        ret = buff;
        /*
        snprintf(buff, sizeof(buff), "datetime.datetime(%ld, %ld, %ld",
                       PyCppUtil::toInt(PyCppUtil::getAttr(context, self, "year")),
                       PyCppUtil::toInt(PyCppUtil::getAttr(context, self, "month")),
                       PyCppUtil::toInt(PyCppUtil::getAttr(context, self, "day"))
                       );
        ret += buff;
        long hour = PyCppUtil::toInt(PyCppUtil::getAttr(context, self, "hour"));
        long minute = PyCppUtil::toInt(PyCppUtil::getAttr(context, self, "minute"));
        long second = PyCppUtil::toInt(PyCppUtil::getAttr(context, self, "second"));
        if (second != 0){
            snprintf(buff, sizeof(buff), "%ld, %ld, %ld)", hour, minute, second);
        }
        else if (minute != 0){
            snprintf(buff, sizeof(buff), "%ld, %ld)", hour, minute);
        }
        else if (hour != 0){
            snprintf(buff, sizeof(buff), "%ld)", hour);
        }
        else{
            snprintf(buff, sizeof(buff), ")");
        }
        ret += buff;
        */
        return PyCppUtil::genStr(ret);
    }
    /*
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
    */
    static bool init(PyContext& pycontext){
        {
            PyObjPtr mod = PyObjModule::BuildModule(pycontext, "datetime", "built-in");

            {
                PyObjPtr objClass = PyObjClassDef::build(pycontext, "datetime");
                PyCppUtil::setAttr(pycontext, objClass, "__init__", PyCppUtil::genFunc(PyDatetimeExt::datetime__init__, "__init__"));
                PyCppUtil::setAttr(pycontext, objClass, "__str__", PyCppUtil::genFunc(PyDatetimeExt::datetime__str__, "__str__"));
                PyCppUtil::setAttr(pycontext, mod, "datetime", objClass);
            }
            /*            
            PyCppUtil::setAttr(pycontext, mod, "time", PyCppUtil::genFunc(PyDatetimeExt::time_impl, "time"));
            PyCppUtil::setAttr(pycontext, mod, "localtime", PyCppUtil::genFunc(PyDatetimeExt::time_localtime, "localtime"));
            PyCppUtil::setAttr(pycontext, mod, "gmtime", PyCppUtil::genFunc(PyDatetimeExt::time_gmtime, "gmtime"));
            PyCppUtil::setAttr(pycontext, mod, "mktime", PyCppUtil::genFunc(PyDatetimeExt::time_mktime, "mktime"));
            */
            pycontext.addModule("datetime", mod);
        }
        return true;
    }
};
    
}
#endif

