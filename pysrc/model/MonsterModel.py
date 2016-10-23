# -*- coding: utf-8 -*-
import random
from base   import Base
from mapmgr import MapMgr
import msgtype.ttypes as MsgDef
import weakref
import ffext
import idtool
import random
from model import SkillModel, ItemModel
from model.skill import SkillCalculatorBase
calPowerFight = SkillCalculatorBase.calPowerFight
from model.monster import MonsterAI

class BuffCtrl:
    def __init__(self, owner):
        self.ownerref      = weakref.ref(owner)
        self.allBuff       = {}
        return
    #眩晕3秒:        buffSec=3
    #3秒内减速20%:   buffSec=3, buffEffect=20
    def addBuff(self, buffId, buffSec = 0, buffEffect = 0, fromSkillId = 0):
        curBuff = self.allBuff.get(buffId)
        if curBuff:
            return False
        endTime = 0
        if buffSec > 0 :
            endTime = ffext.getTime() + buffSec
            owner = self.ownerref
            def cb():
                player = owner()
                if not player or player.mapObj == None:
                    return
                player.buffCtrl.delBuff(buffId)
                player.updateBuffMsg()
            ffext.timer(buffSec*1000, cb)
        newBuff = MsgDef.BuffStatus(endTime, {1:buffEffect}, fromSkillId)
        self.allBuff[buffId] = newBuff
        player = self.ownerref()
        return
    def getBuff(self, buffId):
        return  self.allBuff.get(buffId, None)
    def delBuff(self, buffId):
        return self.allBuff.pop(buffId, None)
def burstCallBack(player, args):
    callbackArg = args
    #callbackArg = {'players':{}, 'prizecallback': tmpPrizeCallBack}
    callbackArg['players'].pop(player.uid, None)
    if len(callbackArg['players']) == 0:#全部点击完成了
        cb = callbackArg['prizecallback']
        if cb:
            callbackArg['prizecallback'] = None
            cb()
    return
class MonsterProp:
    def __init__(self, appr = 1):
        self.appr = appr
        self.cfgId           = 0#配置表里的ID
        self.job             = 0
        self.monstertype     = 0
        self.level           = 0
        self.powerfight      = 0
        self.expgoldtimes    = 0
        self.expval          = 0
        self.hp              = 0
        self.mp              = 0
        #物理攻击
        self.physicAttackMin = 10#最小物理攻击
        self.physicAttackMax = 20#最大物理攻击
        #法术攻击
        self.magicAttackMin  = 10#最小法术攻击
        self.magicAttackMax  = 20#最大法术攻击
        #物理防御
        self.physicDefendMin = 10#最小物理防御
        self.physicDefendMax = 20#最大物理防御
        #法术防御
        self.magicDefendMin  = 10#最小法术防御
        self.magicDefendMax  = 20#最大法术防御
        #暴击
        self.crit            = 0#暴击 影响暴击的概率	浮点数
        self.hit             = 0#命中 影响攻击时的命中率	浮点数
        self.avoid           = 0#躲避 被攻击时，影响降低被命中的概率	浮点数
        self.attackSpeed     = 0#攻击速度
        self.attackSing      = 0#攻击吟唱时间 影响释放攻击动作前的吟唱时间 吟唱时间内被攻击，有50%概率被打断，打断后需要重新吟唱，单位：秒  精确到毫秒
        self.attackInterval  = 0#两次攻击之间间隔时间，单位：秒  精确到毫秒
        self.attackDistance  = 0#攻击距离	以单位为中心的圆内可以攻击，近战标准值：100，远程值：600
        self.moveSpeed       = 0#移动速度 影响地图上移动速度，标准值：100 精确到毫秒
        self.hurtAbsorb      = 0#伤害吸收 受到伤害时，一定比例转换为生命值 百分比
        self.hpAbsorb        = 0#吸血 当对敌人造成伤害时，吸取血量恢复自身生命值 百分比
        #爆落配置
        self.allBurstCfg     = []
        #boss类型，是普通怪，还是精英怪，还是boss
        self.bosstype        = Base.BossType.MON_NORMAL
    def getMonDifficultyType(self):
        return 0# 0普通怪， 1 精英， 2 boss
class MonsterEnemy(Base.BaseObj):
    def __init__(self):
        self.uid = 0
        self.name= ''
        self.hurt= 0#累计伤害
