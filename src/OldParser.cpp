
#include "Base.h"
#include "OldParser.h"
#include <map>
#include <cstdlib>
using namespace std;
using namespace ff;

TokenType ParseHelper::at() {
    return m_nCurTok;
}
TokenType ParseHelper::next() {
    m_nCurTok = gettok();
    return m_nCurTok;
}
TokenType ParseHelper::checkNext(int* nCurIndentOldNext){
    
    TokenType CurTokOld = m_nCurTok;
    char cLastOneOld = cLastOne;
    int  m_nIndexOld =  m_nIndex;
    int  NumValOld =  NumVal;
    int nCurIndentOld = nCurIndent;
    int nIndentWidthOld = nIndentWidth;
    int lineOld = line;
    int colOld = col;
    string IdentifierStrOld = IdentifierStr;
    string strValOld = strVal;
    
    TokenType ret = gettok();
    if (nCurIndentOldNext){
        *nCurIndentOldNext = nCurIndent;
    }
    
    m_nCurTok = CurTokOld;
    cLastOne = cLastOneOld;
    m_nIndex =  m_nIndexOld;
    NumVal =  NumValOld;
    nCurIndent = nCurIndentOld;
    nIndentWidth = nIndentWidthOld;
    line = lineOld;
    col = colOld;
    IdentifierStr = IdentifierStrOld;
    strVal = strValOld;
    
    
    return ret;
}
int  ParseHelper::calNextLevelIndent(int nCurNeedIndent)
{
    return nCurNeedIndent + nIndentWidth;
}
char ParseHelper::getCharNext() {
    if (m_nIndex < m_codeTocheck.size()){
        char ret = m_codeTocheck[m_nIndex++];
        if (ret == '\n'){
            nCurIndent = 0;
            ++line;
            col = 1;
            for (unsigned int i = m_nIndex; i < m_codeTocheck.size(); ++i){
                if (m_codeTocheck[i] == ' '){
                    ++nCurIndent;
                }
                else{
                    break;
                }
            }
        }
        else{
            ++col;
        }
        //DMSG(("getCharNext cur=%c,%d\n", ret, ret));
        return ret;
    }
    return EOF;
}
/// gettok - Return the next token from standard input.
TokenType ParseHelper::gettok() {

    // Skip any whitespace.
    while (isspace(cLastOne)){
        cLastOne = getCharNext();
    }
 
    if (isalpha(cLastOne) || cLastOne == '_') { // identifier: [a-zA-Z][a-zA-Z0-9]*
        IdentifierStr = cLastOne;
        while (isalnum((cLastOne = getCharNext())) || cLastOne == '_')
            IdentifierStr += cLastOne;
        return TOK_VAR;
    }

    if (isdigit(cLastOne)) { // Number: [0-9.]+
        std::string NumStr;
        do {
            NumStr += cLastOne;
            cLastOne = getCharNext();
        } while (isdigit(cLastOne) || cLastOne == '.');

        NumVal = ::atoi(NumStr.c_str());
        return TOK_INT;
    }

    if (cLastOne == '\'' || cLastOne == '\"') {
        char tmpC = cLastOne;
        strVal.clear();
        do {
            cLastOne = getCharNext();
            if (cLastOne == tmpC){
                break;
            }
            strVal += cLastOne;
        } while (cLastOne != TOK_EOF);
        cLastOne = getCharNext();
        return TOK_STR;
    }
    
    if (cLastOne == '#') {
        // Comment until end of line.
        do
            cLastOne = getCharNext();
        while (cLastOne != EOF && cLastOne != '\n' && cLastOne != '\r');

        if (cLastOne != EOF)
            return gettok();
    }

    // Check for end of file.  Don't eat the EOF.
    if (cLastOne == EOF)
        return TOK_EOF;

    // Otherwise, just return the character as its ascii value.
    int ThisChar = cLastOne;
    cLastOne = getCharNext();
    return ThisChar;
}
int ParseTool::GetTokPrecedence(TokenType c) {
    map<int, int> BinopPrecedence;
    BinopPrecedence[TOK_ASSIGN] = 2;
    
    BinopPrecedence[TOK_AND] = 9, // && and
    BinopPrecedence[TOK_OR]  = 9, // || or
    
    BinopPrecedence[TOK_LS]     = 10;
    BinopPrecedence[TOK_LE]     = 10;
    BinopPrecedence[TOK_GT]     = 10;
    BinopPrecedence[TOK_GE]     = 10;
    BinopPrecedence[TOK_EQ]     = 10;
    BinopPrecedence[TOK_NE]     = 10;
    
    BinopPrecedence[TOK_PLUS]   = 20;
    BinopPrecedence[TOK_SUB]    = 20;
    BinopPrecedence[TOK_MUT]    = 40;
    BinopPrecedence[TOK_DIV]    = 40;
    
    BinopPrecedence[TOK_FIELD]   = 50;
    BinopPrecedence[TOK_CALL]    = 50;
    

    map<int, int>::iterator it = BinopPrecedence.find(c);
    if (it == BinopPrecedence.end())
        return -1;
    int TokPrec = it->second;
    if (TokPrec <= 0)
        return -1;
    return TokPrec;
}

