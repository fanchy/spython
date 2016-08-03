#include "Base.h"
#include "PyObj.h"
#include "OldParser.h"
using namespace ff;


void PyObj::dump() {
    DMSG(("dump type:%d\n", this->getType()));
    const ObjIdInfo& p = this->getObjIdInfo();
    for (unsigned int i = 0; i < m_objStack.size(); ++i) {
        
        string n = singleton_t<ObjFieldMetaData>::instance_ptr()->getFiledName(p.nModuleId, p.nObjectId, i);

        DMSG(("[%d-%d] %d %s = ", p.nModuleId, p.nObjectId, i, n.c_str()));
        if (!m_objStack[i]) {
            DMSG(("NULL\n"));
            continue;
        }
        m_objStack[i]->dump();
        DMSG(("\n"));
    }
}

PyObjPtr& PyObj::getVar(PyObjPtr& self, unsigned int nFieldIndex) {
    if (nFieldIndex < m_objStack.size()) {
        return m_objStack[nFieldIndex];
    }
    for (unsigned int i = m_objStack.size(); i <= nFieldIndex; ++i){
        m_objStack.push_back(PyObjTool::buildNone());
    }
    return m_objStack[nFieldIndex];
}


runtime_error PyException::buildIndentException(ParseHelper& parseHelper, int nNeedIndent, string err) {
    char msg[1024];
    snprintf(msg, sizeof(msg) - 1, "line:%d,col:%d,err:space indent need %d, given %d %s", parseHelper.line, parseHelper.col, nNeedIndent, parseHelper.nCurIndent, err.c_str());
    return runtime_error(msg);
}
runtime_error PyException::buildException(ParseHelper& parseHelper, const string& err) {
    char msg[1024];
    snprintf(msg, sizeof(msg) - 1, "line:%d,col:%d,err:%s,curTok=%d", parseHelper.line, parseHelper.col, err.c_str(), parseHelper.at());
    return runtime_error(msg);
}
runtime_error PyException::buildException(const string& err) {
    char msg[1024];
    snprintf(msg, sizeof(msg) - 1, "line:%d,col:%d,err:%s", 0, 0, err.c_str());
    return runtime_error(msg);
}

string PyHelper::token2name(TokenType token){
    map<int, string> cfg;
    cfg[TOK_VAR ] = "TOK_VAR";
    cfg[TOK_NUM ] = "TOK_NUM";
    cfg[TOK_STR ] = "TOK_STR";
    cfg[TOK_CALL] = "TOK_CALL";

    cfg[TOK_LS  ] = "TOK_LS"; //<
    cfg[TOK_LE  ] = "TOK_LE"; //<] = "
    cfg[TOK_GT  ] = "TOK_GT"; //>
    cfg[TOK_GE  ] = "TOK_GE"; //>] = "
    cfg[TOK_EQ  ] = "TOK_EQ"; //] = "] = "
    cfg[TOK_NE  ] = "TOK_NE"; //!] = "
    
    cfg[TOK_ASSIGN] = "TOK_ASSIGN"; // ] = " 
    cfg[TOK_PLUS] = "TOK_PLUS"; // +
    cfg[TOK_SUB ] = "TOK_SUB"; //
    cfg[TOK_MUT ] = "TOK_MUT"; // *
    cfg[TOK_DIV ] = "TOK_DIV"; // /
    
    cfg[TOK_AND ] = "TOK_AND"; // && and
    cfg[TOK_OR  ] = "TOK_OR"; // || or
    cfg[TOK_YU  ] = "TOK_YU"; // &
    cfg[TOK_HUO ] = "TOK_HUO"; // |
    cfg[TOK_FAN ] = "TOK_FAN"; // ! 
    cfg[TOK_FIELD ] = "TOK_FIELD"; // . 
    return cfg[token];
}


struct NoneTraits{
    NoneTraits(){
        retPtr = new PyObjNone();
    }
    PyObjPtr retPtr;
};

PyObjPtr& PyObjTool::buildNone(){
    return singleton_t<NoneTraits>::instance_ptr()->retPtr;
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


PyObjPtr& ExprAST::getFieldVal(PyObjPtr& context){
    const ObjIdInfo& p = context->getObjIdInfo();
    if (p.nModuleId >= module2objcet2fieldIndex.size()){
        module2objcet2fieldIndex.resize(p.nModuleId + 1);
    }

    vector<int>& object2index = module2objcet2fieldIndex[p.nModuleId];
    
    if (p.nObjectId >= object2index.size()){
        object2index.resize(p.nObjectId + 1);
        object2index[p.nObjectId] = context->getFieldNum();
        singleton_t<ObjFieldMetaData>::instance_ptr()->module2object2fieldname[p.nModuleId][p.nObjectId][object2index[p.nObjectId]] = this->name;
        
        //DMSG(("filedname %s\n", this->name.c_str()));
    }
    
    int nIndex = object2index[p.nObjectId];
    
    return context->getVar(context, nIndex);
}