class Monster(Base.BaseObj):
    def __init__(self, propCfg):
        #通过类型，出生点，地图，可以知道这个怪从哪里复活
        self.bornX       = 0
        self.bornY       = 0
        #怪物数据
        self.uid         = idtool.allocTmpId()
        self.mapObj      = None
        self.x           = 0
        self.y           = 0
        self.direction   = Base.Direction.DIRECTION4[random.randint(0, len(Base.Direction.DIRECTION4) -1)]
        #下次移动时间
        self.nextMoveTm  = ffext.getTimeMs()
        #状态机
        self.fsm         = MonsterAI.FSM(self)
        #怪物配置
        self.propCfg    = propCfg
        self.hpMax       = propCfg.hp
        self.hp          = propCfg.hp
        self.mpMax       = propCfg.mp
        self.mp          = propCfg.mp
        #怪物等级
        self.level       = propCfg.level
        self.aiFlag      = 0#1表示主动攻击
        #暴击
        self.crit            = propCfg.crit#暴击 影响暴击的概率	浮点数
        self.hit             = propCfg.hit#命中 影响攻击时的命中率	浮点数
        self.avoid           = propCfg.avoid#躲避 被攻击时，影响降低被命中的概率	浮点数
        self.attackSpeed     = propCfg.attackSpeed#攻击速度
        self.attackSing      = propCfg.attackSing#攻击吟唱时间 影响释放攻击动作前的吟唱时间 吟唱时间内被攻击，有50%概率被打断，打断后需要重新吟唱，单位：秒  精确到毫秒
        self.attackInterval  = propCfg.attackInterval#两次攻击之间间隔时间，单位：秒  精确到毫秒
        self.attackDistance  = propCfg.attackDistance#攻击距离	以单位为中心的圆内可以攻击，近战标准值：100，远程值：600
        self.moveSpeed       = propCfg.moveSpeed#移动速度 影响地图上移动速度，标准值：100 精确到毫秒
        self.hurtAbsorb      = propCfg.hurtAbsorb#伤害吸收 受到伤害时，一定比例转换为生命值 百分比
        self.hpAbsorb        = propCfg.hpAbsorb#吸血 当对敌人造成伤害时，吸取血量恢复自身生命值 百分比
        #物理攻击
        self.physicAttackMin = propCfg.physicAttackMin#最小物理攻击
        self.physicAttackMax = propCfg.physicAttackMax#最大物理攻击
        #法术攻击
        self.magicAttackMin  = propCfg.magicAttackMin#最小法术攻击
        self.magicAttackMax  = propCfg.magicAttackMax#最大法术攻击f
        #物理防御
        self.physicDefendMin = propCfg.physicDefendMin#最小物理防御
        self.physicDefendMax = propCfg.physicDefendMax#最大物理防御
        #法术防御
        self.magicDefendMin  = propCfg.magicDefendMin#最小法术防御
        self.magicDefendMax  = propCfg.magicDefendMax#最大法术防御

        #攻击目标
        self.objTarget = None
        #仇恨系统
        self.allHurtCount       = {}#uid -> MonsterEnemy
        self.allTeamHurtCount = {}  # teamid -> MonsterEnemy 组队的伤害统计
        self.lastAttackObjRef   = None#最后一次攻击者的弱引用
        self.lastSelectTargetMS = 0#上次选择攻击目标的时间

        self.buffCtrl = BuffCtrl(self)#buff 控制
        #怪物的技能系统
        self.skillCtrl      = SkillModel.SkillCtrl(self)
        self.skillCtrl.learnMonsterSkill(4151)#怪物的默认技能
        #怪物重生时间
        self.rebornSec = 30#默认10秒
        #上次回血时间
        self.lastRecoverHPTM = 0
        self.tmpInfo = {}  # 临时数据
    def isDeath(self):
        return self.hp <= 0
    #类型
    def getType(self):
        return Base.MONSTER
    #处理被击杀的事件
    def whenDie(self, objAttack):
        #怪物被击杀，给对方加经验
        self.tmpInfo['_killedtm_'] = ffext.getTimeMs()
        if not objAttack or objAttack.getType() != Base.PLAYER:
            return
        if self.mapObj and self.mapObj.copyMapHandler:
            try:
                self.mapObj.copyMapHandler.handleObjDie(self.mapObj, self)
            except:
                ffext.error('mapObj.copyMapHandler.handleObjDie failed mapname=%s player=%s'%(self.mapObj.mapname, self.name))
        self.handleTaskTrigger(objAttack)
        self.handleDrop(objAttack)
        #测试方便，每次被击杀，掉落一个大补丸
        #item   = ItemModel.createItemByName('大补丸（小）')

        #try:
        #except:
        #    ffext.error('mosnter burst exception %s'%(self.name))

        return
    def handleTaskTrigger(self, objAttack):
        if self.propCfg.bosstype == Base.BossType.MON_NORMAL:
            objAttack.taskCtrl.trigger(Base.Action.KILL_MONSTER, self.propCfg.cfgId, 1)
            ffext.dump('handleTaskTrigger single', self.name, objAttack.name)
        else:
            #如果是精英怪或者boss，组队的也可以完成
            canTriggerTaskList = [objAttack]
            team = objAttack.teamCtrl.getTeam()
            if team:
                for uid, v in team.getTeamMember().iteritems():
                    tmpPlayer = objAttack.mapObj.getPlayerById(uid)
                    if tmpPlayer and tmpPlayer not in canTriggerTaskList:
                        canTriggerTaskList.append(tmpPlayer)
            for k in canTriggerTaskList:
                k.taskCtrl.trigger(Base.Action.KILL_MONSTER, self.propCfg.cfgId, 1)
                ffext.dump('handleTaskTrigger team', self.name, k.name)
            return
    def handleDrop(self, objAttackKill):
        if objAttackKill.getType() != Base.PLAYER:
            return

        objAttack = objAttackKill

        #击杀血量最多的人，给装备奖励
        maxObj = objAttackKill
        maxHurt= 0
        for uid, data in self.allHurtCount.iteritems():
            player = self.mapObj.getPlayerById(uid)
            if not player:
                continue
            if data.hurt > maxHurt:
                maxObj = player
                maxHurt = data.hurt
        maxTeam = None
        maxTeamHurt = 0
        for uid, data in self.allTeamHurtCount.iteritems():
            from model import  TeamModel
            team = TeamModel.getTeamMgr().getTeamById(uid)
            if not team:
                continue
            if data.hurt > maxTeamHurt:
                maxTeam = team
                maxTeamHurt = data.hurt
        #初始化数据，方便复活
        self.allHurtCount = {}
        self.allTeamHurtCount = {}

        objAttack.addExp(self.propCfg.expval, True)
        burstItemList = []
        from handler import ItemHandler
        def burstItemCallBack(itemCfgId, num):
            burstItemList.append((itemCfgId, num))
        def giveItemById(obj, retMsg, itemCfgId, num):
            if itemCfgId == 0:  # 金币
                obj.addGold(num, True)
                return
            item = obj.itemCtrl.addItemByCfgId(itemCfgId, num)
            if item:
                ffext.dump('whenDie itemEnterMap', item.itemCfg.name, num)

                # self.mapObj.itemEnterMap(item, self.x + 1, self.y + 1)
                if item.__class__ == list:
                    for k in item:
                        retItem = MsgDef.Item()
                        ItemHandler.buildItem(retItem, k)
                        retMsg.items.append(retItem)
                else:
                    retItem = MsgDef.Item()
                    ItemHandler.buildItem(retItem, item)
                    retMsg.items.append(retItem)
            return

        def burstItemCallBackName(name, num):
            from model import ItemModel
            itemCfg = ItemModel.getItemMgr().getCfgByName(name)
            if itemCfg:
                burstItemCallBack(itemCfg.cfgId, num)
            else:
                ffext.error('burstItemCallBackName %s %d' % (name, num))
            return

        for k in self.propCfg.allBurstCfg:
            k.genBurst(burstItemCallBackName)

        burstBagCfg = getMonsterMgr().cfgLevel2Drop.get(self.propCfg.level)
        if burstBagCfg:
            ffext.dump('burstBagCfg', burstBagCfg)
            # 1	根据表【怪物掉落包个数】获得该等级怪物的掉落物品的个数
            # 2	每个包掉落概率：根据怪物的等级和类型，获得是否该包是否掉落
            # 3	金币数目：怪物实际掉落金币=怪物等级金币*怪物的金币倍数
            # 4	物品：每一个掉落包从【金币/物品1/物品2/物品3/物品4】中随机一个
            # 5	若随机到【/物品1/物品2/物品3/物品4】，寻找制定的掉落包ID内物品
            monType = self.propCfg.getMonDifficultyType()
            num = burstBagCfg.numList[monType]
            rate = burstBagCfg.rateList[monType]
            dropBagList = burstBagCfg.bagIdList
            for k in range(num):
                rand = random.randint(1, 100)
                ffext.dump('rate trace', rate, rand, len(dropBagList))
                if rate >= rand and len(dropBagList) > 0:  # 爆落
                    destBagId = dropBagList[rand % len(dropBagList)]
                    ffext.dump('rate trace', rate, rand, len(dropBagList), destBagId)
                    if destBagId == 0:  # 金币
                        gold = random.randint(burstBagCfg.goldMin, burstBagCfg.goldMax)
                        burstItemCallBack(destBagId, gold * self.propCfg.expgoldtimes)  # *怪物的金币倍数
                        continue
                    destBagCfg = getMonsterMgr().bagid2cfg.get(destBagId)
                    if destBagCfg:
                        for itemCfgId in destBagCfg.itemIdList:
                            burstItemCallBack(itemCfgId, 1)
        ffext.dump('handledrop', burstItemList, objAttack.name, maxHurt, maxTeamHurt)
        if maxHurt >= maxTeamHurt:#个人获得道具
            objAttack = maxObj
            retMsg = MsgDef.MonserBurstItemsRet(self.uid, objAttack.uid, [], self.propCfg.expval, 0)
            for k in burstItemList:
                giveItemById(objAttack, retMsg, k[0], k[1])
            if len(retMsg.items) > 0:
                ItemHandler.processQueryPkg(objAttack.session)
            objAttack.sendMsg(MsgDef.ServerCmd.MONSTER_BURST_ITEMS, retMsg)
            return
        else:#团队获得道具
            allPlayers = []
            for k, v in maxTeam.getTeamMember().iteritems():
                p = self.mapObj.getPlayerById(k)
                if p:
                    allPlayers.append(p)
            if not allPlayers:
                return
            objPrize = allPlayers[random.randint(0, len(allPlayers) - 1)]
            retMsg = MsgDef.MonserBurstItemsRet(self.uid, objPrize.uid, [], 0, 0)
            objPrizeRef = weakref.ref(objPrize)
            def tmpPrizeCallBack():
                objPrize = objPrizeRef()
                if not objPrize:
                    return
                for k in burstItemList:
                    giveItemById(objPrize, retMsg, k[0], k[1])
                if len(retMsg.items) > 0:
                    ItemHandler.processQueryPkg(objPrize.session)
            retMsg.teamBurstInfo = []
            callbackArg = {'players':{}, 'prizecallback': tmpPrizeCallBack}
            for arg in allPlayers:
                randNum = 1
                if arg == objPrize:
                    randNum = 6
                else:
                    randNum = random.randint(1, 5)
                retMsg.teamBurstInfo.append(MsgDef.BurstRandInfo(arg.uid, arg.name, randNum))
                callbackArg[arg.uid] = arg.name
            for k in burstItemList:
                ffext.dump('busrt info', k)
                from model import  ItemModel
                itemCfg = ItemModel.getItemMgr().getCfgByCfgId(k[0])
                if itemCfg:
                    retItem = MsgDef.Item()
                    ItemModel.tmpBuildItem(retItem, itemCfg)
                    retMsg.items.append(retItem)
            def timercb():
                ffext.dump("timercb teamburst...")
                cb = callbackArg['prizecallback']
                if cb:
                    callbackArg['prizecallback'] = None
                    cb()
                return
            ffext.timer(5*1000, timercb)
            ffext.dump('monter burst items', retMsg)
            for objAttack in allPlayers:
                retMsg.callbackId = objPrize.addCallBack(burstCallBack, callbackArg)
                objAttack.sendMsg(MsgDef.ServerCmd.MONSTER_BURST_ITEMS, retMsg)
        return
    def addHurtLog(self, obj, hurt):
        if not obj:
            return
        self.lastAttackObjRef = weakref.ref(obj)
        if obj.getType() == Base.PLAYER:
            ffext.dump("addHurtLog 1", hurt)
            team = obj.teamCtrl.getTeam()
            if team:
                teamId = obj.teamCtrl.getTeamID()
                ffext.dump("addHurtLog 2", teamId)
                enemy = self.allTeamHurtCount.get(teamId)
                if enemy:
                    enemy.hurt += hurt
                else:
                    enemy = MonsterEnemy()
                    enemy.uid = teamId
                    enemy.hurt += hurt
                    self.allTeamHurtCount[teamId] = enemy
                return

        ffext.dump("addHurtLog 2", obj.uid)
        enemy = self.allHurtCount.get(obj.uid)
        if enemy:
            enemy.hurt += hurt
        else:
            enemy = MonsterEnemy()
            enemy.uid = obj.uid
            enemy.name= obj.name
            enemy.hurt += hurt
            self.allHurtCount[obj.uid] = enemy
    def calMaxReachEnemyDistance(self):
        return 10
    #根据仇恨列表，选择一个敌人
    def selectEnemy(self):
        lastAttackObj = None
        self.lastSelectTargetMS = ffext.getTimeMs()
        if self.lastAttackObjRef != None:
            lastAttackObj = self.lastAttackObjRef()
            if lastAttackObj == None:
                self.lastAttackObjRef = None
        maxN = self.calMaxReachEnemyDistance()
        if lastAttackObj and lastAttackObj.isDeath() == False and Base.distance(self.x, self.y, lastAttackObj.x, lastAttackObj.y) < maxN:
            return lastAttackObj
        objTargetList = self.mapObj.getPlayerInRange(self.x, self.y, maxN)
        #ffext.dump('select enemy', objTargetList)
        if objTargetList:
            obj = objTargetList[random.randint(0, len(objTargetList) - 1)]
            return obj
        return None
    @property
    def showName(self):
        return self.propCfg.name
    @property
    def name(self):
        return self.propCfg.name
    @property#战斗力
    def powerFight(self):
        return calPowerFight(self)
    #血量减少
    def subHurtResult(self, objSrc, hurtResult, msgFlag = True):
        if self.hp <= 0:
            return 0
        hp = self.subHP(hurtResult.hurt, objSrc)
        if msgFlag:
            retHurtMsg = MsgDef.HPHurtRet(self.uid, self.hp,self.mp, hurtResult.hurt, hurtResult.crit, hurtResult.hit)
            self.broadcast(MsgDef.ServerCmd.HURT_RESULT, retHurtMsg)
        return hp
    #血量增加
    def addHPMsg(self, hp, mp = 0, msgFlag = True):
        self.hp += hp
        if self.hp > self.hpMax:
            self.hp = self.hpMax
        elif self.hp < 0:
            self.hp = 0
        if mp != 0:
            self.mp += mp
            if self.mp > self.mpMax:
                self.mp = self.mpMax
            elif self.mp < 0:
                self.mp = 0
        if msgFlag:
            retMsg = MsgDef.SyncHpMpRet(self.uid, self.hp,self.mp)
            self.broadcast(MsgDef.ServerCmd.SYNC_HPMP, retMsg)
    def subHP(self, hp, objSrc = None):
        if self.hp > hp:
            self.hp -= hp
            if hp > 0:
                self.addHurtLog(objSrc, hp)
            return hp
        else:
            hp = self.hp
            self.hp = 0
            if hp > 0:
                self.addHurtLog(objSrc, hp)
            self.whenDie(objSrc)
            return hp
        return hp
    def subMP(self, mp):
        if self.mp > mp:
            self.mp -= mp
            return mp
        else:
            mp = self.mp
            self.mp = 0
            return mp
        return mp
    def broadcast(self, cmd, msg, excludePlayer = None):
        return self.mapObj.broadcast(self.x, self.y, cmd, msg, excludePlayer)
    def foreachInMap(self, func):
        return self.mapObj.foreachInMap(func)
    @property
    def appr(self):
        return self.propCfg.appr
    @property
    def cfgId(self):
        return self.propCfg.cfgId
    def buildEnterMapMsg(self, flag = False):
        retMsg = MsgDef.MonsterEnterMapRet(self.propCfg.appr, self.uid, self.name, self.x, self.y, self.direction, self.hp, self.hpMax, self.propCfg.cfgId)
        retMsg.level = self.propCfg.level
        if flag != False:
            retMsg = ffext.encodeMsg(retMsg)#, flag, flag
        return retMsg

    def buildLeaveMapMsg(self, flag=False):
        retMsg = MsgDef.LeaveMapRet(self.uid)
        if flag != False:
            retMsg = ffext.encodeMsg(retMsg)#, flag, flag
        return retMsg
    def buildMoveMapMsg(self, newX, newY, flag=False):
        retMsg = MsgDef.MoveRet(newX, newY, self.uid, self.direction)
        if flag != False:
            retMsg = ffext.encodeMsg(retMsg)#, flag, flag
        return retMsg
    def updateBuffMsg(self):
        return self.broadcast(MsgDef.ServerCmd.UPDATE_BUFF, MsgDef.UpdateBuffRet(self.buffCtrl.allBuff))
    def showEffect(self, effectType):
        return self.broadcast(MsgDef.ServerCmd.SHOW_EFFECT, MsgDef.ShowEffectRet(effectType))

