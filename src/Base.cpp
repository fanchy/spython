#include "Base.h"
#include "PyObj.h"
#include <stdio.h>
#include <stdarg.h>
using namespace std;
using namespace ff;

string PyObj::dump(PyContext& context, PyObjPtr& self, int preBlank) {
    string ret = self->getHandler()->dump(self);
    if (ret.empty() == false)
        return ret;
    string blank;
    for (int j = 0; j < preBlank; ++j){
        blank += "  ";
    }
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
        
        if (!self->m_objStack[i]) {
            //ret += "NULL\n";
            continue;
        }else{
            ret += blank + msg;
        }
        if ((PyCheckModule(self->m_objStack[i]) || PyCheckClass(self->m_objStack[i])) && preBlank < 4){
            ret += PyObj::dump(context, self->m_objStack[i], preBlank + 1);
            continue;
        }
        ret += self->m_objStack[i]->getHandler()->handleStr(context, self->m_objStack[i]);
        ret += "\n";
    }
    return ret;
}
void PyObj::release(){
    handler->handleRelese(this);
}
int PyObj::getType() const{
    return handler->getType();
}
bool PyObjHandler::handleBool(PyContext& context, const PyObjPtr& self) const{
    return false;
}
bool PyObjHandler::handleEqual(PyContext& context, const PyObjPtr& self, const PyObjPtr& val) const{
    return self.get() == val.get();
}
bool PyObjHandler::handleLessEqual(PyContext& context, const PyObjPtr& self, const PyObjPtr& val) const{
    throw PyException::buildException("handleLessEqual invalid");return self; 
}
bool PyObjHandler::handleGreatEqual(PyContext& context, const PyObjPtr& self, const PyObjPtr& val) const{
    throw PyException::buildException("handleGreatEqual invalid");return self;
}
bool PyObjHandler::handleContains(PyContext& context, const PyObjPtr& self, const PyObjPtr& val) const{
    throw PyException::buildException("handleContains invalid");return self;
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

PyObjPtr& PyObjHandler::handleIAdd(PyContext& context, PyObjPtr& self, PyObjPtr& val){
    return self->getHandler()->handleAdd(context, self, val);
}
PyObjPtr& PyObjHandler::handleISub(PyContext& context, PyObjPtr& self, PyObjPtr& val){
    return self->getHandler()->handleSub(context, self, val);
}
PyObjPtr& PyObjHandler::handleIMul(PyContext& context, PyObjPtr& self, PyObjPtr& val){
    return self->getHandler()->handleMul(context, self, val);
}
PyObjPtr& PyObjHandler::handleIDiv(PyContext& context, PyObjPtr& self, PyObjPtr& val){
    return self->getHandler()->handleDiv(context, self, val);
}
PyObjPtr& PyObjHandler::handleIMod(PyContext& context, PyObjPtr& self, PyObjPtr& val){
    return self->getHandler()->handleMod(context, self, val);
}
PyObjPtr& PyObjHandler::handleCall(PyContext& context, PyObjPtr& self, std::vector<ArgTypeInfo>& allArgsVal, std::vector<PyObjPtr>& argAssignVal){
    throw PyException::buildException("handleCall invalid");return self;
}
long PyObjHandler::handleLen(PyContext& context, PyObjPtr& self){
    return -1;
}
size_t PyObjHandler::handleHash(PyContext& context, const PyObjPtr& self) const{
    return size_t(self.get());
}
bool PyObjHandler::handleIsInstance(PyContext& context, PyObjPtr& self, PyObjPtr& val){
    return false;
}
PyObjPtr& PyObjHandler::handleSlice(PyContext& context, PyObjPtr& self, PyObjPtr& startVal, int* stop, int step){
    throw PyException::buildException("handleSlice invalid");return self;
}
PyObjPtr& PyObjHandler::handleSliceAssign(PyContext& context, PyObjPtr& self, PyObjPtr& k, PyObjPtr& v){
    PyObjPtr& lval = this->handleSlice(context, self, k, NULL, 1);
    if (lval.get() == context.getCacheResult().get()){
        throw PyException::buildException("TypeError: object does not support item assignment");
    }
    lval = v;
    return lval;
}
int PyObjHandler::handleCmp(PyContext& context, const PyObjPtr& self, const PyObjPtr& val) const{
    return 0;
}

PyObjPtr& PyObj::getVar(PyContext& pc, PyObjPtr& self2, ExprAST* e) {
    unsigned int nFieldIndex = e->getFieldIndex(pc, self2);
    //DMSG(("nFieldIndex %d\n", nFieldIndex));
    if (nFieldIndex < m_objStack.size()) {
        return m_objStack[nFieldIndex];
    }
    for (unsigned int i = m_objStack.size(); i <= nFieldIndex; ++i){
        m_objStack.push_back(PyObjTool::buildNULL());
    }
    return m_objStack[nFieldIndex];
}


runtime_error PyException::buildException(const char * format, ...) {
    char msg[512];
      
    va_list vl;  
    va_start(vl, format);  
  
    vsprintf(msg, format, vl);  
    return runtime_error(msg);
}

PyHelper::PyHelper(){
    m_allKeyword.insert("False");
    m_allKeyword.insert("class");
    m_allKeyword.insert("finally");
    m_allKeyword.insert("is");
    m_allKeyword.insert("return");
    //m_allKeyword.insert("None");
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
    m_allKeyword.insert("for");
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
    if (PyCheckBool(b)){
        return b.cast<PyObjBool>()->value;
    }
    else if (PyCheckInt(b)){
        return b.cast<PyObjInt>()->value != 0;
    }
    return false;
}
PyObjPtr& ExprAST::getFieldVal(PyContext& pycontext){
    PyObjPtr& obj = pycontext.curstack;
    return obj->getVar(pycontext, obj, this);
}
/*
unsigned int ExprAST::getFieldIndex(PyContext& context, PyObjPtr& obj){
    const ObjIdInfo& p = obj->getObjIdInfo();
    if (p.nModuleId >= module2objcet2fieldIndex.size()){
        module2objcet2fieldIndex.resize(p.nModuleId + 1);
    }

    vector<int>& object2index = module2objcet2fieldIndex[p.nModuleId];
    
    if (p.nObjectId >= object2index.size()){
        for (size_t i = object2index.size(); i < p.nObjectId + 1; ++i){
            object2index.push_back(-1);
            //DMSG(("filedname5 %s %s [%d-%d]\n", obj->getHandler()->handleStr(context, obj).c_str(), this->name.c_str(), object2index[i], i));
        }
        
        object2index[p.nObjectId] = context.allocFieldIndex(p.nModuleId, p.nObjectId);
        singleton_t<ObjFieldMetaData>::instance_ptr()->module2object2fieldname[p.nModuleId][p.nObjectId][object2index[p.nObjectId]] = this->name;
        //DMSG(("filedname2 %s %s %d[%d-%d]\n", obj->getHandler()->handleStr(context, obj).c_str(), this->name.c_str(), object2index[p.nObjectId], p.nModuleId, p.nObjectId));
    }
    
    int& nIndex = object2index[p.nObjectId];
    if (nIndex < 0){
        nIndex = context.allocFieldIndex(p.nModuleId, p.nObjectId);
        singleton_t<ObjFieldMetaData>::instance_ptr()->module2object2fieldname[p.nModuleId][p.nObjectId][object2index[p.nObjectId]] = this->name;
        //DMSG(("filedname3 [%d]%s %s %d[%d-%d]\n", obj->getType(), obj->getHandler()->handleStr(context, obj).c_str(), this->name.c_str(), object2index[p.nObjectId], p.nModuleId, p.nObjectId));
    }
    //DMSG(("filedname4 [%d]%s %s %d[%d-%d] %d-%p\n", obj->getType(), obj->getHandler()->handleStr(context, obj).c_str(), this->name.c_str(), object2index[p.nObjectId], p.nModuleId, p.nObjectId, nIndex, this));
    return (unsigned int)nIndex;
}
*/
unsigned int ExprAST::getFieldIndex(PyContext& context, PyObjPtr& obj){
    const ObjIdInfo& p = obj->getObjIdInfo();
    vector<int>& object2index = module2objcet2fieldIndex;
    
    if (p.nObjectId >= object2index.size()){
        object2index.resize(p.nObjectId + 1, -1);
        
        object2index[p.nObjectId] = context.allocFieldIndex(p.nModuleId, p.nObjectId);
        singleton_t<ObjFieldMetaData>::instance_ptr()->module2object2fieldname[p.nModuleId][p.nObjectId][object2index[p.nObjectId]] = this->name;
        //DMSG(("filedname2 %s %s %d[%d-%d]\n", obj->getHandler()->handleStr(context, obj).c_str(), this->name.c_str(), object2index[p.nObjectId], p.nModuleId, p.nObjectId));
    }
    
    int& nIndex = object2index[p.nObjectId];
    if (nIndex < 0){
        nIndex = context.allocFieldIndex(p.nModuleId, p.nObjectId);
        singleton_t<ObjFieldMetaData>::instance_ptr()->module2object2fieldname[p.nModuleId][p.nObjectId][object2index[p.nObjectId]] = this->name;
        //DMSG(("filedname3 [%d]%s %s %d[%d-%d]\n", obj->getType(), obj->getHandler()->handleStr(context, obj).c_str(), this->name.c_str(), object2index[p.nObjectId], p.nModuleId, p.nObjectId));
    }
    //DMSG(("filedname4 [%d]%s %s %d[%d-%d] %d-%p\n", obj->getType(), obj->getHandler()->handleStr(context, obj).c_str(), this->name.c_str(), object2index[p.nObjectId], p.nModuleId, p.nObjectId, nIndex, this));
    return (unsigned int)nIndex;
}
int PyContext::allocFieldIndex(int m, int o){
    map<int, int>& v = recordAllFiledIndex[m];
    map<int, int>::iterator it = v.find(o);
    
    int ret = 0;
    if (it != v.end()){
        it->second += 1;
        ret = it->second;
    }
    else{
        v[o] = ret;
    }

    return ret;
}

PyContext& PyContext::addBuiltin(const string& name, PyObjPtr v){
    allBuiltin[name] = v;
    return *this;
}
PyObjPtr&  PyContext::getBuiltin(const string& name){
    return allBuiltin[name];
}
PyContext& PyContext::addModule(const std::string& name, PyObjPtr v){
    int nFileId = allocFileIdByPath(name);
    setFileIdModCache(nFileId, v);
    return *this;
}
PyObjPtr PyContext::getModule(const std::string& name){
    int nFileId = allocFileIdByPath(name);
    return getFileIdModCache(nFileId);
}