/// numberexpr ::= number
ExprASTPtr ParseTool::ParseNumberExpr(ParseHelper& parseHelper) {
    int NumVal = parseHelper.NumVal;
    ExprASTPtr Result = new NumberExprAST(NumVal);
    parseHelper.next(); // consume the number
    return Result;
}

static ExprASTPtr Error(const char *Str) {
    throw PyException::buildException(Str);
    return NULL;
}

/// parenexpr ::= '(' expression ')'
ExprASTPtr ParseTool::ParseParenExpr(ParseHelper& parseHelper) {
    //DMSG(("ParseTool::ParseParenExpr %d %d\n", parseHelper.at(), parseHelper.checkNext()));
    parseHelper.next();// eat (.
    ExprASTPtr V = ParsePrimary(parseHelper, false);
    if (!V)
        return NULL;
    //DMSG(("ParseTool::ParseParenExpr %s %d %d\n", V->name.c_str(), parseHelper.at(), parseHelper.checkNext()));
    if (parseHelper.at() == ','){
        return ParseTupleExpr(parseHelper, V);
    }
    else if (parseHelper.at() != ')'){
        throw PyException::buildException(parseHelper, "ParseParenExpr expected ')'");
        return NULL;
    }

    parseHelper.next(); // eat ).
    return V;
}


ExprASTPtr ParseTool::ParseIfExpr(ParseHelper& parseHelper) {
    int nNeedIndent = parseHelper.nCurIndent;
    TokenType CurTok = parseHelper.next(); // eat if
    //DMSG(("ParseIfExpr1 begin condition CurTok=%d\n", CurTok));

    ExprASTPtr condition = ParseExpression(parseHelper);
    CurTok = parseHelper.at();
    //DMSG(("ParseIfExpr1 nNeedIndent=%d CurTok=%d %s\n", nNeedIndent, CurTok, parseHelper.IdentifierStr.c_str())); 
    IfExprAST* pIf = new IfExprAST();
    ExprASTPtr ifPtr(pIf);
    pIf->conditions.push_back(condition);
    
    if (CurTok != ':'){
        throw PyException::buildException(parseHelper, "if Expected :");
        return NULL;
    }
    CurTok = parseHelper.next();//! eat ':'
    //DMSG(("ParseIfExpr nNeedIndent=%d CurTok=%d %s\n", nNeedIndent, CurTok, parseHelper.IdentifierStr.c_str())); 
    int nNextLevelIndent = parseHelper.calNextLevelIndent(nNeedIndent);
    //FunctionASTPtr f     = new FunctionAST(Proto);
    
    vector<ExprASTPtr> ifBody;
    //int nCurIndent = parseHelper.nCurIndent;
    //parseHelper.checkNext(&nCurIndent);
    do{
        if (nNextLevelIndent != parseHelper.nCurIndent){
            if (parseHelper.nCurIndent <= nNeedIndent)
            {
                if (parseHelper.nCurIndent == nNeedIndent && parseHelper.at() == TOK_VAR
                    && (parseHelper.IdentifierStr == "elif" || parseHelper.IdentifierStr == "else"))//!check elif else
                {
                    pIf->ifbody.push_back(ifBody);
                    ifBody.clear();
                    if (parseHelper.IdentifierStr == "elif"){
                       CurTok = parseHelper.next(); // eat elif
                       condition = ParseExpression(parseHelper);
                       pIf->conditions.push_back(condition);
                       CurTok = parseHelper.at();
                       if (CurTok != ':'){
                            throw PyException::buildException(parseHelper, "elif Expected :");
                            return NULL;
                        }
                        CurTok = parseHelper.next();//! eat ':'
                    }
                    else{
                        condition = new NumberExprAST(1);
                        pIf->conditions.push_back(condition);
                        CurTok = parseHelper.next(); // eat else
                       if (CurTok != ':'){
                            throw PyException::buildException(parseHelper, "else Expected :");
                            return NULL;
                        }
                        CurTok = parseHelper.next();//! eat ':'
                    }
                    continue;
                }
                //DMSG(("ParseIfExpr break % d, %d %s\n", parseHelper.nCurIndent, parseHelper.line, parseHelper.IdentifierStr.c_str()));
                break;
            }
            throw PyException::buildIndentException(parseHelper, nNextLevelIndent, "ParseIfExpr");
        }
        //DMSG(("ParseIfExpr ParseExpression begin\n"));
        if (ExprASTPtr e = ParseExpression(parseHelper)){
            ifBody.push_back(e);
        }
        else{
            break;
        }
    }
    while(true);

    pIf->ifbody.push_back(ifBody);
    //DMSG(("ParseIfExpr end line=%d\n", parseHelper.line));
    return ifPtr;
}

