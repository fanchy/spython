#include "Parser.h"

using namespace ff;

//! single_input: NEWLINE | simple_stmt | compound_stmt NEWLINE
ExprASTPtr Parser::parse_single_input(){
    return NULL;
}

//! file_input: (NEWLINE | stmt)* ENDMARKER
ExprASTPtr Parser::parse_file_input(){
    return NULL;
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
    return NULL;
}

//! parameters: '(' [varargslist] ')'
ExprASTPtr Parser::parse_parameters(){
    return NULL;
}

//! varargslist: ((fpdef ['=' test] ',')*
//!               ('*' NAME [',' '**' NAME] | '**' NAME) |
//!               fpdef ['=' test] (',' fpdef ['=' test])* [','])
ExprASTPtr Parser::parse_varargslist(){
    return NULL;
}

//! fpdef: NAME | '(' fplist ')'
ExprASTPtr Parser::parse_fpdef(){
    return NULL;
}

//! fplist: fpdef (',' fpdef)* [',']
ExprASTPtr Parser::parse_fplist(){
    return NULL;
}

//! stmt: simple_stmt | compound_stmt
ExprASTPtr Parser::parse_stmt(){
    return NULL;
}

//! simple_stmt: small_stmt (';' small_stmt)* [';'] NEWLINE
ExprASTPtr Parser::parse_simple_stmt(){
    return NULL;
}

//! small_stmt: (expr_stmt | print_stmt  | del_stmt | pass_stmt | flow_stmt |
//!              import_stmt | global_stmt | exec_stmt | assert_stmt)
ExprASTPtr Parser::parse_small_stmt(){
    return NULL;
}

//! expr_stmt: testlist (augassign (yield_expr|testlist) |
//!                      ('=' (yield_expr|testlist))*)
ExprASTPtr Parser::parse_expr_stmt(){
    return NULL;
}

//! augassign: ('+=' | '-=' | '*=' | '/=' | '%=' | '&=' | '|=' | '^=' |
//!             '<<=' | '>>=' | '**=' | '//=')
ExprASTPtr Parser::parse_augassign(){
    return NULL;
}

//! print_stmt: 'print' ( [ test (',' test)* [','] ] |
//!                       '>>' test [ (',' test)+ [','] ] )
ExprASTPtr Parser::parse_print_stmt(){
    return NULL;
}

//! del_stmt: 'del' exprlist
ExprASTPtr Parser::parse_del_stmt(){
    return NULL;
}

//! pass_stmt: 'pass'
ExprASTPtr Parser::parse_pass_stmt(){
    return NULL;
}

//! flow_stmt: break_stmt | continue_stmt | return_stmt | raise_stmt | yield_stmt
ExprASTPtr Parser::parse_flow_stmt(){
    return NULL;
}

//! break_stmt: 'break'
ExprASTPtr Parser::parse_break_stmt(){
    return NULL;
}

//! continue_stmt: 'continue'
ExprASTPtr Parser::parse_continue_stmt(){
    return NULL;
}

//! return_stmt: 'return' [testlist]
ExprASTPtr Parser::parse_return_stmt(){
    return NULL;
}

//! yield_stmt: yield_expr
ExprASTPtr Parser::parse_yield_stmt(){
    return NULL;
}

//! raise_stmt: 'raise' [test [',' test [',' test]]]
ExprASTPtr Parser::parse_raise_stmt(){
    return NULL;
}

//! import_stmt: import_name | import_from
ExprASTPtr Parser::parse_import_stmt(){
    return NULL;
}

//! import_name: 'import' dotted_as_names
ExprASTPtr Parser::parse_import_name(){
    return NULL;
}

//! import_from: ('from' ('.'* dotted_name | '.'+)
//!               'import' ('*' | '(' import_as_names ')' | import_as_names))
ExprASTPtr Parser::parse_import_from(){
    return NULL;
}

//! import_as_name: NAME ['as' NAME]
ExprASTPtr Parser::parse_import_as_name(){
    return NULL;
}

//! dotted_as_name: dotted_name ['as' NAME]
ExprASTPtr Parser::parse_dotted_as_name(){
    return NULL;
}

//! import_as_names: import_as_name (',' import_as_name)* [',']
ExprASTPtr Parser::parse_import_as_names(){
    return NULL;
}

//! dotted_as_names: dotted_as_name (',' dotted_as_name)*
ExprASTPtr Parser::parse_dotted_as_names(){
    return NULL;
}

