# -*- coding: utf-8 -*-
from msgtype import ttypes as MsgDef
import idtool
from db import DbServicePlayer as DbServicePlayer
from db import DbService
from base import Base
import ffext
import json
import weakref

SECONDS_PER_MINUTE = 60
ONLINE_AWARD_CFG = [
    (30*60, ),
    (60*60, ),
    (90*60, ),
    (120*60, ),
    (180*60, ),
    (240*60, ),
    (360*60, ),
    (480*60, ),
]
class LoginActCtrl(Base.BaseObj):
    def __init__(self, owner):
        self._owner      = weakref.ref(owner)   # {Player}

        self.seven_login_days = 0       # 七日登录天数，0~28
        self.seven_login_mask = 0       # 七日登录奖励bit,低位开始，每28天重置
        self.online_reward_mask = 0     # 在线时长奖励bit，低位开始，每天重置
        self.invite_reward = 0          # 邀请奖励标记, 1:已领取，没有重置概念
        return

    @property
    def owner(self):
        return self._owner()

    def updateData(self):
        DbService.getPlayerService().updateDailyLoginAct(self.owner.session.user.accountid, self.seven_login_days \
                                                       , self.seven_login_mask, self.online_reward_mask, self.invite_reward)
        return True

    def fromData(self, result):
        ffext.dump("load db data to login-activity ...")
        # 从DB获取的数据初始化邮件
        if not result or len(result) <= 0:
            # 新增每日活动记录
            DbService.getPlayerService().createDailyLoginAct(self.owner.session.user.accountid)
            return False
        row = result[0]

        self.seven_login_days = int(row[1])
        self.seven_login_mask = int(row[2])
        self.online_reward_mask = int(row[3])
        self.invite_reward = int(row[4])

        return True
    def dailyRefresh(self):
        if self.seven_login_days < 7:
            self.seven_login_days += 1
        return
def parseRewardItemList(itemListStr):
    if itemListStr == '':
        return []
    ret = []
    args = itemListStr.split(';')
    for k in args:
        m = k.strip()
        if m != '':
            ret.append(int(m))
    return ret

# 七日登录奖励
class SevenLoginRewardCfg(Base.BaseObj):
    def __init__(self, id, loginDay, itemListStr, num, extra_itemListStr, extra_num):
        self.id           = id#唯一ID
        self.loginDay     = loginDay
        self.itemIdList   = parseRewardItemList(itemListStr)
        self.num          = num
        self.extra_itemIdList = parseRewardItemList(extra_itemListStr)
        self.extra_num    = extra_num

# 在线时长奖励
class OnlineRewardCfg(Base.BaseObj):
    def __init__(self, id, timeMin, itemListStr, num):
        self.id           = id#唯一ID
        self.timeSec      = timeMin * SECONDS_PER_MINUTE
        self.itemIdList   = parseRewardItemList(itemListStr)
        self.num          = num

# 好友邀请奖励
class InviteFriendRewardCfg(Base.BaseObj):
    def __init__(self, id, gold, itemListStr, num):
        self.id           = id#唯一ID
        self.gold         = gold
        self.itemIdList   = parseRewardItemList(itemListStr)
        self.num          = num

class LoginRewardMgr:
    def __init__(self):
        self.allSevenRewardCfg = {} #sevenId -> SevenLoginRewardCfg
        self.allLoginRewardCfg = {} #loginDay -> OnlineRewardCfg
        self.inviteRewardCfg = None #InviteFriendRewardCfg
        return

    def getSevenCfg(self, id):
        return self.allSevenRewardCfg.get(id)

    def getLoginCfg(self, id):
        return self.allLoginRewardCfg.get(id)

    def getInviteCfg(self):
        return self.inviteRewardCfg

    def sevenData2Cfg(self, row):
        id = int(row[0])
        loginDay = int(Base.parseStrBetween(row[1], '登录第', '天'))
        sevenCfg = SevenLoginRewardCfg(id, loginDay, row[2], int(row[3]), row[4], int(row[5]))
        ffext.dump(id, row[1], sevenCfg.loginDay)
        return sevenCfg

    def loginData2Cfg(self, row):
        id = int(row[0])
        timeMin = int(Base.parseStrBetween(row[1], '累计', '分钟'))
        loginCfg = OnlineRewardCfg(id, timeMin, row[2], int(row[3]))
        ffext.dump(id, row[1], loginCfg.timeSec)
        return loginCfg

    def inviteData2Cfg(self, row):
        id = int(row[0])
        inviteCfg = InviteFriendRewardCfg(id, int(row[2]), row[3], int(row[4]))
        ffext.dump(id, row[1], inviteCfg.gold)
        return inviteCfg

    #读取每日奖励配置
    def init(self):
        db = ffext.allocDbConnection('cfg',ffext.getConfig('-cfg'))

        #sample data => 1, '登录第1天', '1020102;1020101', 1, '', 0
        ret = db.queryResult('select id,desc,itemlist,num,extra_itemlist,extra_num from seven_login_reward')
        self.allSevenRewardCfg = {}
        for row in ret.result:
            sevenCfg = self.sevenData2Cfg(row)
            if sevenCfg:
                self.allSevenRewardCfg[sevenCfg.id] = sevenCfg
                pass
            pass

        #sample data => 1, '在线累计30分钟', '1020102;1020101', 1
        ret = db.queryResult('select id,desc,itemlist,num from online_reward')
        self.allLoginRewardCfg = {}
        for row in ret.result:
            loginCfg = self.loginData2Cfg(row)
            if loginCfg:
                self.allLoginRewardCfg[loginCfg.id] = loginCfg
                pass
            pass

        #sample data => 1, '邀请奖励金币', 500, '', 0
        ret = db.queryResult('select id,desc,gold,itemlist,num from invite_friend_reward limit 1')
        for row in ret.result:
            inviteCfg = self.inviteData2Cfg(row)
            if inviteCfg:
                self.inviteRewardCfg = inviteCfg
                break
            pass
        return True

gLRMgr = LoginRewardMgr()
def getLoginRewardMgr():
    return gLRMgr

