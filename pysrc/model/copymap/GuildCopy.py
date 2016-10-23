# -*- coding: utf-8 -*-
import  weakref
import ffext
from base   import Base
from mapmgr import MapMgr
from model import MonsterModel
import msgtype.ttypes as MsgDef
LIMIT_SEC = 30
class GuildCopy(MapMgr.CopyMapHandler):
    def handleTimer(self, mapObj):
        #ffext.dump('CopyMapHandler handleTimer', mapObj.getPlayerNum())
        n = ffext.getTime()
        if n - self.createTime >= LIMIT_SEC:
            self.onEnd()
        return True
    def handleObjEnter(self, mapObj, obj):
        obj.sendMsg(MsgDef.ServerCmd.COPYMAP_START, MsgDef.CopymapStartRet(LIMIT_SEC, '这里是行会副本！'))
        ffext.dump('CopyMapHandler handleObjEnter', mapObj.getPlayerNum())
        return True
    def handleObjDie(self, mapObj, obj):
        #for k, v in mapObj.allPlayer.iteritems():
        #   v.sendMsg(MsgDef.ServerCmd.COPYMAP_END, MsgDef.CopymapEndRet(1, 10, 20, []))
            #v.taskCtrl.trigger(Base.Action.COPY_MAP, int(mapObj.mapname), 1)
        return True
    def onEnd(self):
        ffext.dump('CopyMapHandler onEnd', self.mapname)
        mapObj = MapMgr.getMapMgr().allocMap(self.mapname)
        ffext.dump('CopyMapHandler mapObj.allPlayer', mapObj.getPlayerNum())
        #for k, v in mapObj.allPlayer.iteritems():
        #    v.sendMsg(MsgDef.ServerCmd.COPYMAP_END, MsgDef.CopymapEndRet(0, 0, 0, []))
        MapMgr.getMapMgr().closeCopyMap(self.mapname, '10001', 74, 35)
        self.guildInfo.closeCopyMap()
    def __init__(self, guildInfo):
        MapMgr.CopyMapHandler.__init__(self, False)
        self.mapname = ''
        self.guildInfo = guildInfo
        return
def create(guildInfo, srcMap = '10002'):
    ffext.dump(__name__, srcMap)
    h = GuildCopy(guildInfo)
    mapObj = MapMgr.getMapMgr().createCopyMap(srcMap, h)
    h.mapname = mapObj.mapname
    
    return mapObj