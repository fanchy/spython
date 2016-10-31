# -*- coding: utf-8 -*-
import random
from base   import Base
from mapmgr import MapMgr
import msgtype.ttypes as MsgDef
from model.skill import SkillCalculatorBase
import ffext
import random
import weakref

calRealMagicHurt = SkillCalculatorBase.calRealMagicHurt
#对目标造成魔法攻击105%的魔法伤害
class PuGong(Base.BaseObj):
    def __init__(self, a = 105):
        self.paramHurt = a
    def exe(self, owner, skill, objDest, param):
        hurtResult = calRealMagicHurt(owner, objDest, skill, self)
        objDest.subHurtResult(owner, hurtResult)
        return
#220	引动天雷-1	对目标敌人造成125%的魔法伤害，有30%几率对目标周围造成15%魔法伤害
class YinDongTianLei(PuGong):
    def __init__(self, a = 125, b = 30, c = 15):
        PuGong.__init__(self, a)
        self.paramNomal= a
        self.paramRate = b
        self.paramRange= c
    def exe(self, owner, skill, objDest, param):
        self.paramHurt = self.paramNomal
        PuGong.exe(self, owner, skill, objDest, param)
        if random.randint(1, 100) <= self.paramRate:
            self.paramHurt = self.paramRange
            def cb(objDestNew):
                if objDestNew != owner and objDestNew != objDest:
                    PuGong.exe(self, owner, skill, objDestNew, param)
            owner.mapObj.foreachObjInRange(objDest.x, objDest.y, 5, cb) #todo 距离
        return
#230	冰封之术-1	对目标造成魔法攻击100%的魔法伤害，同时5秒内减速目标15%移动速度
class BingFengZhiShu(PuGong):
    def __init__(self, a = 100, b = 5):
        PuGong.__init__(self, a)
        self.paramNomal= a
        self.paramSec = b
    def exe(self, owner, skill, objDest, param):
        self.paramHurt = self.paramNomal
        PuGong.exe(self, owner, skill, objDest, param)
        objDest.buffCtrl.addBuff(MsgDef.BuffType.JIAN_SU, self.paramSec)
        objDest.updateBuffMsg()
        return

#240	神明护体-1	魔法的能量环绕身体，120秒内降低对法师的造成伤害25%
class ShenMingFuTi:
    def __init__(self, a = 120, b = 25):
        self.paramSec  = a
        self.paramMianShang = b
    def exe(self, owner, skill, objDest, param):
        buff = owner.buffCtrl.getBuff(MsgDef.BuffType.SHEN_MING_HU_TI)
        if buff:
            return
        owner.buffCtrl.addBuff(MsgDef.BuffType.SHEN_MING_HU_TI, self.paramSec, self.paramMianShang, 240)
        owner.hurtAbsorbLimit = random.randint(owner.magicAttackMin, owner.magicAttackMax) * (self.paramMianShang / 100)
        owner.updateBuffMsg()
        return
#250	陨石暴落-1	一颗陨石从天而降，对单个目标造成250%的魔法伤害，5秒内造成2次附带灼烧25%魔法伤害
class YunShiBaoLuo(PuGong):
    def __init__(self, a = 250, b = 5, c = 2, d = 25):
        PuGong.__init__(self, a)
        self.paramNomal= a
        self.paramSec = b
        self.times    = c
        self.paramHurtRate= d
    def exe(self, owner, skill, objDest, param):
        self.paramHurt = self.paramNomal
        PuGong.exe(self, owner, skill, objDest, param)

        objDestRef = weakref.ref(objDest)
        ownerRef  = weakref.ref(owner)
        def cb():
            objDest = objDestRef()
            owner   = ownerRef()
            if not objDest or not owner:
                return
            self.paramHurt = self.paramHurtRate
            PuGong.exe(self, owner, skill, objDest, param)
            objDest.showEffect(MsgDef.EffectType.EFFECT_ZHUO_SHAO)
        for k in range(0, self.times):
            ffext.timer(int(self.paramSec * k * 1000/self.times), cb)
        return
#260	天火燎原-1	对目标造成120%的魔法伤害，同时对目标周围范围的目标造成35%溅射伤害。
class TianHuoLiaoYuan(PuGong):
    def __init__(self, a = 120, b = 35):
        PuGong.__init__(self, a)
        self.paramNomal= a
        self.paramHurtRate= b
    def exe(self, owner, skill, objDest, param):
        self.paramHurt = self.paramNomal
        PuGong.exe(self, owner, skill, objDest, param)
        self.paramHurt = self.paramHurtRate
        def cb(objDestNew):
            if objDestNew != owner and objDest != objDestNew:
                PuGong.exe(self, owner, skill, objDestNew, param)

        owner.mapObj.foreachObjInRange(objDest.x, objDest.y, 5, cb)  # todo 距离
        return

#1002	法师无双-龙啸九天	对目标周围敌人造成魔法攻击250%的魔法伤害，同时击退周围的敌人
class FaShiWuShuang_LongXiaoJiuTian(PuGong):
    def __init__(self, a = 250):
        PuGong.__init__(self, a)
        self.paramNomal= a
    def exe(self, owner, skill, objDest, param):
        self.paramHurt = self.paramNomal
        PuGong.exe(self, owner, skill, objDest, param)

        def cb(objDestNew):
            if objDestNew != owner and objDest != objDestNew:
                #PuGong.exe(self, owner, skill, objDestNew, param)
                pass#TODO
        owner.mapObj.foreachObjInRange(objDest.x, objDest.y, 5, cb)  # todo 距离
        return
