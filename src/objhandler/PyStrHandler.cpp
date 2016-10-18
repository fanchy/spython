
#include "PyObj.h"
#include "ExprAST.h"
#include "objhandler/PyStrHandler.h"

using namespace std;
using namespace ff;

string PyStrHandler::handleStr(PyContext& context, const PyObjPtr& self) const {
    string ret = "'";
    ret += self.cast<PyObjStr>()->value + "'";
    return ret;
}
bool PyStrHandler::handleBool(PyContext& context, const PyObjPtr& self) const{
    return self.cast<PyObjStr>()->value.empty() == false;
}
bool PyStrHandler::handleEqual(PyContext& context, const PyObjPtr& self, const PyObjPtr& val) const{
    if (val->getType() == self->getType() && self.cast<PyObjStr>()->value == val.cast<PyObjStr>()->value){
        return true;
    }
    return false;
}
bool PyStrHandler::handleLessEqual(PyContext& context, const PyObjPtr& self, const PyObjPtr& val) const{
    if (val->getType() == self->getType()){
        return self.cast<PyObjStr>()->value <= val.cast<PyObjStr>()->value;
    }
    else{
        THROW_EVAL_ERROR("can't compare to str");
    }
    return false;
}
bool PyStrHandler::handleGreatEqual(PyContext& context, const PyObjPtr& self, const PyObjPtr& val) const{
    if (val->getType() == self->getType()){
        return self.cast<PyObjStr>()->value >= val.cast<PyObjStr>()->value;
    }
    else{
        THROW_EVAL_ERROR("can't compare to str");
    }
    return false;
}

PyObjPtr& PyStrHandler::handleAdd(PyContext& context, PyObjPtr& self, PyObjPtr& val){
    if (val->getType() == self->getType()){
        string newVal = self.cast<PyObjStr>()->value += val.cast<PyObjStr>()->value;
        return context.cacheResult(new PyObjStr(newVal));
    }
    else{
        THROW_EVAL_ERROR("can't add to str");
    }
    return self;
}
PyObjPtr& PyStrHandler::handleSub(PyContext& context, PyObjPtr& self, PyObjPtr& val){
    THROW_EVAL_ERROR("can't sub to str");
    return self;
}
PyObjPtr& PyStrHandler::handleMul(PyContext& context, PyObjPtr& self, PyObjPtr& val){
    int nType   = val->getType();

    if (nType == PY_INT){
        long times = val.cast<PyObjInt>()->value;
        string newVal;
        for (long i = 0; i < times; ++i){
            newVal += self.cast<PyObjStr>()->value;
        }
        return context.cacheResult(new PyObjStr(newVal));
    }
    else{
        THROW_EVAL_ERROR("can't mul to str");
    }
    return self;
}
PyObjPtr& PyStrHandler::handleDiv(PyContext& context, PyObjPtr& self, PyObjPtr& val){
    THROW_EVAL_ERROR("can't div to str");
    return self;
}
PyObjPtr strFmtGetArg(PyObjPtr& fmtArgs, size_t i){
    if (i == 0){
        if (PyCheckTuple(fmtArgs)){
            if (i >= fmtArgs.cast<PyObjTuple>()->size()){
                THROW_EVAL_ERROR("TypeError: not enough arguments for format string");
            }
            return fmtArgs.cast<PyObjTuple>()->at(i);
        }
        else{
            return fmtArgs;
        }
    }
    else{
        if (PyCheckTuple(fmtArgs)){
            if (i >= fmtArgs.cast<PyObjTuple>()->size()){
                THROW_EVAL_ERROR("TypeError: not enough arguments for format string");
            }
            return fmtArgs.cast<PyObjTuple>()->at(i);
        }
        THROW_EVAL_ERROR("TypeError: not enough arguments for format string");
    }
    return NULL;
}
PyObjPtr& PyStrHandler::handleMod(PyContext& context, PyObjPtr& self, PyObjPtr& fmtArgs){
    const string& selfval = self.cast<PyObjStr>()->value;
    string ret;
    
    //%[(name)][flags][width].[precision]typecode
    string widthArg;
    string tmpVal;
    bool zeroFlag = false;//! fill zero
    bool rightAlign = false;
    int nArgIndex = 0;
    for (size_t i = 0; i < selfval.size(); ++i){
        if (selfval[i] != '%'){
            ret += selfval[i];
            continue;
        }
        size_t j = i + 1;
        widthArg.clear();
        zeroFlag = false;
        rightAlign = false;
        tmpVal.clear();
        
        for (; j < selfval.size(); ++j){
            char nextChar = selfval.at(j);
            if (nextChar == 'd' or nextChar == 'i'){
                tmpVal += PyCppUtil::int2str(PyCppUtil::toInt(strFmtGetArg(fmtArgs, nArgIndex++)));
            }
            else if (nextChar == 's'){
                tmpVal += PyCppUtil::toStr(strFmtGetArg(fmtArgs, nArgIndex++));
            }
            else if (nextChar == 'f' || nextChar == 'F'){
                tmpVal += PyCppUtil::int2str(PyCppUtil::toInt(strFmtGetArg(fmtArgs, nArgIndex++)));
            }
            else if (nextChar == '%'){
                tmpVal += '%';
            }
            else{
                if (widthArg.empty()){
                    if (nextChar == '0'){
                        zeroFlag = true;
                        continue;
                    }
                    else if (nextChar == '-'){
                        rightAlign = true;
                        continue;
                    }
                    else if (nextChar == '+'){
                        continue;
                    }
                    
                }
                widthArg += nextChar;
                continue;
            }
            if (!widthArg.empty()){
                int nWidth = ::atoi(widthArg.c_str());
                for (size_t m = tmpVal.size(); (int)m < nWidth; ++m){
                    if (rightAlign){
                        if (zeroFlag){
                            tmpVal += '0';
                        }
                        else{
                            tmpVal += ' ';
                        }
                    }
                    else{
                        if (zeroFlag){
                            ret += '0';
                        }
                        else{
                            ret += ' ';
                        }
                    }
                }
            }
            ret += tmpVal;
            break;
        }
        i = j;
    }
    return context.cacheResult(PyCppUtil::genStr(ret));
}
long PyStrHandler::handleLen(PyContext& context, PyObjPtr& self){
    return self.cast<PyObjStr>()->value.size();
}

