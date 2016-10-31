# -*- coding: utf-8 -*-
import random
from base   import Base
from mapmgr import MapMgr
import msgtype.ttypes as MsgDef
from db import DbService
from model.copymap import ArenaCopy
from model.monster import MonsterAI
from db import DbService
import  weakref
import ffext
import  json


def arenaTraceTarge(monster, destX, destY, dist = 0):
    srcX = monster.x
    srcY = monster.y
    destDirection = Base.getDirection(srcX, srcY, destX, destY)
    selectList = Base.MOVE_HELP_DIRECTION[destDirection]
    for direction in selectList:
        len = 1
        if dist >= 5:
            len = 3
        elif dist  >= 3:
            dist = 2
        else:
            len = 1
        newX, newY = Base.getPosByDirection(srcX, srcY, direction, len)
        ffext.dump('move ', monster.name, srcX, srcY, newX, newY, direction)
        bFlag = monster.mapObj.canMove(newX, newY)
        if bFlag and True == monster.mapObj.movePlayer(monster, newX, newY):
            ffext.dump('move 1', monster.name, srcX, srcY, monster.x, monster.y, direction)
            return True
        else:
            ffext.dump('move 2', monster.name, srcX, srcY, newX, newY, direction)
            newX, newY = Base.getPosByDirection(srcX, srcY, direction, 1)
            bFlag = monster.mapObj.canMove(newX, newY)
            if bFlag and True == monster.mapObj.movePlayer(monster, newX, newY):
                return True
            else:
                ffext.dump('move failed', monster.name, srcX, srcY, newX, newY, direction)
        
    return False
class ArenaStateAttack(MonsterAI.State):
    def __init__(self):
        MonsterAI.State.__init__(self)
        return
    def onEnter(self, owner):
        return True
        ffext.dump('ai attack enter', owner.name, owner.x, owner.y)
    def update(self, owner, nowMs):
        ffext.dump('ai attack update', owner.name, owner.x, owner.y, owner.hp)
        if owner.hp <= 0:
            return True
        enemyObj = owner.arenaCtrl.destPlayerRef()
        if not enemyObj or enemyObj.isDeath() or enemyObj.mapObj == None:
            return True
        
        #攻击目标
        distance = Base.distance(owner.x, owner.y, enemyObj.x,enemyObj.y)
        if distance > owner.attackDistance:
            if not arenaTraceTarge(owner, enemyObj.x, enemyObj.y, distance):
                ffext.dump('ai attack update mvoe failed', distance, owner.name)
                return True
            ffext.dump('ai arenaTraceTarge', owner.name, owner.x, owner.y)
            return
            distance -= 1
        if distance > owner.attackDistance:
            #ffext.dump('ai attack update', distance,owner.attackDistance)
            return True
        #释放技能
        owner.skillCtrl.autoUseSkill(enemyObj, nowMs)
        ffext.dump('ai attack use skill', owner.name, owner.x, owner.y)
        return True
    def onEvent(self, owner, event):
        return True

class ArenaMgr:
    def __init__(self):
        self.allRank = []
        return
    def getRankByUid(self, uid):
        for i in range(0, len(self.allRank)):
            k = self.allRank[i]
            if k.uid == uid:
                return i + 1
        return 0

    def init(self):
        def cb(ret):
            self.allRank = []
            i = 0
            for row in ret.result:
                i += 1
                #sql = "select uid,name,job,gender,level,fightpower,arenascore from player where arenascore > 0 order by arenascore desc limit 1000 "
                tmpMsg = MsgDef.ArenaPlayerData(long(row[0]), row[1], int(row[2]), int(row[3]), int(row[4]), int(row[5]), i, int(row[6]))
                self.allRank.append(tmpMsg)
            return
        DbService.getPlayerService().loadArenaRankInfo(0, 1000, cb)
        def cbTimer():
            #print('load arena data')
            DbService.getPlayerService().loadArenaRankInfo(0, 1000, cb)
            ffext.timer(10 * 1000, cbTimer)
        ffext.timer(10*1000, cbTimer)
        return True
    def createArena(self, playerSrc, destUid):
        playerSrc.arenaCtrl.usedTimes += 1
        from model import PlayerModel
        mapObj = ArenaCopy.create()
        playerSrc.direction = Base.Direction.LEFT
        mapObj.playerEnterMap(playerSrc, 77, 70)
        def cb(dbSet):
            db = dbSet['player']
            dbitem = dbSet['item']
            dbPet = dbSet['pet']
            session = ffext.SessionNone()
            player = PlayerModel.Player(db.result[0])
            session.setPlayer(player)
            player.session = session
            if dbitem.isOk():
                player.itemCtrl.fromData(dbitem.result)
            player.petCtrl.fromData(dbPet.result)
            player.direction = Base.Direction.RIGHT
            player.arenaCtrl.destPlayerRef = weakref.ref(playerSrc)
            #状态机
            player.fsm       = MonsterAI.FSM(player)
            def goTo():
                mapObj.copyMapHandler.autoPlayerRef = weakref.ref(player)
                mapObj.playerEnterMap(player, 69, 72)
                player.fsm.changeState(ffext.singleton(ArenaStateAttack))
            ffext.timer(1000, goTo)
            return
        DbService.getPlayerService().loadPlayer(destUid, 0, cb, True)
    
gMgr = ArenaMgr()
def getArenaMgr():
    return gMgr