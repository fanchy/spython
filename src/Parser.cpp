#include "Parser.h"
#include "Scanner.h"
#include "ExprAST.h"

using namespace std;
using namespace ff;

#define THROW_ERROR(X) throwError(X, __LINE__)

#define ALLOC_EXPR(X, Y) assignLineInfo(X, Y->nLine, m_curScanner->calLineIndentWidth(Y->nLine))

Parser::Parser():m_curScanner(NULL){
}

ExprASTPtr Parser::parse(Scanner& scanner){
    m_curScanner = &scanner;
    return this->parse_file_input();
}

//! single_input: NEWLINE | simple_stmt | compound_stmt NEWLINE
ExprASTPtr Parser::parse_single_input(){
    return NULL;
}

//! file_input: (NEWLINE | stmt)* ENDMARKER
ExprASTPtr Parser::parse_file_input(){
    StmtAST* allStmt = new StmtAST();
    ExprASTPtr ret = allStmt;
    
    while (m_curScanner->getToken()->nTokenType != TOK_EOF){
        if (m_curScanner->getToken()->strVal == "\n"){
            m_curScanner->seek(1);
        }
        else{
            ExprASTPtr stmt = this->parse_stmt();
            
            if (stmt){
                stmt->dump(0);
                allStmt->exprs.push_back(stmt);
            }else{
                printf("this->parse_stmt ʧ�ܣ�%d %s\n", m_curScanner->seek(0), m_curScanner->getToken()->dump().c_str());
                m_curScanner->seek(1);
            }
        }
    }
    return ret;
}

//! eval_input: testlist NEWLINE* ENDMARKER
ExprASTPtr Parser::parse_eval_input(){
    return NULL;
}

//! decorator: '@' dotted_name [ '(' [arglist] ')' ] NEWLINE
ExprASTPtr Parser::parse_decorator(){
    return NULL;
}

//! decorators: decorator+
ExprASTPtr Parser::parse_decorators(){
    return NULL;
}

//! decorated: decorators (classdef | funcdef)
ExprASTPtr Parser::parse_decorated(){
    return NULL;
}

//! funcdef: 'def' NAME parameters ':' suite
ExprASTPtr Parser::parse_funcdef(){
    if (m_curScanner->getToken()->strVal != "def"){
        return NULL;
    }
    m_curScanner->seek(1);
    
    FuncDefExprAST* f = new FuncDefExprAST();
    ExprASTPtr ret = f;
    
    if (m_curScanner->getToken()->nTokenType != TOK_VAR){
        THROW_ERROR("name needed after def");
    }
    ExprASTPtr name = parse_name();
    
    ExprASTPtr parameters = parse_parameters();
    if (!parameters){
        THROW_ERROR("parameters parse failed after def");
    }
    
    if (m_curScanner->getToken()->strVal != ":"){
        THROW_ERROR(": needed after def");
    }
    m_curScanner->seek(1);
    
    ExprASTPtr suite = parse_suite();
    if (!suite){
        THROW_ERROR("suite parse failed after def");
    }
    
    f->funcname   = name;
    f->parameters = parameters;
    f->suite      = suite;
    return ret;
}

//! parameters: '(' [varargslist] ')'
ExprASTPtr Parser::parse_parameters(){
    if (m_curScanner->getToken()->strVal != "("){
        return NULL;
    }
    m_curScanner->seek(1);
    
    ExprASTPtr varargslist;
    if (m_curScanner->getToken()->strVal != ")"){
        varargslist = parse_varargslist();
    }
    
    if (m_curScanner->getToken()->strVal != ")"){
        THROW_ERROR(") needed when parse parameters");
    }
    m_curScanner->seek(1);
    
    if (!varargslist){
        varargslist = new ParametersExprAST();
    }
    return varargslist;
}

//! varargslist: ((fpdef ['=' test] ',')*
//!               ('*' NAME [',' '**' NAME] | '**' NAME) |
//!               fpdef ['=' test] (',' fpdef ['=' test])* [','])
ExprASTPtr Parser::parse_varargslist(){
    ParametersExprAST* p = new ParametersExprAST();
    ExprASTPtr ret = p;
    do{
        ExprASTPtr fpdef = parse_fpdef();
        if (!fpdef){
            break;
        }
        p->fpdef.push_back(fpdef);
        
        if (m_curScanner->getToken()->strVal == "="){
            m_curScanner->seek(1);
            ExprASTPtr test = parse_test();
            if (!test){
                THROW_ERROR("test parse failed when parse param after =");
            }
            p->test.push_back(test);
        }
        
        if (m_curScanner->getToken()->strVal != ","){
            break;
        }
        m_curScanner->seek(1);
    }
    while (true);
    
    return ret;
}

//! fpdef: NAME | '(' fplist ')'
ExprASTPtr Parser::parse_fpdef(){
    if (m_curScanner->getToken()->nTokenType != TOK_VAR){
        return NULL;
    }
    ExprASTPtr name = parse_name();
    //!TODO
    return name;
}

//! fplist: fpdef (',' fpdef)* [',']
ExprASTPtr Parser::parse_fplist(){
    return NULL;
}

//! stmt: simple_stmt | compound_stmt
ExprASTPtr Parser::parse_stmt(){
    ExprASTPtr retExpr = parse_simple_stmt();
    if (!retExpr){
        retExpr = parse_compound_stmt();
    }
    return retExpr;
}

//! simple_stmt: small_stmt (';' small_stmt)* [';'] NEWLINE
ExprASTPtr Parser::parse_simple_stmt(){
    DTRACE(("parse_simple_stmt begin..."));
    ExprASTPtr small_stmt = parse_small_stmt();
    
    if (small_stmt && m_curScanner->getToken()->strVal == ";"){
        StmtAST* allStmt = new StmtAST();
        ExprASTPtr ret = allStmt;
        allStmt->exprs.push_back(small_stmt);
        
        while (m_curScanner->getToken()->strVal == ";"){
            m_curScanner->seek(1);
            small_stmt = parse_small_stmt();
            if (!small_stmt){
                break;
            }
            allStmt->exprs.push_back(small_stmt);
        }

        if (m_curScanner->getToken()->strVal == ";"){
            m_curScanner->seek(1);
        }
        
        if (m_curScanner->getToken()->strVal == "\n"){
            m_curScanner->seek(1);
        }

        DTRACE(("parse_simple_stmt end muti small..."));
        return ret;
    }
    DTRACE(("parse_simple_stmt end small..."));
    return small_stmt;
}

