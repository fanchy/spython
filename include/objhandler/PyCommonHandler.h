#ifndef _PY_COMMOn_HANDLER_H_
#define _PY_COMMOn_HANDLER_H_

#include <iostream>
#include <string>
#include <vector>
#include <map>
#include <vector>
#include <stdexcept>

#include "Base.h"
#include "Singleton.h"

namespace ff {

class PyCommonHandler: public PyObjHandler{
public:
    PyCommonHandler();
    virtual int getType() const {
        return 0;
    }

    virtual std::string handleStr(PyContext& context, const PyObjPtr& self) const;
    
    virtual std::string handleRepr(PyContext& context, const PyObjPtr& self) const{
        return this->handleStr(context, self);
    }
    bool handleCompare(PyContext& context, const PyObjPtr& self, const PyObjPtr& val, ExprASTPtr e, int flag = 0) const;
    
    virtual bool handleBool(PyContext& context, const PyObjPtr& self) const;
    virtual bool handleLess(PyContext& context, const PyObjPtr& self, const PyObjPtr& val) const;
    virtual bool handleLessEqual(PyContext& context, const PyObjPtr& self, const PyObjPtr& val) const;
    virtual bool handleEqual(PyContext& context, const PyObjPtr& self, const PyObjPtr& val) const;
    virtual bool handleGreat(PyContext& context, const PyObjPtr& self, const PyObjPtr& val) const;
    virtual bool handleGreatEqual(PyContext& context, const PyObjPtr& self, const PyObjPtr& val) const;
    
    virtual long handleLen(PyContext& context, PyObjPtr& self);

    virtual bool handleContains(PyContext& context, const PyObjPtr& self, const PyObjPtr& val) const;

    PyObjPtr& handleBinOps(PyContext& context, PyObjPtr& self, PyObjPtr& val, ExprASTPtr e);
    
    virtual PyObjPtr& handleAdd(PyContext& context, PyObjPtr& self, PyObjPtr& val);
    virtual PyObjPtr& handleSub(PyContext& context, PyObjPtr& self, PyObjPtr& val);
    virtual PyObjPtr& handleMul(PyContext& context, PyObjPtr& self, PyObjPtr& val);
    virtual PyObjPtr& handleDiv(PyContext& context, PyObjPtr& self, PyObjPtr& val);
    virtual PyObjPtr& handleMod(PyContext& context, PyObjPtr& self, PyObjPtr& val);
    virtual PyObjPtr& handleCall(PyContext& context, PyObjPtr& self, std::vector<ArgTypeInfo>& allArgsVal, 
                                 std::vector<PyObjPtr>& argAssignVal);
    virtual std::size_t    handleHash(PyContext& context, const PyObjPtr& self) const;
    virtual bool handleIsInstance(PyContext& context, PyObjPtr& self, PyObjPtr& val);
    virtual std::string dump(PyObjPtr& self) {
        return "";
    }
    virtual PyObjPtr& handleSlice(PyContext& context, PyObjPtr& self, PyObjPtr& startVal, int* stop, int step);
    virtual PyObjPtr& handleSliceAssign(PyContext& context, PyObjPtr& self, PyObjPtr& k, PyObjPtr& v);
    
public:
    ExprASTPtr  expr__str__;
    ExprASTPtr  expr__lt__;
    ExprASTPtr  expr__le__;
    ExprASTPtr  expr__eq__;
    //ExprASTPtr  expr__ne__;
    ExprASTPtr  expr__gt__;
    ExprASTPtr  expr__ge__;
    ExprASTPtr  expr__cmp__;

    ExprASTPtr  expr__len__;
    ExprASTPtr  expr__contains__;
    
    ExprASTPtr  expr__add__;
    ExprASTPtr  expr__sub__;
    ExprASTPtr  expr__mul__;
    //ExprASTPtr  expr__floordiv__;
    ExprASTPtr  expr__mod__;
    
    ExprASTPtr  expr__divmod__;
    //ExprASTPtr  expr__pow__;
    ExprASTPtr  expr__lshift__;
    ExprASTPtr  expr__rshift__;
    //ExprASTPtr  expr__and__;
    //ExprASTPtr  expr__xor__;
    //ExprASTPtr  expr__or__;
    ExprASTPtr  expr__div__;
    //ExprASTPtr  expr__truediv__;
    //ExprASTPtr  expr__radd__
    //ExprASTPtr  expr__rsub__
    //ExprASTPtr  expr__rmul__
    //ExprASTPtr  expr__rdiv__
    //ExprASTPtr  expr__rtruediv__
    //ExprASTPtr  expr__rfloordiv__
    /*
    object.__rmod__(self, other)
    object.__rdivmod__(self, other)
    object.__rpow__(self, other)
    object.__rlshift__(self, other)?
    object.__rrshift__(self, other)
    object.__rand__(self, other)
    object.__rxor__(self, other)
    object.__ror__(self, other)
    */
    ExprASTPtr  expr__iadd__;
    ExprASTPtr  expr__isub__;
    ExprASTPtr  expr__imul__;
    ExprASTPtr  expr__idiv__;
    ExprASTPtr  expr__itruediv__;
    ExprASTPtr  expr__ifloordiv__;
    ExprASTPtr  expr__imod__;
    ExprASTPtr  expr__ipow__;
    ExprASTPtr  expr__ilshift__;
    ExprASTPtr  expr__irshift__;
    ExprASTPtr  expr__iand__;
    ExprASTPtr  expr__ixor__;
    ExprASTPtr  expr__ior__;
    ExprASTPtr  expr__long__;
    ExprASTPtr  expr__enter__;
    ExprASTPtr  expr__exit__;
    
    ExprASTPtr  expr__call__;
    ExprASTPtr  expr__hash__;
};


}
#endif


