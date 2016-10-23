# -*- coding: utf-8 -*-
#此文件用于存放数据库连接初始化操作。并声明一个数据库连接函数getDB()，用于调用将数据库连接
#此文件最后将DbCreateSql中的数据表创建语句进行执行，将数据库中未执行的数据表进行创建
import ffext

gDB = None
def getDB():
    #声明一个全局变量gDb，用于存储数据库链接函数
    global gDB
    return gDB
gUserDb = []#用户专用DB，创建10个连接
def getUserDB(uid):
    global gUserDb
    return gUserDb[uid % len(gUserDb)]

gLogDB = None
def getLogDB():
    global gLogDB
    return gLogDB
gLogDBList = [] #记录日志专用
def getLogDB(id):
    global gLogDBList
    return gLogDBList[id % len(gLogDBList)]

class DbInitParam:
    def __init__(self):
        self.db_config          = ''
        self.db_conn_prefix     = 'db'
        self.db_sql             = 'db.sql'
        self.db_conn_pool_size  = 10

def initialize_db(firstList, dbList, dbParam):
    if not dbParam:
        return False
    print('initialize_db...... config:%s' % (dbParam.db_config))
    # 输出验证
    print('db_config=%s' % (dbParam.db_config))
    if not dbParam.db_conn_prefix or dbParam.db_conn_prefix == '':
        return False
    dbConn = ffext.allocDbConnection(dbParam.db_conn_prefix, dbParam.db_config)
    # 判断db是否赋值成功
    if None == dbConn:
        print('未获取到数据库链接语句.config:%s' % (dbParam.db_config))
        return False
    firstList.append(dbConn)

    # with open(dbParam.db_sql) as f:
        # sql = f.read()
        # sqlList = sql.split(';')
        # for k in sqlList:
            # if k.strip() == '':
                # continue
            # # print(k)
            # if dbConn.queryResult(k).hasError():
                # return False
    if dbParam.db_conn_pool_size <= 0:
        return False
    # 为玩家预先创建N 个连接
    for k in range(0, dbParam.db_conn_pool_size):
        tmpDB = ffext.allocDbConnection('%s#%d' % (dbParam.db_conn_prefix, k), dbParam.db_config)
        if None == tmpDB:
            return False
        dbList.append(tmpDB)

    return True

def init():
    global  gDB
    global gUserDb
    dbParam = DbInitParam()
    dbParam.db_config = ffext.getConfig('-db')
    dbParam.db_conn_prefix = 'db'
    dbParam.db_sql = 'db.sql'
    dbParam.db_conn_pool_size = 10

    firstList = []
    db_ret = initialize_db(firstList, gUserDb, dbParam)
    if db_ret == False:
        return False
    if len(firstList) == 0:
        return False
    gDB = firstList[0]

    global gLogDB
    global gLogDBList

    logDbParam = DbInitParam()
    logDbParam.db_config = ffext.getConfig('-log_db')
    logDbParam.db_conn_prefix = 'log_db'
    logDbParam.db_sql = 'game_log.sql'
    logDbParam.db_conn_pool_size = 5

    firstList2 = []
    db_ret = initialize_db(firstList2, gLogDBList, logDbParam)
    if db_ret == False:
        return False
    if len(firstList2) == 0:
        return False
    gLogDB = firstList2[0]

    return True