//! small_stmt: (expr_stmt | print_stmt  | del_stmt | pass_stmt | flow_stmt |
//!              import_stmt | global_stmt | exec_stmt | assert_stmt)
ExprASTPtr Parser::parse_small_stmt(){
    ExprASTPtr retExpr = parse_expr_stmt();
    if (retExpr){
        return retExpr;
    }
    retExpr = parse_print_stmt();
    if (retExpr){
        return retExpr;
    }
    retExpr = parse_del_stmt();
    if (retExpr){
        return retExpr;
    }
    retExpr = parse_pass_stmt();
    if (retExpr){
        return retExpr;
    }
    retExpr = parse_flow_stmt();
    if (retExpr){
        return retExpr;
    }
    retExpr = parse_import_stmt();
    if (retExpr){
        return retExpr;
    }
    retExpr = parse_global_stmt();
    if (retExpr){
        return retExpr;
    }
    retExpr = parse_exec_stmt();
    if (retExpr){
        return retExpr;
    }
    retExpr = parse_assert_stmt();
    if (retExpr){
        return retExpr;
    }
    return retExpr;
}

//! expr_stmt: testlist (augassign (yield_expr|testlist) |
//!                      ('=' (yield_expr|testlist))*)
ExprASTPtr Parser::parse_expr_stmt(){
    DTRACE(("parse_expr_stmt begin..."));
    ExprASTPtr testlist = parse_testlist();
    if (!testlist){
        DTRACE(("parse_expr_stmt ignore"));
        return NULL;
    }

    ExprASTPtr augassign = parse_augassign();
    if (augassign){
        ExprASTPtr yield_expr = parse_yield_expr();
        if (yield_expr){
            augassign.cast<AugassignAST>()->left  = testlist;
            augassign.cast<AugassignAST>()->right = testlist;
        }
        else{
            ExprASTPtr testlist2 = parse_testlist();
            if (!testlist2){
                THROW_ERROR("parse_expr_stmt failed augassign-2");
            }
            augassign.cast<AugassignAST>()->left  = testlist;
            augassign.cast<AugassignAST>()->right = testlist2;
        }
        return augassign;
    }
    else{
        if (m_curScanner->getToken()->strVal == "="){
            m_curScanner->seek(1);
            
            DMSG(("parse_expr_stmt 2 `=`"));
            
            ExprASTPtr yield_expr = parse_yield_expr();
            if (yield_expr){
                return new BinaryExprAST("=", testlist, yield_expr);
            }
            ExprASTPtr testlist2  = parse_testlist();
            if (!testlist2){
                THROW_ERROR("parse_expr_stmt failed assign-2");
            }
            
            return new BinaryExprAST("=", testlist, testlist2);
        }
        else{
            THROW_ERROR("parse_expr_stmt failed");
        }
    }
    
    return NULL;
}

//! augassign: ('+=' | '-=' | '*=' | '/=' | '%=' | '&=' | '|=' | '^=' |
//!             '<<=' | '>>=' | '**=' | '//=')
ExprASTPtr Parser::parse_augassign(){
    if (m_curScanner->getToken()->strVal == "+=" ||
        m_curScanner->getToken()->strVal == "-=" ||
        m_curScanner->getToken()->strVal == "*=" ||
        m_curScanner->getToken()->strVal == "/=" ||
        m_curScanner->getToken()->strVal == "%=" ||
        m_curScanner->getToken()->strVal == "&=" ||
        m_curScanner->getToken()->strVal == "|=" ||
        m_curScanner->getToken()->strVal == "^=" ||
        m_curScanner->getToken()->strVal == "<<=" ||
        m_curScanner->getToken()->strVal == ">>=" ||
        m_curScanner->getToken()->strVal == "**=" ||
        m_curScanner->getToken()->strVal == "//=")
    {
        m_curScanner->seek(1);
        return new AugassignAST(m_curScanner->getToken()->strVal, NULL, NULL);
    }
    return NULL;
}

//! print_stmt: 'print' ( [ test (',' test)* [','] ] |
//!                       '>>' test [ (',' test)+ [','] ] )
ExprASTPtr Parser::parse_print_stmt(){
    if (m_curScanner->getToken()->strVal == "print"){
        m_curScanner->seek(1);
        
        if (m_curScanner->getToken()->strVal != ">>"){
            ExprASTPtr test = parse_test();
            if (!test){
                THROW_ERROR("test needed when parse print");
            }
            PrintAST* printAst = new PrintAST();
            ExprASTPtr ret = printAst;
            printAst->exprs.push_back(test);
            
            while (m_curScanner->getToken()->strVal == ","){
                m_curScanner->seek(1);
                test = parse_test();
                if (!test){
                    break;
                }
                
                printAst->exprs.push_back(test);
            }
            
            return ret;
        }
        else{
            m_curScanner->seek(1);
            ExprASTPtr test = parse_test();
        }
        
    }
    return NULL;
}

//! del_stmt: 'del' exprlist
ExprASTPtr Parser::parse_del_stmt(){
    if (m_curScanner->getToken()->strVal == "del"){
        m_curScanner->seek(1);
        
        ExprASTPtr exprlist = parse_exprlist();
        if (!exprlist){
            THROW_ERROR("exprlist needed when parse del");
        }
        return new DelAST(exprlist);
    }
    return NULL;
}

//! pass_stmt: 'pass'
ExprASTPtr Parser::parse_pass_stmt(){
    if (m_curScanner->getToken()->strVal == "pass"){
        m_curScanner->seek(1);
        return new PassAST();
    }
    return NULL;
}

//! flow_stmt: break_stmt | continue_stmt | return_stmt | raise_stmt | yield_stmt
ExprASTPtr Parser::parse_flow_stmt(){
    ExprASTPtr retExpr = parse_break_stmt();
    if (retExpr){
        return retExpr;
    }
    retExpr = parse_continue_stmt();
    if (retExpr){
        return retExpr;
    }
    retExpr = parse_return_stmt();
    if (retExpr){
        return retExpr;
    }
    retExpr = parse_raise_stmt();
    if (retExpr){
        return retExpr;
    }
    retExpr = parse_yield_stmt();
    if (retExpr){
        return retExpr;
    }
    return NULL;
}

