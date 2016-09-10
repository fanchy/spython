#include "Base.h"
#include "PyObj.h"

using namespace std;
using namespace ff;

string PyObj::dump(PyObjPtr& self) {
    string ret = self->handler->dump(self);
    if (ret.empty() == false)
        return ret;
    
    char msg[256] = {0};
    snprintf(msg, sizeof(msg), "type:%d\n", self->getType());
    ret += msg;
    const ObjIdInfo& p = self->getObjIdInfo();
    for (unsigned int i = 0; i < self->m_objStack.size(); ++i) {
        
        string n = singleton_t<ObjFieldMetaData>::instance_ptr()->getFieldName(p.nModuleId, p.nObjectId, i);
        if (self->m_objStack.size() < 10)
            snprintf(msg, sizeof(msg), "[%d-%d] %d %s = ", p.nModuleId, p.nObjectId, i, n.c_str());
        else 
            snprintf(msg, sizeof(msg), "[%d-%d] %02d %s = ", p.nModuleId, p.nObjectId, i, n.c_str());
        ret += msg;
        if (!self->m_objStack[i]) {
            ret += "NULL\n";
            continue;
        }
        ret += self->m_objStack[i]->handler->handleStr(self->m_objStack[i]);
        ret += "\n";
    }
    return ret;
}

int PyObj::getType() const{
    return handler->getType();
}
bool PyObjHandler::handleBool(PyContext& context, const PyObjPtr& self) const{
    return false;
}
bool PyObjHandler::handleEqual(PyContext& context, const PyObjPtr& self, const PyObjPtr& val) const{
    return false;
}
bool PyObjHandler::handleLessEqual(PyContext& context, const PyObjPtr& self, const PyObjPtr& val) const{
    throw PyException::buildException("handleLessEqual invalid");return self; 
}
bool PyObjHandler::handleGreatEqual(PyContext& context, const PyObjPtr& self, const PyObjPtr& val) const{
    throw PyException::buildException("handleGreatEqual invalid");return self;
}
bool PyObjHandler::handleIn(PyContext& context, const PyObjPtr& self, const PyObjPtr& val) const{
    throw PyException::buildException("handleIn invalid");return self;
}

PyObjPtr& PyObjHandler::handleAdd(PyContext& context, PyObjPtr& self, PyObjPtr& val){
    throw PyException::buildException("handleAdd invalid");return self;
}
PyObjPtr& PyObjHandler::handleSub(PyContext& context, PyObjPtr& self, PyObjPtr& val){
    throw PyException::buildException("handleSub invalid");return self;
}
PyObjPtr& PyObjHandler::handleMul(PyContext& context, PyObjPtr& self, PyObjPtr& val){
    throw PyException::buildException("handleMul invalid");return self;
}
PyObjPtr& PyObjHandler::handleDiv(PyContext& context, PyObjPtr& self, PyObjPtr& val){
    throw PyException::buildException("handleDiv invalid");return self;
}
PyObjPtr& PyObjHandler::handleMod(PyContext& context, PyObjPtr& self, PyObjPtr& val){
    throw PyException::buildException("handleMod invalid");return self;
}
PyObjPtr& PyObjHandler::handleCall(PyContext& context, PyObjPtr& self, std::vector<ArgTypeInfo>& allArgsVal, std::vector<PyObjPtr>& argAssignVal){
    throw PyException::buildException("handleCall invalid");return self;
}
size_t PyObjHandler::handleHash(const PyObjPtr& self) const{
    return size_t(self.get());
}

PyObjPtr& PyObj::getVar(PyContext& pc, PyObjPtr& self2, unsigned int nFieldIndex) {
    //DMSG(("nFieldIndex %d\n", nFieldIndex));
    if (nFieldIndex < m_objStack.size()) {
        return m_objStack[nFieldIndex];
    }
    for (unsigned int i = m_objStack.size(); i <= nFieldIndex; ++i){
        m_objStack.push_back(PyObjTool::buildNULL());
    }
    return m_objStack[nFieldIndex];
}


runtime_error PyException::buildIndentException(ParseHelper& parseHelper, int nNeedIndent, string err) {
    char msg[1024] = {0};
    //snprintf(msg, sizeof(msg) - 1, "line:%d,col:%d,err:space indent need %d, given %d %s", parseHelper.line, parseHelper.col, nNeedIndent, parseHelper.nCurIndent, err.c_str());
    return runtime_error(msg);
}
runtime_error PyException::buildException(ParseHelper& parseHelper, const string& err) {
    char msg[1024] = {0};
    //snprintf(msg, sizeof(msg) - 1, "line:%d,col:%d,err:%s,curTok=%d", parseHelper.line, parseHelper.col, err.c_str(), parseHelper.at());
    return runtime_error(msg);
}
runtime_error PyException::buildException(const string& err) {
    char msg[1024];
    snprintf(msg, sizeof(msg) - 1, "line:%d,col:%d,err:%s", 0, 0, err.c_str());
    return runtime_error(msg);
}

