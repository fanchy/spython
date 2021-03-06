# -*- coding: utf-8 -*-
import time
import ffext
#引用好友列表及好友临时列表字典的增删查
from model import FriendModel, TeamModel, GuildModel
from model import SkillModel, TaskModel, ItemModel, PetModel, MarryModel, MailModel, MonsterModel, LoginRewardModel
from mapmgr import MapMgr
import msgtype.ttypes as MsgDef
from base import Base
from model.skill import SkillCalculatorBase
from db import DbService
import random
import idtool
import weakref
import json
from model.skill import SkillCalculatorBase
IGNORE_MAGIC_SHIELD = SkillCalculatorBase.CalHurtFlag.IGNORE_MAGIC_SHIELD

calPowerFight = SkillCalculatorBase.calPowerFight
class Role(object):
    def __init__(self, dbRow = None):
        if dbRow:
            self.assignFromDB(dbRow)
            return 
        self.uid    = 0
        self.name   = ''
        self.job    = 0
        self.gender = 0
        self.level  = 0
        self.exp    = 0
    def assignFromDB(self, dbRow):
        self.uid    = int(dbRow[1])
        self.name   = dbRow[2]
        self.job    = int(dbRow[3])
        self.gender = int(dbRow[4])
        if self.gender != Base.Gender.MALE and self.gender != Base.Gender.FEMAIL:
            self.gender = Base.Gender.MALE
        self.level  = int(dbRow[5])
        self.exp    = int(dbRow[6])
        if self.job <  Base.Job.ZHANSHI or self.job > Base.Job.YOUXIA:
            self.job = Base.Job.ZHANSHI
        return self
class User(object):
    def __init__(self):
        self.accountId = 0
        self.username  = ''
        self.allRole   = []
    def addRole(self, role):
        self.allRole.append(role)
    def getRole(self, uid):
        for k in self.allRole:
            if k.uid == uid:
                return k
        return None
class NpcInfo:
    def __init__(self):
        self.npcChating           = None #正在使用的NPC
        self.lastChatContstent    = ''   #上次对话内容
def add1(player, v):
    player.hp    += v
    player.hpMax += v
    if player.hp < 0:
        player.hp = 0
    elif player.hp > player.hpMax:
        player.hp = player.hpMax
def add2(player, v):
    player.mp    += v
    player.mpMax += v
    if player.mp < 0:
        player.mp = 0
    elif player.mp > player.mpMax:
        player.mp = player.mpMax
def add3(player, v):
    player.physicAttackMin += v
def add4(player, v):
    player.physicAttackMax += v
def add5(player, v):
    player.magicAttackMin += v
def add6(player, v):
    player.magicAttackMax += v
def add7(player, v):
    player.physicDefendMin += v
def add8(player, v):
    player.physicDefendMax += v
def add9(player, v):
    player.magicDefendMin += v
def add10(player, v):
    player.magicDefendMax += v
def add11(player, v):
    player.crit += v
def add12(player, v):
    player.hit += v
def add13(player, v):
    player.avoid += v
def add14(player, v):
    player.attackSpeed += v
def add15(player, v):
    player.attackSing += v
def add16(player, v):
    player.attackInterval += v
def add17(player, v):
    player.attackDistance += v
def add18(player, v):
    player.moveSpeed += v
def add19(player, v):
    player.hurtAbsorb += v
def add20(player, v):
    player.hpAbsorb += v
PropHelper = {
    Base.PropType.HP                 : add1,
    Base.PropType.MP                 : add2,
    Base.PropType.HP_MAX             : add1,
    Base.PropType.MP_MAX             : add2,
    Base.PropType.PHYSIC_ATTACK_MIN  : add3,
    Base.PropType.PHYSIC_ATTACK_MAX  : add4,
    Base.PropType.MAGIC_ATTACK_MIN   : add5,
    Base.PropType.MAGIC_ATTACK_MAX   : add6,
    Base.PropType.PHYSIC_DEFEND_MIN  : add7,
    Base.PropType.PHYSIC_DEFEND_MAX  : add8,
    Base.PropType.MAGIC_DEFEND_MIN   : add9,
    Base.PropType.MAGIC_DEFEND_MAX   : add10,
    Base.PropType.CRIT               : add11,#暴击 影响暴击的概率	浮点数
    Base.PropType.HIT                : add12,#命中 影响攻击时的命中率	浮点数
    Base.PropType.AVOID              : add13,#躲避 被攻击时，影响降低被命中的概率	浮点数
    Base.PropType.ATTACK_SPEED       : add14,#攻击速度
    Base.PropType.ATTACK_SING        : add15,#攻击吟唱时间 影响释放攻击动作前的吟唱时间 吟唱时间内被攻击，有50%概率被打断，打断后需要重新吟唱，单位：秒  精确到毫秒
    Base.PropType.ATTACK_INTERVAL    : add16,#两次攻击之间间隔时间，单位：秒  精确到毫秒
    Base.PropType.ATTACK_DISTANCE    : add17,#攻击距离	以单位为中心的圆内可以攻击，近战标准值：100，远程值：600
    Base.PropType.MOVE_SPEED         : add18,#移动速度 影响地图上移动速度，标准值：100 精确到毫秒
    Base.PropType.HURT_ABSORB        : add19,#伤害吸收 受到伤害时，一定比例转换为生命值 百分比
    Base.PropType.HP_ABSORB          : add20,#吸血 当对敌人造成伤害时，吸取血量恢复自身生命值 百分比
}
class PkSinType:
    WHITE = 0
    ORANGE= 1
    RED   = 2