//! break_stmt: 'break'
ExprASTPtr Parser::parse_break_stmt(){
    const Token* token = m_curScanner->getToken();
    if (token->strVal == "break"){
        m_curScanner->seek(1);
        return new BreakAST();
    }
    return NULL;
}

//! continue_stmt: 'continue'
ExprASTPtr Parser::parse_continue_stmt(){
    if (m_curScanner->getToken()->strVal == "continue"){
        m_curScanner->seek(1);
        return new ContinueAST();
    }
    return NULL;
}

//! return_stmt: 'return' [testlist]
ExprASTPtr Parser::parse_return_stmt(){
    if (m_curScanner->getToken()->strVal == "return"){
        m_curScanner->seek(1);
        
        ExprASTPtr testlist = parse_testlist();
        return new ReturnAST(testlist);
    }
    return NULL;
}

//! yield_stmt: yield_expr
ExprASTPtr Parser::parse_yield_stmt(){
    ExprASTPtr yield_expr = parse_yield_expr();
    return yield_expr;
}

//! raise_stmt: 'raise' [test [',' test [',' test]]]
ExprASTPtr Parser::parse_raise_stmt(){
    if (m_curScanner->getToken()->strVal == "raise"){
        m_curScanner->seek(1);
        
        RaiseAST* raiseAST = new RaiseAST();
        ExprASTPtr ret     = raiseAST;
        ExprASTPtr test    = parse_test();
        
        if (test){
            raiseAST->exprs.push_back(test);
            
            if (m_curScanner->getToken()->strVal == ","){
                m_curScanner->seek(1);
                test = parse_test();
                if (!test){
                    THROW_ERROR("test needed when parse raise after ,");
                }
                
                raiseAST->exprs.push_back(test);
                if (m_curScanner->getToken()->strVal == ","){
                    m_curScanner->seek(1);
                    test = parse_test();
                    if (!test){
                        THROW_ERROR("test needed when parse raise after second ,");
                    }
                    raiseAST->exprs.push_back(test);
                }
            }
        }
        return ret;
    }
    return NULL;
}

//! import_stmt: import_name | import_from
ExprASTPtr Parser::parse_import_stmt(){
    ExprASTPtr ret = parse_import_name();
    if (ret){
        return ret;
    }
    ret = parse_import_from();
    return ret;
}

//! import_name: 'import' dotted_as_names
ExprASTPtr Parser::parse_import_name(){
    if (m_curScanner->getToken()->strVal == "import"){
        m_curScanner->seek(1);

        ExprASTPtr dotted_as_names = parse_dotted_as_names();
        return new ImportAST(dotted_as_names);
    }
    
    return NULL;
}

//! import_from: ('from' ('.'* dotted_name | '.'+)
//!               'import' ('*' | '(' import_as_names ')' | import_as_names))
ExprASTPtr Parser::parse_import_from(){
    
    if (m_curScanner->getToken()->strVal == "from"){
        StmtAST* stmt = new StmtAST();
        ExprASTPtr ret = stmt;
        m_curScanner->seek(1);
        
        ExprASTPtr dotted_name = parse_dotted_name();
        if (!dotted_name){
            THROW_ERROR("dotted_name need when parse import after from");
        }
        stmt->exprs.push_back(dotted_name);
        
        if (m_curScanner->getToken()->strVal != "import"){
            THROW_ERROR("import need when parse import after from");
        }
        m_curScanner->seek(1);
        
        if (m_curScanner->getToken()->strVal == "*"){
            stmt->exprs.push_back(new StrExprAST("*"));
            m_curScanner->seek(1);
        }
        else if (m_curScanner->getToken()->strVal == "("){
            m_curScanner->seek(1);
            ExprASTPtr import_as_names = parse_import_as_names();
            if (!import_as_names){
                THROW_ERROR("import_as_names need when parse import after import (");
            }
            stmt->exprs.push_back(import_as_names);
            
            if (m_curScanner->getToken()->strVal != ""){
                THROW_ERROR(") need when parse import after import (");
            }
            m_curScanner->seek(1);
        }
        else{
            ExprASTPtr import_as_names = parse_import_as_names();
            if (!import_as_names){
                THROW_ERROR("import_as_names need when parse import after import");
            }
            stmt->exprs.push_back(import_as_names);
        }
        return ret;
    }
    return NULL;
}

//! import_as_name: NAME ['as' NAME]
ExprASTPtr Parser::parse_import_as_name(){
    DMSG(("parse_import_as_name %s", m_curScanner->getToken()->strVal.c_str()));
    StmtAST* stmt = new StmtAST();
    ExprASTPtr ret = stmt;

    if (m_curScanner->getToken()->nTokenType == TOK_VAR){
        stmt->exprs.push_back(new StrExprAST(m_curScanner->getToken()->strVal));
        m_curScanner->seek(1);

        if (m_curScanner->getToken()->strVal == "as"){
            m_curScanner->seek(1);
            if (m_curScanner->getToken()->nTokenType == TOK_VAR){
                stmt->exprs.push_back(new StrExprAST(m_curScanner->getToken()->strVal));
                m_curScanner->seek(1);
            }
            else{
                THROW_ERROR("name needed when parse import after as");
            }
        }
        
    }
    else{
        THROW_ERROR("name needed when parse import");
    }
    return ret;
}

//! dotted_as_name: dotted_name ['as' NAME]
ExprASTPtr Parser::parse_dotted_as_name(){
    StmtAST* stmt = new StmtAST();
    ExprASTPtr ret = stmt;
    
    ExprASTPtr dotted_name = parse_dotted_name();
    if (!dotted_name){
        return NULL;
    }
    stmt->exprs.push_back(dotted_name);
    if (m_curScanner->getToken()->strVal == "as"){
        m_curScanner->seek(1);
        
        if (m_curScanner->getToken()->nTokenType == TOK_VAR){
            ExprASTPtr expr = new StrExprAST(m_curScanner->getToken()->strVal);
            stmt->exprs.push_back(expr);
            m_curScanner->seek(1);
        }
        else{
            THROW_ERROR("name needed when parse import after as");
            return NULL;
        }
    }
    return ret;
}

