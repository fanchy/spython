


f = open('Grammar')
data = f.read()
f.close()

lines = data.split('\n')
funIncCode = '\nclass Parser{\npublic:\n'
funSrcCode = '#include "Parser.h"\n'

for line in lines:
    if line == '' or line[0] == '#':
        continue
    args = line.split(':')
    if len(args) < 2 or args[1] == '':
        continue
    funcName = '%s'%(args[0].strip())
    funIncCode  += '    //! %s\n' % (line)
    funIncCode  += '    ExprPtr parse_%s();\n'%(funcName)
    
    funSrcCode  += '\n//! %s\n' % (line)
    funSrcCode  += 'ExprPtr Parser::parse_%s(){\n    return NULL;\n}\n'%(funcName)

funIncCode += '}\n'
#print(funIncCode)
#print(funSrcCode)

f = open('Parser.h', 'w')
data = f.write(funIncCode)
f.close()

f = open('Parser.cpp', 'w')
data = f.write(funSrcCode)
f.close()