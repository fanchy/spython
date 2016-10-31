# -*- coding: utf-8 -*-
import random
from base   import Base
from mapmgr import MapMgr
import msgtype.ttypes as MsgDef
import weakref
import ffext
import idtool
import random

def calMaxDistance(mon):
    return 5
class State(Base.BaseObj):
    def __init__(self):
        return
    def update(self, monster, nowMs):
        return True
    def onEnter(self, monster):
        return True
    def onExit(self, monster):
        return  True
    def onEvent(self, monster, event):
        return True
class StateIdle(State):
    def __init__(self):
        State.__init__(self)
        return
    def onEnter(self, monster):
        monster.nextMoveTm = ffext.getTimeMs() - 2000
        monster.lastAttackObjRef = None
        #ffext.dump('ai StateIdle enter', monster.name, monster.x, monster.y)
        return True
    def update(self, monster, nowMs):
        if monster.hp <= 0:
            monster.lastAttackObjRef = None
            if nowMs < monster.nextMoveTm + 10*1000:
                return True
            else:
                if nowMs -  monster.tmpInfo.get('_killedtm_', 0) <= 2000:#2秒内不要消失
                    return True
                #先从地图上消失.,再出现
                mapObj = monster.mapObj
                oldMon = mapObj.monsterLeaveMap(monster)
                #ffext.dump('monster leave map start reborn', monster.name)
                def reborn():
                    oldMon.hp = oldMon.hpMax
                    oldMon.x = oldMon.bornX
                    oldMon.y = oldMon.bornY
                    mapObj.monsterEnterMap(oldMon, oldMon.x, oldMon.y)
                if mapObj.copyMapHandler == None and oldMon.rebornSec > 0:
                    ffext.timer(1000*oldMon.rebornSec, reborn)
                #ffext.dump('monster reborn', monster.name)
                return True
        if nowMs < monster.nextMoveTm:
            if monster.lastAttackObjRef != None:
                targetObj = monster.lastAttackObjRef()
                if targetObj != None:#直接进入攻击模式
                    ffext.dump(monster.name, 'find target', targetObj.name)
                    monster.fsm.changeState(ffext.singleton(StateAttack))
            return True
        #回血
        if monster.hp < monster.hpMax:
            nowTm = ffext.getTime()
            nAddHP = int((nowTm - monster.lastRecoverHPTM) * monster.hpMax / 100)
            if nAddHP > 0:
                monster.addHPMsg(nAddHP)
        # 如果仇恨列表中有敌人在线，那么切换到战斗状态
        if monster.aiFlag == 0:#被动攻击
            if monster.lastAttackObjRef != None:
                targetObj = monster.lastAttackObjRef()
                if targetObj != None:#直接进入攻击模式
                    ffext.dump(monster.name, 'find target', targetObj.name)
                    monster.fsm.changeState(ffext.singleton(StateAttack))
            return True
        enemyObj =  monster.selectEnemy()
        if enemyObj:
            monster.fsm.changeState(ffext.singleton(StateAttack))
            return True
        #先朝一个方向走，走到头，再随机选一个方向
        curDir = monster.direction
        if Base.distance(monster.x, monster.y, monster.bornX, monster.bornY) >= monster.calMaxReachEnemyDistance():
            curDir = int((curDir + 4 ) % 8)
        desrDir= Base.MOVE_HELP_DIRECTION[curDir]
        curDir = desrDir[random.randint(0, len(desrDir) - 1)]
        monster.direction = curDir
        x, y   = Base.getPosByDirection(monster.x, monster.y, curDir)

        monster.nextMoveTm = nowMs + random.randint(5000, 10000)
        monster.mapObj.moveMonster(monster, x, y)
        return True
    def onEvent(self, monster, event):
        return True
#追击
def getNextPosTraceTaget(objSrc, objDest):
    distX = abs(objSrc.x - objDest.x)
    distY = abs(objSrc.y - objDest.y)
    if distX > distY:#先走x轴
        if objSrc.x < objDest.x:
            return (objSrc.x +1, objSrc.y, 2)
        else:
            return (objSrc.x  - 1, objSrc.y, 6)
    else:
        if objSrc.y < objDest.y:
            return (objSrc.x, objSrc.y + 1, 0)
        else:
            return (objSrc.x, objSrc.y - 1, 4)
def traceTarge(monster, destX, destY, dist = 0):
    srcX = monster.x
    srcY = monster.y
    destDirection = Base.getDirection(srcX, srcY, destX, destY)
    #ffext.dump('move traceTarge', monster.name, srcX, srcY, destX, destY, destDirection)
    selectList = Base.MOVE_HELP_DIRECTION[destDirection]
    for direction in selectList:
        len = 1
        if dist >= 5:
            len = 5
        elif dist  >= 3:
            dist = 2
        else:
            len = 1
        newX, newY = Base.getPosByDirection(srcX, srcY, direction, len)
        monster.direction = direction
        if True == monster.mapObj.moveMonster(monster, newX, newY):
            return True
        else:
            newX, newY = Base.getPosByDirection(srcX, srcY, direction, 1)
            if True == monster.mapObj.moveMonster(monster, newX, newY):
                return True
            else:
                ffext.dump('move failed', monster.name, srcX, srcY, newX, newY, direction)
    return False
