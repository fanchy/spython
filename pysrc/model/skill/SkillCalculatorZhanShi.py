# -*- coding: utf-8 -*-
import random
from base   import Base
from mapmgr import MapMgr
import msgtype.ttypes as MsgDef
from model.skill import SkillCalculatorBase
import ffext

calRealPhysicHurt = SkillCalculatorBase.calRealPhysicHurt
IGNORE_PHYSIC_DEFEND = SkillCalculatorBase.CalHurtFlag.IGNORE_PHYSIC_DEFEND
IGNORE_MAGIC_SHIELD = SkillCalculatorBase.CalHurtFlag.IGNORE_MAGIC_SHIELD
#普通攻击 对目标造成物理攻击100%的物理伤害
class PuGong(Base.HurtCalculator):
    def __init__(self, a = 100):
        Base.HurtCalculator.__init__(self, a)
    def exe(self, owner, skill, objDest, param):
        hurtResult = calRealPhysicHurt(owner, objDest, skill, self)
        objDest.subHurtResult(owner, hurtResult)
        return
#穿刺枪术-1 对目标造成物理攻击110%，并且无视对主防御力
class ChuanQiangCiShu(Base.HurtCalculator):
    def __init__(self, a = 100):
        Base.HurtCalculator.__init__(self, a)
    def exe(self, owner, skill, objDest, param):
        hurtResult = calRealPhysicHurt(owner, objDest, skill, self, True, True, IGNORE_MAGIC_SHIELD, 1)
        hurtResult.hurtFlag = IGNORE_MAGIC_SHIELD
        objDest.subHurtResult(owner, hurtResult)
        return
#横扫千军-1 对目标造成110%物理伤害，周围单位受到溅射造成40%物理伤害
class HengSaoQianJun(PuGong):
    def __init__(self, a = 100, b = 40):
        PuGong.__init__(self, a)
        self.paramPuTong  = a
        self.paramJianShe = b
    def exe(self, owner, skill, objDest, param):
        self.paramHurt = self.paramPuTong
        PuGong.exe(self, owner, skill, objDest, param)
        self.paramHurt = self.paramJianShe
        def cb(obj):
            if obj == owner or objDest == obj:
                return
            PuGong.exe(self, owner, skill, objDest, param)
        owner.mapObj.foreachObjInRange(owner.x, owner.y, 10, cb)
        return
#冲锋陷阵-1	用力冲向目标将敌人撞晕，造成100%物理伤害，同时让目标退后数米远，眩晕0.3秒
class ChongFengXianZhen(PuGong):
    def __init__(self, a = 100, b = 2, c = 0.3):
        PuGong.__init__(self, a)
        self.paramJiTui  = b
        self.paramXuanYun= c
    def exe(self, owner, skill, objDest, param):
        PuGong.exe(self, owner, skill, objDest, param)
        oldX = objDest.x
        oldY = objDest.y
        for k in range(0, self.paramJiTui+1 - 2):
            newX, newY = Base.getPosByDirection(oldX, oldY, owner.direction, self.paramJiTui+1 - k)
            if objDest.mapObj.canMove(newX, newY):
                objDest.mapObj.moveObj(objDest, newX, newY, False)
                ffext.dump('ChongFengXianZhen', oldX, oldY, newX, newY)
                break

        objDest.buffCtrl.addBuff(MsgDef.BuffType.XUAN_YUN, 3)#TODO 为了展示效果暂时设置3秒
        objDest.updateBuffMsg()
        return
#151	暴怒一击-2	对目标造成200%物理伤害 就是普通物理攻击 PuGong
#160	银龙呼啸-1	攻击范围三格，对直线上的三个目标造成140%，120%，100%的物理伤害
class YinLongHuXiao(PuGong):
    def __init__(self, a = 140, b = 120, c = 100):
        PuGong.__init__(self, a)
        self.paramList = [a, b, c]
    def exe(self, owner, skill, objDest, param):
        oldX = owner.x
        oldY = owner.y
        allHurtList = []
        for k in range(1, 10):
            newX, newY = Base.getPosByDirection(oldX, oldY, owner.direction, k)
            if objDest.mapObj.canMove(newX, newY):
                obj = objDest.mapObj.getAliveObjByPos(newX, newY)
                if obj and obj not in allHurtList:
                    allHurtList.append(obj)
                if len(allHurtList) >= 3:
                    break
        for k in range(0, len(allHurtList)):
            self.paramHurt = self.paramList[k]
            obj = allHurtList[k]
            PuGong.exe(self, owner, skill, obj, param)
            ffext.dump('YinLongHuXiao', obj.name, obj.x, obj.y)
        return