//! import_as_names: import_as_name (',' import_as_name)* [',']
ExprASTPtr Parser::parse_import_as_names(){
    StmtAST* stmt = new StmtAST();
    ExprASTPtr ret = stmt;
    
    ExprASTPtr import_as_name = parse_import_as_name();
    if (!import_as_name){
        return NULL;
    }
    stmt->exprs.push_back(import_as_name);
    
    while (m_curScanner->getToken()->strVal == ","){
        m_curScanner->seek(1);
        import_as_name = parse_import_as_name();
        if (!import_as_name){
            THROW_ERROR("name needed when parse import after ,");;
        }
        stmt->exprs.push_back(import_as_name);
    }
    return ret;
}

//! dotted_as_names: dotted_as_name (',' dotted_as_name)*
ExprASTPtr Parser::parse_dotted_as_names(){
    ExprASTPtr dotted_as_name = parse_dotted_as_name();
    if (!dotted_as_name){
        return NULL;
    }
    while (m_curScanner->getToken()->strVal == ","){
        m_curScanner->seek(1);
        dotted_as_name = parse_dotted_as_name();
    }
    return dotted_as_name;
}

//! dotted_name: NAME ('.' NAME)*
ExprASTPtr Parser::parse_dotted_name(){
    StmtAST* stmt = new StmtAST();
    ExprASTPtr ret = stmt;
    DMSG(("parse_dotted_name %s", m_curScanner->getToken()->strVal.c_str()));
    
    if (m_curScanner->getToken()->nTokenType == TOK_VAR){
        ExprASTPtr expr = new StrExprAST(m_curScanner->getToken()->strVal);
        stmt->exprs.push_back(expr);
        m_curScanner->seek(1);
    }
    else{
        THROW_ERROR("name needed when parse import");
        return NULL;
    }
    
    while (m_curScanner->getToken()->strVal == "."){
        m_curScanner->seek(1);
        
        if (m_curScanner->getToken()->nTokenType == TOK_VAR){
            ExprASTPtr expr = new StrExprAST(m_curScanner->getToken()->strVal);
            stmt->exprs.push_back(expr);
            m_curScanner->seek(1);
        }
        else{
            THROW_ERROR("name needed when parse import after .");
        }
    }
    return ret;
}

//! global_stmt: 'global' NAME (',' NAME)*
ExprASTPtr Parser::parse_global_stmt(){
    if (m_curScanner->getToken()->strVal != "global"){
        return NULL;
    }
    m_curScanner->seek(1);
    
    GlobalAST* stmt = new GlobalAST();
    ExprASTPtr ret = stmt;
    
    if (m_curScanner->getToken()->nTokenType != TOK_VAR){
        THROW_ERROR("var needed when parse global");
    }
    stmt->exprs.push_back(parse_name());
    
    while (m_curScanner->getToken()->strVal == ","){
        m_curScanner->seek(1);

        if (m_curScanner->getToken()->nTokenType == TOK_VAR){
            stmt->exprs.push_back(parse_name());
        }
        else{
            THROW_ERROR("var needed when parse global after ,");
        }
    }
    return ret;
}

//! exec_stmt: 'exec' expr ['in' test [',' test]]
ExprASTPtr Parser::parse_exec_stmt(){
    if (m_curScanner->getToken()->strVal != "exec"){
        return NULL;
    }
    m_curScanner->seek(1);
    ExecAST* stmt = new ExecAST();
    ExprASTPtr ret = stmt;
    
    ExprASTPtr expr = parse_expr();
    if (!expr){
        THROW_ERROR("expr needed when parse exec after exec");
    }
    stmt->exprs.push_back(expr);
    
    if (m_curScanner->getToken()->strVal == "in"){
        m_curScanner->seek(1);
        
        ExprASTPtr test = parse_test();
        if (!test){
            THROW_ERROR("test needed when parse exec after in");
        }
        stmt->exprs.push_back(test);
        
        if (m_curScanner->getToken()->strVal == ","){
            test = parse_test();
            if (!test){
                THROW_ERROR("test needed when parse exec after ,");
            }
            stmt->exprs.push_back(test);
        }
    }
    return ret;
}

//! assert_stmt: 'assert' test [',' test]
ExprASTPtr Parser::parse_assert_stmt(){
    if (m_curScanner->getToken()->strVal != "assert"){
        return NULL;
    }
    m_curScanner->seek(1);
    AssertAST* stmt = new AssertAST();
    ExprASTPtr ret = stmt;
    
    ExprASTPtr test = parse_test();
    if (!test){
        THROW_ERROR("test needed when parse assert after assert");
    }
    stmt->exprs.push_back(test);
    
    if (m_curScanner->getToken()->strVal == ","){
        m_curScanner->seek(1);
        
        ExprASTPtr test = parse_test();
        if (!test){
            THROW_ERROR("test needed when parse assert after ,");
        }
        stmt->exprs.push_back(test);
    }
    return ret;
}

//! compound_stmt: if_stmt | while_stmt | for_stmt | try_stmt | with_stmt | funcdef | classdef | decorated
ExprASTPtr Parser::parse_compound_stmt(){
    if (ExprASTPtr if_stmt = parse_if_stmt()){
        return if_stmt;
    }
    if (ExprASTPtr while_stmt = parse_while_stmt()){
        return while_stmt;
    }
    if (ExprASTPtr for_stmt = parse_for_stmt()){
        return for_stmt;
    }
    if (ExprASTPtr try_stmt = parse_try_stmt()){
        return try_stmt;
    }
    if (ExprASTPtr with_stmt = parse_with_stmt()){
        return with_stmt;
    }
    if (ExprASTPtr funcdef = parse_funcdef()){
        return funcdef;
    }
    if (ExprASTPtr classdef = parse_classdef()){
        return classdef;
    }
    if (ExprASTPtr decorated = parse_decorated()){
        return decorated;
    }
    return NULL;
}

