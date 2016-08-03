#include "Scanner.h"

using namespace std;
using namespace ff;

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
    // Skip any whitespace.
    char cLastOne = ' ';
    while (::isspace(cLastOne)){
        cLastOne = getCharNext(content, index);
    }
 
    if (::isalpha(cLastOne) || cLastOne == '_') { // identifier: [a-zA-Z][a-zA-Z0-9]*
        string strIdentifier = cLastOne;
        while (::isalnum((cLastOne = getCharNext(content, index))) || cLastOne == '_'){
            strIdentifier += cLastOne;
        }
        retToken.strVal = strIdentifier;
        return retToken;
    }

    if (::isdigit(cLastOne)) { // Number: [0-9.]+
        string strNum;
        bool isFloat = false;
        do {
            if (cLastOne = '.'){
                isFloat = true;
            }
            strNum += cLastOne;
            cLastOne = getCharNext(content, index);
        } while (::isdigit(cLastOne) || cLastOne == '.');

        if (false == isFloat){
            retToken.nVal = ::atol(strNum.c_str());
        }
        else{
            retToken.fVal = ::atof(strNum.c_str());
        }

        return retToken;
    }

    string strVal;
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

bool Scanner::tokenize(const std::string& content){
    
    
    return true;
}