class MoneyBankCtrl:
    def __init__(self, gold = 0):
        self.gold = gold
class QieCuoCtrl:
    def __init__(self, owner):
        self.owener          = weakref.ref(owner)
        self.playerRefQieCuo = None
        self.startMap        = ''
        self.startX          = 0
        self.startY          = 0
        self.warnTimes       = 0#警告次数
        return
    def setQieCuoPlayer(self, player):
        owner = self.owener()
        self.startMap = owner.mapname
        self.startX = owner.x
        self.startY = owner.y
        self.playerRefQieCuo = weakref.ref(player)
#竞技场相关
class ArenaCtrl:
    def __init__(self):
        self.usedTimes          = 0#使用的次数
        self.usedDate           = 0
        self.score              = 0
        self.rank               = 0
        self.destPlayerRef      = None
    @property
    def leftChallengeTimes(self):
        return 10 - self.usedTimes
    def assignFromData(self, data):
        if data:
            #ffext.dump('arena assign', data)
            self.usedTimes = data.get('usedTimes', 0)
            self.usedDate = data.get('usedDate', 0)
            #self.rank = data.get('rank', 0)
            nowDate = ffext.todayAsInt()
            if nowDate != self.usedDate:
                self.usedDate = nowDate
                self.usedTimes = 0
        return
    def saveToData(self, data):
        info = {
            'usedTimes': self.usedTimes,
            'usedDate': self.usedDate
        }
        data['arenaInfo'] = info
        return True
