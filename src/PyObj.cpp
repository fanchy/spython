
#include "PyObj.h"
#include "ExprAST.h"
using namespace ff;


PyObjPtr PyObjFuncDef::handleCall(PyObjPtr context, list<PyObjPtr>& args){
    //DMSG(("PyObjFuncDef::handleCall...\n"));
    //DMSG(("PyObjFuncDef::handleCall2...\n"));
    return funcASTPtr.cast<FuncCodeImpl>()->exeCode(context, args);
}
void PyObjFuncDef::dump() {
    DMSG(("%s(func)", funcASTPtr->name.c_str()));
}

PyObjPtr PyObjClassDef::handleCall(PyObjPtr self, list<PyObjPtr>& args){
    //DMSG(("PyObjFuncDef::handleCall...\n"));
    //DMSG(("PyObjFuncDef::handleCall2...\n"));
    //return funcASTPtr.cast<FuncCodeImpl>()->exeCode(context, args);
    PyObjPtr ret = new PyObjClassObj(self);
    return ret;
}
void PyObjClassDef::dump() {
    DMSG(("%s(class)", classASTPtr->name.c_str()));
}

PyObjPtr PyObjClassFunc::handleCall(PyObjPtr context, list<PyObjPtr>& args){
    //DMSG(("PyObjClassFunc::handleCall...\n"));
    //args.insert(args.begin(), classSelf);
    args.push_front(classSelf);
    return funcDefPtr.cast<PyObjFuncDef>()->handleCall(context, args);
}
void PyObjClassFunc::dump(){
    DMSG(("%s(classfunc)", funcDefPtr.cast<PyObjFuncDef>()->funcASTPtr->name.c_str()));
}

void PyObjClassObj::dump() {
    DMSG(("%s(classobj)", classDefPtr.cast<PyObjClassDef>()->classASTPtr->name.c_str()));
}

PyObjPtr& PyObjClassObj::getVar(PyObjPtr& self, unsigned int nFieldIndex)
{
    if (nFieldIndex < m_objStack.size()) {
        return this->PyObj::getVar(self, nFieldIndex);
    }

    for (unsigned int i = m_objStack.size(); i <= nFieldIndex; ++i){
        m_objStack.push_back(PyObjTool::buildNone());
    }
    
    PyObjPtr& ret = m_objStack[nFieldIndex];
    ret = classDefPtr->getVar(classDefPtr, nFieldIndex);
    if (PY_FUNC_DEF == ret->getType()){
        ret = new PyObjClassFunc(self, ret);
    }
    return ret;
}