class StateBackBornPoint(State):
    def __init__(self):
        State.__init__(self)
        return
    def onEnter(self, monster):
        monster.nextMoveTm = ffext.getTimeMs() - 2000
        monster.lastAttackObjRef = None
        ffext.dump('ai attack StateBackBornPoint enter', monster.name, monster.x, monster.y)
        return True
    def update(self, monster, nowMs):
        if monster.hp <= 0:
            monster.fsm.changeState(ffext.singleton(StateIdle))
            return True
        if monster.lastAttackObjRef != None:
            targetObj = monster.lastAttackObjRef()
            if targetObj != None:#直接进入攻击模式
                ffext.dump(monster.name, 'find target', targetObj.name)
                monster.fsm.changeState(ffext.singleton(StateAttack))
                return True
        if nowMs < monster.nextMoveTm:
            return True
        distance = Base.distance(monster.x, monster.y, monster.bornX,monster.bornY)
        if monster.x != monster.bornX or monster.y != monster.bornY:
            #ffext.dump('ai attack update mvoe begin', monster.bornX, monster.bornY, monster.name)
            if not traceTarge(monster, monster.bornX, monster.bornY, distance):
                ffext.dump('ai attack update mvoe failed', monster.bornX, monster.bornY, monster.name)
                return True
        else:
            monster.fsm.changeState(ffext.singleton(StateIdle))
        return True
    def onEvent(self, monster, event):
        return True
class StateAttack(State):
    def __init__(self):
        State.__init__(self)
        return
    def onEnter(self, monster):
        enemyObj =  monster.selectEnemy()
        if enemyObj:
            monster.objTarget = weakref.ref(enemyObj)
        ffext.dump('ai attack enter', monster.name, monster.x, monster.y)
        return True
    def update(self, monster, nowMs):
        #ffext.dump('ai attack update', monster.name, monster.x, monster.y, monster.direction)
        if monster.hp <= 0:
            monster.fsm.changeState(ffext.singleton(StateIdle))
            return True
        enemyObj = None
        if monster.objTarget != None:
            enemyObj = monster.objTarget()
        if not enemyObj or enemyObj.isDeath() or enemyObj.mapObj == None:
            monster.objTarget = None
            enemyObj =  monster.selectEnemy()
            if enemyObj:
                monster.objTarget = weakref.ref(enemyObj)
            else:
                ffext.dump('ai attack update exit1',  monster.name)
                monster.fsm.changeState(ffext.singleton(StateBackBornPoint))
                return
        elif nowMs - monster.lastSelectTargetMS >= 5*1000:
            monster.objTarget = None
            enemyObj =  monster.selectEnemy()
            if enemyObj:
                monster.objTarget = weakref.ref(enemyObj)
            else:
                ffext.dump('ai attack update exit2',  monster.name)
                monster.fsm.changeState(ffext.singleton(StateBackBornPoint))
                return
        #攻击目标
        distance = Base.distance(monster.x, monster.y, enemyObj.x,enemyObj.y)
        if distance > monster.attackDistance:
            boranDict = Base.distance(monster.x, monster.y, monster.bornX, monster.bornY)
            if boranDict > Base.ZHUJI_LEN:
                ffext.dump('ai attack changeto StateBackBornPoint',  monster.name)
                monster.fsm.changeState(ffext.singleton(StateBackBornPoint))
                return
            if not traceTarge(monster, enemyObj.x, enemyObj.y, distance):
                ffext.dump('ai attack update mvoe failed', distance, monster.name)
                return True
            return
            distance -= 1
        if distance > monster.attackDistance:
            #ffext.dump('ai attack update', distance,monster.attackDistance)
            return
        #释放技能
        monster.skillCtrl.autoUseSkill(enemyObj, nowMs)
        #ffext.dump('ai attack use skill', monster.name, monster.x, monster.y, monster.direction)
        return True
    def onEvent(self, monster, event):
        return True
class FSM(Base.BaseObj):
    def __init__(self, owner):
        self.owner = weakref.ref(owner)
        self.state= None
        self.lastUpdateMS = ffext.getTimeMs()
        return
    def update(self, owner, nowMs):
        if abs(nowMs - self.lastUpdateMS) < 1500:
            return
        self.lastUpdateMS = nowMs + random.randint(0, 100)
        if self.state:
            self.state.update(owner, nowMs)
        return True
    def changeState(self, state):
        owner = self.owner()
        if self.state:
            self.state.onExit(owner)
        self.state = state
        self.state.onEnter(owner)
        self.state.update(owner, ffext.getTimeMs())
        return True
    def onEvent(self, event):
        if self.state:
            return self.state.onEvent(self.owner(), event)