class Player(object):
    NUM = 0
    def __del__(self):
        Player.NUM -= 1
        ffext.dump ('Player deleted', Player.NUM)
    def __init__(self, dbRow = None):
        Player.NUM += 1
        ffext.dump ('Player new', Player.NUM)
        #各个模块增加的属性
        self.allPropByModule = {}
        self.mapObj  = None
        self.session = None
        self.last_move_tm = time.time()
        self.friendCtrl = FriendModel.FriendCtrl()
        self.teamCtrl   = TeamModel.PersonTeamCtrl(self)
        self.guildCtrl  = GuildModel.PersonGuildCtrl(self)
        self.skillCtrl    = SkillModel.SkillCtrl(self)
        self.taskCtrl     = TaskModel.TaskCtrl(self)
        self.itemCtrl     = ItemModel.ItemCtrl(self)
        self.buffCtrl     = MonsterModel.BuffCtrl(self)
        self.petCtrl      = PetModel.PetCtrl(self)
        self.brotherCtrl  = TeamModel.PersonBrotherCtrl()
        self.mailCtrl = MailModel.MailCtrl(self)
        self.loginActCtrl = LoginRewardModel.LoginActCtrl(self)
        #竞技场相关的
        self.arenaCtrl = ArenaCtrl()
        self.marriageCtrl = MarryModel.PersonMarryCtrl(self)
        self.moneyBankCtrl= MoneyBankCtrl()
        self.tmpInfo      = {}#临时数据
        self.uid  = 0
        self.name = ''
        self.job  = 0
        self.gender=0
        self.gold  = 0
        self.mapname  = ''
        self.x    = 0
        self.y    = 0
        self.level= 1
        self.exp       = 0
        self.direction = 0
        #self.powerFight      = 0#战斗力 实时计算

        self.hp              = 0
        self.mp              = 0
        self.hpMax           = 0
        self.mpMax           = 0
        self.physicAttackMin = 0#最小物理攻击
        self.physicAttackMax = 0#最大物理攻击
        #法术攻击
        self.magicAttackMin  = 0#最小法术攻击
        self.magicAttackMax  = 0#最大法术攻击
        #物理防御
        self.physicDefendMin = 0#最小物理防御
        self.physicDefendMax = 0#最大物理防御
        #法术防御
        self.magicDefendMin  = 0#最小法术防御
        self.magicDefendMax  = 0#最大法术防御
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
        self.pkSinValue      = 0#pk 罪恶值 即杀人数量 白：无杀人记录 橙：杀一个人后在线时间12小时内显示，被人杀死后0.1%掉落身上任一装备 红色：在线时间12小时内杀2个人以上，被人杀死后1%掉落身上任一装备
        self.modeAttack      = 0#攻击模式


        self.hurtAbsorbLimit   = 0#伤害吸收量

        #战斗力
        self.fightPower      = 0
        self.sumAngerTmp     = 0#技能累计怒气是小数
        self.anger           = 0#怒气
        self.angerMax        = Base.MAX_ANGER
        #名字颜色
        self.nameColor       = 0
        #NPC相关的
        self.npcInfo         = NpcInfo()
        #用于回调的函数容器
        self.callbackFuncs   = {}
        #记录当前切磋的目标玩家
        self.ctrlQieCuo = QieCuoCtrl(self)

        self.last_logout = 0 #登出时间
        #在线时间
        self.logintime = ffext.getTime() #不存DB
        self.gametime = 0  #离线时计算，并存DB

        #状态机
        self.fsm         = None#MonsterAI.FSM(self)
        #if dbRow:
        self.assignFromDB(dbRow)
        #安全密码验证状态
        self.isVerified = False

    #检测判断player是否上次登出时间至今已跨天了
    def checkTimeAfterInit(self):
        ffext.dump("last_logout:", self.last_logout," gametime",self.gametime)
        if self.last_logout == 0:
            return True
        now = ffext.getTime()
        if ffext.tmIsSameDay(now, self.last_logout):
            #跨天了
            self.dailyRefresh()
            #是否跨周
            nowTm = ffext.datetime_now()
            if nowTm.weekday() == 0:
                self.weeklyRefresh()
            pass

        return True

    def forkFrom(self, srcPlayer, paramPropRate = 100):
        paramPropRate = paramPropRate * 1.0 / 100
        self.uid = idtool.allocTmpId()
        self.name = srcPlayer.name + '的幻象'
        self.job = Base.Job.ZHANSHI
        self.gender = srcPlayer.gender
        self.level = srcPlayer.level
        self.hp = int(srcPlayer.hp * paramPropRate)
        self.mp = int(srcPlayer.mp* paramPropRate)
        self.hpMax = int(srcPlayer.hpMax* paramPropRate)
        self.mpMax = int(srcPlayer.mpMax* paramPropRate)
        self.physicAttackMin = int(srcPlayer.physicAttackMin* paramPropRate)  # 最小物理攻击
        self.physicAttackMax = int(srcPlayer.physicAttackMax* paramPropRate)  # 最大物理攻击
        # 法术攻击
        self.magicAttackMin = int(srcPlayer.magicAttackMin* paramPropRate)  # 最小法术攻击
        self.magicAttackMax = int(srcPlayer.magicAttackMax* paramPropRate)  # 最大法术攻击
        # 物理防御
        self.physicDefendMin = int(srcPlayer.physicDefendMin* paramPropRate)  # 最小物理防御
        self.physicDefendMax = int(srcPlayer.physicDefendMax* paramPropRate)  # 最大物理防御
        # 法术防御
        self.magicDefendMin = int(srcPlayer.magicDefendMin* paramPropRate)  # 最小法术防御
        self.magicDefendMax = int(srcPlayer.magicDefendMax * paramPropRate) # 最大法术防御
        # 暴击
        self.crit = int(srcPlayer.crit * paramPropRate)# 暴击 影响暴击的概率	浮点数
        self.crit = int(srcPlayer.crit * paramPropRate) # 命中 影响攻击时的命中率	浮点数
        self.avoid = int(srcPlayer.avoid* paramPropRate) # 躲避 被攻击时，影响降低被命中的概率	浮点数
        self.attackSpeed = srcPlayer.attackSpeed  # 攻击速度
        self.attackSing =  srcPlayer.attackSing   # 攻击吟唱时间 影响释放攻击动作前的吟唱时间 吟唱时间内被攻击，有50%概率被打断，打断后需要重新吟唱，单位：秒  精确到毫秒
        self.attackInterval = srcPlayer.attackInterval  # 两次攻击之间间隔时间，单位：秒  精确到毫秒
        self.attackDistance = 4# 攻击距离	以单位为中心的圆内可以攻击，近战标准值：100，远程值：600
        self.moveSpeed =  srcPlayer.moveSpeed  # 移动速度 影响地图上移动速度，标准值：100 精确到毫秒
        self.hurtAbsorb = int(srcPlayer.hurtAbsorb* paramPropRate)  # 伤害吸收 受到伤害时，一定比例转换为生命值 百分比
        self.hpAbsorb =int( srcPlayer.hpAbsorb * paramPropRate) # 吸血 当对敌人造成伤害时，吸取血量恢复自身生命值 百分比
        self.modeAttack = srcPlayer.modeAttack # 攻击模式
        # 战斗力
        self.fightPower = srcPlayer.fightPower
        self.skillCtrl.learnSkill(110, 1)#自动获得普攻
        from model.monster import MonsterAI
        self.fsm = MonsterAI.FSM(self)


    @property
    def isWebDebug(self):
        return  self.session.isWebDebug
    def addAnger(self, value):
        if value < 0:
            self.anger += value
            if self.anger < 0:
                self.anger =0
        self.sumAngerTmp += value
        if self.sumAngerTmp > 1:
            val = int(self.sumAngerTmp)
            self.anger += val
            self.sumAngerTmp -= val
            if self.anger > self.angerMax:
                self.anger = self.angerMax
    def AddScoreArena(self, score, saveFlag = True):
        self.arenaCtrl.score += score
        if self.arenaCtrl.score < 0:
            self.arenaCtrl.score = 0
        if saveFlag:
            DbService.getPlayerService().saveAreaInfo(self)
    def updateLevelProp(self):#增加对一个的等级的属性
        propCfg        = getPlayerMgr().getProp(self.job, self.level)
        if not propCfg:
            propCfg = PlayerLevelProp()#全部显示为0
        propData = propCfg.toPropData()
        self.addModuleProp(Base.PropModule.LEVEL, propData)
    def addCallBack(self, func, arg = None):
        callbackId = idtool.allocTmpId()
        self.callbackFuncs[callbackId] = (func, arg)
        #ffext.dump('doCallBack', callbackId, self.callbackFuncs)
        return callbackId
    def doCallBack(self, callbackId):
        ffext.dump('doCallBack', callbackId, self.callbackFuncs)
        func = self.callbackFuncs.pop(callbackId, None)
        if None != func:
            func[0](self, func[1])
            return True
        return False
    #属性系统
    def subModuleProp(self, moduleName):
        propLog = self.allPropByModule.pop(moduleName, None)
        if None == propLog:
            return False
        for k, v in propLog.iteritems():
            func = PropHelper.get(k)
            if func != None:
                func(self, v * -1)
        self.fightPower = calPowerFight(self)
        return True
    def addModuleProp(self, moduleName, propData):
        self.subModuleProp(moduleName)
        for k, v in propData.iteritems():
            func = PropHelper.get(k)
            if func != None:
                func(self, v)
        self.allPropByModule[moduleName] = propData
        self.fightPower = calPowerFight(self)
        return
    def isMarry(self):
        return self.marriageCtrl.marryFlag == MsgDef.MarryStatusCmd.MARRY_STATUS_MARRIED
    def isDeath(self):
        return self.hp <= 0
    #类型
    def getType(self):
        return Base.PLAYER
    #获取在线时间
    def getGameTime(self):
        now = ffext.getTime()
        return self.gametime + (now - self.logintime)
    #每日刷新
    def dailyRefresh(self):
        self.logintime = ffext.getTime()
        self.gametime = 0
        self.loginActCtrl.dailyRefresh()
        return True
    #每周刷新（即每周一凌晨）
    def weeklyRefresh(self):
        return True
    #获取罪恶类型
    def getSinType(self):
        if self.pkSinValue <= 0:
            return PkSinType.WHITE
        elif self.pkSinValue <= 1:
            return PkSinType.ORANGE
        else:
            return PkSinType.RED
    #处理被击杀的事件
    def whenDie(self, objAttack):
        if objAttack.getType() == Base.PLAYER:
            try:#增加仇人
                if objAttack.uid not in self.friendCtrl.getEnemy():
                    DbService.getFriendService().addEnemy(self.uid, objAttack.uid, 0)
                    self.friendCtrl.addEnemy(objAttack)
                    from handler import  FriendHandler
                    opstype = MsgDef.FriendOpsClientCmd.ADD_ENEMY
                    self.sendMsg(MsgDef.ServerCmd.FRIEHND_MSG, FriendHandler.processFriendPlayerMsgRet(opstype, objAttack.uid, objAttack.name, objAttack.job, objAttack.gender, objAttack.level, True))
            except:
                ffext.error('whenDie error %s'%(self.name))
            pksinVal = 100
            if objAttack.guildCtrl.GuildRankWarWhenKillOther(self): #行会排名战
                pksinVal = 0
            if objAttack.guildCtrl.GuildWarWhenKillOther(self):#行会战进行中
                pksinVal = 0
            if pksinVal > 0:
                objAttack.pkSinValue += pksinVal
                #更新pk罪恶值
                objAttack.broadcast(MsgDef.ServerCmd.PK_SIN_UPDATE_OPS, MsgDef.PkSinUpdateRet(0, objAttack.pkSinValue, objAttack.uid))#objAttack.sendMsg(MsgDef.ServerCmd.PK_SIN_UPDATE_OPS, MsgDef.PkSinUpdateRet(0, objAttack.pkSinValue))
        self.processDrop()
        if self.mapObj and self.mapObj.copyMapHandler:
            #try:
            self.mapObj.copyMapHandler.handleObjDie(self.mapObj, self)
            #except:
                #ffext.error('mapObj.copyMapHandler.handleObjDie failed mapname=%s player=%s'%(self.mapObj.mapname, self.name))
        self.handleReborn()
        return
    def handleReborn(self, rebornTm = Base.REBORN_TIMEOUT, rebornLife = 10):
        #血回复10% 死亡后2s后，自动回到重生点
        if self.fsm:#模拟怪的player，不需要重生
            return
        playerref = weakref.ref(self)
        def cb():
            player = playerref()
            if not player:
                return
            if not player.isDeath():
                return
            player.hp = int(player.hpMax * 10 / 100)
            x = player.x
            y = player.y
            mapObj = player.mapObj
            if mapObj.cfg.reviveMap != None:
                mapName = mapObj.cfg.reviveMap.mapname
                x       = mapObj.cfg.reviveMap.x
                y       = mapObj.cfg.reviveMap.y
                mapObj =  MapMgr.getMapMgr().allocMap(mapName)
                #ffext.info('reborn name=%s, offlineMap=%s, x=%d, y=%d' % (player.name, player.mapname, x, y))
            #发送重生消息
            retMsg = buildPlayerInfoRet(player)
            retMsg.mapname = mapObj.mapname
            retMsg.x = x
            retMsg.y = y
            player.sendMsg(MsgDef.ServerCmd.REBORN, MsgDef.RebornRet(retMsg))
            mapObj.playerEnterMap(player, x, y, False)
            #ffext.info('reborn2 name=%s, offlineMap=%s, x=%d, y=%d' % (player.name, player.mapname, x, y))
            # 角色重生也要出发到副本
            if mapObj.copyMapHandler:
                try:
                    mapObj.copyMapHandler.handlePlayerRevive(mapObj, player)
                except:
                    ffext.error('mapObj.copyMapHandler.handlePlayerRevive failed mapname=%s player=%s' % (
                                mapObj.mapname, player.name))
            return
        ffext.timer(rebornTm, cb)
        return
    def processDrop(self):
        #橙：杀一个人后在线时间12小时内显示，被人杀死后0.1%掉落身上任一装备。红色：在线时间12小时内杀2个人以上，被人杀死后1%掉落身上任一装备
        sinType = self.getSinType()
        dropRate= 0
        if sinType == PkSinType.ORANGE:
            dropRate = 1#0.1%
        elif sinType == PkSinType.RED:
            dropRate = 10#0.1%
        if dropRate == 0:
            return False
        rand = random.randint(1, 1000)
        if rand > dropRate:
            return False
        #触发掉落
        self.itemCtrl.dropEquip()
        return  True
    #血量减少
    def subHurtResult(self, objSrc, hurtResult, msgFlag = True):
        if self.hp <= 0:
            return
        if objSrc and objSrc.getType() == Base.PLAYER:#攻击模式
            modeAttack = objSrc.modeAttack
            bQieCuo = False
            if modeAttack == MsgDef.EATTACK_MODE.PEACE:
                if objSrc and self.ctrlQieCuo.playerRefQieCuo != None:
                    dest = self.ctrlQieCuo.playerRefQieCuo()
                    if dest != None and dest.uid == objSrc.uid:  # 正在切磋
                        bQieCuo = True
                if False == bQieCuo:
                    return 0
            elif modeAttack == MsgDef.EATTACK_MODE.GUILD and self.guildCtrl.guildInfo != None and self.guildCtrl.guildInfo.guildID == objSrc.guildCtrl.guildInfo.guildID:
                return 0
            elif modeAttack == MsgDef.EATTACK_MODE.TEAM and \
                    ( (self.teamCtrl.teamID != 0 and self.teamCtrl.teamID == objSrc.teamCtrl.teamID) or \
                      (self.marriageCtrl and self.marriageCtrl.marryTotalInfo and self.marriageCtrl.marryTotalInfo.marryId == objSrc.marriageCtrl.marryTotalInfo.marryId) or\
                      (self.brotherCtrl.brotherInfo and self.brotherCtrl.brotherInfo.bid == objSrc.brotherCtrl.brotherInfo.bid) \
                      ):
                return 0
        #hurtResult.hurt += 1000
        if self.job == Base.Job.FASHI and hurtResult.hurtFlag != IGNORE_MAGIC_SHIELD:
            buff = self.buffCtrl.getBuff(MsgDef.BuffType.SHEN_MING_HU_TI)
            if buff:
                rateMian = buff.param.get(1, 0)
                #if rateMian < 0:
                    #rateMian = 0
                #elif rateMian > 100:
                    #rateMian = 100
                if self.hurtAbsorbLimit > hurtResult.hurt:
                    self.hurtAbsorbLimit -= hurtResult.hurt
                    hurtResult.hurt = 0
                elif self.hurtAbsorb == hurtResult.hurt:
                    self.hurtAbsorbLimit = 0
                    hurtResult.hurt = 0
                    self.buffCtrl.delBuff(MsgDef.BuffType.SHEN_MING_HU_TI)
                else:
                    hurtResult -= self.hurtAbsorbLimit
                    self.buffCtrl.delBuff(MsgDef.BuffType.SHEN_MING_HU_TI)
                #hurtResult.hurt -= int(hurtResult.hurt * rateMian / 100)
                ffext.dump('神明护体免伤', rateMian)
        hp = self.subHP(hurtResult.hurt, objSrc)
        #生命值每损失5%增加3点怒气值 即 1% 增加 0.6怒气值
        addAnger = hurtResult.hurt * 100.0 / self.hpMax * 0.6
        self.addAnger(addAnger)
        if msgFlag:
            retHurtMsg = MsgDef.HPHurtRet(self.uid, self.hp,self.mp, hurtResult.hurt, hurtResult.crit, hurtResult.hit, self.anger, self.angerMax)
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
            return hp
        else:
            hp = self.hp
            self.hp = 0
            if objSrc and self.ctrlQieCuo.playerRefQieCuo != None:
                dest = self.ctrlQieCuo.playerRefQieCuo()
                if dest != None and dest.uid == objSrc.uid:#正在切磋
                    self.hp = 1
            if self.hp == 0:
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
    def getMaxExp(self):
        return getPlayerMgr().getMaxExp(self.level)
    def assignFromDB(self, dbRow):
        if not dbRow:
            if self.level <= 0:
                self.level = 1
            self.updateLevelProp()
            return

        self.uid    = long(dbRow[0])
        self.name   = dbRow[1]
        self.job    = int(dbRow[2])
        self.gender = int(dbRow[3])
        self.mapname   = dbRow[4]
        self.x         = int(dbRow[5])
        self.y         = int(dbRow[6])
        self.direction = int(dbRow[7])
        self.level     = int(dbRow[8])
        if self.level <= 0:
            self.level = 1
        self.exp       = int(dbRow[9])
        self.updateLevelProp()
        self.hp        = int(dbRow[10])
        self.mp        = int(dbRow[11])
        if self.hp == 0:
            self.hp = self.hpMax
        if self.mp == 0:
            self.mp = self.mpMax

        if self.job <  Base.Job.ZHANSHI or self.job > Base.Job.YOUXIA:
            self.job = Base.Job.ZHANSHI
        self.skillCtrl.fromData(dbRow[12])
        self.gold      = int(dbRow[13])
        self.pkSinValue= int(dbRow[14])
        self.petCtrl.fromJson(dbRow[15])
        pkgmaxsize = int(dbRow[16])
        repomaxsize= int(dbRow[17])
        if pkgmaxsize > 0:
            self.itemCtrl.pkgMaxSize = pkgmaxsize
        if repomaxsize > 0:
            self.itemCtrl.repoMaxSize = repomaxsize
        extra = dbRow[18]
        if extra != '':
            extra = json.loads(extra)
        else:
            extra = {}
        brotherid = long(dbRow[19])
        if brotherid != 0:
            self.brotherCtrl.fromData(brotherid, self)
        #self.uidmarry = long(dbRow[20])
        self.moneyBankCtrl.gold = int(dbRow[20])
        marryId = long(dbRow[21])
        self.marriageCtrl = MarryModel.PersonMarryCtrl(self, marryId)
        ffext.dump('player.marryid', marryId)
        if marryId > 0:
            # do marry init
            self.marriageCtrl.initFromDb(self, dbRow)
        #ffext.dump('dbRow', dbRow)
        if dbRow[22] != '':
            self.arenaCtrl.score = long(dbRow[22])
            arenaInfo = extra.get('arenaInfo')
            self.arenaCtrl.assignFromData(arenaInfo)
        if dbRow[23] != '':
            self.last_logout = long(dbRow[23])
        if dbRow[24] != '':
            self.gametime = int(dbRow[24])
        if dbRow[25] !='':
            self.isSetPasswd = 1
        else:
            self.isSetPasswd = 0
        return self
    def sendMsg(self,cmd, msg):
        return self.session.sendMsg(cmd, msg)
    def sendShowUIMsg(self, uitype):
        return self.session.sendMsg(MsgDef.ServerCmd.SHOW_UI, MsgDef.ShowUiRet(uitype))
    def broadcast(self, cmd, msg, excludePlayer = None):
        return self.mapObj.broadcast(self.x, self.y, cmd, msg, excludePlayer)
    def foreachInMap(self, func):
        return self.mapObj.foreachInMap(func)
    def buildEnterMapMsg(self, flag = False):
        retPlayer = buildPlayerInfoRet(self)
        retMsg = MsgDef.EnterMapRet(retPlayer)
        retMsg2 = retMsg
        if flag != False:
            retMsg = ffext.encodeMsg(retMsg)
        #tmpTest = MsgDef.EnterMapRet()
        #ffext.thriftDecodeMsg(tmpTest, retMsg)
        #ffext.dump('buildEnterMapMsg', self.name, retMsg2, len(retMsg), tmpTest)
        return retMsg

    def buildLeaveMapMsg(self, flag=False):
        retMsg = MsgDef.LeaveMapRet(self.uid)
        if flag != False:
            retMsg = self.session.encodeMsg(retMsg)
        return retMsg
    def buildMoveMapMsg(self, newX, newY, flag=False):
        retMsg = MsgDef.MoveRet(newX, newY, self.uid, self.direction)
        if flag != False:
            retMsg = self.session.encodeMsg(retMsg)
        return retMsg
    def onLevelUp(self):
        self.skillCtrl.onLevelUp(self.level)
        TaskModel.onLevelUp(self)
        return
    def addGold(self, gold, msgFlag = False):
        self.gold += gold
        if self.gold < 0:
            self.gold = 0
        if msgFlag:
            sendPropUpdateMsg(self)
        return
    def addExp(self, exp, msgFlag = False):
        self.exp += exp
        oldLevel    = self.level
        curMaxExp   = getPlayerMgr().getMaxExp(self.level)
        while (self.exp >= curMaxExp and curMaxExp > 0):
            newLevel  = self.level + 1
            curNextExp= getPlayerMgr().getMaxExp(newLevel)
            if curNextExp <= 0:#top level
                self.exp = curMaxExp
                break
            self.exp -= curMaxExp
            curMaxExp   = curNextExp
            self.level= newLevel
            self.level= newLevel
            self.updateLevelProp()
            self.onLevelUp()
        if msgFlag:#发送消息给客户端
            self.session.sendMsg(MsgDef.ServerCmd.UPDATE_EXP, MsgDef.UpdateExpRet(self.exp, self.level, curMaxExp))
        return self.level - oldLevel
    def trigger(self, action, object, val = 1):
        return self.taskCtrl.trigger(action, object, val)
    def updateBuffMsg(self, uid=None):
        nowTm = ffext.getTime()
        for k, v in self.buffCtrl.allBuff.iteritems():
            v.endTime -= nowTm
        retMsg = MsgDef.UpdateBuffRet(self.buffCtrl.allBuff, uid)
        self.broadcast(MsgDef.ServerCmd.UPDATE_BUFF, retMsg)
        for k, v in self.buffCtrl.allBuff.iteritems():
            v.endTime += nowTm
    def showEffect(self, effectType):
        return self.broadcast(MsgDef.ServerCmd.SHOW_EFFECT, MsgDef.ShowEffectRet(effectType))
    #改变外观
    def SendChangeApprMsg(self):
        xiongJiaCfgId = 0
        xiongJiaItem = self.itemCtrl.allEquiped.get(Base.EQUIP_XIONGJIA_POS, None)
        if xiongJiaItem:
            xiongJiaCfgId = xiongJiaItem.itemCfg.cfgId
        self.broadcast(MsgDef.ServerCmd.CHANGE_APPR, MsgDef.ChangeApprRet(self.nameColor, xiongJiaCfgId, self.uid))
