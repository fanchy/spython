#ifndef _SCANNER_H_
#define _SCANNER_H_

#include <string>
#include <vector>

namespace ff {

struct Token{
    Token():nTokenType(0), nVal(0), fVal(0.0){
    }
    
    std::string dump() const;
    int             nTokenType;
    long            nVal;
    double          fVal;
    std::string     strVal;
};

class Scanner{
public:
    Scanner();
    
    //!parse string to token vector
    bool tokenize(const std::string& content);

    //!get cur token obj
    const Token* getToken(int nOffset = 0);
    int seek(int nOffset);

protected:
    int                     m_nSeekIndex;
    Token                   m_tokenEOF;
    std::vector<Token>      m_allTokens;
};
    
}

#endif

