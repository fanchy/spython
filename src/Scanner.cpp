#include <stdlib.h>

#include "Base.h"
#include "Scanner.h"

using namespace std;
using namespace ff;

string Token::dump() const{
    char msg[64] = {0};
    switch(nTokenType){
        case TOK_EOF:{
            return "TOK_EOF";
            break;
        }
        case TOK_VAR:{
            return strVal + "(var)";
            break;
        }
        case TOK_INT:{
            snprintf(msg, sizeof(msg), "%ld(int)", nVal);
            return msg;
            break;
        }
        case TOK_FLOAT:{
            snprintf(msg, sizeof(msg), "%f(float)", fVal);
            return msg;
            break;
        }
        case TOK_CHAR:{
            if (strVal.empty() == false && strVal[0] == '\n'){
                return "\\n(char)";
            }
            return strVal + "(char)";
            break;
        }
        default:
            break;
    }
    return msg;
}

char Scanner::getCharNext(const string& content, int& index) {
    char ret = 0;
    do{
        if (index < content.size()){
            ret = content[index++];
        }else{
            ret = 0;
        }
    }while(ret == '\r');
    
    if (ret == '\n' & index > m_hasSearchMaxIndex){
        m_hasSearchMaxIndex = index;
        m_nCurLine++;
    }
    return ret;
}
/// gettok - Return the next token from standard input.
Token Scanner::getOneToken(const std::string& content, int& index) {
    Token retToken;

    //!ignore comment 
    char cLastOne = getCharNext(content, index);
    
    while (cLastOne == '#' || cLastOne == ' ') {
        // Comment until end of line.
        if (cLastOne == ' '){
            cLastOne = getCharNext(content, index);
        }
        else if (cLastOne == '#'){
            do{
                cLastOne = getCharNext(content, index);
            }
            while (cLastOne != TOK_EOF && cLastOne != '\n');
            cLastOne = getCharNext(content, index);
        }
    }
 
    if (::isalpha(cLastOne) || cLastOne == '_') { // identifier: [a-zA-Z][a-zA-Z0-9]*
        retToken.strVal = cLastOne;
        while (::isalnum((cLastOne = getCharNext(content, index))) || cLastOne == '_'){
            retToken.strVal += cLastOne;
        }
        if (cLastOne != 0)
            index--;//!pop last char \n
        retToken.nTokenType = TOK_VAR;
        return retToken;
    }

    int nPlusMinus = 1;
    if (cLastOne == '-'){//! check plus symbol
       char nextOne = getCharNext(content, index);
       if (::isdigit(nextOne)){
           nPlusMinus = -1;
           cLastOne = nextOne;
       }
       else{
           index--;//! back push one char
       }
    }
    if (::isdigit(cLastOne)) { // Number: [0-9.]+
        string strNum;
        bool isFloat = false;
        do {
            if (cLastOne == '.'){
                isFloat = true;
            }
            strNum += cLastOne;
            cLastOne = getCharNext(content, index);
        } while (::isdigit(cLastOne) || cLastOne == '.');

        if (false == isFloat){
            retToken.nVal = nPlusMinus * ::atol(strNum.c_str());
            retToken.nTokenType = TOK_INT;
        }
        else{
            retToken.fVal = nPlusMinus * ::atof(strNum.c_str());
            retToken.nTokenType = TOK_FLOAT;
        }

        if (cLastOne != 0)
            index--;//!pop last char \n
        return retToken;
    }

    if (cLastOne == '\'' || cLastOne == '\"') {
        char tmpC = cLastOne;
        retToken.strVal.clear();
        do {
            cLastOne = getCharNext(content, index);
            if (cLastOne == tmpC){
                //cLastOne = getCharNext(content, index);
                break;
            }
            retToken.strVal += cLastOne;
        } while (cLastOne != TOK_EOF);

        retToken.nTokenType = TOK_STR;
        return retToken;
    }

    // Check for end of file.  Don't eat the EOF.
    if (cLastOne == TOK_EOF)
        return retToken;

    retToken.strVal        = cLastOne;
    if (cLastOne ==';'){
        retToken.strVal        = cLastOne;
    }
    //! augassign: ('+=' | '-=' | '*=' | '/=' | '%=' | '&=' | '|=' | '^=' |
    //!             '<<=' | '>>=' | '**=' | '//=')
    //! comp_op: '<'|'>'|'=='|'>='|'<='|'<>'|'!='|
    switch (cLastOne){
        case '+':
        case '-':
        case '%':
        case '&':
        case '^':
        {
            cLastOne = getCharNext(content, index);
            if (cLastOne == '='){
                retToken.strVal += '=';
            }
            else{
                --index;
            }
        }break;
        case '<':
        case '>':
        {
            char cLastOne2 = getCharNext(content, index);
            char cLastOne3 = getCharNext(content, index);
            if (cLastOne2 == '='){
                retToken.strVal += cLastOne2;
                index -= 1;
            }
            else if (cLastOne == cLastOne2 && cLastOne3 == '='){
                retToken.strVal += cLastOne2;
                retToken.strVal += cLastOne3;
            }
            else if (cLastOne == '<' && cLastOne2 == '>'){
                retToken.strVal += cLastOne2;
                index -= 1;
            }
            else{
                index -= 2;
            }
        }break;
        case '/':
        case '*':{
            char cLastOne2 = getCharNext(content, index);
            char cLastOne3 = getCharNext(content, index);
            if (cLastOne2 == '='){
                retToken.strVal += cLastOne2;
                index -= 1;
            }
            else if (cLastOne == cLastOne2 && cLastOne3 == '='){
                retToken.strVal += cLastOne2;
                retToken.strVal += cLastOne3;
            }
            else{
                index -= 2;
            }
            break;
        }
        case '=':
        case '!':
        {
            cLastOne = getCharNext(content, index);
            if (cLastOne == '='){
                retToken.strVal += '=';
            }
            else{
                --index;
            }
        }break;
        default:
            break;
    }
    // Otherwise, just return the character as its ascii value.
    
    
    retToken.nTokenType    = TOK_CHAR;
    return retToken;
}