def buildPlayerInfoRet(player):
    mapname = None
    if player.mapObj:
        mapname = player.mapObj.mapname
        if player.mapObj.copyMapHandler:
            mapname = mapname.split('_')[0]
    else:
        mapname = player.mapname
    xiongJiaCfgId = 0
    xiongJiaItem  = player.itemCtrl.allEquiped.get(Base.EQUIP_XIONGJIA_POS, None)
    if xiongJiaItem:
        xiongJiaCfgId = xiongJiaItem.itemCfg.cfgId
    return MsgDef.PlayerInfoRet(player.uid, player.name, player.job, player.gender, mapname, player.x, player.y, player.level, player.direction,
                                 player.hp, player.hpMax, player.mp, player.mpMax, player.exp, player.getMaxExp(), player.pkSinValue, player.nameColor, xiongJiaCfgId)
def buildPropInfoRet(player, info):
    info.physicAttackMin = player.physicAttackMin
    info.physicAttackMax = player.physicAttackMax
    info.magicAttackMin = player.magicAttackMin
    info.magicAttackMax = player.magicAttackMax
    info.physicDefendMin = player.physicDefendMin
    info.physicDefendMax = player.physicDefendMax
    info.magicDefendMin = player.magicDefendMin
    info.magicDefendMax = player.magicDefendMax
    info.gold           = player.gold
    info.crit            = player.crit#暴击 影响暴击的概率	浮点数
    info.hit             = player.hit#命中 影响攻击时的命中率	浮点数
    info.avoid           = player.avoid#躲避 被攻击时，影响降低被命中的概率	浮点数
    info.attackSpeed     = player.attackSpeed#攻击速度
    info.attackSing      = player.attackSing#攻击吟唱时间 影响释放攻击动作前的吟唱时间 吟唱时间内被攻击，有50%概率被打断，打断后需要重新吟唱，单位：秒  精确到毫秒
    info.attackInterval  = player.attackInterval#两次攻击之间间隔时间，单位：秒  精确到毫秒
    info.attackDistance  = player.attackDistance#攻击距离	以单位为中心的圆内可以攻击，近战标准值：100，远程值：600
    info.moveSpeed       = player.moveSpeed#移动速度 影响地图上移动速度，标准值：100 精确到毫秒
    info.hurtAbsorb      = player.hurtAbsorb#伤害吸收 受到伤害时，一定比例转换为生命值 百分比
    info.hpAbsorb        = player.hpAbsorb#吸血 当对敌人造成伤害时，吸取血量恢复自身生命值 百分比
    info.fightPower      = player.fightPower
    info.anger           = player.anger
    info.angerMax        = player.angerMax
