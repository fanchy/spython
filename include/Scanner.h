#ifndef _SCANNER_H_
#define _SCANNER_H_

#include <string>
#include <vector>
#include <map>
#include <stdint.h>
#include<sstream>

namespace ff {

struct Token{
    Token():nTokenType(0), nVal(0), fVal(0.0), nLine(0){
    }
    
    std::string dump() const;
    int             nTokenType;
    int64_t         nVal;
    double          fVal;
    std::string     strVal;
    int             nLine;
};

struct LineInfo{
    LineInfo():nIndent(0){
    }
    int         nIndent;
    std::string strLine;
};

class Scanner{
public:
    Scanner();
    
    //!parse string to token vector
    bool tokenizeFile(const std::string& path, int nFileId);
    bool tokenize(const std::string& content);

    //!get cur token obj
    const Token* getToken(int nOffset = 0);
    int seek(int nOffset);
    int skipEnterChar();
    int curIndentWidth(int nOffset = 0);

    int getCurFileId(){
        return m_nCurFileId;
    }
    std::string getLineCode(int n);
    
    std::map<int, std::string> getAllLineCode();
    void dump();
private:
    char getCharNext(const std::string& content, int& index);
    Token getOneToken(const std::string& content, int& index);
    void calLineIndentInfo(const std::string& content);
protected:
    int                     m_nSeekIndex;
    Token                   m_tokenEOF;
    std::vector<Token>      m_allTokens;
    int                     m_nCurLine;
    std::map<int, LineInfo> m_allLines;
    int                     m_hasSearchMaxIndex;
    int                     m_nCurFileId;
    std::stringstream       m_istr;
};

}

#endif

