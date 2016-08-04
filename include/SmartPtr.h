#ifndef _SMART_PTR_H_
#define _SMART_PTR_H_

#include <assert.h>
#include <stdexcept>

namespace ff {
#define FF_ASSERT(X) if (!(X)) throw std::runtime_error("SmartPtr NULL DATA")

#define ATOMIC_ADD(src_ptr, v)            (void)__sync_add_and_fetch(src_ptr, v)
#define ATOMIC_SUB_AND_FETCH(src_ptr, v)  __sync_sub_and_fetch(src_ptr, v)
#define ATOMIC_ADD_AND_FETCH(src_ptr, v)  __sync_add_and_fetch(src_ptr, v)
#define ATOMIC_FETCH(src_ptr)             __sync_add_and_fetch(src_ptr, 0)
#define ATOMIC_SET(src_ptr, v)            (void)__sync_bool_compare_and_swap(src_ptr, *(src_ptr), v)

class ref_count_t
{
    typedef  volatile long atomic_t;
public:
    ref_count_t():
        m_ref_num(0)
    {}
    ~ref_count_t()
    {}

    inline void inc(int n = 1)
    {
        ATOMIC_ADD(&m_ref_num, n);
    }
    inline bool dec_and_check_zero(int n = 1)
    {
        return 0 == ATOMIC_SUB_AND_FETCH(&m_ref_num, n);
    }
    inline atomic_t inc_and_fetch(int n = 1)
    {
        return ATOMIC_ADD_AND_FETCH(&m_ref_num, n);
    }
    inline atomic_t value()
    {
        return ATOMIC_FETCH(&m_ref_num);
    }

private:
    atomic_t m_ref_num;
};

struct ref_data_t
{
    ref_count_t      m_ref_count;
    ref_count_t      m_weak_ref_count;
    //spin_lock_t      m_mutex;
};

template<typename T>
class SmartPtr
{
public:
    typedef T                         object_t;
    typedef SmartPtr<T>           self_type_t;
public:
    SmartPtr();
    SmartPtr(object_t* p);
    SmartPtr(self_type_t& p);
    template<typename R>
    SmartPtr(const SmartPtr<R>& p):
        m_dest_ptr(p.get()),
        m_ref_data(p.ger_ref_count())
    {
        if (NULL != m_dest_ptr)
        {
            m_ref_data->m_ref_count.inc();
            m_ref_data->m_weak_ref_count.inc();
        }
    }
    SmartPtr(object_t* p, ref_data_t* data_):
        m_dest_ptr(p),
        m_ref_data(data_)
    {
        if (NULL != m_dest_ptr)
        {
            //!外部已经累加过，无需重复累加
            m_ref_data->m_weak_ref_count.inc();
        }
    }

    virtual ~SmartPtr();

    ref_data_t* ger_ref_count()  const  { return m_ref_data; }
    size_t       ref_count() const       { return m_ref_data != NULL? (size_t)m_ref_data->m_ref_count.value(): 0; }
    object_t*    get() const             { return m_dest_ptr; }
    void         reset();
    object_t&    operator*();
    object_t*    operator->();
    bool         operator==(const self_type_t& p);
    bool         operator==(const object_t* p);
    self_type_t& operator=(const self_type_t& src_);
    
    operator bool() const
    {
        return NULL != m_dest_ptr;
    }

    template<typename R>
    SmartPtr<T>& operator=(const SmartPtr<R>& p)
    {
        m_dest_ptr = p.get();
        m_ref_data(p.ger_ref_count());
        if (NULL != m_dest_ptr)
        {
            m_ref_data->m_ref_count.inc();
            m_ref_data->m_weak_ref_count.inc();
        }
        return *this;
    }
    
