# -*- coding: utf-8 -*-
import  weakref
import ffext
from base   import Base
from mapmgr import MapMgr
from model import MonsterModel
import msgtype.ttypes as MsgDef
LIMIT_SEC = 60
class TestCopy(MapMgr.CopyMapHandler):
    def handleTimer(self, mapObj):
        #ffext.dump('CopyMapHandler handleTimer', len(mapObj.allPlayer))
        n = ffext.getTime()
        if n - self.createTime >= LIMIT_SEC:
            self.onEnd()
        return True
    def handleObjEnter(self, mapObj, obj):
        obj.sendMsg(MsgDef.ServerCmd.COPYMAP_START, MsgDef.CopymapStartRet(LIMIT_SEC, '清怪'))
        ffext.dump('CopyMapHandler handleObjEnter', len(mapObj.allPlayer))
        return True
    def handleObjDie(self, mapObj, obj):
        for k, v in mapObj.allPlayer.iteritems():
            v.sendMsg(MsgDef.ServerCmd.COPYMAP_END, MsgDef.CopymapEndRet(1, 10, 20, []))
            v.taskCtrl.trigger(Base.Action.COPY_MAP, int(mapObj.mapname), 1)
        return True
    def onEnd(self):
        ffext.dump('CopyMapHandler onEnd', self.mapname)
        mapObj = MapMgr.getMapMgr().allocMap(self.mapname)
        ffext.dump('CopyMapHandler mapObj.allPlayer', len(mapObj.allPlayer))
        for k, v in mapObj.allPlayer.iteritems():
            v.sendMsg(MsgDef.ServerCmd.COPYMAP_END, MsgDef.CopymapEndRet(0, 0, 0, []))
        MapMgr.getMapMgr().closeCopyMap(self.mapname, '10001', 74, 35)
    def __init__(self):
        MapMgr.CopyMapHandler.__init__(self)
        self.mapname = ''
        return
def create(srcMap = '10002'):
    ffext.dump(__name__, srcMap)
    h = TestCopy()
    mapObj = MapMgr.getMapMgr().createCopyMap(srcMap, h)
    h.mapname = mapObj.mapname
    for k in MonsterModel.getMonsterMgr().mnstergen:
        MonsterModel.genMonster(mapObj.mapname, k[1], k[2], k[3], k[4], k[5], k[6])
        break
    return mapObj