//! dotted_name: NAME ('.' NAME)*
ExprASTPtr Parser::parse_dotted_name(){
    return NULL;
}

//! global_stmt: 'global' NAME (',' NAME)*
ExprASTPtr Parser::parse_global_stmt(){
    return NULL;
}

//! exec_stmt: 'exec' expr ['in' test [',' test]]
ExprASTPtr Parser::parse_exec_stmt(){
    return NULL;
}

//! assert_stmt: 'assert' test [',' test]
ExprASTPtr Parser::parse_assert_stmt(){
    return NULL;
}

//! compound_stmt: if_stmt | while_stmt | for_stmt | try_stmt | with_stmt | funcdef | classdef | decorated
ExprASTPtr Parser::parse_compound_stmt(){
    return NULL;
}

//! if_stmt: 'if' test ':' suite ('elif' test ':' suite)* ['else' ':' suite]
ExprASTPtr Parser::parse_if_stmt(){
    return NULL;
}

//! while_stmt: 'while' test ':' suite ['else' ':' suite]
ExprASTPtr Parser::parse_while_stmt(){
    return NULL;
}

//! for_stmt: 'for' exprlist 'in' testlist ':' suite ['else' ':' suite]
ExprASTPtr Parser::parse_for_stmt(){
    return NULL;
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
    return NULL;
}

//! or_test: and_test ('or' and_test)*
ExprASTPtr Parser::parse_or_test(){
    return NULL;
}

//! and_test: not_test ('and' not_test)*
ExprASTPtr Parser::parse_and_test(){
    return NULL;
}

//! not_test: 'not' not_test | comparison
ExprASTPtr Parser::parse_not_test(){
    return NULL;
}

//! comparison: expr (comp_op expr)*
ExprASTPtr Parser::parse_comparison(){
    return NULL;
}

//! comp_op: '<'|'>'|'=='|'>='|'<='|'<>'|'!='|'in'|'not' 'in'|'is'|'is' 'not'
ExprASTPtr Parser::parse_comp_op(){
    return NULL;
}

//! expr: xor_expr ('|' xor_expr)*
ExprASTPtr Parser::parse_expr(){
    return NULL;
}

//! xor_expr: and_expr ('^' and_expr)*
ExprASTPtr Parser::parse_xor_expr(){
    return NULL;
}

//! and_expr: shift_expr ('&' shift_expr)*
ExprASTPtr Parser::parse_and_expr(){
    return NULL;
}

//! shift_expr: arith_expr (('<<'|'>>') arith_expr)*
ExprASTPtr Parser::parse_shift_expr(){
    return NULL;
}

//! arith_expr: term (('+'|'-') term)*
ExprASTPtr Parser::parse_arith_expr(){
    return NULL;
}

//! term: factor (('*'|'/'|'%'|'//') factor)*
ExprASTPtr Parser::parse_term(){
    return NULL;
}

//! factor: ('+'|'-'|'~') factor | power
ExprASTPtr Parser::parse_factor(){
    return NULL;
}

//! power: atom trailer* ['**' factor]
ExprASTPtr Parser::parse_power(){
    return NULL;
}

//! atom: ('(' [yield_expr|testlist_comp] ')' |
//!        '[' [listmaker] ']' |
//!        '{' [dictorsetmaker] '}' |
//!        '`' testlist1 '`' |
//!        NAME | NUMBER | STRING+)
ExprASTPtr Parser::parse_atom(){
    return NULL;
}

//! listmaker: test ( list_for | (',' test)* [','] )
ExprASTPtr Parser::parse_listmaker(){
    return NULL;
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
    return NULL;
}

//! testlist: test (',' test)* [',']
ExprASTPtr Parser::parse_testlist(){
    return NULL;
}

//! dictorsetmaker: ( (test ':' test (comp_for | (',' test ':' test)* [','])) |
//!                   (test (comp_for | (',' test)* [','])) )
ExprASTPtr Parser::parse_dictorsetmaker(){
    return NULL;
}

//! classdef: 'class' NAME ['(' [testlist] ')'] ':' suite
ExprASTPtr Parser::parse_classdef(){
    return NULL;
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
    return NULL;
}

//! encoding_decl: NAME
ExprASTPtr Parser::parse_encoding_decl(){
    return NULL;
}

//! yield_expr: 'yield' [testlist]
ExprASTPtr Parser::parse_yield_expr(){
    return NULL;
}
