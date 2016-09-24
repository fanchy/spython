#ifndef _PY_COMMOn_HANDLER_H_
#define _PY_COMMOn_HANDLER_H_

#include <iostream>
#include <string>
#include <vector>
#include <map>
#include <vector>
#include <stdexcept>

#include "Base.h"
#include "singleton.h"

namespace ff {

class PyCommonHandler: public PyObjHandler{
public:
    PyCommonHandler();
    virtual int getType() const {
        return 0;
    }
    virtual PyIterPtr getIter(){
        return NULL;
    }
    virtual std::string handleStr(PyContext& context, const PyObjPtr& self) const;
    
    virtual std::string handleRepr(PyContext& context, const PyObjPtr& self) const{
        return this->handleStr(context, self);
    }
    virtual bool handleBool(PyContext& context, const PyObjPtr& self) const;
    virtual bool handleEqual(PyContext& context, const PyObjPtr& self, const PyObjPtr& val) const;
    virtual bool handleLessEqual(PyContext& context, const PyObjPtr& self, const PyObjPtr& val) const;
    virtual bool handleGreatEqual(PyContext& context, const PyObjPtr& self, const PyObjPtr& val) const;
    virtual bool handleIn(PyContext& context, const PyObjPtr& self, const PyObjPtr& val) const;
    
    virtual bool handleLess(PyContext& context, const PyObjPtr& self, const PyObjPtr& val) const{
        if (self->getHandler()->handleGreatEqual(context, self, val) == false){
            return true;
        }
        return false;
    }
    virtual bool handleGreat(PyContext& context, const PyObjPtr& self, const PyObjPtr& val) const{
        if (self->getHandler()->handleLessEqual(context, self, val) == false){
            return true;
        }
        return false;
    }
    
    virtual PyObjPtr& handleAdd(PyContext& context, PyObjPtr& self, PyObjPtr& val);
    virtual PyObjPtr& handleSub(PyContext& context, PyObjPtr& self, PyObjPtr& val);
    virtual PyObjPtr& handleMul(PyContext& context, PyObjPtr& self, PyObjPtr& val);
    virtual PyObjPtr& handleDiv(PyContext& context, PyObjPtr& self, PyObjPtr& val);
    virtual PyObjPtr& handleMod(PyContext& context, PyObjPtr& self, PyObjPtr& val);
    virtual PyObjPtr& handleCall(PyContext& context, PyObjPtr& self, std::vector<ArgTypeInfo>& allArgsVal, 
                                 std::vector<PyObjPtr>& argAssignVal);
    virtual std::size_t    handleHash(const PyObjPtr& self) const;
    virtual bool handleIsInstance(PyContext& context, PyObjPtr& self, PyObjPtr& val);
    virtual long handleLen(PyContext& context, PyObjPtr& self);
    virtual std::string dump(PyObjPtr& self) {
        return "";
    }
    virtual PyObjPtr& handleSlice(PyContext& context, PyObjPtr& self, int start, int* stop, int step);
    
public:
    ExprASTPtr  expr__str__;
    ExprASTPtr  expr__eq__;
};


}
#endif


