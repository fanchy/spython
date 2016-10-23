# -*- coding: utf-8 -*-
import random
from base   import Base
from mapmgr import MapMgr
import msgtype.ttypes as MsgDef
from model.skill import SkillCalculatorBase
import ffext
import weakref

calRealMagicHurt = SkillCalculatorBase.calRealMagicHurt
IGNORE_MAGIC_DEFEND = SkillCalculatorBase.CalHurtFlag.IGNORE_MAGIC_DEFEND
#对目标造成魔法攻击105%的魔法伤害
class PuGong(Base.HurtCalculator):
    def __init__(self, a = 95):
        self.paramHurt = a
    def exe(self, owner, skill, objDest, param):
        hurtResult = calRealMagicHurt(owner, objDest, skill, self)
        objDest.subHurtResult(owner, hurtResult)
        return

#治愈术 对目标30秒内每3秒回复60点生命值
class ZhiYuShu(Base.HurtCalculator):
    def __init__(self, a = 60):
        self.paramHurt = a
    def exe(self, owner, skill, objDest, param):
        if objDest.getType() != Base.PLAYER:
            return

        objDest.tmpInfo['_leftZYS_']=  10
        def cb():
            leftTimes = objDest.tmpInfo.get('_leftZYS_', 0)
            leftTimes = leftTimes - 1
            objDest.tmpInfo['_leftZYS_']=  leftTimes
            if leftTimes <= 0:
                return
            objDest.addHPMsg(self.paramHurt)
            ffext.timer(3*1000, cbvar)

            buff = objDest.buffCtrl.getBuff(MsgDef.BuffType.ZHIYUSHU)
            if not buff:
                objDest.buffCtrl.addBuff(MsgDef.BuffType.ZHIYUSHU, 3, 0, 320)
                objDest.updateBuffMsg()
            return
        cbvar = cb
        ffext.timer(3*1000, cb)
        return

#召唤幻象-1 召唤1个战士为自己战斗，战士属性为自身属性50%
class ZhaoHuanYinXiang(Base.HurtCalculator):
    def __init__(self, a = 1, b = 50):
        self.paramNum = a
        self.paramPropRate = b
        pass
    def exe(self, owner, skill, objDest, param):
        #TODO
        from model import  PlayerModel
        newX = owner.x + 2
        newY = owner.y + 2
        if not owner.mapObj.canMove(newX, newY):
            newX = owner.x
            newY = owner.y
        player = PlayerModel.Player()
        player.forkFrom(owner, self.paramPropRate)
        player.arenaCtrl.destPlayerRef = weakref.ref(objDest)
        player.session = owner.session
        owner.mapObj.playerEnterMap(player, newX, newY)
        from model import ArenaModel
        player.fsm.changeState(ffext.singleton(ArenaModel.ArenaStateAttack))
        beginTm = ffext.getTime()
        def cb():
            if ffext.getTime() - beginTm >= 20 or player.isDeath():
                player.mapObj.playerLeaveMap(player)
                player.session = None
            else:
                try:
                    player.fsm.update(player, ffext.getTimeMs())
                except:
                    pass
                ffext.timer(1000, cb)
        ffext.timer(1000, cb)
        return

#施毒术-1 对目标中毒，10秒内每2秒受到30%的魔法伤害，无视防御
class ShiDuShu(Base.HurtCalculator):
    def __init__(self, a = 10, b = 2, c = 30):
        self.paramHurt = c
        self.paramTotalSec = a
        self.paramInterval = b
        pass
    def exe(self, owner, skill, objDest, param):
        objDest.tmpInfo['_leftSH_']=  int(self.paramTotalSec / self.paramInterval)
        def cb():
            leftTimes = objDest.tmpInfo.get('_leftSH_', 0)
            if leftTimes <= 0 or objDest.isDeath():
                return
            hurtResult = calRealMagicHurt(owner, objDest, skill, selfvar, True, True, IGNORE_MAGIC_DEFEND)
            objDest.subHurtResult(owner, hurtResult)

            leftTimes = leftTimes - 1
            objDest.tmpInfo['_leftSH_']=  leftTimes
            ffext.timer(cbinterval*1000, cbvar)
            return
        cbvar = cb
        selfvar = self
        cbinterval = self.paramInterval
        ffext.timer(self.paramInterval*1000, cb)
        return

#鼓舞士气-1 60秒内增加目标10%物理攻击和魔法攻击
class GuWuShiQi(Base.HurtCalculator):
    def __init__(self, a = 60, b = 10):
        self.paramTotalSec = a
        self.paramHurtAdd = b
        pass
    def exe(self, owner, skill, objDest, param):
        if objDest.getType() != Base.PLAYER:
            return

        buff = objDest.buffCtrl.getBuff(MsgDef.BuffType.GUWU_SHIQI)
        if buff:
            return
        objDest.buffCtrl.addBuff(MsgDef.BuffType.GUWU_SHIQI, self.paramTotalSec, self.paramHurtAdd)
        objDest.updateBuffMsg()
        return

#复活之术-1 复活死亡的队友，复活后的生命值为最大生命值20%
class FuHuoZhiShu(Base.HurtCalculator):
    def __init__(self, a = 20):
        self.paramRebornLife = a
        pass
    def exe(self, owner, skill, objDest, param):
        if objDest.getType() != Base.PLAYER:
            return
        if objDest.isDeath() != True:
            return
        srcTeam = owner.getTeam()
        if not srcTeam:
            return
        if not srcTeam.getTeamMemberByUid(objDest.uid):
            return

        #暂定500ms后复活
        objDest.handleReborn(500, self.paramRebornLife)
        return