def sendPropUpdateMsg(player):
    tmpProp = MsgDef.PlayerPropRet()
    tmpProp.baseInfo = buildPlayerInfoRet(player)
    buildPropInfoRet(player, tmpProp)
    player.session.sendMsg(MsgDef.ServerCmd.UPDATE_PROP, tmpProp)
class ExpProp(Base.BaseObj):
    def __init__(self):
        self.level   = 0
        self.expMax  = 0
        self.standardMonsterExp = 0
        self.onhookHourExp      = 0
        self.onhook8HourExp     = 0
class PlayerLevelProp(Base.BaseObj):
    def __init__(self):
        self.level   = 0
        self.expMax  = 0
        self.hp              = 0
        self.mp              = 0
        #物理攻击
        self.physicAttackMin = 0#最小物理攻击
        self.physicAttackMax = 0#最大物理攻击
        #法术攻击
        self.magicAttackMin  = 0#最小法术攻击
        self.magicAttackMax  = 0#最大法术攻击
        #物理防御
        self.physicDefendMin = 0#最小物理防御
        self.physicDefendMax = 0#最大物理防御
        #法术防御
        self.magicDefendMin  = 0#最小法术防御
        self.magicDefendMax  = 0#最大法术防御
        self.propData        = None#属性key -> 属性值
    def toPropData(self):
        if None != self.propData:
            return self.propData
        self.propData = {}
        self.propData[Base.PropType.HP_MAX] = self.hp
        self.propData[Base.PropType.MP_MAX] = self.mp
        self.propData[Base.PropType.PHYSIC_ATTACK_MIN] = self.physicAttackMin
        self.propData[Base.PropType.PHYSIC_ATTACK_MAX] = self.physicAttackMax
        self.propData[Base.PropType.MAGIC_ATTACK_MIN]  = self.magicAttackMin
        self.propData[Base.PropType.MAGIC_ATTACK_MAX]  = self.magicAttackMax
        self.propData[Base.PropType.PHYSIC_DEFEND_MIN] = self.physicDefendMin
        self.propData[Base.PropType.PHYSIC_DEFEND_MAX] = self.physicDefendMax
        self.propData[Base.PropType.MAGIC_DEFEND_MIN]  = self.magicDefendMin
        self.propData[Base.PropType.MAGIC_DEFEND_MAX]  = self.magicDefendMax
        toDel = []
        for k,v in self.propData.iteritems():
            if v == 0:
                toDel.append(k)
        for k in toDel:
            self.propData.pop(k, None)
        return self.propData