# 1001 战士无双 - 无人能挡 对自身周围敌人造成物理攻击250 % 的物理伤害，同时敌人眩晕1秒
class WuShuangWuRenNengDang(PuGong):
    def __init__(self, a = 250, b = 1):
        PuGong.__init__(self, a)
        self.paramXuanYun= b
    def exe(self, owner, skill, objDest, param):
        def cb(objDest):
            if objDest != owner:
                PuGong.exe(self, owner, skill, objDest, param)
                objDest.buffCtrl.addBuff(MsgDef.BuffType.XUAN_YUN, 3, 0, Base.WUSHUANG_SKILL_ID)  # TODO 为了展示效果暂时设置3秒
                objDest.updateBuffMsg()
        owner.mapObj.foreachObjInRange(owner.x, owner.y, 5, cb)  # todo 距离

        return


# 2001	结义技能	当结义队友在场时，释放技能后，60秒内结义队友全部增加10%物理和魔法攻击力
class JieYi(PuGong):#结义技能
    def __init__(self, a=60, b=10):
        PuGong.__init__(self)
        self.paramTotalSec = a
        self.paramDefendAdd = b
    def exe(self, owner, skill, objDest, param):
        ffext.dump("JieYi", self.paramTotalSec, self.paramDefendAdd)
        brotherInfo = owner.brotherCtrl.brotherInfo
        objDest = owner
        buff = objDest.buffCtrl.getBuff(MsgDef.BuffType.DEFEND)
        if buff:
            return
        objDest.buffCtrl.addBuff(MsgDef.BuffType.DEFEND, self.paramTotalSec, self.paramDefendAdd,Base.BRO_SKILL_ID)
        objDest.updateBuffMsg(owner.uid)
        ffext.dump("JieYi addbuff", MsgDef.BuffType.DEFEND, self.paramTotalSec, self.paramDefendAdd, objDest.name)
        return
        #if None == brotherInfo:
            #ffext.dump("JieYi none brother")
            #objDest = owner
            #buff = objDest.buffCtrl.getBuff(MsgDef.BuffType.GUWU_SHIQI)
            #if buff:
                #return
            #objDest.buffCtrl.addBuff(MsgDef.BuffType.GUWU_SHIQI, self.paramTotalSec, self.paramHurtAdd,Base.BRO_SKILL_ID)
            #objDest.updateBuffMsg()
            #ffext.dump("JieYi addbuff", MsgDef.BuffType.GUWU_SHIQI, self.paramTotalSec, self.paramHurtAdd, objDest.name)
            #return
        #objDest = owner
        #buff = objDest.buffCtrl.getBuff(MsgDef.BuffType.GUWU_SHIQI)
        #f buff:
            #return
        #objDest.buffCtrl.addBuff(MsgDef.BuffType.GUWU_SHIQI, self.paramTotalSec, self.paramHurtAdd,Base.BRO_SKILL_ID)
        #objDest.updateBuffMsg()
        #ffext.dump("JieYi addbuff", MsgDef.BuffType.GUWU_SHIQI, self.paramTotalSec, self.paramHurtAdd, objDest.name)
        #return
        #对结义成员添加BUFF
        #for key, val in brotherInfo.getBrotherMember().iteritems():
            #memberSession = ffext.getSessionMgr().findByUid(val.uid)
            #if None != memberSession:
                #objDest = memberSession.player
                #buff = objDest.buffCtrl.getBuff(MsgDef.BuffType.GUWU_SHIQI)
                #if buff:
                    #return
                #objDest.buffCtrl.addBuff(MsgDef.BuffType.GUWU_SHIQI, self.paramTotalSec, self.paramHurtAdd, Base.BRO_SKILL_ID)
                #objDest.updateBuffMsg()
                #ffext.dump("JieYi addbuff", MsgDef.BuffType.GUWU_SHIQI, self.paramTotalSec, self.paramHurtAdd, objDest.name)
                #return
        #return

#夫妻技能BUFF
class Wedding(PuGong):
    def __init__(self, a=60, b=10):
        PuGong.__init__(self)
        self.paramTotalSec = a
        self.paramAttackAdd = b
    def exe(self, owner, skill, objDest, param):
        ffext.dump("JieYi", self.paramTotalSec, self.paramAttackAdd)
        objDest = owner
        buff = objDest.buffCtrl.getBuff(MsgDef.BuffType.GUWU_SHIQI)
        if buff:
            return
        from handler import MarryHandler
        objDest.buffCtrl.addBuff(MsgDef.BuffType.GUWU_SHIQI, self.paramTotalSec, self.paramAttackAdd, MarryHandler.WEDDING_SKILL_ID)
        objDest.updateBuffMsg()
        ffext.dump("JieYi addbuff", MsgDef.BuffType.GUWU_SHIQI, self.paramTotalSec, self.paramAttackAdd, objDest.name)
        return