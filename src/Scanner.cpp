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

static char getCharNext(const string& content, int& index) {
    char ret = 0;
    do{
        if (index < content.size()){
            ret = content[index++];
        }else{
            ret = 0;
        }
    }while(ret == '\r');

    return ret;
}
/// gettok - Return the next token from standard input.
static Token getOneToken(const string& content, int& index) {
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
        index--;//!pop last char \n
        retToken.nTokenType = TOK_VAR;
        return retToken;
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
            retToken.nVal = ::atol(strNum.c_str());
            retToken.nTokenType = TOK_INT;
        }
        else{
            retToken.fVal = ::atof(strNum.c_str());
            retToken.nTokenType = TOK_FLOAT;
        }

        index--;//!pop last char \n
        return retToken;
    }

    if (cLastOne == '\'' || cLastOne == '\"') {
        char tmpC = cLastOne;
        retToken.strVal.clear();
        do {
            cLastOne = getCharNext(content, index);
            if (cLastOne == tmpC){
                cLastOne = getCharNext(content, index);
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

    // Otherwise, just return the character as its ascii value.
    retToken.strVal        = cLastOne;
    retToken.nTokenType    = TOK_CHAR;
    return retToken;
}

Scanner::Scanner():m_nSeekIndex(0){
}

bool Scanner::tokenize(const std::string& content){

    int nIndex = 0;

    Token retToken;
    do{
        retToken = getOneToken(content, nIndex);
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