def genMonster(mapName, monName, x, y, num, rangeMax, rebornSec = 10, autoattackFlag = 0):
    ret = []
    propCfg = getMonsterMgr().getCfgByName(monName)
    if not propCfg:
        ffext.error('propCfg not found mosntername=%s'%(monName))
        return ret
    mapObj   = MapMgr.getMapMgr().allocMap(mapName)
    if None == mapObj:
        ffext.error('mon gen map failed %s %s %d %d %d %d'%( mapName, monName, x, y, num, rangeMax))
        return ret
    for i in range(num):
        mon = Monster(propCfg)
        #mon.showName = monName
        mon.aiFlag = autoattackFlag
        mon.bornX    = x
        mon.bornY    = y
        rangeMinX    = -1 * rangeMax
        if mon.bornX + rangeMinX < 0:
            rangeMinX= -1 * mon.bornX
        rangeMinY    = -1 * rangeMax
        if mon.bornY + rangeMinY < 0:
            rangeMinY= -1 * mon.bornY
        newPos = None
        for kk in range(rangeMax* rangeMax):
            x        = mon.bornX + random.randint(rangeMinX, rangeMax)
            y        = mon.bornY + random.randint(rangeMinY, rangeMax)

            bFlag = mapObj.canMove(x, y)
            if  bFlag:
                mon.bornX    = x
                mon.bornY    = y
                break

        if not mapObj.monsterEnterMap(mon, mon.bornX, mon.bornY):
            ffext.error('mon gen pos failed %s %s %d %d %d %d'%( mapName, monName, mon.bornX, mon.bornY, num, rangeMax))
            continue
        mon.fsm.changeState(ffext.singleton(MonsterAI.StateIdle))
        mon.rebornSec = rebornSec
        #print('genMonster=%s'%(mon))
        ffext.info('genMonster name=%s,map=%s,x=%d,y=%d'%(monName, mapName, x, y))
        ret.append(mon)
    return ret

