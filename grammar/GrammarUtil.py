


f = open('Grammar')
data = f.read()
f.close()

lines = data.split('\n')
funIncCode = '#ifndef _PARSE_H_\n#define _PARSE_H_\n\n#include "Base.h"\n\nnamespace spython{\n\nclass Parser{\npublic:\n'
funSrcCode = '#include "Parser.h"\n'
funcName_code= ''
comment_code = ''
comment_code2 = ''
for line in lines:
    if line == '' or line[0] == '#':
        continue
    args = line.split(':')
    if len(args) < 2:
        if line[0] == ' ':
            comment_code += '\n    //! ' + line
            comment_code2+= '\n//! ' + line
        continue
    if line[0] == ' ':
        comment_code += '\n    //! ' + line
        comment_code2+= '\n//! ' + line
        continue
    if args[1] == '':
        continue
    funcName = '%s'%(args[0].strip())
    if funcName_code != '':
        funIncCode  += '    //! %s\n' % (comment_code)
        funIncCode  += '    ExprASTPtr parse_%s();\n'%(funcName_code)
        
        funSrcCode  += '\n//! %s\n' % (comment_code2)
        funSrcCode  += 'ExprASTPtr Parser::parse_%s(){\n    return NULL;\n}\n'%(funcName_code)
        funcName_code = ''
        comment_code  = ''
        comment_code2 = ''
    
    funcName_code = funcName
    comment_code += line
    comment_code2+= line

if funcName_code != '':
    funIncCode  += '    //! %s\n' % (comment_code)
    funIncCode  += '    ExprASTPtr parse_%s();\n'%(funcName_code)
        
    funSrcCode  += '\n//! %s\n' % (comment_code2)
    funSrcCode  += 'ExprASTPtr Parser::parse_%s(){\n    return NULL;\n}\n'%(funcName_code)
    funcName_code = ''
    comment_code  = ''
    comment_code2 = ''
        
funIncCode += '};\n\n}\n\n#endif\n'
#print(funIncCode)
#print(funSrcCode)

f = open('Parser.h', 'w')
data = f.write(funIncCode)
f.close()

f = open('Parser.cpp', 'w')
data = f.write(funSrcCode)
f.close()
