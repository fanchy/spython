# -*- coding: utf-8 -*-
import  weakref
import ffext
from base   import Base
from mapmgr import MapMgr
from model import MonsterModel
import msgtype.ttypes as MsgDef
LIMIT_SEC = 60*5
AWARD_EXP = 10
GOLD_ADD  = 0

SCORE_CFG = [
    [1,1,	1000      ],
    [2,2,	700       ],
    [3,3,	500       ],
    [4,5,	400       ],
    [6,10	,320      ],
    [11,20	,260      ],
    [21,50	,240      ],
    [51,100	,200      ],
    [101,200	,160  ],
    [201,500	,130  ],
    [501,800	,100  ],
    [801,1000	,50   ],
    [1001,2000	,30   ],
    [2001,999999	,0]
]
def getScoreBytimes(times):
    for k in SCORE_CFG:
        if times >= k[0] and times <= k[1]:
            return k[2]
    return 0
class ArenaCopy(MapMgr.CopyMapHandler):
    def handleTimer(self, mapObj):
        #ffext.dump('CopyMapHandler handleTimer', len(mapObj.allPlayer))
        n = ffext.getTime()
        if n - self.createTime >= LIMIT_SEC:
            self.onEnd()
        if self.autoPlayerRef != None:
            player = self.autoPlayerRef()
            if player and player.mapObj:
                nowMs = ffext.getTimeMs()
                player.fsm.update(player, nowMs)
            else:
                self.autoPlayerRef = None
        return True
    def handleObjEnter(self, mapObj, obj):
        obj.sendMsg(MsgDef.ServerCmd.COPYMAP_START, MsgDef.CopymapStartRet(LIMIT_SEC, '决出胜负'))
        ffext.dump('CopyMapHandler handleObjEnter', len(mapObj.allPlayer))
        return True
    def handleObjDie(self, mapObj, obj):
        playerOther = None
        bWin = True
        if self.autoPlayerRef != None:
            playerOther = self.autoPlayerRef()
            def cb():
                playerOther.mapObj.playerLeaveMap(playerOther)
            if playerOther:
                ffext.timer(100, cb)
                if obj.uid != playerOther.uid:
                    bWin = False
            self.autoPlayerRef =None
        #self.onEnd()

        for k, v in mapObj.allPlayer.iteritems():
            if v.uid != playerOther.uid:
                v.sendMsg(MsgDef.ServerCmd.COPYMAP_END, MsgDef.CopymapEndRet(1, AWARD_EXP, GOLD_ADD, []))
                v.AddScoreArena(getScoreBytimes(v.arenaCtrl.usedTimes))
                #v.taskCtrl.trigger(Base.Action.COPY_MAP, int(mapObj.mapname), 1)
        #5秒后关闭副本
        self.createTime = ffext.getTime() + 5 - LIMIT_SEC
        return True
    def onEnd(self):
        ffext.dump('CopyMapHandler onEnd', self.mapname)
        mapObj = MapMgr.getMapMgr().allocMap(self.mapname)
        ffext.dump('CopyMapHandler mapObj.allPlayer', len(mapObj.allPlayer))
        for k, v in mapObj.allPlayer.iteritems():
            v.sendMsg(MsgDef.ServerCmd.COPYMAP_END, MsgDef.CopymapEndRet(0, 0, 0, []))
        MapMgr.getMapMgr().closeCopyMap(self.mapname, '10001', 47, 171)
    def __init__(self):
        MapMgr.CopyMapHandler.__init__(self)
        self.mapname = ''
        self.autoPlayerRef = None
        return
def create(srcMap = '10002'):
    ffext.dump(__name__, srcMap)
    h = ArenaCopy()
    mapObj = MapMgr.getMapMgr().createCopyMap(srcMap, h)
    h.mapname = mapObj.mapname
    
    return mapObj