def genMonsterById(mapName, monId, x, y, num, rangeMax, rebornSec = 10, autoattackFlag = 0):
    ret = []
    propCfg = getMonsterMgr().getCfgById(monId)
    if not propCfg:
        ffext.error('propCfg not found mosnterid=%d'%(monId))
        return ret
    return genMonster(mapName, propCfg.name, x, y, num, rangeMax, rebornSec, autoattackFlag)

def destroyMonster(monster):  # 怪物清除
    # ffext.dump('destroyMonster', monster.name)
    if monster and monster.mapObj:
        monster.mapObj.monsterLeaveMap(monster)

class BurstType:
    BURST_ALL = 0#必爆
    BURST_ONE = 1#必爆1个
    BURST_SOME= 2#各个随机爆
class BurstRateCfg(Base.BaseObj):
    def __init__(self, burstItemName, burstNum = 1, burtRate = 0, burtRateTatal = 100):
        self.burstItemName  = burstItemName
        self.burstNum       = burstNum
        self.burtRate       = burtRate
        self.burtRateTatal  = burtRateTatal
class BurstGroupCfg(Base.BaseObj):
    def __init__(self, burstType = 0):
        self.burstType      = burstType
        self.allBurstCfg    = []
    def genBurst(self, callback):
        if self.burstType == BurstType.BURST_ALL:
            for cfg in self.allBurstCfg:
                ffext.dump('genburst', cfg.burstItemName, cfg.burstNum)
                callback(cfg.burstItemName, cfg.burstNum)
            return True
        elif self.burstType == BurstType.BURST_ONE:
            allRate = 0
            for cfg in self.allBurstCfg:
                allRate += cfg.burtRate
            curRate = 0
            rand = random.randint(1, allRate)
            for cfg in self.allBurstCfg:
                curRate += cfg.burtRate
                if curRate >= rand:
                    ffext.dump('genburst', cfg.burstItemName, cfg.burstNum)
                    callback(cfg.burstItemName, cfg.burstNum)
                    break
            return True
        elif self.burstType == BurstType.BURST_SOME:

            for cfg in self.allBurstCfg:
                allRate = cfg.burtRateTatal
                rand = random.randint(1, allRate)
                curRate = cfg.burtRate
                if curRate >= rand:
                    ffext.dump('genburst', cfg.burstItemName, cfg.burstNum)
                    callback(cfg.burstItemName, cfg.burstNum)
                    continue
            return True
        return
