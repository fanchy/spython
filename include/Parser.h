
class Parser{
public:
    //! single_input: NEWLINE | simple_stmt | compound_stmt NEWLINE
    ExprPtr parse_single_input();
    //! file_input: (NEWLINE | stmt)* ENDMARKER
    ExprPtr parse_file_input();
    //! eval_input: testlist NEWLINE* ENDMARKER
    ExprPtr parse_eval_input();
    //! decorator: '@' dotted_name [ '(' [arglist] ')' ] NEWLINE
    ExprPtr parse_decorator();
    //! decorators: decorator+
    ExprPtr parse_decorators();
    //! decorated: decorators (classdef | funcdef)
    ExprPtr parse_decorated();
    //! funcdef: 'def' NAME parameters ':' suite
    ExprPtr parse_funcdef();
    //! parameters: '(' [varargslist] ')'
    ExprPtr parse_parameters();
    //! varargslist: ((fpdef ['=' test] ',')*
    ExprPtr parse_varargslist();
    //! fpdef: NAME | '(' fplist ')'
    ExprPtr parse_fpdef();
    //! fplist: fpdef (',' fpdef)* [',']
    ExprPtr parse_fplist();
    //! stmt: simple_stmt | compound_stmt
    ExprPtr parse_stmt();
    //! simple_stmt: small_stmt (';' small_stmt)* [';'] NEWLINE
    ExprPtr parse_simple_stmt();
    //! small_stmt: (expr_stmt | print_stmt  | del_stmt | pass_stmt | flow_stmt |
    ExprPtr parse_small_stmt();
    //! expr_stmt: testlist (augassign (yield_expr|testlist) |
    ExprPtr parse_expr_stmt();
    //! augassign: ('+=' | '-=' | '*=' | '/=' | '%=' | '&=' | '|=' | '^=' |
    ExprPtr parse_augassign();
    //! print_stmt: 'print' ( [ test (',' test)* [','] ] |
    ExprPtr parse_print_stmt();
    //! del_stmt: 'del' exprlist
    ExprPtr parse_del_stmt();
    //! pass_stmt: 'pass'
    ExprPtr parse_pass_stmt();
    //! flow_stmt: break_stmt | continue_stmt | return_stmt | raise_stmt | yield_stmt
    ExprPtr parse_flow_stmt();
    //! break_stmt: 'break'
    ExprPtr parse_break_stmt();
    //! continue_stmt: 'continue'
    ExprPtr parse_continue_stmt();
    //! return_stmt: 'return' [testlist]
    ExprPtr parse_return_stmt();
    //! yield_stmt: yield_expr
    ExprPtr parse_yield_stmt();
    //! raise_stmt: 'raise' [test [',' test [',' test]]]
    ExprPtr parse_raise_stmt();
    //! import_stmt: import_name | import_from
    ExprPtr parse_import_stmt();
    //! import_name: 'import' dotted_as_names
    ExprPtr parse_import_name();
    //! import_from: ('from' ('.'* dotted_name | '.'+)
    ExprPtr parse_import_from();
    //! import_as_name: NAME ['as' NAME]
    ExprPtr parse_import_as_name();
    //! dotted_as_name: dotted_name ['as' NAME]
    ExprPtr parse_dotted_as_name();
    //! import_as_names: import_as_name (',' import_as_name)* [',']
    ExprPtr parse_import_as_names();
    //! dotted_as_names: dotted_as_name (',' dotted_as_name)*
    ExprPtr parse_dotted_as_names();
    //! dotted_name: NAME ('.' NAME)*
    ExprPtr parse_dotted_name();
    //! global_stmt: 'global' NAME (',' NAME)*
    ExprPtr parse_global_stmt();
    //! exec_stmt: 'exec' expr ['in' test [',' test]]
    ExprPtr parse_exec_stmt();
    //! assert_stmt: 'assert' test [',' test]
    ExprPtr parse_assert_stmt();
    //! compound_stmt: if_stmt | while_stmt | for_stmt | try_stmt | with_stmt | funcdef | classdef | decorated
    ExprPtr parse_compound_stmt();
    //! if_stmt: 'if' test ':' suite ('elif' test ':' suite)* ['else' ':' suite]
    ExprPtr parse_if_stmt();
    //! while_stmt: 'while' test ':' suite ['else' ':' suite]
    ExprPtr parse_while_stmt();
    //! for_stmt: 'for' exprlist 'in' testlist ':' suite ['else' ':' suite]
    ExprPtr parse_for_stmt();
    //! try_stmt: ('try' ':' suite
    ExprPtr parse_try_stmt();
    //!            ((except_clause ':' suite)+
    ExprPtr parse_((except_clause '();
    //!             ['else' ':' suite]
    ExprPtr parse_['else' '();
    //!             ['finally' ':' suite] |
    ExprPtr parse_['finally' '();
    //!            'finally' ':' suite))
    ExprPtr parse_'finally' '();
    //! with_stmt: 'with' with_item (',' with_item)*  ':' suite
    ExprPtr parse_with_stmt();
    //! with_item: test ['as' expr]
    ExprPtr parse_with_item();
    //! except_clause: 'except' [test [('as' | ',') test]]
    ExprPtr parse_except_clause();
    //! suite: simple_stmt | NEWLINE INDENT stmt+ DEDENT
    ExprPtr parse_suite();
    //! testlist_safe: old_test [(',' old_test)+ [',']]
    ExprPtr parse_testlist_safe();
    //! old_test: or_test | old_lambdef
    ExprPtr parse_old_test();
    //! old_lambdef: 'lambda' [varargslist] ':' old_test
    ExprPtr parse_old_lambdef();
    //! test: or_test ['if' or_test 'else' test] | lambdef
    ExprPtr parse_test();
    //! or_test: and_test ('or' and_test)*
    ExprPtr parse_or_test();
    //! and_test: not_test ('and' not_test)*
    ExprPtr parse_and_test();
    //! not_test: 'not' not_test | comparison
    ExprPtr parse_not_test();
    //! comparison: expr (comp_op expr)*
    ExprPtr parse_comparison();
    //! comp_op: '<'|'>'|'=='|'>='|'<='|'<>'|'!='|'in'|'not' 'in'|'is'|'is' 'not'
    ExprPtr parse_comp_op();
    //! expr: xor_expr ('|' xor_expr)*
    ExprPtr parse_expr();
    //! xor_expr: and_expr ('^' and_expr)*
    ExprPtr parse_xor_expr();
    //! and_expr: shift_expr ('&' shift_expr)*
    ExprPtr parse_and_expr();
    //! shift_expr: arith_expr (('<<'|'>>') arith_expr)*
    ExprPtr parse_shift_expr();
    //! arith_expr: term (('+'|'-') term)*
    ExprPtr parse_arith_expr();
    //! term: factor (('*'|'/'|'%'|'//') factor)*
    ExprPtr parse_term();
    //! factor: ('+'|'-'|'~') factor | power
    ExprPtr parse_factor();
    //! power: atom trailer* ['**' factor]
    ExprPtr parse_power();
    //! atom: ('(' [yield_expr|testlist_comp] ')' |
    ExprPtr parse_atom();
    //! listmaker: test ( list_for | (',' test)* [','] )
    ExprPtr parse_listmaker();
    //! testlist_comp: test ( comp_for | (',' test)* [','] )
    ExprPtr parse_testlist_comp();
    //! lambdef: 'lambda' [varargslist] ':' test
    ExprPtr parse_lambdef();
    //! trailer: '(' [arglist] ')' | '[' subscriptlist ']' | '.' NAME
    ExprPtr parse_trailer();
    //! subscriptlist: subscript (',' subscript)* [',']
    ExprPtr parse_subscriptlist();
    //! subscript: '.' '.' '.' | test | [test] ':' [test] [sliceop]
    ExprPtr parse_subscript();
    //! sliceop: ':' [test]
    ExprPtr parse_sliceop();
    //! exprlist: expr (',' expr)* [',']
    ExprPtr parse_exprlist();
    //! testlist: test (',' test)* [',']
    ExprPtr parse_testlist();
    //! dictorsetmaker: ( (test ':' test (comp_for | (',' test ':' test)* [','])) |
    ExprPtr parse_dictorsetmaker();
    //! classdef: 'class' NAME ['(' [testlist] ')'] ':' suite
    ExprPtr parse_classdef();
    //! arglist: (argument ',')* (argument [',']
    ExprPtr parse_arglist();
    //! argument: test [comp_for] | test '=' test
    ExprPtr parse_argument();
    //! list_iter: list_for | list_if
    ExprPtr parse_list_iter();
    //! list_for: 'for' exprlist 'in' testlist_safe [list_iter]
    ExprPtr parse_list_for();
    //! list_if: 'if' old_test [list_iter]
    ExprPtr parse_list_if();
    //! comp_iter: comp_for | comp_if
    ExprPtr parse_comp_iter();
    //! comp_for: 'for' exprlist 'in' or_test [comp_iter]
    ExprPtr parse_comp_for();
    //! comp_if: 'if' old_test [comp_iter]
    ExprPtr parse_comp_if();
    //! testlist1: test (',' test)*
    ExprPtr parse_testlist1();
    //! encoding_decl: NAME
    ExprPtr parse_encoding_decl();
    //! yield_expr: 'yield' [testlist]
    ExprPtr parse_yield_expr();
}