ExprASTPtr ParseTool::ParseForExpr(ParseHelper& parseHelper) {
    int nNeedIndent = parseHelper.nCurIndent;
    TokenType CurTok = parseHelper.next(); // eat for
    //DMSG(("ParseForExpr begin condition CurTok=%d\n", CurTok));

    ExprASTPtr iterTuple = ParseExpression(parseHelper); //! k or k, v
    CurTok = parseHelper.at();
    //DMSG(("ParseIfExpr1 nNeedIndent=%d CurTok=%d %s\n", nNeedIndent, CurTok, parseHelper.IdentifierStr.c_str())); 
    ForExprAST* pFor = new ForExprAST();
    ExprASTPtr forPtr(pFor);
    pFor->iterTuple = iterTuple;
    
    if (parseHelper.IdentifierStr != "in"){
        throw PyException::buildException(parseHelper, "in Expected for");
        return NULL;
    }
    CurTok = parseHelper.next();//! eat 'in'
    
    pFor->iterFunc = ParseExpression(parseHelper);
    
    CurTok = parseHelper.at();
    if (CurTok != ':'){
        throw PyException::buildException(parseHelper, ": Expected for");
        return NULL;
    }
    CurTok = parseHelper.next();//! eat ':'
    //DMSG(("ParseForExpr nNeedIndent=%d CurTok=%d %s\n", nNeedIndent, CurTok, parseHelper.IdentifierStr.c_str())); 
    int nNextLevelIndent = parseHelper.calNextLevelIndent(nNeedIndent);
    //FunctionASTPtr f     = new FunctionAST(Proto);
    
    if (nNextLevelIndent != parseHelper.nCurIndent){
        if (parseHelper.nCurIndent <= nNeedIndent)
        {
            throw PyException::buildException(parseHelper, "ParseForExpr indent failed");
        }
    }
    
    do{
        int nCurIndent = nNextLevelIndent;
        parseHelper.checkNext(&nCurIndent);
        if (ExprASTPtr e = ParseExpression(parseHelper)){
            //DMSG(("ParseForExpr ParseExpression begin name=%s\n", e->name.c_str()));
            pFor->forBody.push_back(e);
        }
        else{
            break;
        }
        if (nNextLevelIndent != nCurIndent){
            if (nCurIndent <= nNeedIndent)
            {
                break;
            }
        }
        
    }
    while(true);

    //DMSG(("ParseForExpr end line=%d\n", parseHelper.line));
    return forPtr;
}
/// identifierexpr
///   ::= identifier
///   ::= identifier '(' expression* ')'
ExprASTPtr ParseTool::ParseIdentifierExpr(ParseHelper& parseHelper) {
    std::string IdName = parseHelper.IdentifierStr;
    //DMSG(("ParseIdentifierExpr IdName=%s\n", IdName.c_str()));
    if (IdName == "if")
    {
        return ParseIfExpr(parseHelper);
    }
    else if (IdName == "for")
    {
        return ParseForExpr(parseHelper);
    }
    else if (IdName == "continue")
    {
        parseHelper.next(); 
        return singleton_t<VariableExprAllocator>::instance_ptr()->allocIfNotExist<ContinueExprAST>(IdName);
    }
    else if (IdName == "break")
    {
        //DMSG(("ParseIdentifierExpr IdName=%s\n", IdName.c_str()));
        parseHelper.next(); 
        return singleton_t<VariableExprAllocator>::instance_ptr()->allocIfNotExist<BreakExprAST>(IdName);
    }
    else if (IdName == "def")
    {
        return ParseDefinition(parseHelper, parseHelper.nCurIndent);
    }
    else if (IdName == "class")
    {
        return ParseClassExpr(parseHelper, parseHelper.nCurIndent);
    }

    parseHelper.next(); // eat identifier.
    return singleton_t<VariableExprAllocator>::instance_ptr()->alloc(IdName);//new VariableExprAST(IdName);
    /*
    if (CurTok != '(') {// Simple variable ref.
        return singleton_t<VariableExprAllocator>::instance_ptr()->alloc(IdName);//new VariableExprAST(IdName);
    }

    // Call.
    CurTok = parseHelper.next(); // eat (
    ExprASTPtr argsTuple;
    if (CurTok != ')') {
        //!args as tuple
        ExprASTPtr tmpArg = ParseExpression(parseHelper);
        if (!tmpArg){
            return NULL;
        }
        
        if (tmpArg->getType() == EXPR_TUPLE){
            argsTuple = tmpArg;
        }else{
            TupleExprAST* p = new TupleExprAST();
            p->values.push_back(tmpArg);
            argsTuple = p; 
        }

        CurTok = parseHelper.at();

        if (CurTok != ')'){
            throw PyException::buildException(parseHelper, "Expected ')' or ',' in arguments list");
            return NULL;
        }
    }

    // Eat the ')'.
    CurTok = parseHelper.next();
    ExprASTPtr callF = singleton_t<VariableExprAllocator>::instance_ptr()->alloc(IdName);//new VariableExprAST(IdName);
    
    if (!argsTuple){
        argsTuple = new TupleExprAST();
    }
    return new CallExprAST(callF, argsTuple);
    */
}