def strToBurstGroupCfg(data, burstType = 0):
    ret = BurstGroupCfg(burstType)
    allArgs = data.strip().split(';')
    for k in allArgs:
        args  = k .strip().split('/')
        if len(args) == 0 or args[0] == '':
            continue
        itemName = args[0].split('*')
        burstCfg = BurstRateCfg(itemName[0])
        if len(itemName) >= 2:
            burstCfg.burstNum = int(itemName[1])
        if len(args) >= 2:
            try:
                burstCfg.burtRate =  int(args[1])
            except:
                ffext.error('parse monster burst rate failed %s'%(data))
                pass
            pass
        if len(args) >= 3:
            burstCfg.burtRateTatal =  int(args[2])
        ret.allBurstCfg.append(burstCfg)
    return ret

class MonDropCfg(Base.BaseObj):
    def __init__(self, lv = 0, goldMin = 0, goldMax = 0, dropbagid1 = 0, dropbagid2 = 0, dropbagid3 = 0, dropbagid4 = 0):
        self.level = lv
        self.goldMin = goldMin
        self.goldMax = goldMax
        self.dropbagid1 = dropbagid1
        self.dropbagid2 = dropbagid2
        self.dropbagid3 = dropbagid3
        self.dropbagid4 = dropbagid4
        self.bagIdList = [0, self.dropbagid1, self.dropbagid2, self.dropbagid3, self.dropbagid4]#0 表示金币
        self.rateList   = [0, 0, 0]# 小怪 精英怪 BOSS
        self.numList    = [0, 0, 0]# 小怪 精英怪 BOSS
        return
