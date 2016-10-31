
#include <sys/stat.h>
#include <unistd.h>
#include <sys/types.h>
#include <dirent.h>
#include <unistd.h>
#include <stdio.h>

#include "Util.h"

using namespace std;
using namespace ff;


bool Util::isDir(const string& path){
    struct stat buf;
    if (::stat(path.c_str(), &buf)){
        return false;
    }
    return S_ISDIR(buf.st_mode);
}
bool Util::isFile(const string& path){
    struct stat buf;
    if (::stat(path.c_str(), &buf)){
        return false;
    }
    return S_ISREG (buf.st_mode);
}

bool Util::getAllFileInDir(const std::string& path, std::vector<std::string>& ret, string extFilter){
    DIR    *dir = NULL;
    struct    dirent    *ptr = NULL;
    dir = ::opendir(path.c_str()); ///open the dir
    if (!dir){
        return false;
    }
    while((ptr = ::readdir(dir)) != NULL) ///read the list of this dir
    {
        string fileName = ptr->d_name;
        if (!extFilter.empty()){
            if (fileName.find(extFilter) == string::npos)
                continue;
        }
        ret.push_back(fileName);
    }
    ::closedir(dir);
    return true;
}

