# -*- coding: utf-8 -*-
#本页面存放一个DbServiceLog类，日志保存操作接口

from db import DbServiceBase as DbServiceBase

USER_LOG_INDEX = 1
ITEM_LOG_INDEX = 2
MONEY_LOG_INDEX = 3
ACTION_LOG_INDEX = 4
GM_LOG_INDEX = 5

class BaseLogParam:
    def __init__(self, svr_id=0, acc_id=0, p_id=0, p_name='', op=0, subop=0, delta=0, res=0, ext1=0, ext2=0, ext3=0, ext4=0, ext5=0, param=''):
        self.server_id = svr_id
        self.account_id = acc_id
        self.player_id = p_id
        self.player_name = p_name
        self.op_type = op
        self.op_sub_type = subop
        self.delta = delta
        self.result_val = res
        self.ext1 = ext1
        self.ext2 = ext2
        self.ext3 = ext3
        self.ext4 = ext4
        self.ext5 = ext5
        self.param = param

class UserLogParam:
    def __init__(self, svr_id=0, acc_id=0, p_id=0, p_name='', op=0, reason=0, ip=0, x=0, y=0, param=''):
        self.server_id = svr_id
        self.account_id = acc_id
        self.player_id = p_id
        self.player_name = p_name
        self.op_type = op
        self.reason = reason
        self.from_ip = ip
        self.geo_x = x
        self.geo_y = y
        self.param = param

class ItemLogParam(BaseLogParam):
    def __init__(self, svr_id=0, acc_id=0, p_id=0, p_name='', op=0, subop=0, delta=0, res=0, ext1=0, ext2=0, ext3=0, ext4=0, ext5=0, param=''):
        BaseLogParam.__init__(self, svr_id, acc_id, p_id, p_name, op, subop, delta, res, ext1, ext2, ext3, ext4, ext5, param)

class MoneyLogParam(BaseLogParam):
    def __init__(self, svr_id=0, acc_id=0, p_id=0, p_name='', op=0, subop=0, delta=0, res=0, ext1=0, ext2=0, ext3=0, ext4=0, ext5=0, param=''):
        BaseLogParam.__init__(self, svr_id, acc_id, p_id, p_name, op, subop, delta, res, ext1, ext2, ext3, ext4, ext5, param)

class ActionLogParam(BaseLogParam):
    def __init__(self, svr_id=0, acc_id=0, p_id=0, p_name='', op=0, subop=0, delta=0, res=0, ext1=0, ext2=0, ext3=0, ext4=0, ext5=0, param=''):
        BaseLogParam.__init__(self, svr_id, acc_id, p_id, p_name, op, subop, delta, res, ext1, ext2, ext3, ext4, ext5, param)

class GmLogParam:
    def __init__(self, svr_id=0, gm_id=0, gm_name='', cmd=0, f_type=0, res=0, raw='', param=''):
        self.server_id = svr_id
        self.gm_user_id = gm_id
        self.gm_name = gm_name
        self.gm_cmd = cmd
        self.from_type = f_type
        self.result_val = res
        self.raw_input = raw
        self.param = param

class DbServiceLog:
    #user_log记录
    def addUserLog(self, userParam, callback=None):
        if not userParam:
            return
        try:
            sql = "INSERT INTO `user_log` (`server_id`,`account_id`,`player_id`,`player_name`,`op_type`,`reason`,`from_ip`,`geo_x`,`geo_y`,`param`) \
                  VALUES (%d, %d, %d, '%s', %d, %d, %d, %d, %d, '%s') " % \
                  (userParam.server_id, userParam.account_id, userParam.player_id, userParam.player_name, userParam.op_type, userParam.reason, \
                   userParam.from_ip, userParam.geo_x, userParam.geo_y, userParam.param)
            DbServiceBase.getLogDB(USER_LOG_INDEX).query(sql, callback)
        except:
            pass
        return

    #item_log记录
    def addItemLog(self, itemParam, callback):
        if not itemParam:
            return
        sql = "INSERT INTO `item_log` (`server_id`,`account_id`,`player_id`,`player_name`,`op_type`,`op_sub_type`,`delta`, \
               `result_val`,`ext1`,`ext2`,`ext3`,`ext4`,`ext5`,`param`) \
              VALUES (%d, %d, %d, '%s', %d, %d, %d, %d, %d, %d, %d, %d, %d, '%s') " % \
              (itemParam.server_id, itemParam.account_id, itemParam.player_id, itemParam.player_name, \
               itemParam.op_type, itemParam.op_sub_type, itemParam.delta, itemParam.result_val, itemParam.ext1, \
               itemParam.ext2, itemParam.ext3, itemParam.ext4, itemParam.ext5, itemParam.param)
        DbServiceBase.getLogDB(ITEM_LOG_INDEX).query(sql, callback)
        return

    #money_log记录
    def addMoneyLog(self, moneyParam, callback):
        if moneyParam:
            return
        sql = "INSERT INTO `money_log` (`server_id`,`account_id`,`player_id`,`player_name`,`op_type`,`op_sub_type`,`delta`, \
               `result_val`,`ext1`,`ext2`,`ext3`,`ext4`,`ext5`,`param`) \
              VALUES (%d, %d, %d, '%s', %d, %d, %d, %d, %d, %d, %d, %d, %d, '%s') " % \
              (moneyParam.server_id, moneyParam.account_id, moneyParam.player_id, moneyParam.player_name, \
               moneyParam.op_type, moneyParam.op_sub_type, moneyParam.delta, moneyParam.result_val, moneyParam.ext1, \
               moneyParam.ext2, moneyParam.ext3, moneyParam.ext4, moneyParam.ext5, moneyParam.param)
        DbServiceBase.getLogDB(MONEY_LOG_INDEX).query(sql, callback)
        return

    #action_log记录
    def addActionLog(self, actionParam, callback):
        if not actionParam:
            return
        sql = "INSERT INTO `action_log` (`server_id`,`account_id`,`player_id`,`player_name`,`op_type`,`op_sub_type`,`delta`, \
               `result_val`,`ext1`,`ext2`,`ext3`,`ext4`,`ext5`,`param`) \
              VALUES (%d, %d, %d, '%s', %d, %d, %d, %d, %d, %d, %d, %d, %d, '%s') " % \
              (actionParam.server_id, actionParam.account_id, actionParam.player_id, actionParam.player_name, \
               actionParam.op_type, actionParam.op_sub_type, actionParam.delta, actionParam.result_val, actionParam.ext1, \
               actionParam.ext2, actionParam.ext3, actionParam.ext4, actionParam.ext5, actionParam.param)
        DbServiceBase.getLogDB(ACTION_LOG_INDEX).query(sql, callback)
        return

    #gm_log记录
    def addGmLog(self, gmParam, callback):
        if not gmParam:
            return
        sql = "INSERT INTO `gm_log` (`server_id`,`gm_user_id`,`gm_name`,`gm_cmd`,`from_type`,`result_val`,`raw_input`,`param`) \
              VALUES (%d, %d, '%s', %d, %d, %d, '%s', '%s') " % \
              (gmParam.server_id, gmParam.gm_user_id, gmParam.gm_name, gmParam.gm_cmd, gmParam.from_type, gmParam.result_val, \
               gmParam.raw_input, gmParam.param)
        DbServiceBase.getLogDB(GM_LOG_INDEX).query(sql, callback)
        return