class MonDropBagCfg(Base.BaseObj):
    def __init__(self, bagid = 0, baginro = '', rate = 0, itemList = '', num = 0):
        self.bagid = bagid
        self.baginro = baginro
        self.rate = rate
        self.itemIdList = self.parseItemList(itemList)
        self.num = num
        return
    def parseItemList(self, itemListStr):
        if itemListStr == '':
            return []
        ret = []
        args = itemListStr.split(';')
        for k in args:
            m = k.strip()
            if m != '':
                ret.append(int(m))
        return ret

class MonsterMgr(Base.BaseObj):
    def __init__(self):
        self.allMonPropCfgById= {} #怪物类型对应的属性配置
        self.allMonPropCfgByName= {} #怪物类型对应的属性配置
        #self.allMonGenCfg = {} #所有怪对应的生成配置
        self.cfgLevel2Drop = {} #level 2 drop Cfg
        self.bagid2cfg = {} #bagid -> Cfg
    def loadCfg(self):
        #读取所有怪物的配置
        self.allMonPropCfgById.clear()
        self.allMonPropCfgByName.clear()
        db = ffext.allocDbConnection('cfg',ffext.getConfig('-cfg'))
        ret = db.queryResult('select cfgid,job,monstertype,level,powerfight,expgoldtimes,expval,hp,mp,\
physic_attack_min,physic_attack_max,magic_attack_min,magic_attack_max,\
physic_defend_min, physic_defend_max, magic_defend_min, magic_defend_max,\
crit, hit, avoid, attackspeed, attacksing, attackinterval, \
attackdistance, movespeed, hurtaborb, hpabsorb, name,burst_all,burst_one,burst_some,bosstype from monsterprop')
        for row in ret.result:
            propCfg = MonsterProp()
            propCfg.cfgId           = int(row[0])
            propCfg.job             = int(row[1])
            propCfg.monstertype     = int(row[2])
            propCfg.level           = int(row[3])
            propCfg.powerfight      = int(row[4])
            propCfg.expgoldtimes    = int(row[5])
            if propCfg.expgoldtimes < 1:
                propCfg.expgoldtimes = 1
            propCfg.expval          = int(row[6])
            propCfg.hp              = int(row[7])
            propCfg.mp              = int(row[8])
            #物理攻击
            propCfg.physicAttackMin = int(row[9])#最小物理攻击
            propCfg.physicAttackMax = int(row[10])#最大物理攻击
            #法术攻击
            propCfg.magicAttackMin  = int(row[11])#最小法术攻击
            propCfg.magicAttackMax  = int(row[12])#最大法术攻击
            #物理防御
            propCfg.physicDefendMin = int(row[13])#最小物理防御
            propCfg.physicDefendMax = int(row[14])#最大物理防御
            #法术防御
            propCfg.magicDefendMin  = int(row[15])#最小法术防御
            propCfg.magicDefendMax  = int(row[16])#最大法术防御
            #暴击
            propCfg.crit            = int(ffext.perToNum(row[17]) * Base.CRIT_RATE_BASE / 100)#暴击 影响暴击的概率	浮点数
            propCfg.hit             = int(ffext.perToNum(row[18]) * Base.HIT_RATE_BASE / 100)#命中 影响攻击时的命中率	浮点数
            propCfg.avoid           = int(ffext.perToNum(row[19]) * Base.AVOID_RATE_BASE / 100)#躲避 被攻击时，影响降低被命中的概率	浮点数
            propCfg.attackSpeed     = int(row[20])#攻击速度
            propCfg.attackSing      = int(row[21])#攻击吟唱时间 影响释放攻击动作前的吟唱时间 吟唱时间内被攻击，有50%概率被打断，打断后需要重新吟唱，单位：秒  精确到毫秒
            propCfg.attackInterval  = int(row[22])#两次攻击之间间隔时间，单位：秒  精确到毫秒
            propCfg.attackDistance  = int(row[23])#攻击距离	以单位为中心的圆内可以攻击，近战标准值：100，远程值：600
            if propCfg.attackDistance >= 100:
                propCfg.attackDistance = int(propCfg.attackDistance / 100)
            #propCfg.attackDistance += 1
            propCfg.moveSpeed       = int(row[24])#移动速度 影响地图上移动速度，标准值：100 精确到毫秒
            propCfg.hurtAbsorb      = int(row[25])#伤害吸收 受到伤害时，一定比例转换为生命值 百分比
            propCfg.hpAbsorb        = int(row[26])#吸血 当对敌人造成伤害时，吸取血量恢复自身生命值 百分比
            propCfg.name            = row[27].strip()
            burstGroupCfg = strToBurstGroupCfg(row[28], BurstType.BURST_ALL)
            if len(burstGroupCfg.allBurstCfg) > 0:
                propCfg.allBurstCfg.append(burstGroupCfg)
                #ffext.dump('monster burst cfg', burstGroupCfg)
            burstGroupCfg = strToBurstGroupCfg(row[29], BurstType.BURST_ONE)
            if len(burstGroupCfg.allBurstCfg) > 0:
                propCfg.allBurstCfg.append(burstGroupCfg)
                #ffext.dump('monster burst cfg', burstGroupCfg)
            burstGroupCfg = strToBurstGroupCfg(row[30], BurstType.BURST_SOME)
            if len(burstGroupCfg.allBurstCfg) > 0:
                propCfg.allBurstCfg.append(burstGroupCfg)
                #ffext.dump('monster burst cfg', burstGroupCfg)
            if row[31] != '':
                propCfg.bosstype = int(row[31])
            self.allMonPropCfgById[propCfg.cfgId]   = propCfg
            self.allMonPropCfgByName[propCfg.name]  = propCfg
        sql = 'select name, mapid, x,y, num,rebornSec,autoattack from monstergen'
        db = ffext.allocDbConnection('cfg',ffext.getConfig('-cfg'))
        ret = db.queryResult(sql)
        self.mnstergen = []
        for row in ret.result:
            monName= row[0].strip()
            mapName = row[1].strip()
            x = int(row[2])
            y = int(row[3])
            num = int(row[4])
            rangeMax = 0
            if num > 1:
                rangeMax = num
            rebornSec = int(row[5])
            autoattack=int(row[6])
            self.mnstergen.append([mapName, monName, x, y, num, rangeMax, rebornSec])
            genMonster(mapName, monName, x, y, num, rangeMax, rebornSec, autoattack)
        #爆落相关的配置
        self.readBagIdCfg()
        self.readmonsterdrop_lv2bag()
        return True
    def readBagIdCfg(self):
        db = ffext.allocDbConnection('cfg',ffext.getConfig('-cfg'))
        ret = db.queryResult('select id,intro,rate,itemlist,num from monsterdrop_bag2item')
        self.bagid2cfg = {}
        for row in ret.result:
            obj = MonDropBagCfg(int(row[0]), row[1], int(ffext.perToNum(row[2])), row[3], int(row[4]))
            self.bagid2cfg[obj.bagid] = obj
            #ffext.dump('bag obj', obj)
        return True
    def readmonsterdrop_lv2bag(self):
        db = ffext.allocDbConnection('cfg',ffext.getConfig('-cfg'))
        ret = db.queryResult('select monsterdrop_lv2bag.level,goldmin,goldmax,dropbagid1,dropbagid2,dropbagid3,dropbagid4,rate1,rate2,rate3,num1,num2,num3 \
                            from monsterdrop_lv2bag,monsterdrop_lv2rate,monsterdrop_lv2num \
                            where monsterdrop_lv2bag.level = monsterdrop_lv2rate.level and monsterdrop_lv2bag.level=monsterdrop_lv2num.level')
        self.cfgLevel2Drop = {}
        for row in ret.result:
            obj = MonDropCfg(int(row[0]), int(row[1]), int(row[2]), int(row[3]), int(row[4]),int(row[5]), int(row[6]))
            obj.rateList[0] = int(float(row[7]) * 100)
            obj.rateList[1] = int(float(row[8]) * 100)
            obj.rateList[2] = int(float(row[9]) * 100)
            obj.numList[0] = int(row[10])
            obj.numList[1] = int(row[11])
            obj.numList[2] = int(row[12])
            self.cfgLevel2Drop[obj.level] = obj
            #ffext.dump('MonDropCfg obj', obj)
        return True
    def getCfgById(self, cfgId):
        return self.allMonPropCfgById.get(cfgId)
    def getCfgByName(self, name):
        return self.allMonPropCfgByName.get(name)
    def onTimer(self):
        #print ('Ontimer', __name__)
        nowMs = ffext.getTimeMs()
        allMap = MapMgr.getMapMgr().allMap
        for mapName, mapObj in allMap.iteritems():
            if mapObj.getPlayerNum() <= 0:
                if nowMs - mapObj.lastMonsterUpdateMs >= 10*1000:
                    continue
            else:
                mapObj.lastMonsterUpdateMs = nowMs
            allMonster = [v for k, v in mapObj.allMonter.iteritems()]
            for monster in allMonster:
                monster.fsm.update(monster, nowMs)

        return True

gMonsterMgr = MonsterMgr()
def getMonsterMgr():
    return gMonsterMgr
def onTimer():
    gMonsterMgr.onTimer()
    ffext.timer(Base.MONSTER_TIMER_MS, onTimer)