/// primary
///   ::= identifierexpr
///   ::= numberexpr
///   ::= parenexpr
ExprASTPtr ParseTool::ParsePrimary(ParseHelper& parseHelper, bool checkTuple) {
    TokenType CurTok = parseHelper.at();
    //DMSG(("ParseTool::ParsePrimary begin CurTok:%d\n", int(CurTok)));
    ExprASTPtr result;
    switch (CurTok) {
        case TOK_VAR:{
            result =  ParseIdentifierExpr(parseHelper);
            //DMSG(("ParseTool::ParsePrimary end token CurTok:%d\n", int(parseHelper.at())));
        }break;
        case TOK_INT:{
            result = ParseNumberExpr(parseHelper);
            //DMSG(("ParseTool::ParsePrimary end token CurTok:%d\n", int(parseHelper.at())));
        }break;
        case TOK_STR:{
            result = new StrExprAST(parseHelper.strVal);
            parseHelper.next();
        }break;
        case '(':{
            result= ParseParenExpr(parseHelper);
        }break;
        case TOK_EOF:{
            return NULL;
        }break;
        default:{
            DMSG(("ParseTool::ParsePrimary unkonwn token CurTok:%d\n", int(CurTok)));
            throw PyException::buildException(parseHelper, "ParseTool::ParsePrimary unkonwn token CurTok");
            parseHelper.next();
            return NULL;
        }break;
    }

    CurTok = parseHelper.at();
    if (checkTuple && CurTok == ','){
        //DMSG(("ParseTool::ParsePrimary check tuple\n"));
        result = ParseTupleExpr(parseHelper, result);
    }
    return result;
}