//! if_stmt: 'if' test ':' suite ('elif' test ':' suite)* ['else' ':' suite]
ExprASTPtr Parser::parse_if_stmt(){
    if (m_curScanner->getToken()->strVal != "if"){
        return NULL;
    }
    m_curScanner->seek(1);
    
    IfExprAST* ifexpr = new IfExprAST();
    ExprASTPtr ret    = ifexpr;
    
    ExprASTPtr test = parse_test();
    if (!test){
        THROW_ERROR("test needed when parse if after if");
    }
    if (m_curScanner->getToken()->strVal != ":"){
        THROW_ERROR(": needed when parse if after if");
    }
    m_curScanner->seek(1);
    
    ExprASTPtr suite = parse_suite();
    if (!suite){
        THROW_ERROR("suite needed when parse if after :");
    }
    ifexpr->ifTest.push_back(test);
    ifexpr->ifSuite.push_back(suite);
    
    m_curScanner->skipEnterChar();
    DMSG(("parse_if_stmt %s", m_curScanner->getToken()->strVal.c_str()));
    while (m_curScanner->getToken()->strVal == "elif"){
        m_curScanner->seek(1);
        test = parse_test();
        if (!test){
            THROW_ERROR("test needed when parse if after elif");
        }
        if (m_curScanner->getToken()->strVal != ":"){
            THROW_ERROR(": needed when parse if after elif");
        }
        m_curScanner->seek(1);
        
        suite = parse_suite();
        if (!suite){
            THROW_ERROR("suite needed when parse if after elif :");
        }
        
        ifexpr->ifTest.push_back(test);
        ifexpr->ifSuite.push_back(suite);
    }
    m_curScanner->skipEnterChar();
    if (m_curScanner->getToken()->strVal == "else"){
        m_curScanner->seek(1);
        if (m_curScanner->getToken()->strVal != ":"){
            THROW_ERROR(": needed when parse if after else");
        }
        m_curScanner->seek(1);
        suite = parse_suite();
        if (!suite){
            THROW_ERROR("suite needed when parse if after elif :");
        }
        
        ifexpr->elseSuite = suite;
    }
    return ret;
}

//! while_stmt: 'while' test ':' suite ['else' ':' suite]
ExprASTPtr Parser::parse_while_stmt(){
    if (m_curScanner->getToken()->strVal != "while"){
        return NULL;
    }
    m_curScanner->seek(1);
    
    WhileExprAST* whileexpr = new WhileExprAST();
    ExprASTPtr ret          = whileexpr;
    
    ExprASTPtr test = parse_test();
    if (!test){
        THROW_ERROR("test needed when parse while after while");
    }
    if (m_curScanner->getToken()->strVal != ":"){
        THROW_ERROR(": needed when parse while after while");
    }
    m_curScanner->seek(1);
    
    ExprASTPtr suite = parse_suite();
    if (!suite){
        THROW_ERROR("suite needed when parse while after :");
    }
    whileexpr->test  = test;
    whileexpr->suite = suite;
    
    m_curScanner->skipEnterChar();
    if (m_curScanner->getToken()->strVal == "else"){
        m_curScanner->seek(1);
        if (m_curScanner->getToken()->strVal != ":"){
            THROW_ERROR(": needed when parse while after else");
        }
        m_curScanner->seek(1);
        suite = parse_suite();
        if (!suite){
            THROW_ERROR("suite needed when parse while after else:");
        }
        
        whileexpr->elseSuite = suite;
    }
    return ret;
}

//! for_stmt: 'for' exprlist 'in' testlist ':' suite ['else' ':' suite]
ExprASTPtr Parser::parse_for_stmt(){
    if (m_curScanner->getToken()->strVal != "for"){
        return NULL;
    }
    m_curScanner->seek(1);
    
    ForExprAST* forexpr = new ForExprAST();
    ExprASTPtr ret      = forexpr;
    
    ExprASTPtr exprlist = parse_exprlist();
    if (!exprlist){
        THROW_ERROR("test needed when parse while after for");
    }
    if (m_curScanner->getToken()->strVal != "in"){
        THROW_ERROR("in needed when parse for after for");
    }
    m_curScanner->seek(1);
    
    ExprASTPtr testlist = parse_testlist();
    if (!testlist){
        THROW_ERROR("suite needed when parse for after :");
    }
    forexpr->exprlist = exprlist;
    forexpr->testlist = testlist;
    
    if (m_curScanner->getToken()->strVal != ":"){
        THROW_ERROR(": needed when parse for after for in");
    }
    m_curScanner->seek(1);

    ExprASTPtr suite = parse_suite();
    if (!suite){
        THROW_ERROR("suite needed when parse while after for:");
    }
    forexpr->suite   = suite;
    
    m_curScanner->skipEnterChar();
    if (m_curScanner->getToken()->strVal == "else"){
        m_curScanner->seek(1);
        if (m_curScanner->getToken()->strVal != ":"){
            THROW_ERROR(": needed when parse for after else");
        }
        m_curScanner->seek(1);
        suite = parse_suite();
        if (!suite){
            THROW_ERROR("suite needed when parse for after else:");
        }
        
        forexpr->elseSuite = suite;
    }
    return ret;
}

//! try_stmt: ('try' ':' suite
//!            ((except_clause ':' suite)+
//!             ['else' ':' suite]
//!             ['finally' ':' suite] |
//!            'finally' ':' suite))
ExprASTPtr Parser::parse_try_stmt(){
    return NULL;
}

//! with_stmt: 'with' with_item (',' with_item)*  ':' suite
ExprASTPtr Parser::parse_with_stmt(){
    return NULL;
}

//! with_item: test ['as' expr]
ExprASTPtr Parser::parse_with_item(){
    return NULL;
}

//! except_clause: 'except' [test [('as' | ',') test]]
ExprASTPtr Parser::parse_except_clause(){
    return NULL;
}

//! suite: simple_stmt | NEWLINE INDENT stmt+ DEDENT
ExprASTPtr Parser::parse_suite(){
    if (m_curScanner->getToken()->strVal != "\n"){
        ExprASTPtr simple_stmt = parse_simple_stmt();
        return simple_stmt;
    }
    else{
        StmtAST* allStmt = new StmtAST();
        ExprASTPtr ret = allStmt;
        
        m_curScanner->skipEnterChar();
        
        int nIndent = m_curScanner->curIndentWidth();
        
        DMSG(("parse_suite %s %d %d", m_curScanner->getToken()->strVal.c_str(), m_curScanner->getToken()->nLine, m_curScanner->curIndentWidth()));
        while (ExprASTPtr stmt = parse_stmt()){
            
            if (!stmt){
                break;
            }
            allStmt->exprs.push_back(stmt);
            m_curScanner->skipEnterChar();
            if (nIndent != m_curScanner->curIndentWidth()){
                break;
            }
            
            DMSG(("parse_suite %s %d %d", m_curScanner->getToken()->strVal.c_str(), m_curScanner->getToken()->nLine, m_curScanner->curIndentWidth()));
        }
        
        return ret;
    }
    return NULL;
}