PyObjPtr& PyStrHandler::handleSlice(PyContext& context, PyObjPtr& self, PyObjPtr& startVal, int* stop, int step){
    PyAssertInt(startVal);
    int start = startVal.cast<PyObjInt>()->value;
    const string& s = self.cast<PyObjStr>()->value;
    
    string newVal;
    if (NULL == stop){
        if (start < 0){
            start = int(s.size()) + start;
        }
        if (start >= 0 && start < (int)s.size()){
            newVal = s[start];
        }
        return context.cacheResult(PyCppUtil::genStr(newVal));
    }
    
    if (step > 0){
        if (start < 0){
            start += (int)s.size();
        }
        if (*stop <= start){
            return context.cacheResult(PyCppUtil::genStr(newVal));
        }
        if (step == 1){
            newVal = s.substr(start, *stop - start);
        }
        else{
            for (int i = start; i < *stop && i < (int)s.size(); i += step){
                newVal += s[i];
            }
        }
    }
    else{
        for (int i = start; i > *stop; i += step){
            int index = i;
            if (index < 0){
                index = int(s.size()) + index;
            }
            if (index < 0 || index >= (int)s.size()){
                break;
            }
            newVal += s[index];
        }
    }
    return context.cacheResult(PyCppUtil::genStr(newVal));
}
static size_t hashStr(const string& s){
    size_t result = 0;
    for (size_t i = 0; i < s.size(); ++i) {
        result = (result * 131) + s[i];
    }
    return result; 
}

size_t PyStrHandler::handleHash(PyContext& context, const PyObjPtr& self) const{
    return size_t(-1 * hashStr(self.cast<PyObjStr>()->value));
}




