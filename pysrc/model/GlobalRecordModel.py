# -*- coding: utf-8 -*-
from msgtype import ttypes as MsgDef
import idtool
from db import DbServicePlayer as DbServicePlayer
from db import DbService
from base import Base
from model import RankModel
import ffext
import json
import weakref

SECONDS_PER_DAY = 86400
GLOBAL_RECORD_INDEX = 1

class CitWarInfo:
    def __init__(self):
        self.queue_guild = []
        self.master_guild = 0
        self.copyMap = None
        return

    def getFirstGuildPop(self):
        if len(self.queue_guild) <= 0:
            return -1
        topGuild = self.queue_guild[0]
        del self.queue_guild[0]
        return topGuild

    def isInCityWarQueue(self, guildId):
        return guildId in self.queue_guild

    def removeCityWarQueue(self, guildId):
        self.queue_guild.remove(guildId)

    def addCityWarQueue(self, guildid):
        self.queue_guild.append(guildid)

    def parseFrom(self, str):
        if not str or str == '':
            return False
        dataObj = json.loads(str)
        if not dataObj:
            return False
        dataObjQueue = dataObj.get('queue', [])
        for guildid in dataObjQueue:
            self.queue_guild.append(guildid)
            pass
        self.master_guild = dataObj.get('master', 0)
        return True

    def toString(self):
        ret = {
            'queue':    self.queue_guild,
            'master':   self.master_guild,
        }
        return json.dumps(ret, ensure_ascii=False)

class GlobalRecordMgr:
    def __init__(self):
        self.last_refresh_time = 0          # [DB]server_global.last_refresh_time
        self.citywar_info = CitWarInfo()    # [DB]server_global.citywar_info
        return

    def updateRefreshTime(self):
        self.last_refresh_time = ffext.getTime() + 1
        DbService.getPlayerService().updateGlobalOfRefreshTime(GLOBAL_RECORD_INDEX, self.last_refresh_time)
        return True

    def updateCityWarInfo(self):
        DbService.getPlayerService().updateGlobalOfCityWar(GLOBAL_RECORD_INDEX, self.citywar_info.toString())
        return True

    def checkOnInit(self):
        nowTime = ffext.getTime()
        nowTm = ffext.datetime_now()
        if self.last_refresh_time > 0:
            if ffext.tmIsSameDay(self.last_refresh_time, nowTime):
                #服务器重启时，跨越了凌晨
                self.onMiddleNightEvent()
                # 是否跨周
                if nowTm.weekday() == 0:
                    self.onWeeklyNightEvent()
                pass
        # 计算出到达午夜的时间，启动定时器
        secondUtilMiddleNight = SECONDS_PER_DAY - (nowTime % SECONDS_PER_DAY)
        ffext.timer(secondUtilMiddleNight * 1000, self.onMiddleNightEvent)
        # 计算到达下一个周（一）午夜的时间，启动定时器
        secondUtilNextWeek = secondUtilMiddleNight + (6 - nowTm.weekday()) * SECONDS_PER_DAY
        ffext.timer(secondUtilNextWeek * 1000, self.onWeeklyNightEvent)
        return

    def dailyRefresh4Session(self, session):
        if not session:
            return
        if not session.player:
            return
        session.player.dailyRefresh()
        return True

    def weeklyRefresh4Session(self, session):
        if not session:
            return
        if not session.player:
            return
        session.player.weeklyRefresh()
        return True

    def onMiddleNightEvent(self):
        ffext.dump("***************** New Day Process Begin ... ******************:", ffext.getTime())
        #添加每日凌晨更新时间到这里，依次处理
        self.updateRefreshTime()

        #每日排行榜刷新
        RankModel.getRankMgr().dailyRefresh()
        #所有在线玩家对象，每日refresh
        ffext.getSessionMgr().foreach(self.dailyRefresh4Session)

        ffext.dump("***************** New Day Process End ... ******************:", ffext.getTime())
        return True

    def onWeeklyNightEvent(self):
        ffext.dump("***************** New Week Process Begin ... ******************:", ffext.getTime())

        #所有在线玩家对象，每日refresh
        ffext.getSessionMgr().foreach(self.weeklyRefresh4Session)

        ffext.dump("***************** New Week Process End ... ******************:", ffext.getTime())
        return True

    def init(self):
        def cb(ret):
            if ret and ret.result:
                if len(ret.result) <= 0:
                    #原来没有记录，插入一条新的-cb判断缺失???
                    DbService.getPlayerService().addGlobalRecord(GLOBAL_RECORD_INDEX)
                    pass
                else:
                    dbRow = ret.result[0]
                    getGlobalRecordMgr().last_refresh_time = int(dbRow[1])
                    getGlobalRecordMgr().citywar_info.parseFrom(dbRow[2])
                    pass
            getGlobalRecordMgr().checkOnInit()
            return

        DbService.getPlayerService().loadGlobalRecord(GLOBAL_RECORD_INDEX, cb)
        return True

gGRMgr = GlobalRecordMgr()
def getGlobalRecordMgr():
    return gGRMgr