ExprASTPtr ParseTool::ParseTupleExpr(ParseHelper& parseHelper, ExprASTPtr first){
    TokenType CurTok = parseHelper.at();
    TupleExprAST* tuple = new TupleExprAST();
    
    ExprASTPtr ret = tuple;
    if (first){
        tuple->values.push_back(first);
        //DMSG(("ParseTool::ParseTupleExpr first name=%s\n", first->name.c_str()));
    }

    do{
        if (CurTok == ',' || CurTok == '('){
            CurTok = parseHelper.next();//!eat , or (
        }
        if (CurTok == ')') //!end tuple
        {
            break;
        }
        ExprASTPtr val = ParsePrimary(parseHelper, false);
        if (!val)
        {
            throw PyException::buildException(parseHelper, "tuple parse fail");
        }
        //DMSG(("ParseTool::ParseTupleExpr name=%s\n", val->name.c_str()));
        tuple->values.push_back(val);
        CurTok = parseHelper.at();
    }
    while(CurTok == ',');

    if (parseHelper.at() == ')') //!end tuple
    {
        parseHelper.next();
    }
    return ret;
}

static int parseOperator(ParseHelper& parseHelper){
    TokenType curOps = parseHelper.at();
    if (curOps == '<'){
        TokenType nextToken = parseHelper.checkNext(); // eat binop
        if (nextToken == '='){
            return TOK_LE;
        }
        else{
            return TOK_LS;
        }
    }
    else if (curOps == '>'){
        TokenType nextToken = parseHelper.checkNext(); // eat binop
        if (nextToken == '='){
            return TOK_GE;
        }
        else{
            return TOK_GT;
        }
    }
    else if (curOps == '='){
        //DMSG(("parseOperator 111 curOps=%d line=%d, col=%d\n", curOps, parseHelper.line, parseHelper.col)); 
        TokenType nextToken = parseHelper.checkNext(); // eat binop
        //DMSG(("parseOperator 111 nextToken=%d  line=%d, col=%d\n", nextToken, parseHelper.line, parseHelper.col)); 
        if (nextToken == '='){
            return TOK_EQ;
        }
        else{
            return TOK_ASSIGN;
        }
    }
    else if (curOps == '!'){
        TokenType nextToken = parseHelper.checkNext(); // eat binop
        if (nextToken == '='){
            return TOK_NE;
        }
    }
    else if (curOps == '&'){
        TokenType nextToken = parseHelper.checkNext(); // eat binop
        if (nextToken == '&'){
            return TOK_AND;
        }else{
            return TOK_YU;
        }
    }
    else if (curOps == '.'){
        //DMSG(("parseOperator ...222222222........\n")); 
        return TOK_FIELD;
    }
    else if (curOps == '('){
        //DMSG(("parseOperator ...33333333333........\n")); 
        return TOK_CALL;
    }
    else if (curOps == TOK_VAR){
        string& varname = parseHelper.IdentifierStr;
        //DMSG(("parseOperator name=%s\n", varname.c_str())); 
        if (varname == "and"){
            return TOK_AND;
        }
        else if (varname == "or"){
            return TOK_OR;
        }
    }
    return curOps;
}