//! testlist_safe: old_test [(',' old_test)+ [',']]
ExprASTPtr Parser::parse_testlist_safe(){
    return NULL;
}

//! old_test: or_test | old_lambdef
ExprASTPtr Parser::parse_old_test(){
    return NULL;
}

//! old_lambdef: 'lambda' [varargslist] ':' old_test
ExprASTPtr Parser::parse_old_lambdef(){
    return NULL;
}

//! test: or_test ['if' or_test 'else' test] | lambdef
ExprASTPtr Parser::parse_test(){
    ExprASTPtr or_test = parse_or_test();
    return or_test;
}

//! or_test: and_test ('or' and_test)*
ExprASTPtr Parser::parse_or_test(){
    ExprASTPtr ret = parse_and_test();
    
    while (m_curScanner->getToken()->strVal == "or"){
        m_curScanner->seek(1);
        
        ExprASTPtr and_test = parse_and_test();
        if (!and_test){
            THROW_ERROR("test expr needed after or");
        }
        ret = new BinaryExprAST("or", ret, and_test);
    }
    return ret;
}

//! and_test: not_test ('and' not_test)*
ExprASTPtr Parser::parse_and_test(){
    ExprASTPtr ret = parse_not_test();
    while (m_curScanner->getToken()->strVal == "and"){
        m_curScanner->seek(1);
        
        ExprASTPtr not_test = parse_not_test();
        if (!not_test){
            THROW_ERROR("test expr needed after or");
        }
        ret = new BinaryExprAST("and", ret, not_test);
    }
    return ret;
}

//! not_test: 'not' not_test | comparison
ExprASTPtr Parser::parse_not_test(){
    ExprASTPtr comparison = parse_comparison();
    return comparison;
}

//! comparison: expr (comp_op expr)*
ExprASTPtr Parser::parse_comparison(){
    ExprASTPtr expr = parse_expr();
    ExprASTPtr ret  = parse_comp_op(expr);
    return ret;
}

//! comp_op: '<'|'>'|'=='|'>='|'<='|'<>'|'!='|'in'|'not' 'in'|'is'|'is' 'not'
ExprASTPtr Parser::parse_comp_op(ExprASTPtr& expr){
    string op = m_curScanner->getToken()->strVal;
    if (op == "<" || op == ">" ||
        op == "==" || op == ">=" ||
        op == "<=" || op == "<>" ||
        op == "!=" || op == "in"){
        m_curScanner->seek(1);
        ExprASTPtr expr2 = parse_expr();
        if (!expr2){
            THROW_ERROR("expr needed after comp_op");
        }
        return new BinaryExprAST(op, expr, expr2);
    }
    else if (op == "not"){
        if (m_curScanner->getToken(1)->strVal == "in"){
            m_curScanner->seek(2);
            ExprASTPtr expr2 = parse_expr();
            if (!expr2){
                THROW_ERROR("expr needed after comp_op");
            }
            return new BinaryExprAST("not in", expr, expr2);
        }
        else{
            m_curScanner->seek(1);
            ExprASTPtr expr2 = parse_expr();
            if (!expr2){
                THROW_ERROR("expr needed after comp_op");
            }
            return new BinaryExprAST(op, expr, expr2);
        }
    }
    else if (op == "is"){
        if (m_curScanner->getToken(1)->strVal == "not"){
            m_curScanner->seek(2);
            ExprASTPtr expr2 = parse_expr();
            if (!expr2){
                THROW_ERROR("expr needed after comp_op");
            }
            return new BinaryExprAST("is not", expr, expr2);
        }
        else{
            m_curScanner->seek(1);
            ExprASTPtr expr2 = parse_expr();
            if (!expr2){
                THROW_ERROR("expr needed after comp_op");
            }
            return new BinaryExprAST(op, expr, expr2);
        }
    }
    return expr;
}

//! expr: xor_expr ('|' xor_expr)*
ExprASTPtr Parser::parse_expr(){
    ExprASTPtr xor_expr = parse_xor_expr();
    return xor_expr;
}

//! xor_expr: and_expr ('^' and_expr)*
ExprASTPtr Parser::parse_xor_expr(){
    ExprASTPtr and_expr = parse_and_expr();
    return and_expr;
}

//! and_expr: shift_expr ('&' shift_expr)*
ExprASTPtr Parser::parse_and_expr(){
    ExprASTPtr shift_expr = parse_shift_expr();
    return shift_expr;
}

//! shift_expr: arith_expr (('<<'|'>>') arith_expr)*
ExprASTPtr Parser::parse_shift_expr(){
    ExprASTPtr arith_expr = parse_arith_expr();
    return arith_expr;
}

//! arith_expr: term (('+'|'-') term)*
ExprASTPtr Parser::parse_arith_expr(){
    ExprASTPtr ret = parse_term();
    while (m_curScanner->getToken()->strVal == "+" || m_curScanner->getToken()->strVal == "-"){
        string op = m_curScanner->getToken()->strVal;
        m_curScanner->seek(1);
        
        ExprASTPtr term = parse_term();
        if (!term){
            THROW_ERROR("term need after +/-");
        }
        ret = new BinaryExprAST(op, ret, term);
    }
    return ret;
}

//! term: factor (('*'|'/'|'%'|'//') factor)*
ExprASTPtr Parser::parse_term(){
    ExprASTPtr ret = parse_factor();
    while (m_curScanner->getToken()->strVal == "*" ||
           m_curScanner->getToken()->strVal == "/" ||
           m_curScanner->getToken()->strVal == "%" ){

        string op = m_curScanner->getToken()->strVal;
        m_curScanner->seek(1);
        
        ExprASTPtr term = parse_factor();
        if (!term){
            THROW_ERROR("term need after * / %");
        }
        ret = new BinaryExprAST(op, ret, term);
    }
    return ret;
}

//! factor: ('+'|'-'|'~') factor | power
ExprASTPtr Parser::parse_factor(){
    ExprASTPtr power = parse_power();
    return power;
}

