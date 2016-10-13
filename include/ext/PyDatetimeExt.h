#ifndef _PY_DATETIME_EXT_H_
#define _PY_DATETIME_EXT_H_

#include <time.h>
#include<sys/time.h>
#include <stdio.h>  
#include <string.h> 

#include "ExprAST.h"
#include "PyObj.h"

#include "StrTool.h"

namespace ff {
struct PyDatetimeExt{
    
    static bool strp_atoi(const char * & s, int & result, int low, int high, int offset)
    {
    bool worked = false;
    char * end;
    unsigned long num = strtoul(s, & end, 10);
    if (num >= (unsigned long)low && num <= (unsigned long)high)
        {
        result = (int)(num + offset);
        s = end;
        worked = true;
        }
    return worked;
    }
    static char * mystrptime(const char *s, const char *format, struct tm *tm)
    {
    const char * strp_weekdays[] = 
    { "sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"};
const char * strp_monthnames[] = 
    { "january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"};
    
    bool working = true;
    while (working && *format && *s)
        {
        switch (*format)
            {
        case '%':
            {
            ++format;
            switch (*format)
                {
            case 'a':
            case 'A': // weekday name
                tm->tm_wday = -1;
                working = false;
                for (size_t i = 0; i < 7; ++ i)
                    {
                    size_t len = strlen(strp_weekdays[i]);
                    if (!strnicmp(strp_weekdays[i], s, len))
                        {
                        tm->tm_wday = i;
                        s += len;
                        working = true;
                        break;
                        }
                    else if (!strnicmp(strp_weekdays[i], s, 3))
                        {
                        tm->tm_wday = i;
                        s += 3;
                        working = true;
                        break;
                        }
                    }
                break;
            case 'b':
            case 'B':
            case 'h': // month name
                tm->tm_mon = -1;
                working = false;
                for (size_t i = 0; i < 12; ++ i)
                    {
                    size_t len = strlen(strp_monthnames[i]);
                    if (!strnicmp(strp_monthnames[i], s, len))
                        {
                        tm->tm_mon = i;
                        s += len;
                        working = true;
                        break;
                        }
                    else if (!strnicmp(strp_monthnames[i], s, 3))
                        {
                        tm->tm_mon = i;
                        s += 3;
                        working = true;
                        break;
                        }
                    }
                break;
            case 'd':
            case 'e': // day of month number
                working = strp_atoi(s, tm->tm_mday, 1, 31, 0);
                break;
            case 'D': // %m/%d/%y
                {
                const char * s_save = s;
                working = strp_atoi(s, tm->tm_mon, 1, 12, -1);
                if (working && *s == '/')
                    {
                    ++ s;
                    working = strp_atoi(s, tm->tm_mday, 1, 31, 0);
                    if (working && *s == '/')
                        {
                        ++ s;
                        working = strp_atoi(s, tm->tm_year, 0, 99, 0);
                        if (working && tm->tm_year < 69)
                            tm->tm_year += 100;
                        }
                    }
                if (!working)
                    s = s_save;
                }
                break;
            case 'H': // hour
                working = strp_atoi(s, tm->tm_hour, 0, 23, 0);
                break;
            case 'I': // hour 12-hour clock
                working = strp_atoi(s, tm->tm_hour, 1, 12, 0);
                break;
            case 'j': // day number of year
                working = strp_atoi(s, tm->tm_yday, 1, 366, -1);
                break;
            case 'm': // month number
                working = strp_atoi(s, tm->tm_mon, 1, 12, -1);
                break;
            case 'M': // minute
                working = strp_atoi(s, tm->tm_min, 0, 59, 0);
                break;
            case 'n': // arbitrary whitespace
            case 't':
                while (isspace((int)*s)) 
                    ++s;
                break;
            case 'p': // am / pm
                if (!strnicmp(s, "am", 2))
                    { // the hour will be 1 -> 12 maps to 12 am, 1 am .. 11 am, 12 noon 12 pm .. 11 pm
                    if (tm->tm_hour == 12) // 12 am == 00 hours
                        tm->tm_hour = 0;
                    }
                else if (!strnicmp(s, "pm", 2))
                    {
                    if (tm->tm_hour < 12) // 12 pm == 12 hours
                        tm->tm_hour += 12; // 1 pm -> 13 hours, 11 pm -> 23 hours
                    }
                else
                    working = false;
                break;
            case 'r': // 12 hour clock %I:%M:%S %p
                {
                const char * s_save = s;
                working = strp_atoi(s, tm->tm_hour, 1, 12, 0);
                if (working && *s == ':')
                    {
                    ++ s;
                    working = strp_atoi(s, tm->tm_min, 0, 59, 0);
                    if (working && *s == ':')
                        {
                        ++ s;
                        working = strp_atoi(s, tm->tm_sec, 0, 60, 0);
                        if (working && isspace((int)*s))
                            {
                            ++ s;
                            while (isspace((int)*s)) 
                                ++s;
                            if (!strnicmp(s, "am", 2))
                                { // the hour will be 1 -> 12 maps to 12 am, 1 am .. 11 am, 12 noon 12 pm .. 11 pm
                                if (tm->tm_hour == 12) // 12 am == 00 hours
                                    tm->tm_hour = 0;
                                }
                            else if (!strnicmp(s, "pm", 2))
                                {
                                if (tm->tm_hour < 12) // 12 pm == 12 hours
                                    tm->tm_hour += 12; // 1 pm -> 13 hours, 11 pm -> 23 hours
                                }
                            else
                                working = false;
                            }
                        }
                    }
                if (!working)
                    s = s_save;
                }
                break;
            case 'R': // %H:%M
                {
                const char * s_save = s;
                working = strp_atoi(s, tm->tm_hour, 0, 23, 0);
                if (working && *s == ':')
                    {
                    ++ s;
                    working = strp_atoi(s, tm->tm_min, 0, 59, 0);
                    }
                if (!working)
                    s = s_save;
                }
                break;
            case 'S': // seconds
                working = strp_atoi(s, tm->tm_sec, 0, 60, 0);
                break;
            case 'T': // %H:%M:%S
                {
                const char * s_save = s;
                working = strp_atoi(s, tm->tm_hour, 0, 23, 0);
                if (working && *s == ':')
                    {
                    ++ s;
                    working = strp_atoi(s, tm->tm_min, 0, 59, 0);
                    if (working && *s == ':')
                        {
                        ++ s;
                        working = strp_atoi(s, tm->tm_sec, 0, 60, 0);
                        }
                    }
                if (!working)
                    s = s_save;
                }
                break;
            case 'w': // weekday number 0->6 sunday->saturday
                working = strp_atoi(s, tm->tm_wday, 0, 6, 0);
                break;
            case 'Y': // year
                working = strp_atoi(s, tm->tm_year, 1900, 65535, -1900);
                break;
            case 'y': // 2-digit year
                working = strp_atoi(s, tm->tm_year, 0, 99, 0);
                if (working && tm->tm_year < 69)
                    tm->tm_year += 100;
                break;
            case '%': // escaped
                if (*s != '%')
                    working = false;
                ++s;
                break;
            default:
                working = false;
                }
            }
            break;
        case ' ':
        case '\t':
        case '\r':
        case '\n':
        case '\f':
        case '\v':
            // zero or more whitespaces:
            while (isspace((int)*s))
                ++ s;
            break;
        default:
            // match character
            if (*s != *format)
                working = false;
            else
                ++s;
            break;
            }
        ++format;
        }
    return (working?(char *)s:0);
    }
    static PyObjPtr time_impl(PyContext& context, std::vector<PyObjPtr>& argAssignVal){
        if (argAssignVal.size() != 0){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: time() takes exactly 0 argument (%u given)", argAssignVal.size()));
        }
        
        struct timeval curtm;
	    ::gettimeofday(&curtm, NULL);
	
	    double ret = curtm.tv_sec + double(curtm.tv_usec) / (1000 * 1000);
	    return PyCppUtil::genFloat(ret);
    }
    static PyObjPtr datetime_now(PyContext& context, std::vector<PyObjPtr>& argAssignVal){
        if (argAssignVal.size() != 0){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: now() takes exactly 0 argument (%u given)", argAssignVal.size()));
        }
        
        time_t rawtime  = ::time(NULL);
        struct tm *info = ::localtime(&rawtime);
        
        argAssignVal.push_back(PyCppUtil::genInt(1900 + info->tm_year));
        argAssignVal.push_back(PyCppUtil::genInt(info->tm_mon));
        argAssignVal.push_back(PyCppUtil::genInt(info->tm_mday));
        argAssignVal.push_back(PyCppUtil::genInt(info->tm_hour));
        argAssignVal.push_back(PyCppUtil::genInt(info->tm_min));
        argAssignVal.push_back(PyCppUtil::genInt(info->tm_sec));
        
        PyObjPtr mod = context.getModule("datetime");
        PyObjPtr objClass = PyCppUtil::getAttr(context, mod, "datetime");
        return PyCppUtil::callPyfunc(context, objClass, argAssignVal);
    }
    static PyObjPtr datetime_strptime(PyContext& context, std::vector<PyObjPtr>& argAssignValOld){
        if (argAssignValOld.size() != 2){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: strptime() takes exactly 2 argument (%u given)", argAssignValOld.size()));
        }
        
        struct tm tmifo;
        struct tm *info = &tmifo;
        mystrptime(PyCppUtil::toStr(argAssignValOld[0]).c_str(), PyCppUtil::toStr(argAssignValOld[1]).c_str(), info);
        
        std::vector<PyObjPtr> argAssignVal;
        argAssignVal.push_back(PyCppUtil::genInt(1900 + info->tm_year));
        argAssignVal.push_back(PyCppUtil::genInt(info->tm_mon + 1));
        argAssignVal.push_back(PyCppUtil::genInt(info->tm_mday));
        argAssignVal.push_back(PyCppUtil::genInt(info->tm_hour));
        argAssignVal.push_back(PyCppUtil::genInt(info->tm_min));
        argAssignVal.push_back(PyCppUtil::genInt(info->tm_sec));
        
        PyObjPtr mod = context.getModule("datetime");
        PyObjPtr objClass = PyCppUtil::getAttr(context, mod, "datetime");
        return PyCppUtil::callPyfunc(context, objClass, argAssignVal);
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
        return PyCppUtil::genStr(ret);
    }
    static PyObjPtr datetime_strftime(PyContext& context, PyObjPtr& self, std::vector<PyObjPtr>& argAssignVal){
        PyAssertInstance(self);
        if (argAssignVal.size() != 1){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: strftime() takes exactly 1 argument (%u given)", argAssignVal.size()));
        }
        PyObjPtr& fmt = argAssignVal[0];
        
        struct tm info;
        info.tm_year = PyCppUtil::toInt(PyCppUtil::getAttr(context, self, "year"))-1900;
        info.tm_mon  = PyCppUtil::toInt(PyCppUtil::getAttr(context, self, "month")) - 1;
        info.tm_mday =  PyCppUtil::toInt(PyCppUtil::getAttr(context, self, "day"));
        info.tm_hour = PyCppUtil::toInt(PyCppUtil::getAttr(context, self, "hour"));
        info.tm_min = PyCppUtil::toInt(PyCppUtil::getAttr(context, self, "minute"));
        info.tm_sec = PyCppUtil::toInt(PyCppUtil::getAttr(context, self, "second"));
        info.tm_isdst = 0;
        
        std::string ret;
        char buff[512] = {0};
        ::strftime(buff, sizeof(buff), PyCppUtil::toStr(fmt).c_str(), &info);
        ret = buff;
        return PyCppUtil::genStr(ret);
    }
    static PyObjPtr datetime_date(PyContext& context, PyObjPtr& self, std::vector<PyObjPtr>& argAssignVal){
        PyAssertInstance(self);
        if (argAssignVal.size() != 0){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: date() takes exactly 0 argument (%u given)", argAssignVal.size()));
        }
        argAssignVal.push_back(PyCppUtil::getAttr(context, self, "year"));
        argAssignVal.push_back(PyCppUtil::getAttr(context, self, "month"));
        argAssignVal.push_back(PyCppUtil::getAttr(context, self, "day"));
        PyObjPtr mod = context.getModule("datetime");
        PyObjPtr objClass = PyCppUtil::getAttr(context, mod, "date");
        return PyCppUtil::callPyfunc(context, objClass, argAssignVal);
    }
    /*************************************** date */
    static PyObjPtr date__init__(PyContext& context, std::vector<PyObjPtr>& argAssignVal){
        if (argAssignVal.size() < 4){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: date() takes exactly 3 argument (%u given)", argAssignVal.size()));
        }
        PyObjPtr& self = argAssignVal[0];
        PyAssertInstance(self);
        
        PyCppUtil::setAttr(context, self, "year", argAssignVal[1]);
        PyCppUtil::setAttr(context, self, "month", argAssignVal[2]);
        PyCppUtil::setAttr(context, self, "day", argAssignVal[3]);
        
        return PyObjTool::buildNone();
    }
    static PyObjPtr date__str__(PyContext& context, PyObjPtr& self, std::vector<PyObjPtr>& argAssignVal){
        PyAssertInstance(self);
        std::string ret;
        char buff[512] = {0};
        snprintf(buff, sizeof(buff), "%04ld-%02ld-%02ld",
                        PyCppUtil::toInt(PyCppUtil::getAttr(context, self, "year")),
                        PyCppUtil::toInt(PyCppUtil::getAttr(context, self, "month")),
                        PyCppUtil::toInt(PyCppUtil::getAttr(context, self, "day")));
        ret = buff;
        return PyCppUtil::genStr(ret);
    }
    static PyObjPtr date_today(PyContext& context, std::vector<PyObjPtr>& argAssignVal){
        if (argAssignVal.size() != 0){
            PY_RAISE_STR(context, PyCppUtil::strFormat("TypeError: today() takes exactly 0 argument (%u given)", argAssignVal.size()));
        }
        
        time_t rawtime  = ::time(NULL);
        struct tm *info = ::localtime(&rawtime);
        
        argAssignVal.push_back(PyCppUtil::genInt(1900 + info->tm_year));
        argAssignVal.push_back(PyCppUtil::genInt(info->tm_mon));
        argAssignVal.push_back(PyCppUtil::genInt(info->tm_mday));
        
        PyObjPtr mod = context.getModule("datetime");
        PyObjPtr objClass = PyCppUtil::getAttr(context, mod, "date");
        return PyCppUtil::callPyfunc(context, objClass, argAssignVal);
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
                PyCppUtil::setAttr(pycontext, objClass, "strftime", PyCppUtil::genFunc(PyDatetimeExt::datetime_strftime, "strftime"));
                PyCppUtil::setAttr(pycontext, objClass, "now", PyCppUtil::genFunc(PyDatetimeExt::datetime_now, "now"));
                PyCppUtil::setAttr(pycontext, objClass, "strptime", PyCppUtil::genFunc(PyDatetimeExt::datetime_strptime, "strptime"));
                PyCppUtil::setAttr(pycontext, objClass, "date", PyCppUtil::genFunc(PyDatetimeExt::datetime_date, "date"));
                PyCppUtil::setAttr(pycontext, mod, "datetime", objClass);
            }
            {
                PyObjPtr objClass = PyObjClassDef::build(pycontext, "date");
                PyCppUtil::setAttr(pycontext, objClass, "__init__", PyCppUtil::genFunc(PyDatetimeExt::date__init__, "__init__"));
                PyCppUtil::setAttr(pycontext, objClass, "__str__", PyCppUtil::genFunc(PyDatetimeExt::date__str__, "__str__"));
                PyCppUtil::setAttr(pycontext, objClass, "today", PyCppUtil::genFunc(PyDatetimeExt::date_today, "today"));
                PyCppUtil::setAttr(pycontext, mod, "date", objClass);
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

