# -*- coding: utf-8 -*-
import ffext

class idgen_t:
    def __init__(self, db_host_, type_id_ = 0, server_id_ = 0, processId = 0, dbflag = 1):
        self.type_id = type_id_
        self.server_id = server_id_#区组id
        self.proces_id = processId#进程ID
        self.auto_inc_id = 0
        self.db_host = db_host_
        self.db      = None
        self.saving_flag = False
        self.runing_flag = 0
        #有些id是临时的，不需要保存数据库，只需要每次启动归零
        self.db_flag = dbflag#0表示不需要保存

    def init(self):
        sql = '''create table IF NOT EXISTS idtool
(
  AUTO_INC_ID bigint not null default 0,
  RUNING_FLAG tinyint not null default 0,
  TYPE int not null default 0,
  SERVER_ID int not null default 0,
  PROCESS_ID int not null default 0,
  primary key(TYPE, SERVER_ID, PROCESS_ID)
);'''
        self.db = ffext.allocDbConnection('idtool', self.db_host)
        if None == self.db:
            print("coonnect db failed")
            return False
        ret = self.db.queryResult(sql)
        sql = "SELECT `AUTO_INC_ID`, `RUNING_FLAG` FROM `idtool` WHERE `TYPE` = '%d' AND `SERVER_ID` = '%d' AND `PROCESS_ID` = '%d' " % \
                                 (self.type_id, self.server_id, self.proces_id)
        ret = self.db.queryResult(sql)
        #print(ret.flag, ret.result, ret.column)
        if len(ret.result) == 0:
            #数据库中还没有这一行，插入
            if not self.db_flag:
                return True
            self.db.queryResult("INSERT INTO `idtool` SET `AUTO_INC_ID` = '0',`TYPE` = '%d', `SERVER_ID` = '%d', `RUNING_FLAG` = '1', `PROCESS_ID` = '%d' " % \
                                (self.type_id, self.server_id, self.proces_id))
            return True
        else:
            #print(sql, ret.result)
            self.auto_inc_id = int(ret.result[0][0])
            self.runing_flag = int(ret.result[0][1])
            if not self.db_flag:
                return True
            if self.runing_flag != 0:
                self.auto_inc_id += 100
                ffext.error('last idgen shut down not ok, inc 100')
            self.db.queryResult("UPDATE `idtool` SET `RUNING_FLAG` = '1' WHERE `TYPE` = '%d' AND `SERVER_ID` = '%d' and `PROCESS_ID` = '%d'" % (self.type_id, self.server_id, self.proces_id))
        #if self.auto_inc_id < 65535:
        #    self.auto_inc_id = 65535
        return True
    def cleanup(self):
        if not self.db_flag:
            return True
        now_val = self.auto_inc_id
        if  not self.db:
            return True
        sql = "UPDATE `idtool` SET `AUTO_INC_ID` = '%d', `RUNING_FLAG` = '0' WHERE `TYPE` = '%d' AND `SERVER_ID` = '%d' and `PROCESS_ID` = '%d'" \
              % (now_val, self.type_id, self.server_id, self.proces_id)
        self.db.queryResult(sql)
        #print('idtool cleanup ok', sql)
        return True
    def gen_id(self):
        self.auto_inc_id += 1
        self.update_id()
        low20 = self.auto_inc_id & 0xFFFFF#大于20位的移动到36位
        #进程id保留3位即可，最多8个场景
        low21_23 = self.proces_id << 20
        #type id 3位
        low24_26 = self.type_id  << 24
        #serverId 保留12位,即25-36
        low27_38 = (self.server_id << 27)
        high  = (self.auto_inc_id >> 20) << 38
        val   = high | low27_38 | low24_26 | low21_23 | low20
        return val
    def dump_id(self, id_):
        low16 = id_ & 0xFFFF
        high  = id_ >> 32
        return high << 16 | low16
    def update_id(self):
        #ffext.info('update_id ..............%d %d %d %d %d'% (self.type_id, self.server_id, self.proces_id,self.auto_inc_id, int(self.saving_flag)))
        if True == self.saving_flag:
            return
        self.saving_flag = True
        now_val = self.auto_inc_id
        def cb(ret):
            #print(ret.flag, ret.result, ret.column)
            self.saving_flag = False
            if now_val < self.auto_inc_id:
                self.update_id()
        sql = "UPDATE `idtool` SET `AUTO_INC_ID` = '%d' WHERE `TYPE` = '%d' AND `SERVER_ID` = '%d' AND `PROCESS_ID` = %d AND `AUTO_INC_ID` < '%d'" % (now_val, self.type_id, self.server_id, self.proces_id, now_val)
        # if ffext.WiNOS:
        #     ret = self.db.queryResult(sql)
        #     cb(ret)
        #     return
        #ffext.dump('update_id', sql)
        if self.db_flag:
            self.db.query(sql, cb)
        return

idtool = None
item_idtool = None
idTmpTool = None
uidtool   = None
def init(host_, server_id_ = 0, processId = 0):
    global idtool, item_idtool, idTmpTool, uidtool
    uidtool     = idgen_t(host_, 0, server_id_, 0xF)
    idtool      = idgen_t(host_, 0, server_id_, processId)
    item_idtool = idgen_t(host_, 1, server_id_, processId)
    idTmpTool   = idgen_t(host_, 2, server_id_, processId, 0)
    if False == uidtool.init():
        return  False
    if False == idtool.init():
        return False
    if False == item_idtool.init():
        return  False
    if False == idTmpTool.init():
        return False
    return True

def cleanup():
    global idtool, item_idtool, idTmpTool, uidtool
    if None != uidtool:
        uidtool.cleanup()
    if None != idtool:
        idtool.cleanup()
        idtool = None
    if None != item_idtool:
        item_idtool.cleanup()
        item_idtool = None
    if None != idTmpTool:
        idTmpTool.cleanup()
        idTmpTool = None
    return True

def allocUid():
    global uidtool
    return uidtool.gen_id()
def allocId():
    global idtool
    return idtool.gen_id()

def allocItemId():
    global item_idtool
    return item_idtool.gen_id()

def allocTmpId():
    global idTmpTool
    return idTmpTool.gen_id()