//! power: atom trailer* ['**' factor]
ExprASTPtr Parser::parse_power(){
    ExprASTPtr atom = parse_atom();
    if (!atom){
        return NULL;
    }
    
    PowerAST* p    = new PowerAST();
    ExprASTPtr ret = p;
    
    p->atom = atom;
    while (ExprASTPtr trailer = parse_trailer()){
        p->trailer.push_back(trailer);
    }
    return ret;
}

//! atom: ('(' [yield_expr|testlist_comp] ')' |
//!        '[' [listmaker] ']' |
//!        '{' [dictorsetmaker] '}' |
//!        '`' testlist1 '`' |
//!        NAME | NUMBER | STRING+)
ExprASTPtr Parser::parse_atom(){
    
    ExprASTPtr retExpr;
    if (m_curScanner->getToken()->nTokenType == TOK_INT){
        retExpr = new NumberExprAST(m_curScanner->getToken()->nVal);
    }
    else if (m_curScanner->getToken()->nTokenType == TOK_FLOAT){
        retExpr = new FloatExprAST(m_curScanner->getToken()->fVal);
    }
    else if (m_curScanner->getToken()->nTokenType == TOK_STR){
        retExpr = new StrExprAST(m_curScanner->getToken()->strVal);
    }
    else if (m_curScanner->getToken()->nTokenType == TOK_VAR){
        if (singleton_t<PyHelper>::instance_ptr()->isKeyword(m_curScanner->getToken()->strVal)){
            return NULL;
        }
        retExpr = singleton_t<VariableExprAllocator>::instance_ptr()->alloc(m_curScanner->getToken()->strVal);//new VariableExprAST(m_curScanner->getToken()->strVal);
    }
    else if (m_curScanner->getToken()->strVal == "["){
        m_curScanner->seek(1);
        if (m_curScanner->getToken()->strVal == "]"){
            m_curScanner->seek(1);
            retExpr = new ListMakerExprAST();
        }
        else{
            retExpr = parse_listmaker();
            if (!retExpr){
                THROW_ERROR("listmake needed when parse list");
            }
            m_curScanner->skipEnterChar();
            if (m_curScanner->getToken()->strVal != "]"){
                THROW_ERROR("] needed when parse listmake");
            }
            m_curScanner->seek(1);
        }
    }
    else if (m_curScanner->getToken()->strVal == "{"){
        m_curScanner->seek(1);
        if (m_curScanner->getToken()->strVal == "}"){
            m_curScanner->seek(1);
            retExpr = new DictorsetMakerExprAST();
        }
        else{
            retExpr = parse_dictorsetmaker();
            if (!retExpr){
                THROW_ERROR("dictorsetmaker needed when parse list");
            }
            m_curScanner->skipEnterChar();
            if (m_curScanner->getToken()->strVal != "}"){
                THROW_ERROR("} needed when parse dictorsetmaker");
            }
            m_curScanner->seek(1);
        }
    }
    else{
        return retExpr;
    }
    
    DMSG(("parse_atom %s", m_curScanner->getToken()->dump().c_str()));
    m_curScanner->seek(1);
    return retExpr;
}

//! listmaker: test ( list_for | (',' test)* [','] )
ExprASTPtr Parser::parse_listmaker(){
    m_curScanner->skipEnterChar();
    ExprASTPtr test = parse_test();
    if (!test){
        return NULL;
    }
    
    ListMakerExprAST* listMaker = new ListMakerExprAST();
    ExprASTPtr ret = listMaker;
    
    listMaker->test.push_back(test);
    
    if (m_curScanner->getToken()->strVal != ","){
        ExprASTPtr list_for = parse_list_for();
        if (!list_for){
            THROW_ERROR("list_for needed when parse_listmaker");
        }
        listMaker->list_for = list_for;
    }
    else{
        while (m_curScanner->getToken()->strVal == ","){
            m_curScanner->seek(1);
            
            m_curScanner->skipEnterChar();
            test = parse_test();
            if (!test){
                break;
            }
            listMaker->test.push_back(test);
        }
    }
    return ret;
}

//! testlist_comp: test ( comp_for | (',' test)* [','] )
ExprASTPtr Parser::parse_testlist_comp(){
    return NULL;
}

//! lambdef: 'lambda' [varargslist] ':' test
ExprASTPtr Parser::parse_lambdef(){
    return NULL;
}

//! trailer: '(' [arglist] ')' | '[' subscriptlist ']' | '.' NAME
ExprASTPtr Parser::parse_trailer(){
    if (m_curScanner->getToken()->strVal == "("){ //!call func
        m_curScanner->seek(1);
        if (m_curScanner->getToken()->strVal != ")"){
            ExprASTPtr arglist = parse_arglist();
            if (!arglist){
                THROW_ERROR("arglist parse failed when parse trailer after (");
            }
        }
        m_curScanner->seek(1);
    }
    else if (m_curScanner->getToken()->strVal == "["){ //!call [] operator
        m_curScanner->seek(1);
        if (m_curScanner->getToken()->strVal != "]"){
            ExprASTPtr subscriptlist = parse_subscriptlist();
            if (!subscriptlist){
                THROW_ERROR("subscriptlist parse failed when parse trailer after [");
            }
        }
        m_curScanner->seek(1);
    }
    else if (m_curScanner->getToken()->strVal == "."){ //!call [] operator
        m_curScanner->seek(1);
        if (m_curScanner->getToken()->nTokenType != TOK_VAR){
            THROW_ERROR("name parse failed when parse trailer after .");
        }
        ExprASTPtr name = parse_name();
        return name;
    }
    return NULL;
}

//! subscriptlist: subscript (',' subscript)* [',']
ExprASTPtr Parser::parse_subscriptlist(){
    return NULL;
}

//! subscript: '.' '.' '.' | test | [test] ':' [test] [sliceop]
ExprASTPtr Parser::parse_subscript(){
    return NULL;
}

//! sliceop: ':' [test]
ExprASTPtr Parser::parse_sliceop(){
    return NULL;
}

