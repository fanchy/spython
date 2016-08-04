#ifndef _PARSER_H_
#define _PARSER_H_

#include <iostream>
#include <string>
#include <vector>
#include <map>
#include <stdexcept>

#include "Base.h"
#include "PyObj.h"
#include "ExprAST.h"

namespace ff{

class ExprAST;
class PyObjModule;



struct ParseHelper {
    ParseHelper(const std::string& strCode):m_nCurTok(0), cLastOne(' '), m_codeTocheck(strCode), m_nIndex(0),NumVal(0),nCurIndent(0),nIndentWidth(4),line(1),col(1) {
        m_codeTocheck += '\n';
        for (unsigned int i = m_nIndex; i < m_codeTocheck.size(); ++i) {
            if (m_codeTocheck[i] == ' ') {
                ++nCurIndent;
            } else {
                break;
            }
        }
    }

    TokenType at();
    TokenType next();
    TokenType checkNext(int* nCurIndentOldNext = NULL);
    TokenType gettok();
    char getCharNext();
    int  calNextLevelIndent(int nCurNeedIndent);

    TokenType m_nCurTok;
    char cLastOne;
    std::string m_codeTocheck;
    unsigned int    m_nIndex;
    int    NumVal;
    int nCurIndent;
    int nIndentWidth;
    int line;
    int col;
    std::string IdentifierStr;
    std::string strVal;
};


struct PyObjOpsTool{
    static PyObjPtr assign(PyObjPtr& dest, ExprASTPtr& lval, PyObjPtr& rval){
        PyObjPtr& v = lval->getFieldVal(dest);
        v = rval;
        return rval;
    }
};

struct ParseTool {
    ParseTool(PyObjPtr obj):objModule(obj) {
    }
    int GetTokPrecedence(TokenType c);
    void popTokenIfBinOps(ParseHelper& parseHelper, TokenType curTok);
    
    ExprASTPtr ParseNumberExpr(ParseHelper& parseHelper);
    ExprASTPtr ParseParenExpr(ParseHelper& parseHelper);
    
    ExprASTPtr ParseIfExpr(ParseHelper& parseHelper);
    ExprASTPtr ParseForExpr(ParseHelper& parseHelper);
    
    ExprASTPtr ParseIdentifierExpr(ParseHelper& parseHelper);
    ExprASTPtr ParsePrimary(ParseHelper& parseHelper, bool checkTuple = true);
    ExprASTPtr ParseBinOpRHS(ParseHelper& parseHelper, int ExprPrec, ExprASTPtr LHS);
    ExprASTPtr ParseExpression(ParseHelper& parseHelper);
    bool       ParsePrototype(ParseHelper& parseHelper, FunctionAST& f);
    ExprASTPtr ParseDefinition(ParseHelper& parseHelper, int nNeedIndent);
    
    ExprASTPtr ParseClassExpr(ParseHelper& parseHelper, int nNeedIndent);

    ExprASTPtr ParseTopLevelExpr(ParseHelper& parseHelper);
    
    ExprASTPtr ParseTupleExpr(ParseHelper& parseHelper, ExprASTPtr first);
    

    void HandleTopLevelExpression(ParseHelper& parseHelper, int nNeedIndent);

    bool MainLoop(ParseHelper& parseHelper);

    PyObjPtr objModule;
};

}
#endif
  
  
    
    





