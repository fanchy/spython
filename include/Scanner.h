#ifndef _SCANNER_H_
#define _SCANNER_H_

#include <string>
#include <vector>

namespace ff {

struct Token{
    Token():nTokenType(0), nVal(0), fVal(0.0){
    }
    
    int             nTokenType;
    long            nVal;
    double          fVal;
    std::string     strVal;
};

class Scanner{
public:
    bool tokenize(const std::string& content);

protected:
    std::vector<Token>      m_allTokens;
};
    
}

#endif