Scanner::Scanner():m_nSeekIndex(0), m_nCurLine(1), m_hasSearchMaxIndex(0), m_nCurFileId(0){
}
void Scanner::calLineIndentInfo(const std::string& content){
    int nLine = 1;
    LineInfo& lineInfo = m_allLines[nLine];
    bool bLineCal = true;
    for (unsigned int j = 0; j < content.size(); ++j){
        if (content[j] == '\n')
            break;
        lineInfo.strLine += content[j];
        
        if (bLineCal && content[j] == ' '){
            lineInfo.nIndent ++;
        }
        else{
            bLineCal = false;
        }
    }
    
    for (unsigned int i = 0; i < content.size(); ++i)
    {
        char ret = content[i];
        if (ret != '\n'){
            continue;
        }
        ++nLine;
        
        LineInfo& lineInfo = m_allLines[nLine];
        bool bLineCal = true;
        for (unsigned int j = i + 1; j < content.size(); ++j){
            if (content[j] == '\n')
                break;
            lineInfo.strLine += content[j];
            
            if (bLineCal && content[j] == ' '){
                lineInfo.nIndent ++;
            }
            else{
                bLineCal = false;
            }
        }
        //printf("line:%d indent:%d\n", nLine, lineInfo.nIndent);
    }
}
bool Scanner::tokenizeFile(const std::string& path, int nFileId){
    FILE* fp = ::fopen(path.c_str(), "r");
    string strCode;
    if(NULL == fp)
    {
        printf("¶ÁÈ¡Ê§°Ü£¡\n");
        return false;
    }
    
    char buf[2048];
    int n = fread(buf, 1, sizeof(buf), fp);
    ::fclose(fp);
    strCode.assign(buf, n);
    m_nCurFileId = nFileId;
    return tokenize(strCode);
}
bool Scanner::tokenize(const std::string& content){

    int nIndex = 0;
    m_nCurLine = 1;
    m_hasSearchMaxIndex = 0;
    Token retToken;
    
    calLineIndentInfo(content);
    do{
        retToken = getOneToken(content, nIndex);
        retToken.nLine = m_nCurLine;
        m_allTokens.push_back(retToken);

        //printf("token:%s\n", retToken.dump().c_str());

    }while (retToken.nTokenType != TOK_EOF);
    
    m_nSeekIndex = 0;
    return true;
}

const Token* Scanner::getToken(int nOffset){
    
    int nIndex = m_nSeekIndex + nOffset;
    if (nIndex >= 0 && nIndex < m_allTokens.size()){
        return &(m_allTokens[nIndex]);
    }
    
    return &(m_tokenEOF);
}

int Scanner::seek(int nOffset){
    m_nSeekIndex += nOffset;
    return m_nSeekIndex;
}

int Scanner::resetTo(int nOffset){
    m_nSeekIndex = nOffset;
    return m_nSeekIndex;
}
int Scanner::skipEnterChar(){
    while (this->getToken()->strVal == "\n"){
        this->seek(1);
    }
    return m_nSeekIndex;
}
int Scanner::curIndentWidth(){
    int nIndex = 0;
    while (this->getToken(nIndex)->strVal == "\n"){
        ++nIndex;
    }
    return m_allLines[this->getToken(nIndex)->nLine].nIndent;
}

int Scanner::calLineIndentWidth(int nLine){
    return m_allLines[nLine].nIndent;
}
std::string Scanner::getLineCode(int nLine){
    return m_allLines[nLine].strLine; 
}
 
std::map<int, std::string> Scanner::getAllLineCode(){
    std::map<int, std::string> ret;
    std::map<int, LineInfo>::iterator it = m_allLines.begin();
    for (; it != m_allLines.end(); ++it){
        ret[it->first] = it->second.strLine;
    }
    return ret;
}