void ParseTool::popTokenIfBinOps(ParseHelper& parseHelper, TokenType curTok){
    parseHelper.at();
    //DMSG(("popTokenIfBinOps begin cat=%d\n",  parseHelper.at()));
    parseHelper.next();
    if (TOK_LS  == curTok || //<
        TOK_LE  == curTok ||//<=
        TOK_GT  == curTok || //>
        TOK_GE  == curTok ||//>=
        TOK_EQ  == curTok || //==
        TOK_NE  == curTok //!=
        ){
        
        parseHelper.next();
    }
    
    //DMSG(("popTokenIfBinOps end c=%d name=%s\n", c, parseHelper.IdentifierStr.c_str()));
    return;
}
/// binoprhs
///   ::= ('+' primary)*
ExprASTPtr ParseTool::ParseBinOpRHS(ParseHelper& parseHelper, int ExprPrec, ExprASTPtr LHS) {
    // If this is a binop, find its precedence.
    while (1) {
        int curTmp = parseHelper.at();
        TokenType BinOp = parseOperator(parseHelper);

        int TokPrec = GetTokPrecedence(BinOp);

        //DMSG(("ParseBinOpRHS whilie begin...%s %d %d [%d,%d]\n", LHS->name.c_str(), curTmp, parseHelper.at(), TokPrec, ExprPrec)); 
        
        //DMSG(("ParseBinOpRHS name=%s (TokPrec:%d,ExprPrec=%d )CurTok:%d BinOp=%d\n", LHS->name.c_str(), TokPrec, ExprPrec, parseHelper.at(), BinOp));
        // If this is a binop that binds at least as tightly as the current binop,
        // consume it, otherwise we are done.
        if (TokPrec < ExprPrec)
            return LHS;
        
        popTokenIfBinOps(parseHelper, BinOp);
        
        if (curTmp == '('){
            //DMSG(("ParseBinOpRHS 999999999999999\n")); 
            ExprASTPtr result = ParseTupleExpr(parseHelper, NULL);
            LHS = new CallExprAST(LHS, result);
            continue;
        }
        
        // Parse the primary expression after the binary operator.
        ExprASTPtr RHS = ParsePrimary(parseHelper);
        if (!RHS)
            return NULL;

        // If BinOp binds less tightly with RHS than the operator after RHS, let
        // the pending operator take RHS as its LHS.
        TokenType nextOps = parseOperator(parseHelper);
        int NextPrec = GetTokPrecedence(nextOps);
        
        //DMSG(("ParseBinOpRHS RHS=%s,nextOps:%d CurTok:%d NextPrec=%d\n", RHS->name.c_str(), nextOps, parseHelper.at(), NextPrec));
        
        if (TokPrec < NextPrec) {
            
            RHS = ParseBinOpRHS(parseHelper, TokPrec+1, RHS);
            if (!RHS)
                return NULL;
        }
         
        // Merge LHS/RHS.
        LHS = new BinaryExprAST(BinOp, LHS, RHS);
    }

    return NULL;
}

/// expression
///   ::= primary binoprhs
///
ExprASTPtr ParseTool::ParseExpression(ParseHelper& parseHelper) {
    ExprASTPtr LHS = ParsePrimary(parseHelper);
    if (!LHS)
        return NULL;
    //DMSG(("parse expr %s, %d\n", LHS->name.c_str(), LHS->getType()));
    if (LHS->getType() == EXPR_CALL || LHS->getType() == EXPR_FUNC || LHS->getType() == EXPR_CLASS){
        return LHS;
    }
    return ParseBinOpRHS(parseHelper, 0, LHS);
}


ExprASTPtr ErrorP(const char *Str) {
    Error(Str);
    return NULL;
}
/// prototype
///   ::= id '(' id* ')'
bool ParseTool::ParsePrototype(ParseHelper& parseHelper, FunctionAST& f) {
    TokenType CurTok = parseHelper.at();
    if (CurTok != TOK_VAR){
        ErrorP("Expected function name in prototype");
        return false;
    }

    std::string FnName = parseHelper.IdentifierStr;
    f.codeImplptr.cast<FuncCodeImpl>()->name = FnName;
    f.codeImplptr.cast<FuncCodeImpl>()->varAstforName = singleton_t<VariableExprAllocator>::instance_ptr()->alloc(FnName);
    CurTok = parseHelper.next();

    if (CurTok != '('){
        ErrorP("Expected '(' in prototype");
        return false;
    }

    std::vector<ExprASTPtr> argExpr;
    CurTok = parseHelper.next();
    while (CurTok == TOK_VAR){
        f.codeImplptr.cast<FuncCodeImpl>()->argsDef.push_back(singleton_t<VariableExprAllocator>::instance_ptr()->alloc(parseHelper.IdentifierStr));
        CurTok = parseHelper.next();
        if (CurTok == ','){
            CurTok = parseHelper.next();
        }
    }

    CurTok = parseHelper.at();
    if (CurTok != ')'){
        throw PyException::buildException(parseHelper, "ParsePrototype Expected ')' in prototype");
        return false;
    }

    // success.
    CurTok = parseHelper.next(); // eat ')'.
    if (CurTok != ':'){
        ErrorP("Expected ':' in prototype");
        return false;
    }
    // success.
    parseHelper.next(); // eat ':'.
    return true;
}



