#ifndef _PYSMART_PTR_H_
#define _PYSMART_PTR_H_

#include <assert.h>
#include <stdexcept>
#include "RefCounter.h"
namespace ff {
//#define FF_ASSERT(X) if (!(X)) throw std::runtime_error("PySmartPtr NULL DATA")

template<typename T>
class PySmartPtr
{
public:
    typedef T                         object_t;
    typedef PySmartPtr<T>               self_type_t;
public:
    void FF_ASSERT(bool X) const{
        if (!(X)) {
            throw std::runtime_error("PySmartPtr NULL DATA");
        }
    }
    PySmartPtr();
    PySmartPtr(object_t* p);
    PySmartPtr(self_type_t& p);
    template<typename R>
    PySmartPtr(const PySmartPtr<R>& p):
        m_dest_ptr(p.get()),
        m_ref_data(p.ger_ref_count())
    {
        if (NULL != m_dest_ptr)
        {
            m_ref_data->m_ref_count.inc();
            m_ref_data->m_weak_ref_count.inc();
        }
    }
    PySmartPtr(object_t* p, RefCounterData* data_):
        m_dest_ptr(p),
        m_ref_data(data_)
    {
        if (NULL != m_dest_ptr)
        {
            //!外部已经累加过，无需重复累加
            m_ref_data->m_weak_ref_count.inc();
        }
    }

    virtual ~PySmartPtr();

    RefCounterData* ger_ref_count()  const  { return m_ref_data; }
    size_t       ref_count() const       { return m_ref_data != NULL? (size_t)m_ref_data->m_ref_count.value(): 0; }
    object_t*    get() const             { return m_dest_ptr; }
    void         reset();
    object_t&    operator*();
    object_t*    operator->();
    const object_t*    operator->() const;
    bool         operator==(const self_type_t& p);
    bool         operator==(const object_t* p);
    self_type_t& operator=(const self_type_t& src_);
    
    operator bool() const
    {
        return NULL != m_dest_ptr;
    }

    template<typename R>
    PySmartPtr<T>& operator=(const PySmartPtr<R>& p)
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
    template<typename R>
    const R* cast() const
    {
        return (R*)m_dest_ptr;
    }
private:
    object_t*         m_dest_ptr;
    RefCounterData*       m_ref_data;
};

template<typename T>
PySmartPtr<T>::PySmartPtr():
    m_dest_ptr(NULL),
    m_ref_data(NULL)
{
}

template<typename T>
PySmartPtr<T>::PySmartPtr(object_t* p):
    m_dest_ptr(p),
    m_ref_data(NULL)
{
    if (NULL != m_dest_ptr)
    {
        m_ref_data = p->getRefData();
        m_ref_data->m_ref_count.inc();
        m_ref_data->m_weak_ref_count.inc();
    }
}

template<typename T>
PySmartPtr<T>::PySmartPtr(self_type_t& p):
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
PySmartPtr<T>::~PySmartPtr()
{
    reset();
}

template<typename T>
void PySmartPtr<T>::reset()
{
    if (m_dest_ptr)
    {
        if (true == m_ref_data->m_ref_count.dec_and_check_zero())
        {
            //delete m_dest_ptr;
            m_dest_ptr->release();
            m_dest_ptr = NULL;
        }
        /*
        if (true == m_ref_data->m_weak_ref_count.dec_and_check_zero())
        {
            delete m_ref_data;
            m_ref_data = NULL;
        }*/
    }
}

template<typename T>
typename PySmartPtr<T>::object_t&    PySmartPtr<T>::operator*()
{
    FF_ASSERT(NULL != m_dest_ptr);
    return *m_dest_ptr;
}

template<typename T>
typename PySmartPtr<T>::object_t*    PySmartPtr<T>::operator->()
{
    FF_ASSERT(NULL != m_dest_ptr);
    return m_dest_ptr;
}
template<typename T>
const typename  PySmartPtr<T>::object_t*    PySmartPtr<T>::operator->() const
{
    FF_ASSERT(NULL != m_dest_ptr);
    return m_dest_ptr;
}

template<typename T>
bool PySmartPtr<T>::operator==(const self_type_t& p)
{
    return m_dest_ptr == p.get();
}

template<typename T>
bool PySmartPtr<T>::operator==(const object_t* p)
{
    return m_dest_ptr == p;
}

template<typename T>
typename PySmartPtr<T>::self_type_t& PySmartPtr<T>::operator=(const self_type_t& src_)
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
class PyWeakPtr
{
public:
    typedef T                         object_t;
    typedef PyWeakPtr<T>             self_type_t;
    typedef PySmartPtr<T>           shared_type_t;
public:
    PyWeakPtr():
        m_dest_ptr(NULL),
        m_ref_data(NULL)
    {
    }
    template<typename R>
    PyWeakPtr(const PySmartPtr<R>& p):
        m_dest_ptr(p.get()),
        m_ref_data(p.ger_ref_count())
    {
        if (NULL != m_ref_data)
        {
            m_ref_data->m_weak_ref_count.inc();
        }
    }
    PyWeakPtr(const self_type_t& p):
        m_dest_ptr(p.get()),
        m_ref_data(p.ger_ref_count())
    {
        if (NULL != m_ref_data)
        {
            m_ref_data->m_weak_ref_count.inc();
        }
    }

    virtual ~PyWeakPtr()
    {
        reset();
    }

    RefCounterData* ger_ref_count()  const  { return m_ref_data; }
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
    self_type_t& operator=(const PySmartPtr<R>& p)
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
    RefCounterData*       m_ref_data;
};
}

#endif