#定时，自动回血
def recoverHpMp(session):
    player = session.player
    if player.getSinType() != PkSinType.WHITE:
        curTm  = ffext.getTime()#跟随在线时间罪恶值会消掉，罪恶值累计在线时间4小时减少100罪恶值。
        lastTm = player.tmpInfo.get('_lastCheckSin_', 0)
        if lastTm == 0:
            player.tmpInfo['_lastCheckSin_'] = curTm
        elif  curTm  - lastTm > 2*60:#TODO
            player.tmpInfo['_lastCheckSin_'] = curTm
            player.pkSinValue -= 10#TODO 100
            if player.pkSinValue < 0:
                player.pkSinValue = 0
            #更新pk罪恶值
            session.sendMsg(MsgDef.ServerCmd.PK_SIN_UPDATE_OPS, MsgDef.PkSinUpdateRet(0, player.pkSinValue))
        #TODO
    if player.mapObj == None or player.hp == 0 or player.hp >= player.hpMax:
        return
    player.addHPMsg(int(player.hpMax / 100))
def autoRecoverHpMp():
    #ffext.dump('autoRecoverHpMp...')
    ffext.getSessionMgr().foreach(recoverHpMp)
    ffext.timer(Base.PLAYER_RECOVER_HPMP_MS, autoRecoverHpMp)
    return