    template<typename R>
    R* cast()
    {
        return (R*)m_dest_ptr;
    }
private:
    object_t*         m_dest_ptr;
    ref_data_t*       m_ref_data;
};

template<typename T>
SmartPtr<T>::SmartPtr():
    m_dest_ptr(NULL),
    m_ref_data(NULL)
{
}

template<typename T>
SmartPtr<T>::SmartPtr(object_t* p):
    m_dest_ptr(p),
    m_ref_data(NULL)
{
    if (NULL != m_dest_ptr)
    {
        m_ref_data = new ref_data_t();
        m_ref_data->m_ref_count.inc();
        m_ref_data->m_weak_ref_count.inc();
    }
}

template<typename T>
SmartPtr<T>::SmartPtr(self_type_t& p):
    m_dest_ptr(p.get()),
    m_ref_data(p.ger_ref_count())
{
    if (NULL != m_dest_ptr)
    {
        m_ref_data->m_ref_count.inc();
        m_ref_data->m_weak_ref_count.inc();
    }
}

template<typename T>
SmartPtr<T>::~SmartPtr()
{
    reset();
}

template<typename T>
void SmartPtr<T>::reset()
{
    if (m_dest_ptr)
    {
        if (true == m_ref_data->m_ref_count.dec_and_check_zero())
        {
            delete m_dest_ptr;
            m_dest_ptr = NULL;
        }
        if (true == m_ref_data->m_weak_ref_count.dec_and_check_zero())
        {
            delete m_ref_data;
            m_ref_data = NULL;
        }
    }
}

template<typename T>
typename SmartPtr<T>::object_t&    SmartPtr<T>::operator*()
{
    FF_ASSERT(NULL != m_dest_ptr);
    return *m_dest_ptr;
}

template<typename T>
typename SmartPtr<T>::object_t*    SmartPtr<T>::operator->()
{
    FF_ASSERT(NULL != m_dest_ptr);
    return m_dest_ptr;
}

template<typename T>
bool SmartPtr<T>::operator==(const self_type_t& p)
{
    return m_dest_ptr == p.get();
}

template<typename T>
bool SmartPtr<T>::operator==(const object_t* p)
{
    return m_dest_ptr == p;
}

template<typename T>
typename SmartPtr<T>::self_type_t& SmartPtr<T>::operator=(const self_type_t& src_)
{
    if (&src_ == this)
    {
        return *this;
    }
    reset();
    m_dest_ptr = src_.get();
    m_ref_data = src_.ger_ref_count();
    if (NULL != m_dest_ptr)
    {
        m_ref_data->m_ref_count.inc();
        m_ref_data->m_weak_ref_count.inc();
    }
    return *this;
}


template<typename T>
class weak_ptr_t
{
public:
    typedef T                         object_t;
    typedef weak_ptr_t<T>             self_type_t;
    typedef SmartPtr<T>           shared_type_t;
public:
    weak_ptr_t():
        m_dest_ptr(NULL),
        m_ref_data(NULL)
    {
    }
    template<typename R>
    weak_ptr_t(const SmartPtr<R>& p):
        m_dest_ptr(p.get()),
        m_ref_data(p.ger_ref_count())
    {
        if (NULL != m_ref_data)
        {
            m_ref_data->m_weak_ref_count.inc();
        }
    }
    weak_ptr_t(const self_type_t& p):
        m_dest_ptr(p.get()),
        m_ref_data(p.ger_ref_count())
    {
        if (NULL != m_ref_data)
        {
            m_ref_data->m_weak_ref_count.inc();
        }
    }

    virtual ~weak_ptr_t()
    {
        reset();
    }

    ref_data_t* ger_ref_count()  const  { return m_ref_data; }
    object_t* get() const { return m_dest_ptr; }
    shared_type_t lock()
    {
        if (m_dest_ptr == NULL || m_ref_data == NULL)
        {
            return shared_type_t();
        }
        {
            //spin_lock_guard_t lock(m_ref_data->m_mutex);
            if (1 == m_ref_data->m_ref_count.inc_and_fetch(1))
            {
                //! 数据已经被销毁
                m_ref_data->m_ref_count.dec_and_check_zero();
                m_dest_ptr = NULL;
                return shared_type_t();
            }
        }
        //! 构造新的sharedptr
        return shared_type_t(m_dest_ptr, m_ref_data);
    }
    void reset()
    {
        if (m_ref_data)
        {
            if (true == m_ref_data->m_weak_ref_count.dec_and_check_zero())
            {
                delete m_ref_data;
                m_ref_data = NULL;
            }
        }
        m_dest_ptr = NULL;
    }
    
    template<typename R>
    self_type_t& operator=(const SmartPtr<R>& p)
    {
        reset();
        m_dest_ptr = p.get();
        m_ref_data = p.ger_ref_count();
        if (NULL != m_ref_data)
        {
            m_ref_data->m_weak_ref_count.inc();
        }
        return *this;
    }
    self_type_t& operator=(const self_type_t& p)
    {
        if (&p == this)
        {
            return *this;
        }
        reset();
        m_dest_ptr = p.get();
        m_ref_data = p.ger_ref_count();
        if (NULL != m_ref_data)
        {
            m_ref_data->m_weak_ref_count.inc();
        }
        return *this;
    }
    operator bool() const
    {
        return bool(lock());
    }

private:
    object_t*         m_dest_ptr;
    ref_data_t*       m_ref_data;
};
}

#endif
