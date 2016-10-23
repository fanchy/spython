# -*- coding: utf-8 -*-
import random
from base   import Base
from mapmgr import MapMgr
import msgtype.ttypes as MsgDef
from model.skill import SkillCalculatorBase
import ffext


calRealPhysicHurt = SkillCalculatorBase.calRealPhysicHurt
IGNORE_PHYSIC_DEFEND = SkillCalculatorBase.CalHurtFlag.IGNORE_PHYSIC_DEFEND
#普通攻击 对目标造成物理攻击105%的物理伤害
class PuGong(Base.HurtCalculator):
    def __init__(self, a = 105):
        Base.HurtCalculator.__init__(self, a)
    def exe(self, owner, skill, objDest, param):
        hurtResult = calRealPhysicHurt(owner, objDest, skill, self)
        objDest.subHurtResult(owner, hurtResult)
        return
#五箭连射-1 同时射出五只箭对目标造成110%的物理伤害，对目标周围的四个目标造成35%溅射伤害 420
class WuJianLianShe(PuGong):
    def __init__(self, a = 110, b = 4, c = 35):
        PuGong.__init__(self, a)
        self.paramPutong = a
        self.num = b
        self.paramJianshe = c
        pass
    def exe(self, owner, skill, objDest, param):
        self.paramHurt = self.paramPutong
        PuGong.exe(self, owner, skill, objDest, param)

        matchNum = 0
        def cb(obj):
            if obj == owner or objDest == obj:
                return
            if matchNum >= self.num:
                return
            PuGong.exe(owner, skill, objDest, param)
            matchNum = matchNum + 1

        owner.mapObj.foreachObjInRange(owner.x, owner.y, 10, cb)
        return
#虚弱之箭-1 对目标造成物理攻击75%的物理伤害，同时3秒内减速目标20%移动速度 430
class XuRuoZhiJian(PuGong):
    def __init__(self, a = 75, b = 3, c = 20):
        PuGong.__init__(self, a)
        self.slowSec = int(b)
        self.slowSpeed = c
        pass
    def exe(self, owner, skill, objDest, param):
        PuGong.exe(self, owner, skill, objDest, param)
        objDest.buffCtrl.addBuff(MsgDef.BuffType.JIAN_SU, self.slowSec, self.slowSpeed)
        return
#破甲之箭-1 对目标造成物理攻击120%的物理伤害，并无视目标的物理防御 440
class PoJiaZhiJian(Base.HurtCalculator):
    def __init__(self, a = 120):
        Base.HurtCalculator.__init__(self, a)
        pass
    def exe(self, owner, skill, objDest, param):
        hurtResult = calRealPhysicHurt(owner, objDest, skill, self, True, True, IGNORE_PHYSIC_DEFEND, 0.4)
        objDest.subHurtResult(owner, hurtResult)
        return
#三连激射-1 对目标造成3次50%物理伤害 450
class SanLianJiShe(PuGong):
    def __init__(self, a = 3, b = 50):
        Base.HurtCalculator.__init__(self, b)
        self.count = a
        pass
    def exe(self, owner, skill, objDest, param):
        PuGong.exe(self, owner, skill, objDest, param)
        def onTimer():
            PuGong.exe(self, owner, skill, objDest, param)
        ffext.timer(5*100, onTimer)
        return
#急速后撤-1 向后方倒退一定的距离，拉开与目标之间的距离 460
class JiSuHouChe(PuGong):
    def __init__(self):
        self.paramHoutui = 5
        pass
    def exe(self, owner, skill, objDest, param):
        oldX = objDest.x
        oldY = objDest.y
        directionTo = Base.getReverseDirection(owner.direction)
        for k in range(0, self.paramHoutui + 1 - 2):
            newX, newY = Base.getPosByDirection(oldX, oldY, directionTo, self.paramHoutui + 1 - k)
            if objDest.mapObj.canMove(newX, newY):
                objDest.mapObj.moveObj(objDest, newX, newY, False)
                ffext.dump('JiSuHouChe', oldX, oldY, newX, newY)
                break
        return


