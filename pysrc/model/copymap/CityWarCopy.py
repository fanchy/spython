# -*- coding: utf-8 -*-
import weakref
import ffext
from base import Base
from mapmgr import MapMgr
from model import MonsterModel, GlobalRecordModel
import msgtype.ttypes as MsgDef
import weakref

CITYWAR_LIMIT_SEC = 120 * 60    # 持续2个小时

# 城战地图id（洛阳）
CITYWAR_MAP_ID = '10002'
# 城战争夺雕像id
CITYWAR_STATUE_ID = 101#19527
CITYWAR_STATUE_X = 14
CITYWAR_STATUE_Y = 50

ATK_REBORN_X = 33
ATK_REBORN_Y = 253
DEF_REBORN_X = 318
DEF_REBORN_Y = 110

class CityWarCopy(MapMgr.CopyMapHandler):
    def handleTimer(self, mapObj):
        #ffext.dump('CityWarCopy handleTimer', mapObj.getPlayerNum())
        n = ffext.getTime()
        if n - self.createTime >= CITYWAR_LIMIT_SEC:
            self.onEnd(mapObj)
        return True

    def handleObjEnter(self, mapObj, obj):
        # obj.sendMsg(MsgDef.ServerCmd.COPYMAP_START, MsgDef.CopymapStartRet(CITYWAR_LIMIT_SEC, '这里是城战副本！'))
        ffext.dump('CityWarCopy handleObjEnter', mapObj.getPlayerNum())
        return True

    def handleObjDie(self, mapObj, obj):
        if obj.getType() == Base.MONSTER and obj.cfgId == CITYWAR_STATUE_ID:
            return self._onSuccess(mapObj, obj)
        return True

    def handlePlayerRevive(self, mapObj, obj):
        # 玩家复活逻辑设定（攻守复活坐标不同）
        if not mapObj:
            return False
        if obj.getType() != Base.PLAYER:
            return False
        if obj and obj.guildCtrl.guildInfo:
            if obj.guildCtrl.guildInfo.guildID == self.attackGuild.guildID:
                mapObj.movePlayer(obj, ATK_REBORN_X, ATK_REBORN_Y)
            elif self.defendGuild and obj.guildCtrl.guildInfo.guildID == self.defendGuild.guildID:
                mapObj.movePlayer(obj, DEF_REBORN_X, DEF_REBORN_Y)
        return True

    def onStart(self, mapObj):
        if not mapObj:
            return False
        # 1. 清理战场先（以防万一）
        if self.statueMonster:
            MonsterModel.destroyMonster(self.statueMonster)
            self.statueMonster = None
        # 2. spawn雕像
        retMon = MonsterModel.genMonsterById(mapObj.mapname, CITYWAR_STATUE_ID, CITYWAR_STATUE_X, CITYWAR_STATUE_Y, 1, 2)
        if len(retMon) >= 1:
            self.statueMonster = retMon[0]
        # 3. 通知双方行会
        inform_msg = MsgDef.GuildCityWarOpsMsgRet()
        inform_msg.opstype = MsgDef.GuildCityWarOpsCmd.CITYWAR_START
        inform_msg.tmStart = ffext.getTime()
        self.startTime = ffext.getTime()
        self.attackGuild.sendMsg2OnlineMember(MsgDef.ServerCmd.GUILD_CITYWAR_MSG, inform_msg)
        if self.defendGuild:
            self.defendGuild.sendMsg2OnlineMember(MsgDef.ServerCmd.GUILD_CITYWAR_MSG, inform_msg)
        # 4. 通知全服？
        return True

    def onEnd(self, mapObj):
        ffext.dump('CityWarCopy onEnd', self.mapname)
        if not mapObj:
            return
        #mapObj = MapMgr.getMapMgr().allocMap(self.mapname)
        ffext.dump('CityWarCopy mapObj.allPlayer', mapObj.getPlayerNum())
        # 1. 清理战场先（以防万一）
        if self.statueMonster:
            MonsterModel.destroyMonster(self.statueMonster)
            self.statueMonster = None
        # 2. 失败处理
        self._onFail(mapObj)

    def _onSuccess(self, mapObj, obj):
        citywar_info = GlobalRecordModel.getGlobalRecordMgr().citywar_info
        # 设置胜利行会为皇城主
        citywar_info.master_guild = self.attackGuild.guildID

        ret_msg = self.guildMgr().buildCityWarRetMsg(MsgDef.GuildCityWarOpsCmd.CITYWAR_END, 1, self.startTime, True, False)
        self.attackGuild.sendMsg2OnlineMember(MsgDef.ServerCmd.GUILD_CITYWAR_MSG, ret_msg)
        if self.defendGuild:
            self.defendGuild.sendMsg2OnlineMember(MsgDef.ServerCmd.GUILD_CITYWAR_MSG, ret_msg)
        # 通知全服？

        self._doClear()
        return True

    def _onFail(self, mapObj):
        if not self.attackGuild:
            return True
        ret_msg = self.guildMgr().buildCityWarRetMsg(MsgDef.GuildCityWarOpsCmd.CITYWAR_END, -1, self.startTime, True, False)
        self.attackGuild.sendMsg2OnlineMember(MsgDef.ServerCmd.GUILD_CITYWAR_MSG, ret_msg)
        if self.defendGuild:
            self.defendGuild.sendMsg2OnlineMember(MsgDef.ServerCmd.GUILD_CITYWAR_MSG, ret_msg)
        # 通知全服？

        self._doClear()
        return True

    def _doClear(self):
        # 释放副本，直接全部传出
        MapMgr.getMapMgr().closeCopyMap(self.mapname, '10001', 74, 35)
        self.attackGuild = None
        self.defendGuild = None
        self.statueMonster = None
        self.startTime = 0

    def __init__(self, attackGuild, defendGuild, mgr):
        MapMgr.CopyMapHandler.__init__(self, False)
        self.mapname = '洛阳'
        self.attackGuild = attackGuild
        self.defendGuild = defendGuild
        self.guildMgr = weakref.ref(mgr)
        self.statueMonster = None
        self.startTime = 0
        return

# 暂定地图id（10003）
def create(attackGuild, defendGuild, mgr, srcMap=CITYWAR_MAP_ID):
    ffext.dump(__name__, srcMap)
    h = CityWarCopy(attackGuild, defendGuild, mgr)
    mapObj = MapMgr.getMapMgr().createCopyMap(srcMap, h)
    h.mapname = mapObj.mapname

    return mapObj