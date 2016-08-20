#ifndef _PARSE_H_
#define _PARSE_H_

#include "Base.h"

namespace ff{

class Scanner;
class Parser{
public:
    Parser();
    ExprASTPtr parse(Scanner& scanner);
    
    //! single_input: NEWLINE | simple_stmt | compound_stmt NEWLINE
    ExprASTPtr parse_single_input();
    //! file_input: (NEWLINE | stmt)* ENDMARKER
    ExprASTPtr parse_file_input();
    //! eval_input: testlist NEWLINE* ENDMARKER
    ExprASTPtr parse_eval_input();
    //! decorator: '@' dotted_name [ '(' [arglist] ')' ] NEWLINE
    ExprASTPtr parse_decorator();
    //! decorators: decorator+
    ExprASTPtr parse_decorators();
    //! decorated: decorators (classdef | funcdef)
    ExprASTPtr parse_decorated();
    //! funcdef: 'def' NAME parameters ':' suite
    ExprASTPtr parse_funcdef();
    //! parameters: '(' [varargslist] ')'
    ExprASTPtr parse_parameters();
    //! varargslist: ((fpdef ['=' test] ',')*
    //!               ('*' NAME [',' '**' NAME] | '**' NAME) |
    //!               fpdef ['=' test] (',' fpdef ['=' test])* [','])
    ExprASTPtr parse_varargslist();
    //! fpdef: NAME | '(' fplist ')'
    ExprASTPtr parse_fpdef();
    //! fplist: fpdef (',' fpdef)* [',']
    ExprASTPtr parse_fplist();
    //! stmt: simple_stmt | compound_stmt
    ExprASTPtr parse_stmt();
    //! simple_stmt: small_stmt (';' small_stmt)* [';'] NEWLINE
    ExprASTPtr parse_simple_stmt();
    //! small_stmt: (expr_stmt | print_stmt  | del_stmt | pass_stmt | flow_stmt |
    //!              import_stmt | global_stmt | exec_stmt | assert_stmt)
    ExprASTPtr parse_small_stmt();
    //! expr_stmt: testlist (augassign (yield_expr|testlist) |
    //!                      ('=' (yield_expr|testlist))*)
    ExprASTPtr parse_expr_stmt();
    //! augassign: ('+=' | '-=' | '*=' | '/=' | '%=' | '&=' | '|=' | '^=' |
    //!             '<<=' | '>>=' | '**=' | '//=')
    ExprASTPtr parse_augassign();
    //! print_stmt: 'print' ( [ test (',' test)* [','] ] |
    //!                       '>>' test [ (',' test)+ [','] ] )
    ExprASTPtr parse_print_stmt();
    //! del_stmt: 'del' exprlist
    ExprASTPtr parse_del_stmt();
    //! pass_stmt: 'pass'
    ExprASTPtr parse_pass_stmt();
    //! flow_stmt: break_stmt | continue_stmt | return_stmt | raise_stmt | yield_stmt
    ExprASTPtr parse_flow_stmt();
    //! break_stmt: 'break'
    ExprASTPtr parse_break_stmt();
    //! continue_stmt: 'continue'
    ExprASTPtr parse_continue_stmt();
    //! return_stmt: 'return' [testlist]
    ExprASTPtr parse_return_stmt();
    //! yield_stmt: yield_expr
    ExprASTPtr parse_yield_stmt();
    //! raise_stmt: 'raise' [test [',' test [',' test]]]
    ExprASTPtr parse_raise_stmt();
    //! import_stmt: import_name | import_from
    ExprASTPtr parse_import_stmt();
    //! import_name: 'import' dotted_as_names
    ExprASTPtr parse_import_name();
    //! import_from: ('from' ('.'* dotted_name | '.'+)
    //!               'import' ('*' | '(' import_as_names ')' | import_as_names))
    ExprASTPtr parse_import_from();
    //! import_as_name: NAME ['as' NAME]
    ExprASTPtr parse_import_as_name();
    //! dotted_as_name: dotted_name ['as' NAME]
    ExprASTPtr parse_dotted_as_name();
    //! import_as_names: import_as_name (',' import_as_name)* [',']
    ExprASTPtr parse_import_as_names();
    //! dotted_as_names: dotted_as_name (',' dotted_as_name)*
    ExprASTPtr parse_dotted_as_names();
    //! dotted_name: NAME ('.' NAME)*
    ExprASTPtr parse_dotted_name();
    //! global_stmt: 'global' NAME (',' NAME)*
    ExprASTPtr parse_global_stmt();
    //! exec_stmt: 'exec' expr ['in' test [',' test]]
    ExprASTPtr parse_exec_stmt();
    //! assert_stmt: 'assert' test [',' test]
    ExprASTPtr parse_assert_stmt();
    //! compound_stmt: if_stmt | while_stmt | for_stmt | try_stmt | with_stmt | funcdef | classdef | decorated
    ExprASTPtr parse_compound_stmt();
    //! if_stmt: 'if' test ':' suite ('elif' test ':' suite)* ['else' ':' suite]
    ExprASTPtr parse_if_stmt();
    //! while_stmt: 'while' test ':' suite ['else' ':' suite]
    ExprASTPtr parse_while_stmt();
    //! for_stmt: 'for' exprlist 'in' testlist ':' suite ['else' ':' suite]
    ExprASTPtr parse_for_stmt();
    //! try_stmt: ('try' ':' suite
    //!            ((except_clause ':' suite)+
    //!             ['else' ':' suite]
    //!             ['finally' ':' suite] |
    //!            'finally' ':' suite))
    ExprASTPtr parse_try_stmt();
    //! with_stmt: 'with' with_item (',' with_item)*  ':' suite
    ExprASTPtr parse_with_stmt();
    //! with_item: test ['as' expr]
    ExprASTPtr parse_with_item();
    //! except_clause: 'except' [test [('as' | ',') test]]
    ExprASTPtr parse_except_clause();
    //! suite: simple_stmt | NEWLINE INDENT stmt+ DEDENT
    ExprASTPtr parse_suite();
    //! testlist_safe: old_test [(',' old_test)+ [',']]
    ExprASTPtr parse_testlist_safe();
    //! old_test: or_test | old_lambdef
    ExprASTPtr parse_old_test();
    //! old_lambdef: 'lambda' [varargslist] ':' old_test
    ExprASTPtr parse_old_lambdef();
    //! test: or_test ['if' or_test 'else' test] | lambdef
    ExprASTPtr parse_test();
    //! or_test: and_test ('or' and_test)*
    ExprASTPtr parse_or_test();
    //! and_test: not_test ('and' not_test)*
    ExprASTPtr parse_and_test();
    //! not_test: 'not' not_test | comparison
    ExprASTPtr parse_not_test();
    //! comparison: expr (comp_op expr)*
    ExprASTPtr parse_comparison();
    //! comp_op: '<'|'>'|'=='|'>='|'<='|'<>'|'!='|'in'|'not' 'in'|'is'|'is' 'not'
    ExprASTPtr parse_comp_op(ExprASTPtr& expr);
    //! expr: xor_expr ('|' xor_expr)*
    ExprASTPtr parse_expr();
    //! xor_expr: and_expr ('^' and_expr)*
    ExprASTPtr parse_xor_expr();
    //! and_expr: shift_expr ('&' shift_expr)*
    ExprASTPtr parse_and_expr();
    //! shift_expr: arith_expr (('<<'|'>>') arith_expr)*
    ExprASTPtr parse_shift_expr();
    //! arith_expr: term (('+'|'-') term)*
    ExprASTPtr parse_arith_expr();
    //! term: factor (('*'|'/'|'%'|'//') factor)*
    ExprASTPtr parse_term();
    //! factor: ('+'|'-'|'~') factor | power
    ExprASTPtr parse_factor();
    //! power: atom trailer* ['**' factor]
    ExprASTPtr parse_power();
    //! atom: ('(' [yield_expr|testlist_comp] ')' |
    //!        '[' [listmaker] ']' |
    //!        '{' [dictorsetmaker] '}' |
    //!        '`' testlist1 '`' |
    //!        NAME | NUMBER | STRING+)
    ExprASTPtr parse_atom();
    //! listmaker: test ( list_for | (',' test)* [','] )
    ExprASTPtr parse_listmaker();
    //! testlist_comp: test ( comp_for | (',' test)* [','] )
    ExprASTPtr parse_testlist_comp();
    //! lambdef: 'lambda' [varargslist] ':' test
    ExprASTPtr parse_lambdef();
    //! trailer: '(' [arglist] ')' | '[' subscriptlist ']' | '.' NAME
    ExprASTPtr parse_trailer();
    //! subscriptlist: subscript (',' subscript)* [',']
    ExprASTPtr parse_subscriptlist();
    //! subscript: '.' '.' '.' | test | [test] ':' [test] [sliceop]
    ExprASTPtr parse_subscript();
    //! sliceop: ':' [test]
    ExprASTPtr parse_sliceop();
    //! exprlist: expr (',' expr)* [',']
    ExprASTPtr parse_exprlist();
    //! testlist: test (',' test)* [',']
    ExprASTPtr parse_testlist();
    //! dictorsetmaker: ( (test ':' test (comp_for | (',' test ':' test)* [','])) |
    //!                   (test (comp_for | (',' test)* [','])) )
    ExprASTPtr parse_dictorsetmaker();
    //! classdef: 'class' NAME ['(' [testlist] ')'] ':' suite
    ExprASTPtr parse_classdef();
    //! arglist: (argument ',')* (argument [',']
    //!                          |'*' test (',' argument)* [',' '**' test] 
    //!                          |'**' test)
    ExprASTPtr parse_arglist();
    //! argument: test [comp_for] | test '=' test
    ExprASTPtr parse_argument(ExprASTPtr& pFuncArglist);
    //! list_iter: list_for | list_if
    ExprASTPtr parse_list_iter();
    //! list_for: 'for' exprlist 'in' testlist_safe [list_iter]
    ExprASTPtr parse_list_for();
    //! list_if: 'if' old_test [list_iter]
    ExprASTPtr parse_list_if();
    //! comp_iter: comp_for | comp_if
    ExprASTPtr parse_comp_iter();
    //! comp_for: 'for' exprlist 'in' or_test [comp_iter]
    ExprASTPtr parse_comp_for();
    //! comp_if: 'if' old_test [comp_iter]
    ExprASTPtr parse_comp_if();
    //! testlist1: test (',' test)*
    ExprASTPtr parse_testlist1();
    //! encoding_decl: NAME
    ExprASTPtr parse_encoding_decl();
    //! yield_expr: 'yield' [testlist]
    ExprASTPtr parse_yield_expr();
    
    
    
    ExprASTPtr parse_name(bool throwFlag = true);
    
    void throwError(const std::string& err, int nLine = 0);
private:
    template<typename T>
    T* assignLineInfo(T* p, int nLine, int nIndent){
        p->lineInfo.nLine   = nLine;
        p->lineInfo.nIndent = nIndent;
    }
protected:
    Scanner*            m_curScanner;
};

}

#endif

