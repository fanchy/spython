#ifndef _PY_UTIL_H_
#define _PY_UTIL_H_

#include <string>
#include <vector>

namespace ff {

class Util{
public:
    static bool isDir(const std::string& path);
    static bool isFile(const std::string& path);
    static bool getAllFileInDir(const std::string& path, std::vector<std::string>& ret, std::string extFilter = "");
};

};

#endif