class PlayerMgr(Base.BaseObj):
    def __init__(self):
        self.levelMax   = 100
        self.level2prop = {} #level -> PlayerLevelProp
        self.level2exp  = {}
        #随机角色名配置
        self.randName1 = []
        self.randName2 = []
        self.randName3 = []
        self.randName4 = []
        self.randName5 = []
        return
    def init(self):
        #if  len(self.level2exp) == 0:

        db = ffext.allocDbConnection('cfg',ffext.getConfig('-cfg'))
        ret = db.queryResult('select level,expmax,standard_monster_exp,onhook_hour_exp,onhook_8hour_exp from level2exp')
        self.level2exp = {}
        self.levelMax  = 0
        for i in range(0, len(ret.result)):
            row = ret.result[i]
            expProp = ExpProp()
            expProp.level = int(row[0])
            expProp.expMax = ffext.strToNum(row[1])
            expProp.standardMonsterExp = ffext.strToNum(row[2])
            expProp.onhookHourExp = ffext.strToNum(row[3])
            expProp.onhook8HourExp = ffext.strToNum(row[4])
            self.level2exp[expProp.level] = expProp
            if expProp.level > self.levelMax :
                self.levelMax   = expProp.level

        self.level2prop = {}
        for job in Base.ALL_JOB:
            self.level2prop[job] = {}
            ret = db.queryResult('select level,hp,mp,physic_attack_min,physic_attack_max,magic_attack_min,magic_attack_max,physic_defend_min, \
physic_defend_max,magic_defend_min,magic_defend_max from levelprop%d'%(job))

            for i in range(0, len(ret.result)):
                row = ret.result[i]
                prop = PlayerLevelProp()
                prop.level  = int(row[0])
                prop.hp     = ffext.strToNum(row[1])
                prop.mp     = ffext.strToNum(row[2])
                prop.physicAttackMin = ffext.strToNum(row[3])
                prop.physicAttackMax = ffext.strToNum(row[4])
                prop.magicAttackMin = ffext.strToNum(row[5])
                prop.magicAttackMax = ffext.strToNum(row[6])
                prop.physicDefendMin  = ffext.strToNum(row[7])
                prop.physicDefendMax  = ffext.strToNum(row[8])
                prop.magicDefendMin  = ffext.strToNum(row[9])
                prop.magicDefendMax  = ffext.strToNum(row[10])

                self.level2prop[job][prop.level] = prop
            ffext.dump('load level2prop job=%d num=%d'%(job, len(self.level2prop[job])))
        self.readRandNames()
        return True
    def readRandNames(self):
        sql = 'select name1, name2, name3, name4, name5 from randnames'
        db = ffext.allocDbConnection('cfg',ffext.getConfig('-cfg'))
        ret = db.queryResult(sql)
        self.randName1 = []
        self.randName2 = []
        self.randName3 = []
        self.randName4 = []
        self.randName5 = []
        for row in ret.result:
            if row[0] != '':
                self.randName1.append(row[0])
            if row[1] != '':
                self.randName2.append(row[1])
            if row[2] != '':
                self.randName3.append(row[2])
            if row[3] != '':
                self.randName4.append(row[3])
            if row[4] != '':
                self.randName5.append(row[4])
    def randName(self, gender):
        rand = random.randint(0, len(self.randName1) - 1)
        name1= self.randName1[rand]
        name2= ''
        while True:
            if gender == Base.Gender.MALE:
                rand = random.randint(0, len(self.randName2) - 1)
                name2= self.randName2[rand]
            else:
                rand = random.randint(0, len(self.randName3) - 1)
                name2= self.randName3[rand]
            break
        return name1+name2
    def getProp(self, job, level):
        cfg = self.level2prop.get(job)
        if cfg:
            return cfg.get(level)
        return None
    def getMaxExp(self, level):
        cfg = self.level2exp.get(level)
        if cfg:
            return cfg.expMax
        return 0

gPlayerMgr = PlayerMgr()
def getPlayerMgr():
    return gPlayerMgr