PyHelper::PyHelper(){
    m_allKeyword.insert("False");
    m_allKeyword.insert("class");
    m_allKeyword.insert("finally");
    m_allKeyword.insert("is");
    m_allKeyword.insert("return");
    m_allKeyword.insert("None");
    m_allKeyword.insert("continuefor");
    m_allKeyword.insert("lambda");
    m_allKeyword.insert("try");
    m_allKeyword.insert("True");
    m_allKeyword.insert("def");
    m_allKeyword.insert("from");
    m_allKeyword.insert("nonlocalwhile");
    m_allKeyword.insert("and");
    m_allKeyword.insert("del");
    m_allKeyword.insert("global");
    m_allKeyword.insert("not");
    m_allKeyword.insert("with");
    m_allKeyword.insert("as");
    m_allKeyword.insert("elif");
    m_allKeyword.insert("if");
    m_allKeyword.insert("or");
    m_allKeyword.insert("yield");
    m_allKeyword.insert("assert");
    m_allKeyword.insert("else");
    m_allKeyword.insert("import");
    m_allKeyword.insert("pass");
    m_allKeyword.insert("break");
    m_allKeyword.insert("except");
    m_allKeyword.insert("in");
    m_allKeyword.insert("raise");
    
    m_allKeyword.insert("print");
    m_allKeyword.insert("continue");
    m_allKeyword.insert("while");
}


bool PyHelper::isKeyword(const string& v){
    if (m_allKeyword.find(v) != m_allKeyword.end()){
        return true;
    }
    return false;
}

struct NoneTraits{
    NoneTraits(){
        retPtr = new PyObjNone();
    }
    PyObjPtr retPtr;
};
struct NULLTraits{
    NULLTraits(){
        retPtr = new PyObjNone(true);
    }
    PyObjPtr retPtr;
};
PyObjPtr& PyObjTool::buildNone(){
    return singleton_t<NoneTraits>::instance_ptr()->retPtr;
}
PyObjPtr PyObjTool::buildNULL(){
    return NULL;//singleton_t<NULLTraits>::instance_ptr()->retPtr;
}


struct boolTrueTraits{
    boolTrueTraits(){
        retPtr = new PyObjBool(true);
    }
    PyObjPtr retPtr;
};

struct boolFalseTraits{
    boolFalseTraits(){
        retPtr = new PyObjBool(false);
    }
    PyObjPtr retPtr;
};

PyObjPtr& PyObjTool::buildBool(bool b){
    if (b){
        return singleton_t<boolTrueTraits>::instance_ptr()->retPtr;
    }
    return singleton_t<boolFalseTraits>::instance_ptr()->retPtr;
}
PyObjPtr& PyObjTool::buildTrue(){
    return singleton_t<boolTrueTraits>::instance_ptr()->retPtr;
}
PyObjPtr& PyObjTool::buildFalse(){
    return singleton_t<boolFalseTraits>::instance_ptr()->retPtr;
}

bool PyObjTool::handleBool(PyObjPtr b){
    if (!b){
        return false;
    }
    if (b->getType() == PY_BOOL){
        return b.cast<PyObjBool>()->value;
    }
    else if (b->getType() == PY_INT){
        return b.cast<PyObjInt>()->value != 0;
    }
    return false;
}

unsigned int ExprAST::getFieldIndex(PyContext& pycontext){
    
    PyObjPtr& context = pycontext.curstack;
    const ObjIdInfo& p = context->getObjIdInfo();
    if (p.nModuleId >= module2objcet2fieldIndex.size()){
        module2objcet2fieldIndex.resize(p.nModuleId + 1);
    }

    vector<int>& object2index = module2objcet2fieldIndex[p.nModuleId];
    
    if (p.nObjectId >= object2index.size()){
        object2index.resize(p.nObjectId + 1, -1);
        object2index[p.nObjectId] = context->getFieldNum();
        singleton_t<ObjFieldMetaData>::instance_ptr()->module2object2fieldname[p.nModuleId][p.nObjectId][object2index[p.nObjectId]] = this->name;
        DMSG(("filedname2 %s %s %d\n", context->handler->handleStr(context).c_str(), this->name.c_str(), object2index[p.nObjectId]));
    }
    
    int& nIndex = object2index[p.nObjectId];
    if (nIndex < 0){
        nIndex = context->getFieldNum();
        singleton_t<ObjFieldMetaData>::instance_ptr()->module2object2fieldname[p.nModuleId][p.nObjectId][object2index[p.nObjectId]] = this->name;
    }
    return (unsigned int)nIndex;
}
PyObjPtr& ExprAST::getFieldVal(PyContext& pycontext){
    //DMSG(("filedname %s\n", this->name.c_str()));
    PyObjPtr& context = pycontext.curstack;
    return context->getVar(pycontext, context, this->getFieldIndex(pycontext));
}

