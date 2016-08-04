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
            return strVal + "(char)";
            break;
        }
    }
    return msg;
}

static char getCharNext(const string& content, int& index) {
    if (index < content.size()){
        char ret = content[index++];
        return ret;
    }
    return 0;
}
/// gettok - Return the next token from standard input.
static Token getOneToken(const string& content, int& index) {
    Token retToken;

    //!ignore comment 
    char cLastOne = getCharNext(content, index);
    
    while (cLastOne == '#' || cLastOne == '\n' || cLastOne == '\r') {
        // Comment until end of line.
        if (cLastOne == '#'){
            do{
                cLastOne = getCharNext(content, index);
            }
            while (cLastOne != TOK_EOF && cLastOne != '\n');
            cLastOne = getCharNext(content, index);
        }
        else{
             //!ignore \n
            if (cLastOne == '\n' || cLastOne == '\r') {
                do{
                    cLastOne = getCharNext(content, index);
                    //printf("lastone2:%c %d \n", cLastOne, cLastOne);
                }
                while (cLastOne == '\n' || cLastOne == '\r');
            }
        }
    }

    
    // Skip any whitespace.
    while (::isspace(cLastOne)){
        cLastOne = getCharNext(content, index);
    }
 
    if (::isalpha(cLastOne) || cLastOne == '_') { // identifier: [a-zA-Z][a-zA-Z0-9]*
        retToken.strVal = cLastOne;
        while (::isalnum((cLastOne = getCharNext(content, index))) || cLastOne == '_'){
            retToken.strVal += cLastOne;
        }
        index--;
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

bool Scanner::tokenize(const std::string& content){
    
    int nIndex = 0;
    
    Token retToken;
    do{
        retToken = getOneToken(content, nIndex);
        m_allTokens.push_back(retToken);

        printf("token:%s\n", retToken.dump().c_str());
        
    }while (retToken.nTokenType != TOK_EOF);
    
    return true;
}