/// definition ::= 'def' prototype expression
ExprASTPtr ParseTool::ParseDefinition(ParseHelper& parseHelper, int nNeedIndent) {
    if (nNeedIndent != parseHelper.nCurIndent){
        throw PyException::buildIndentException(parseHelper, nNeedIndent, "ParseDefinition 1");
    }

    parseHelper.next(); // eat def.
    FunctionAST* f     = new FunctionAST();
    ExprASTPtr fp(f);
    
    if (!ParsePrototype(parseHelper, *f))
        return NULL;

    int nNextLevelIndent = parseHelper.calNextLevelIndent(nNeedIndent);
    
    do{
        if (nNextLevelIndent != parseHelper.nCurIndent){
            if (parseHelper.nCurIndent <= nNeedIndent)
            {
                break;
            }
            throw PyException::buildIndentException(parseHelper, nNextLevelIndent, "ParseDefinition");
        }
        if (ExprASTPtr e = ParseExpression(parseHelper)){
            f->codeImplptr.cast<FuncCodeImpl>()->body.push_back(e);
        }
        else{
            throw PyException::buildException(parseHelper, f->name + " when ParseDefinition");
        }
    }
    while(true);
    return fp;
}

ExprASTPtr ParseTool::ParseClassExpr(ParseHelper& parseHelper, int nNeedIndent){
    parseHelper.next(); // eat def.
    ClassAST* c     = new ClassAST();
    ExprASTPtr cp(c);
    
    TokenType CurTok = parseHelper.at();
    if (CurTok != TOK_VAR){
        ErrorP("Expected class name after class");
        return NULL;
    }

    std::string strName = parseHelper.IdentifierStr;
    c->codeImplptr.cast<ClassCodeImpl>()->name = strName;
    c->codeImplptr.cast<ClassCodeImpl>()->varAstforName = singleton_t<VariableExprAllocator>::instance_ptr()->alloc(strName);
    CurTok = parseHelper.next();

    if (CurTok != ':'){
        ErrorP("Expected ':' after class name");
        return NULL;
    }
    CurTok = parseHelper.next();
    
    int nNextLevelIndent = parseHelper.calNextLevelIndent(nNeedIndent);
    
    do{
        if (nNextLevelIndent != parseHelper.nCurIndent){
            if (parseHelper.nCurIndent <= nNeedIndent)
            {
                break;
            }
            throw PyException::buildIndentException(parseHelper, nNextLevelIndent);
        }
        if (ExprASTPtr e = ParseExpression(parseHelper)){
            c->classFieldCode.push_back(e);
        }
        else{
            throw PyException::buildException(parseHelper, c->name + " when ParseClassExpr");
        }
    }
    while(true);
    return cp;
}

/// toplevelexpr ::= expression
ExprASTPtr ParseTool::ParseTopLevelExpr(ParseHelper& parseHelper) {
    if (ExprASTPtr E = ParseExpression(parseHelper)) {
        //DMSG(("ParseTool::ParseTopLevelExpr indent=%d\n", parseHelper.nCurIndent));
        // Make an anonymous proto.s
        E->eval(objModule);
        return E;
    }
    return NULL;
}



//===----------------------------------------------------------------------===//
// Top-Level parsing
//===----------------------------------------------------------------------===//

void ParseTool::HandleTopLevelExpression(ParseHelper& parseHelper, int nNeedIndent) {
    // Evaluate a top-level expression into an anonymous function.
    if (ExprASTPtr e = ParseTopLevelExpr(parseHelper)) {
        //DMSG(("Parsed a top-level expr\n"));
    } else {
        // Skip token for error recovery.
        parseHelper.next();
    }
}


/// top ::= definition | external | expression | ';'
bool ParseTool::MainLoop(ParseHelper& parseHelper) {
    parseHelper.next();
    while (1) {
        TokenType CurTok = parseHelper.at();
        //DMSG(("ParseTool::MainLoop CurTok:%d\n", int(CurTok)));
        switch (CurTok) {
            case TOK_EOF:
                return true;;
            case ';': // ignore top-level semicolons.
                parseHelper.next();
                break;
            default:
                HandleTopLevelExpression(parseHelper, 0);
                break;
        }
    }
    return true;
}