//! exprlist: expr (',' expr)* [',']
ExprASTPtr Parser::parse_exprlist(){
    ExprASTPtr expr = parse_expr();
    if (!expr){
        return NULL;
    }

    StmtAST* stmtAST = new StmtAST();
    stmtAST->exprs.push_back(expr);
    ExprASTPtr ret   = stmtAST;

    while (m_curScanner->getToken()->strVal == ","){
        m_curScanner->seek(1);
        expr = parse_expr();
        if (!expr){
            break;
        }
        stmtAST->exprs.push_back(expr);
    }
    return ret;
}

//! testlist: test (',' test)* [',']
ExprASTPtr Parser::parse_testlist(){
    ExprASTPtr retExpr = parse_test();
    return retExpr;
}

//! dictorsetmaker: ( (test ':' test (comp_for | (',' test ':' test)* [','])) |
//!                   (test (comp_for | (',' test)* [','])) )
ExprASTPtr Parser::parse_dictorsetmaker(){
    m_curScanner->skipEnterChar();
    ExprASTPtr testKey = parse_test();
    if (!testKey){
        return NULL;
    }
    
    DictorsetMakerExprAST* dict = new DictorsetMakerExprAST();
    ExprASTPtr ret = dict;
    
    if (m_curScanner->getToken()->strVal == ":"){
        m_curScanner->seek(1);
        
        ExprASTPtr testVal = parse_test();
        if (!testVal){
            THROW_ERROR("test needed whern parse dict after key:");
        }
        
        dict->testKey.push_back(testKey);
        dict->testVal.push_back(testVal);
    
        if (m_curScanner->getToken()->strVal != ","){
            ExprASTPtr comp_for = parse_comp_for();
            if (!comp_for){
                THROW_ERROR("comp_for needed whern parse dict");
            }
            dict->comp_for = comp_for;
        }
        else{
            while (m_curScanner->getToken()->strVal == ",")
            {
                m_curScanner->seek(1);
                m_curScanner->skipEnterChar();
                
                testKey = parse_test();
                if (!testKey){
                    break;
                }
                if (m_curScanner->getToken()->strVal != ":"){
                    THROW_ERROR(": needed whern parse dict after key");
                }
                m_curScanner->seek(1);
                
                testVal = parse_test();
                if (!testVal){
                    THROW_ERROR("test val needed whern parse dict after key:");
                }
                
                dict->testKey.push_back(testKey);
                dict->testVal.push_back(testVal);
            }
            
        }
    }
    return ret;
}

//! classdef: 'class' NAME ['(' [testlist] ')'] ':' suite
ExprASTPtr Parser::parse_classdef(){
    if (m_curScanner->getToken()->strVal != "class"){
        return NULL;
    }
    m_curScanner->seek(1);
    
    ClassDefExprAST* f = new ClassDefExprAST();
    ExprASTPtr ret = f;
    
    if (m_curScanner->getToken()->nTokenType != TOK_VAR){
        THROW_ERROR("name needed after class");
    }
    ExprASTPtr name = parse_name();

    if (m_curScanner->getToken()->strVal != ":"){
        THROW_ERROR(": needed after class");
    }
    m_curScanner->seek(1);
    
    ExprASTPtr suite = parse_suite();
    if (!suite){
        THROW_ERROR("suite parse failed after class");
    }
    
    f->classname  = name;
    //f->testlist   = testlist;
    f->suite      = suite;
    return ret;
}

//! arglist: (argument ',')* (argument [',']
//!                          |'*' test (',' argument)* [',' '**' test] 
//!                          |'**' test)
ExprASTPtr Parser::parse_arglist(){
    return NULL;
}

//! argument: test [comp_for] | test '=' test
ExprASTPtr Parser::parse_argument(){
    return NULL;
}

//! list_iter: list_for | list_if
ExprASTPtr Parser::parse_list_iter(){
    return NULL;
}

//! list_for: 'for' exprlist 'in' testlist_safe [list_iter]
ExprASTPtr Parser::parse_list_for(){
    return NULL;
}

//! list_if: 'if' old_test [list_iter]
ExprASTPtr Parser::parse_list_if(){
    return NULL;
}

//! comp_iter: comp_for | comp_if
ExprASTPtr Parser::parse_comp_iter(){
    return NULL;
}

//! comp_for: 'for' exprlist 'in' or_test [comp_iter]
ExprASTPtr Parser::parse_comp_for(){
    return NULL;
}

//! comp_if: 'if' old_test [comp_iter]
ExprASTPtr Parser::parse_comp_if(){
    return NULL;
}

//! testlist1: test (',' test)*
ExprASTPtr Parser::parse_testlist1(){
    ExprASTPtr test = parse_test();
    if (!test){
        return NULL;
    }
    StmtAST* stmp = new StmtAST();
    ExprASTPtr ret= stmp;
    
    stmp->exprs.push_back(test);
    
    while (m_curScanner->getToken()->strVal == ","){
        m_curScanner->seek(1);
        
        test = parse_test();
        if (!test){
            THROW_ERROR("test expr needed when parse testlist1 after ,");
        }
        stmp->exprs.push_back(test);
    }
    return NULL;
}

//! encoding_decl: NAME
ExprASTPtr Parser::parse_encoding_decl(){
    return NULL;
}

//! yield_expr: 'yield' [testlist]
ExprASTPtr Parser::parse_yield_expr(){
    if (m_curScanner->getToken()->strVal == "yield"){
        THROW_ERROR("yield not supported");
    }
    
    return NULL;
}

ExprASTPtr Parser::parse_name(bool throwFlag){
    if (m_curScanner->getToken()->nTokenType == TOK_VAR){
        if (singleton_t<PyHelper>::instance_ptr()->isKeyword(m_curScanner->getToken()->strVal)){
            if (throwFlag){
                THROW_ERROR("keyword can't be var");
            }
            return NULL;
        }
        ExprASTPtr retExpr = singleton_t<VariableExprAllocator>::instance_ptr()->alloc(m_curScanner->getToken()->strVal);;//new VariableExprAST(m_curScanner->getToken()->strVal);
        m_curScanner->seek(1);
        return retExpr;
    }
    if (throwFlag){
        THROW_ERROR("not valid var given");
    }
    return NULL;
}

void Parser::throwError(const string& err, int nLine){
    char msg[256] = {0};
    snprintf(msg, sizeof(msg), "%s(%d) given:%s,indent=%d", err.c_str(), nLine, m_curScanner->getToken()->strVal.c_str(), m_curScanner->curIndentWidth());
    throw PyException::buildException(msg);
}
