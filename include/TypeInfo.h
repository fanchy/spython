
#ifndef _FF_TYPE_H_
#define _FF_TYPE_H_

#ifndef _WIN32
#define MKDIR(a) ::mkdir((a),0755)
#define SOCKET_TYPE int
#else
#include <winsock2.h>
#include <stdio.h>
#include <windows.h>
#define MKDIR(a) ::mkdir((a)) 
#define SOCKET_TYPE SOCKET
//typedef int socklen_t; 
//typedef int ssize_t; 
#endif

#include "Singleton.h"

#include <stdint.h>
#include <list>
#include <fstream>
#include <string>
#include <map>
#include <time.h>

#define TYPEID(X)              singleton_t<ff::type_helper_t<X> >::instance().id()
#define TYPE_NAME(X)           singleton_t<ff::type_helper_t<X> >::instance().get_type_name()
#define TYPE_NAME_TO_ID(name_) singleton_t<ff::type_id_generator_t>::instance().get_id_by_name(name_)


namespace ff
{


    
struct type_id_generator_t
{
    type_id_generator_t():m_id(0){}
    int alloc_id(const std::string& name_)
    {
        //lock_guard_t lock(m_mutex);
        int id = ++ m_id;
        m_name2id[name_] = id;
        return id;
    }
    int get_id_by_name(const std::string& name_)
    {
        //lock_guard_t lock(m_mutex);
        std::map<std::string, int>::const_iterator it = m_name2id.find(name_);
        if (it != m_name2id.end())
        {
            return it->second;
        }
        return 0;
    }
    //mutex_t          m_mutex;
    int              m_id;
    std::map<std::string, int> m_name2id;
};

template<typename T>
struct type_helper_t
{
    type_helper_t():
        m_type_id(0)
    {
        std::string tmp  = __PRETTY_FUNCTION__;
        int pos     = tmp.find("type_helper_t() [with T = ");
        m_type_name = tmp.substr(pos + 26, tmp.size() - 26 - pos - 1);
        m_type_id   = singleton_t<type_id_generator_t>::instance().alloc_id(m_type_name);
    }
    int id() const
    {
        return m_type_id;
    }
    const std::string& get_type_name() const
    {
        return m_type_name;
    }
    int     m_type_id;
    std::string  m_type_name;
};

class BaseTypeInfo
{
public:
    virtual ~BaseTypeInfo(){}
    virtual int getTypeId() const = 0;
    virtual std::string getTypeName() const = 0;
    template<typename R>
    R* cast()
    {
        if (this->getTypeId() == TYPEID(R))
        {
            return (R*)this;
        }
        throw std::runtime_error("SafeTypeHelper cast failed");
        return NULL;
    }
};

class IgnoreSuperType{
public:
};
template<typename T, typename W>
class SafeTypeHelper:public W
{
public:
    virtual ~ SafeTypeHelper(){}
    virtual int getTypeId() const
    {
        return TYPEID(T);
    }
    virtual std::string getTypeName() const
    {
        return TYPE_NAME(T);
    }
    template<typename R>
    R* cast()
    {
        if (TYPEID(T) == TYPEID(R))
        {
            return (R*)this;
        }
        
        throw std::runtime_error("SafeTypeHelper cast failed");
        return NULL;
    }
};
struct SafeType{
   template<typename R>
    R* cast(BaseTypeInfo* p)
    {
        if (p && p->getTypeId() == TYPEID(R))
        {
            return (R*)this;
        }
        throw std::runtime_error("SafeTypeHelper cast failed");
        return NULL;
    }
};


class obj_counter_sum_i
{
public:
    obj_counter_sum_i():m_ref_count(0){}
    virtual ~ obj_counter_sum_i(){}
    void inc(int n = 1) { (void)__sync_add_and_fetch(&m_ref_count, n); }
    void dec(int n = 1) { __sync_sub_and_fetch(&m_ref_count, n); 	   }
    long val() const{ return m_ref_count; 						   }

    virtual const std::string& name() = 0;
protected:
    volatile long m_ref_count;
};


class obj_sum_mgr_t
{
public:
    void reg(obj_counter_sum_i* p)
    {
        //lock_guard_t lock(m_mutex);
        m_all_counter.push_back(p);
    }

    std::map<std::string, long> get_all_obj_num()
    {
        //lock_guard_t lock(m_mutex);
        std::map<std::string, long> ret;
        for (std::list<obj_counter_sum_i*>::iterator it = m_all_counter.begin(); it != m_all_counter.end(); ++it)
        {
            ret.insert(make_pair((*it)->name(), (*it)->val()));
        }
        return ret;
    }

    void dump(const std::string& path_)
    {
        FILE* fp = ::fopen(path_.c_str(), "a+");
        if (NULL == fp)
        {
            return;
        }
    
        char tmp_buff[256] = {0};
        if(getc(fp) == EOF)
        {           
            int n = snprintf(tmp_buff, sizeof(tmp_buff), "time,obj,num\n");
            ::fwrite(tmp_buff, n, 1, fp);
        }

        std::map<std::string, long> ret = get_all_obj_num();
        std::map<std::string, long>::iterator it = ret.begin();

        time_t timep   = ::time(NULL);
        struct tm *tmp = ::localtime(&timep);
        
        sprintf(tmp_buff, "%04d%02d%02d-%02d:%02d:%02d",
                        tmp->tm_year + 1900, tmp->tm_mon + 1, tmp->tm_mday,
                        tmp->tm_hour, tmp->tm_min, tmp->tm_sec);
        char buff[1024] = {0};

        for (; it != ret.end(); ++it)
        {
            int n = snprintf(buff, sizeof(buff), "%s,%s,%ld\n", tmp_buff, it->first.c_str(), it->second);
            fwrite(buff, n, 1, fp);
        }

        fclose(fp);
    }
protected:
    //mutex_t                     m_mutex;
    std::list<obj_counter_sum_i*>	m_all_counter;
};

template<typename T>
class obj_counter_sum_t: public obj_counter_sum_i
{
public:
    obj_counter_sum_t()
    {
        m_name = TYPE_NAME(T);
        singleton_t<obj_sum_mgr_t>::instance().reg(this);
    }
    virtual const std::string& name() { return m_name; }
protected:
    std::string m_name;
};

template<typename T>
class obj_counter_t
{
public:
    obj_counter_t()
    {
        singleton_t<obj_counter_sum_t<T> >::instance().inc(1);
    }
    ~obj_counter_t()
    {
        singleton_t<obj_counter_sum_t<T> >::instance().dec(1);
    }
};
}
#endif
