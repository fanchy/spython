# -*- coding: utf-8 -*-
import random
import weakref
import ffext
import idtool
from base   import Base
from mapmgr import MapMgr
from db import DbService
import msgtype.ttypes as MsgDef
import copy
import json

EQUIP_QH_PROP_TYPE = {
    1101 : [Base.PropType.PHYSIC_ATTACK_MIN, Base.PropType.PHYSIC_ATTACK_MAX],
    1102 : [Base.PropType.MAGIC_DEFEND_MIN, Base.PropType.MAGIC_DEFEND_MAX],
    1103 : [Base.PropType.PHYSIC_DEFEND_MIN, Base.PropType.PHYSIC_DEFEND_MAX],
    1104 : [Base.PropType.HP_MAX],
    1105 : [Base.PropType.HP_MAX],
    1106 : [Base.PropType.PHYSIC_ATTACK_MIN, Base.PropType.PHYSIC_ATTACK_MAX],
    1107 : [Base.PropType.PHYSIC_ATTACK_MIN, Base.PropType.PHYSIC_ATTACK_MAX],
    1108 : [Base.PropType.HP_MAX],

    2101 : [Base.PropType.MAGIC_ATTACK_MIN, Base.PropType.MAGIC_ATTACK_MAX],
    2102 : [Base.PropType.MAGIC_DEFEND_MIN, Base.PropType.MAGIC_DEFEND_MAX],
    2103 : [Base.PropType.PHYSIC_DEFEND_MIN, Base.PropType.PHYSIC_DEFEND_MAX],
    2104 : [Base.PropType.HP_MAX],
    2105 : [Base.PropType.HP_MAX],
    2106 : [Base.PropType.MAGIC_ATTACK_MIN, Base.PropType.MAGIC_ATTACK_MAX],
    2107 : [Base.PropType.MAGIC_ATTACK_MIN, Base.PropType.MAGIC_ATTACK_MAX],
    2108 : [Base.PropType.HP_MAX],

    3101 : [Base.PropType.MAGIC_ATTACK_MIN, Base.PropType.MAGIC_ATTACK_MAX],
    3102 : [Base.PropType.MAGIC_DEFEND_MIN, Base.PropType.MAGIC_DEFEND_MAX],
    3103 : [Base.PropType.PHYSIC_DEFEND_MIN, Base.PropType.PHYSIC_DEFEND_MAX],
    3104 : [Base.PropType.HP_MAX],
    3105 : [Base.PropType.HP_MAX],
    3106 : [Base.PropType.MAGIC_ATTACK_MIN, Base.PropType.MAGIC_ATTACK_MAX],
    3107 : [Base.PropType.MAGIC_ATTACK_MIN, Base.PropType.MAGIC_ATTACK_MAX],
    3108 : [Base.PropType.HP_MAX],

    4101 : [Base.PropType.PHYSIC_ATTACK_MIN, Base.PropType.PHYSIC_ATTACK_MAX],
    4102 : [Base.PropType.MAGIC_DEFEND_MIN, Base.PropType.MAGIC_DEFEND_MAX],
    4103 : [Base.PropType.PHYSIC_DEFEND_MIN, Base.PropType.PHYSIC_DEFEND_MAX],
    4104 : [Base.PropType.HP_MAX],
    4105 : [Base.PropType.HP_MAX],
    4106 : [Base.PropType.PHYSIC_ATTACK_MIN, Base.PropType.PHYSIC_ATTACK_MAX],
    4107 : [Base.PropType.PHYSIC_ATTACK_MIN, Base.PropType.PHYSIC_ATTACK_MAX],
    4108 : [Base.PropType.HP_MAX],
}
class StengthenCfg(Base.BaseObj):#强化相关的配置
    def __init__(self, row = None):
        if row == None:
            row = (0, 0, 0, 0, 0, 0, '0.0%', 0, 0, 0,
                   0, 0 , 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        self.level       = int(row[2]) #强化等级
        self.consumeId   = int(row[3])
        self.consumeNum  = int(row[4])
        self.consumeGold = int(row[5])
        self.rate        = int(float(row[6].split('%')[0]))#暴击 影响暴击的概率	浮点数
        self.hp              = int(row[7])
        #物理攻击
        self.physicAttackMin = int(row[8])#最小物理攻击
        self.physicAttackMax = int(row[9])#最大物理攻击
        #法术攻击
        self.magicAttackMin  = int(row[10])#最小法术攻击
        self.magicAttackMax  = int(row[11])#最大法术攻击
        #物理防御
        self.physicDefendMin = int(row[12])#最小物理防御
        self.physicDefendMax = int(row[13])#最大物理防御
        #法术防御
        self.magicDefendMin  = int(row[14])#最小法术防御
        self.magicDefendMax  = int(row[15])#最大法术防御
        #强化的部位 属性对应的系数
        self.strengthenRateCfg   = None #job -> equipType ->  Rate
        #属性数据暂存转换
        self.propData = {}
        self.propData[Base.PropType.HP_MAX] = self.hp
        #self.propData[Base.PropType.MP_MAX] = self.mp
        self.propData[Base.PropType.PHYSIC_ATTACK_MIN] = self.physicAttackMin
        self.propData[Base.PropType.PHYSIC_ATTACK_MAX] = self.physicAttackMax
        self.propData[Base.PropType.MAGIC_ATTACK_MIN]  = self.magicAttackMin
        self.propData[Base.PropType.MAGIC_ATTACK_MAX]  = self.magicAttackMax
        self.propData[Base.PropType.PHYSIC_DEFEND_MIN] = self.physicDefendMin
        self.propData[Base.PropType.PHYSIC_DEFEND_MAX] = self.physicDefendMax
        self.propData[Base.PropType.MAGIC_DEFEND_MIN]  = self.magicDefendMin
        self.propData[Base.PropType.MAGIC_DEFEND_MAX]  = self.magicDefendMax
    def toPropData(self, equipType):
        propTypes = EQUIP_QH_PROP_TYPE[equipType]
        newprop = {}
        for k in propTypes:
            v = self.propData.get(k)
            if v == None:
                continue
            newprop[k] = v
        return newprop
class ItemCfg(Base.BaseObj):
    def __init__(self):
        self.cfgId           = 0
        self.name            = ''
        self.itemType        = 0
        self.quality         = 0
        self.needLevel       = 0
        self.propType        = 0
        self.bindType        = 0
        self.job             = 0
        self.desc            = ''#描述
        self.decomposePrize  = 0#分解价格
        self.arenaScore      = 0#竞技场积分
        self.flagDieJia      = 0#释放可以叠加
        #所有的对应的强化等级配置
        self.allStrengthenCfg = {} #level -> config
        #属性数据暂存转换
        self.propData        = None

        self.price           = 0  #购买价格
    def assignCfg(self, row):
        if row == None:
            row = (0, '', 0, 0, 0, 0, 0, 0, 0, 0,
                   0, 0 , 0, 0, 0, 0, 0, 0, 0, 0,
                   0, '0.0%', '0.0%', '0.0%', 0, 0, 0, 0, 0, 0, 0)
        self.cfgId  = int(row[0])
        self.name   = row[1]
        self.itemType = int(row[2])
        self.quality = int(row[3])
        self.needLevel = int(row[4])
        self.propType = int(row[5])
        self.bindType  = int(row[6])
        self.job  = int(row[7])
        self.suitid = int(row[8])
        self.powerfight = 0#int(row[9])
        if row[10].isdigit():
            self.base_powerfight = int(row[10])
        else:
            self.base_powerfight = 0
        self.hp              = int(row[11])
        self.mp              = int(row[12])
        #物理攻击
        self.physicAttackMin = int(row[13])#最小物理攻击
        self.physicAttackMax = int(row[14])#最大物理攻击
        #法术攻击
        self.magicAttackMin  = int(row[15])#最小法术攻击
        self.magicAttackMax  = int(row[16])#最大法术攻击
        #物理防御
        self.physicDefendMin = int(row[17])#最小物理防御
        self.physicDefendMax = int(row[18])#最大物理防御
        #法术防御
        self.magicDefendMin  = int(row[19])#最小法术防御
        self.magicDefendMax  = int(row[20])#最大法术防御
        #暴击
        self.crit            = int(float(row[21].split('%')[0]) * Base.CRIT_RATE_BASE / 100)#暴击 影响暴击的概率	浮点数
        self.hit             = int(float(row[22].split('%')[0]) * Base.HIT_RATE_BASE / 100)#命中 影响攻击时的命中率	浮点数
        self.avoid           = int(float(row[23].split('%')[0]) * Base.AVOID_RATE_BASE / 100)#躲避 被攻击时，影响降低被命中的概率	浮点数

        self.attackSpeed     = int(row[24])#攻击速度
        self.attackSing      = int(row[25])#攻击吟唱时间 影响释放攻击动作前的吟唱时间 吟唱时间内被攻击，有50%概率被打断，打断后需要重新吟唱，单位：秒  精确到毫秒
        self.attackInterval  = int(row[26])#两次攻击之间间隔时间，单位：秒  精确到毫秒
        self.attackDistance  = int(row[27])#攻击距离	以单位为中心的圆内可以攻击，近战标准值：100，远程值：600
        self.moveSpeed       = int(row[28])#移动速度 影响地图上移动速度，标准值：100 精确到毫秒
        self.hurtAbsorb      = int(row[29])#伤害吸收 受到伤害时，一定比例转换为生命值 百分比
        self.hpAbsorb        = int(row[30])#吸血 当对敌人造成伤害时，吸取血量恢复自身生命值 百分比
    def toPropData(self):
        if None != self.propData:
            return self.propData
        self.propData = {}
        try:
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

            self.propData[Base.PropType.CRIT]              = self.crit
            self.propData[Base.PropType.HIT]               = self.hit
            self.propData[Base.PropType.AVOID]             = self.avoid
            self.propData[Base.PropType.ATTACK_SPEED]      = self.attackSpeed
            self.propData[Base.PropType.ATTACK_SING]       = self.attackSing
            self.propData[Base.PropType.ATTACK_INTERVAL]   = self.attackInterval
            self.propData[Base.PropType.ATTACK_DISTANCE]   = self.attackDistance
            self.propData[Base.PropType.MOVE_SPEED]        = self.moveSpeed
            self.propData[Base.PropType.HURT_ABSORB]       = self.hurtAbsorb
            self.propData[Base.PropType.HP_ABSORB]         = self.hpAbsorb
        except:
            ffext.error("item cfgid=%d.name=%s no prop data", self.cfgId, self.name)
        toDel = []
        for k,v in self.propData.iteritems():
            if v == 0:
                toDel.append(k)
        for k in toDel:
            self.propData.pop(k, None)
        return self.propData
    def toStrenthenPropData(self, level):
        if level <= 0:
            return {}

        #ffext.dump('toStrenthenPropData', self.allStrengthenCfg[1].propData, self.allStrengthenCfg[2].propData)
        strengthenCfg = self.allStrengthenCfg.get(level)
        propStrengthen = None
        if strengthenCfg:
            propStrengthen = strengthenCfg.toPropData(self.job*1000 + self.itemType)
        else:
            propStrengthen = {}
        return propStrengthen
class Item(Base.BaseObj):
    def __init__(self):
        self.ownerref     = None#技能拥有者,玩家或者怪
        self.itemCfg      = None
        self.uid          = 0
        self.createTime   = 0
        self.position     = 0#包裹中的位置

        self.mapObj       = None
        self.x            = 0
        self.y            = 0
        #强化等级
        self.strengthenLevel = 0
        self.lefttimes       = 1
        #inherit propData
        self.propExt     = {}

        #售卖标记
        self.toSell      = 0
        self.toSellNum   = 0
    def subLeftTimes(self, num):
        self.lefttimes -= num
    def getType(self):
        return Base.ITEM
    def buildEnterMapMsg(self, flag = False):
        retMsg = MsgDef.ItemEnterMapRet(self.uid, self.itemCfg.cfgId, self.x, self.y)
        if flag != False:
            retMsg = ffext.encodeMsg(retMsg)#, flag, flag
        return retMsg

    def buildLeaveMapMsg(self, flag=False):
        retMsg = MsgDef.LeaveMapRet(self.uid)
        if flag != False:
            retMsg = ffext.encodeMsg(retMsg)#, flag, flag
        return retMsg
    def toStrenthenPropData(self):
        return self.itemCfg.toStrenthenPropData(self.strengthenLevel)
    def toAllProp(self):
        propData = self.itemCfg.toPropData()
        if self.strengthenLevel > 0:
            extProp = self.toStrenthenPropData()
            for k, v in extProp.iteritems():
                if propData.get(k) != None:
                    propData[k] += v
                else:
                    propData[k] = v
        return propData

def splitItem(player, itemOld, num):
    cfgId = itemOld.itemCfg.cfgId
    itemCfg = getItemMgr().getCfgByCfgId(cfgId)
    if not itemCfg:
        return None
    item = Item()
    item.ownerref   = weakref.ref(player)
    item.itemCfg    = itemCfg
    item.uid        = idtool.allocItemId()
    item.createTime = ffext.getTime()
    itemOld.lefttimes -= num
    item.lefttimes = num
    DbService.getPlayerService().updateItemLeftTimes(itemOld.ownerref(), itemOld)
    return item
def createItemByCfg(itemCfg, id = None):
    item = Item()
    item.itemCfg    = itemCfg
    if None != id:
        item.uid     = id
    else:
        item.uid        = idtool.allocItemId()
        item.createTime = ffext.getTime()
    return item
def createItemByName(name, num = 1):
    itemCfg = getItemMgr().getCfgByName(name)
    if not itemCfg:
        ffext.error('addItemByName no cfg name=%s'%(name))
        return None
    if num == 1:
        return createItemByCfg(itemCfg)
    else:
        ret = []
        for k in range(num):
            item = createItemByCfg(itemCfg)
            ret.append(item)
        return ret
    return None
class CollectCfg(Base.BaseObj):
    def __init__(self):
        self.showName = ''
        self.mapname  = ''
        self.x        = 0
        self.y        = 0
        self.itemGive =''
        self.itemNum  = 0

class ItemCtrl(Base.BaseObj):
    def __init__(self, owner):
        self.ownerref   = weakref.ref(owner)
        self.allItem    = {}   #uid -> item 包裹中的道具都放在这里
        #记录所有的包裹位置
        self.allPkgPos  = {}   #postion-> itemId
        self.allEquiped = {}   #已经穿在身上的装备position -> item
        self.allRepo    = {}   #仓库pos -> item
        self.pkgMaxSize = Base.DEFAULT_PKG_SIZE   #默认大小
        self.repoMaxSize= Base.DEFAULT_REPO_SIZE   #默认大小

        self.toSellItems = {}  #待售物品列表
        return
    def getFreePkgSize(self):
        return self.pkgMaxSize - len(self.allItem)
    def getItem(self, itemId):
        return self.allItem.get(itemId)
    def addToExistItemTims(self, cfgId, leftNum):
        item = None
        for k, item in self.allItem.iteritems():
            if item.itemCfg.cfgId == cfgId and item.lefttimes < Base.MAX_DIEJIA_NUM:
                item.lefttimes += leftNum
                if item.lefttimes <= Base.MAX_DIEJIA_NUM:
                    leftNum = 0
                    DbService.getPlayerService().updateItemLeftTimes(self.ownerref(), item)
                    break
                else:
                    leftNum = item.lefttimes - Base.MAX_DIEJIA_NUM
                    item.lefttimes = Base.MAX_DIEJIA_NUM
                    DbService.getPlayerService().updateItemLeftTimes(self.ownerref(), item)
        return leftNum,item
    def addItemByName(self, name, num = 1):
        itemCfg = getItemMgr().getCfgByName(name)
        if not itemCfg:
            ffext.error('addItemByName no cfg name=%s'%(name))
            return None
        if itemCfg.flagDieJia:
            item = None
            num, oldItem = self.addToExistItemTims(itemCfg.cfgId, num)
            if oldItem and num == 0:
                return oldItem
            while True:
                if self.getFreePkgSize() <= 0:
                    self.ownerref().sendMsg(MsgDef.ServerCmd.ERROR_MSG, MsgDef.ErrorMsgRet(0, MsgDef.ClientCmd.MAKE_ITEM, '包裹空间不足!'))
                    return
                item = self.addItemByCfg(itemCfg)
                if not item:
                    ffext.error('addItemByCfgId name:%s failed'%(name))
                    return None
                item.lefttimes = num
                if item.lefttimes > Base.MAX_DIEJIA_NUM:
                    num = item.lefttimes - Base.MAX_DIEJIA_NUM
                    item.lefttimes = Base.MAX_DIEJIA_NUM
                else:
                    num = 0
                DbService.getPlayerService().updateItemLeftTimes(self.ownerref(), item)
                if num <= 0:
                    break
            return item
        elif num == 1:
            return self.addItemByCfg(itemCfg)
        else:
            ret = []
            for k in range(num):
                item = self.addItemByCfg(itemCfg)
                ret.append(item)
            return ret
    def addItemByCfgId(self, cfgId, num = 1):
        itemCfg = getItemMgr().getCfgByCfgId(cfgId)
        #ffext.dump('DIEJIAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA', itemCfg.flagDieJia)
        if not itemCfg:
            return None
        if itemCfg.flagDieJia:
            #ffext.dump('WRONG')
            item = None
            num, oldItem = self.addToExistItemTims(itemCfg.cfgId, num)
            if oldItem and num == 0:
                return oldItem
            while True:
                if self.getFreePkgSize() <= 0:
                    self.ownerref().sendMsg(MsgDef.ServerCmd.ERROR_MSG, MsgDef.ErrorMsgRet(0, MsgDef.ClientCmd.MAKE_ITEM, '包裹空间不足!'))
                    return
                item = self.addItemByCfg(itemCfg)
                if not item:
                    ffext.error('addItemByCfgId cfgId:%d failed'%(cfgId))
                    return None
                item.lefttimes = num
                if item.lefttimes > Base.MAX_DIEJIA_NUM:
                    num = item.lefttimes - Base.MAX_DIEJIA_NUM
                    item.lefttimes = Base.MAX_DIEJIA_NUM
                else:
                    num = 0
                DbService.getPlayerService().updateItemLeftTimes(self.ownerref(), item)
                if num <= 0:
                    break
            return item
        elif num == 1:
            if self.getFreePkgSize() <= 0:
                self.ownerref().sendMsg(MsgDef.ServerCmd.ERROR_MSG,
                                        MsgDef.ErrorMsgRet(0, MsgDef.ClientCmd.MAKE_ITEM, '包裹空间不足!'))
                return
            return self.addItemByCfg(itemCfg)
        else:
            ret = []
            ffext.dump('num', num)
            for k in range(num):
                if self.getFreePkgSize() <= 0:
                    self.ownerref().sendMsg(MsgDef.ServerCmd.ERROR_MSG,
                                            MsgDef.ErrorMsgRet(0, MsgDef.ClientCmd.MAKE_ITEM, '包裹空间不足!'))
                    return
                item = self.addItemByCfg(itemCfg)
                ret.append(item)
            return ret
    #分配一个包裹位置
    def setPosition(self, item):
        for k in range(self.pkgMaxSize):
            if self.allPkgPos.get(k) != None:
                continue
            self.allPkgPos[k] = item.uid
            item.position     = k
            return True
        return False

    #添加到包裹
    def addItemByCfg(self, itemCfg, saveFlag = True, id = 0, position = 0, propExt = None):
        item = Item()
        item.ownerref   = self.ownerref
        item.itemCfg    = itemCfg
        if propExt != None:
            item.propExt = propExt
        if id:
            item.uid     = id
            item.position= position

            if position >= 0:
                if  position > Base.REPO_POS_START:
                    self.allRepo[position - Base.REPO_POS_START] = item
                elif self.allPkgPos.get(position) == None:#重复位置，只好放到包裹最后
                    self.allPkgPos[position] = id
                else:
                    self.setPosition(item)
                    DbService.getPlayerService().updateItemPos(self.ownerref(), item)
            else:
                self.allEquiped[abs(position)] = item
                #一上线，自动穿上装备
                #增加属性
                propData = item.toAllProp()
                self.ownerref().addModuleProp(itemCfg.itemType, propData)
        else:
            item.uid        = idtool.allocItemId()
            item.createTime = ffext.getTime()
            if self.setPosition(item) == False:
                return None
        if position >= 0 :
            for k,v in self.allItem.iteritems():
                if v.position == position:
                    position += 1
            if position < Base.REPO_POS_START:
                item.position = position
                self.allItem[item.uid] = item
            if position >= Base.REPO_POS_START:
                item.position = position
                self.allRepo[item.position] = item
        if saveFlag:
            DbService.getPlayerService().addItem(self.ownerref(), item)
        return item
    #从包裹中删除
    def delItem(self, itemId, bUpdate = True):
        item = self.allItem.pop(itemId, None)
        if not item:
            return item
        self.allPkgPos.pop(item.position, None)
        if bUpdate:
            DbService.getPlayerService().delItemById(self.ownerref(), itemId)
        return item

    #从仓库中删除
    def delItemFromRepo(self, itemId, position, bUpdate = True):
        ffext.dump('DELITEMID', itemId)
        item = self.allRepo.pop(position, None)
        if not item:
            return item
        self.allPkgPos.pop(item.position, None)
        if bUpdate:
            DbService.getPlayerService().delItemById(self.ownerref(), itemId)
        return item
    #从包裹中移动
    def moveItemToPkg(self, oldItem, bUpdate = True):
        oldItem.ownerref = self.ownerref
        self.allItem[oldItem.uid] = oldItem
        self.setPosition(oldItem)
        if bUpdate:
            DbService.getPlayerService().addItem(self.ownerref(), oldItem)
        return oldItem
    #从db中构建
    def fromData(self, result):
        for row in result:
            itemId    = int(row[0])
            cfgId     = int(row[1])
            position  = int(row[3])
            lefttimes = int(row[5])
            propExt   = row[6]
            if propExt == '':
                propExt = {}
            else:
                propExtDB = json.loads(propExt)
                propExt = {}
                for k, v in propExtDB.iteritems():
                    propExt[int(k)] = int(v)
            if None == propExt:
                propExt = {}
            itemCfg   = getItemMgr().getCfgByCfgId(cfgId)
            if not itemCfg:
                ffext.error('uid=%d,cfgId=%d not found'%(self.ownerref().uid, cfgId))
                continue
            item = self.addItemByCfg(itemCfg, False, itemId, position, propExt)
            item.lefttimes = lefttimes
            item.createTime = ffext.str2timestamp(row[2])
            item.strengthenLevel = int(row[4])
        # needItemDebug = [30111101, 30111102, 30111103, 30111104, 30111105, 30111106, 30111107, 30111108, 1020101, 1020201, 1020301]
        #
        # for k in needItemDebug:
        #     if self.countItemNumbyCfgId(k) <= 0:
        #         self.addItemByCfgId(k)
        return True
    #整理包裹
    def arrangePkg(self):
        #按照物品id 重新排列
        allItemId = [v for k, v in self.allItem.iteritems()]
        allItemId.sort(lambda x,y:cmp(x.itemCfg.itemType,y.itemCfg.itemType))
        self.allPkgPos = {}
        flag = False
        isRepo = True
        offset = 0
        for k in range(len(allItemId)):
            item = allItemId[k]
            #self.allPkgPos[k] = item.uid
            #if item.position != k and item.position < Base.REPO_POS_START:
                #item.position = k
                #DbService.getPlayerService().updateItemPos(self.ownerref(), item)
            #ffext.dump("POSITION", item.position)
            for j in range(k+1, len(allItemId)):
                anotherItem = allItemId[j]
                ffext.dump("POSITION", item.position, anotherItem.position)
                if item.position < Base.REPO_POS_START and anotherItem.position < Base.REPO_POS_START:
                    isRepo = False
                ffext.dump("isRepo", isRepo)
                if item.itemCfg.cfgId == anotherItem.itemCfg.cfgId and item.lefttimes <= Base.MAX_DIEJIA_NUM \
                        and anotherItem.lefttimes <= Base.MAX_DIEJIA_NUM and item.itemCfg.flagDieJia and not isRepo:
                    num_minus = Base.MAX_DIEJIA_NUM - item.lefttimes
                    if num_minus >= anotherItem.lefttimes:
                        item.lefttimes += anotherItem.lefttimes
                        self.delItem(anotherItem.uid)
                        flag = True
                    else:
                        anotherItem.lefttimes -= num_minus
                        item.lefttimes = Base.MAX_DIEJIA_NUM
                        DbService.getPlayerService().updateItemLeftTimes(self.ownerref(), anotherItem)
                    DbService.getPlayerService().updateItemLeftTimes(self.ownerref(), item)
                    break
            if item.position >= Base.REPO_POS_START:
                self.allRepo[item.position] = item
                self.delItem(item, False)
                offset += 1
            if item.position != k and item.position < Base.REPO_POS_START:
                item.position = k - offset
            DbService.getPlayerService().updateItemPos(self.ownerref(), item)
        #allItemId = [v for k, v in self.allItem.iteritems()]
        #allItemId.sort(lambda x,y:cmp(x.itemCfg.itemType,y.itemCfg.itemType))
        #self.allPkgPos = {}
        #for i in range(len(allItemId)):
            #self.allPkgPos[i] = item.uid
            #if item.position != i:
                #item.position = i
                #DbService.getPlayerService().updateItemPos(self.ownerref(), item)
        return flag

    #装备一个道具到身上
    def equipItem(self, item, retMsg):
        player  = self.ownerref()
        itemCfg = item.itemCfg
        postion = Base.EQUIP_TYPE_TO_POS.get(itemCfg.itemType)
        if postion == None:
            return Base.lang('此物品无法装备!')
        if player.level < itemCfg.needLevel:
            return Base.lang('等级不足')
        if player.job != itemCfg.job:
            return Base.lang('不是本职业的装备!!!')
        #装备后，从包裹中删除
        oldItem = self.allItem.pop(item.uid, None)
        if not oldItem:
            return Base.lang('包裹中没有此物品!!!!')
        self.allPkgPos.pop(oldItem.position, None)
        #如果此位置上有装备，先卸下此装备
        oldEquip = self.allEquiped.get(postion)
        self.allEquiped[postion] = item
        pkgPos = item.position
        retMsg.itemIdEquip = item.uid
        item.position = -1 * postion
        if oldEquip:#放入包裹
            oldId  = oldEquip.uid
            retMsg.itemIdUnEquip    = oldId
            retMsg.itemIdUnEquipPos = pkgPos
            oldEquip.position       = pkgPos
            self.allPkgPos[pkgPos]  = oldId
            self.allItem[oldId]     = oldEquip
            DbService.getPlayerService().updateItemPos(player, oldEquip)
        DbService.getPlayerService().updateItemPos(player, item)
        #增加属性
        propData = item.toAllProp()
        player.addModuleProp(itemCfg.itemType, propData)
        player.SendChangeApprMsg()
        return None

    #def movePkgToRepo(self, uid, newPos):
        #player  = self.ownerref()
        #if newPos == 0:
            #for k in range(1, self.repoMaxSize + 1):
                #if self.allRepo.get(k) == None:
                    #newPos = k
                    #break
            #if newPos == 0:
                #return False
        #elif self.allRepo.get(newPos):
            #return False
        #if newPos > self.repoMaxSize:
            #return False
        #oldItem = self.allItem.pop(uid, None)
        #if not oldItem:
            #return False
        #self.allPkgPos.pop(oldItem.position, None)
        #self.allRepo[newPos] = oldItem
        #oldItem.position     = newPos + Base.REPO_POS_START
        #DbService.getPlayerService().updateItemPos(player, oldItem)
        #return oldItem


    #包裹->仓库
    #newItemCounts = 0
    def movePkgToRepo(self, uid, itemNum):
        player  = self.ownerref()
        oldItem = self.allItem.get(uid, None)
        if not oldItem:
            return False
        elif itemNum > oldItem.lefttimes:
            return False
        #elif not oldItem:
            #return False
        elif len(self.allRepo) > self.repoMaxSize:
            return False
        elif len(self.allRepo) == self.repoMaxSize:
            if not oldItem.itemCfg.flagDieJia:
                return False
            for k, v in self.allRepo.iteritems():
                newItem = v
                if newItem.itemCfg.cfgId == oldItem.itemCfg.cfgId:
                    if newItem.lefttimes + itemNum <= Base.MAX_DIEJIA_NUM:
                        if itemNum == oldItem.lefttimes:
                            oldItem = self.allItem.pop(uid, None)
                            newItem.lefttimes += itemNum
                            DbService.getPlayerService().delItemById(player,uid)
                        elif itemNum < oldItem.lefttimes:
                            oldItem.lefttimes -= itemNum
                            newItem.lefttimes += itemNum
                            DbService.getPlayerService().updateItemLeftTimes(player, oldItem)
                    else:
                        minus_num = Base.MAX_DIEJIA_NUM - newItem.lefttimes
                        newItem.lefttimes = Base.MAX_DIEJIA_NUM
                        oldItem.lefttimes -= minus_num
                        DbService.getPlayerService().updateItemLeftTimes(player, oldItem)
                    DbService.getPlayerService().updateItemLeftTimes(player, newItem)
                    break
            else:
                return False
        else:
            #ffext.dump('DIEJIA',oldItem)
            if oldItem.lefttimes == itemNum:
                newItem = copy.deepcopy(self.allItem.pop(uid, None))
                newItem.position += Base.REPO_POS_START
                newItem.uid = idtool.allocItemId()
                #ffext.dump("AAAAAAAAAA", self.allRepo)
                while self.allRepo.get(newItem.position, None):
                    newItem.position += 1
                self.allRepo[newItem.position] = newItem
                DbService.getPlayerService().delItemById(player, uid)
            else:
                #ffext.dump('OLDITEM', oldItem)
                #ffext.dump("  OK!!!!!!!!!!!!!!!!!!!!!")
                newItem = copy.deepcopy(oldItem)
                newItem.lefttimes = itemNum
                oldItem.lefttimes -= itemNum
                newItem.position += Base.REPO_POS_START
                newItem.uid = idtool.allocItemId()
                #ffext.dump("PPPPPPPPPPPPPPP",newItem.position)
                #ffext.dump("TTTTT", self.allRepo.get(newItem.position,None))
                while self.allRepo.get(newItem.position, None):
                    newItem.position += 1
                    ffext.dump("NEEPPPPPPPPPPPPP", newItem.position)
                self.allRepo[newItem.position] = newItem
                DbService.getPlayerService().updateItemLeftTimes(player,oldItem)
            #ffext.dump("NewItem", newItem)
            DbService.getPlayerService().addItem(player,newItem)
            #ffext.dump("11111111111111111111111")

        #oldItem = self.allItem.pop(uid, None)
        #self.allPkgPos.pop(oldItem.position, None)
        #self.allRepo[newPos] = oldItem
        #oldItem.position     = newPos + Base.REPO_POS_START
        #DbService.getPlayerService().updateItemPos(player, oldItem)
        return newItem

    #def moveRepoToPkg(self, uid, newPos):
        #player  = self.ownerref()
        #if newPos != 0 and self.allPkgPos.get(newPos) != None:
            #return False
        #oldItem = None
        #oldPos = 0
        #for k, v in self.allRepo.iteritems():
            #if v.uid == uid:
                #oldPos = k
                #oldItem = v
                #break
        #if None == oldItem:
            #return False
        #self.allRepo.pop(oldPos, None)
        #self.allItem[oldItem.uid] = oldItem
        #if newPos == 0:
            #self.setPosition(oldItem)
        #else:
            #self.allPkgPos[newPos] = oldItem.uid
            #oldItem.position     = newPos
        #DbService.getPlayerService().updateItemPos(player, oldItem)
        #return oldItem

    #仓库->包裹
    def moveRepoToPkg(self, uid, itemNum):
        player  = self.ownerref()
        ffext.dump('allRepo', self.allRepo)
        for k_o, v_o in self.allRepo.iteritems():
            ffext.dump("UIIIIIIIIIIIID", v_o.uid, uid)
            if v_o.uid == uid:
                oldItem = v_o
                position = k_o
                break
        else:
            return False
        if itemNum > oldItem.lefttimes:
            return False
        #elif not oldItem:
            #return False
        elif len(self.allItem) > self.pkgMaxSize:
            return False
        elif len(self.allItem) == self.pkgMaxSize:
            if not oldItem.itemCfg.flagDieJia:
                return False
            for k,v in self.allItem.iteritems():
                newItem = v
                if newItem.itemCfg.cfgId == oldItem.itemCfg.cfgId:
                    if newItem.lefttimes + itemNum <= Base.MAX_DIEJIA_NUM:
                        if itemNum == oldItem.lefttimes:
                            oldItem = self.allRepo.pop(position, None)
                            newItem.lefttimes += itemNum
                            DbService.getPlayerService().delItemById(player, oldItem.uid)
                        elif itemNum < oldItem.lefttimes:
                            oldItem.lefttimes -= itemNum
                            newItem.lefttimes += itemNum
                            DbService.getPlayerService().updateItemLeftTimes(player, oldItem)
                    else:
                        minus_num = Base.MAX_DIEJIA_NUM - newItem.lefttimes
                        newItem.lefttimes = Base.MAX_DIEJIA_NUM
                        oldItem.lefttimes -= minus_num
                        DbService.getPlayerService().updateItemLeftTimes(player, oldItem)
                    DbService.getPlayerService().updateItemLeftTimes(player, newItem)
                    break
            else:
                return False
        else:
            #ffext.dump('DIEJIA',oldItem)
            if oldItem.lefttimes == itemNum:
                newItem = copy.deepcopy(self.allRepo.pop(position, None))
                newItem.position -= Base.REPO_POS_START
                newItem.uid = idtool.allocItemId()
                for k,v in self.allItem.iteritems():
                    if v.position == newItem.position:
                        newItem.position += 1
                        continue
                self.allItem[newItem.uid] = newItem
                DbService.getPlayerService().delItemById(player, oldItem.uid)
            else:
                #ffext.dump('OLDITEM', oldItem)
                #ffext.dump("  OK!!!!!!!!!!!!!!!!!!!!!")
                newItem = copy.deepcopy(oldItem)
                newItem.lefttimes = itemNum
                oldItem.lefttimes -= itemNum
                newItem.position -= Base.REPO_POS_START
                newItem.uid = idtool.allocItemId()
                #ffext.dump("PPPPPPPPPPPPPPP",newItem.position)
                #ffext.dump("TTTTT", self.allRepo.get(newItem.position,None))
                for k,v in self.allItem.iteritems():
                    if v.position == newItem.position:
                        newItem.position += 1
                        continue
                self.allItem[newItem.uid] = newItem
                DbService.getPlayerService().updateItemLeftTimes(player,oldItem)
            #ffext.dump("NewItem", newItem)
            DbService.getPlayerService().addItem(player,newItem)
            #ffext.dump("11111111111111111111111")
        return newItem

    #def arrangeRepo(self):
        #allItem = [v for k, v in self.allRepo.iteritems()]
        #allItem.sort(lambda x,y:cmp(x.itemCfg.itemType,y.itemCfg.itemType))
        #self.allRepo = {}
        #player = self.ownerref()
        #for k in range(len(allItem)):
            #item = allItem[k]
            #self.allRepo[k] = item
            #if item.position != k + Base.REPO_POS_START:
                #item.position = k + Base.REPO_POS_START
                #DbService.getPlayerService().updateItemPos(player, item)
        #return True
    def arrangeRepo(self):
        #按照物品id 重新排列
        allRepoItem = [v for k, v in self.allRepo.iteritems()]
        allRepoItem.sort(lambda x,y:cmp(x.itemCfg.itemType,y.itemCfg.itemType))
        #self.allPkgPos = {}
        isRepo = True
        flag = False
        offset = 0
        #ffext.dump('LENNNNNNNN!', len(allRepoItem))
        for k in range(len(allRepoItem)):
            item = allRepoItem[k]
            #self.allPkgPos[k] = item.uid
            #if item.position != k and item.position < Base.REPO_POS_START:
                #item.position = k
                #DbService.getPlayerService().updateItemPos(self.ownerref(), item)
            #ffext.dump("POSIIIIII", item.position)#, anotherItem.position)
            for j in range(k+1, len(allRepoItem)):
                anotherItem = allRepoItem[j]
                #ffext.dump("POSIIIIII", item.position, anotherItem.position)
                if item.position < Base.REPO_POS_START and anotherItem.position < Base.REPO_POS_START:
                    isRepo = False
                if item.itemCfg.cfgId == anotherItem.itemCfg.cfgId and item.lefttimes <= Base.MAX_DIEJIA_NUM \
                        and anotherItem.lefttimes <= Base.MAX_DIEJIA_NUM and item.itemCfg.flagDieJia and isRepo:
                    num_minus = Base.MAX_DIEJIA_NUM - item.lefttimes
                    #ffext.dump("num_minus", num_minus)
                    if num_minus >= anotherItem.lefttimes:
                        ffext.dump("UIDDDDDDDDDDDD", anotherItem.uid)
                        item.lefttimes += anotherItem.lefttimes
                        self.delItemFromRepo(anotherItem.uid, anotherItem.position)
                        flag = True
                    else:
                        anotherItem.lefttimes -= num_minus
                        item.lefttimes = Base.MAX_DIEJIA_NUM
                        DbService.getPlayerService().updateItemLeftTimes(self.ownerref(), anotherItem)
                    DbService.getPlayerService().updateItemLeftTimes(self.ownerref(), item)
                    break
            if item.position < Base.REPO_POS_START:
                self.allItem[item.uid] = item
                self.delItemFromRepo(item.uid, item.position)
                offset += 1
            if item.position != k + Base.REPO_POS_START and item.position >= Base.REPO_POS_START:
                item.position = k + Base.REPO_POS_START - offset
            DbService.getPlayerService().updateItemPos(self.ownerref(), item)
        return flag
    #卸载一个道具
    def unequipItem(self, itemId, retMsg):
        player  = self.ownerref()
        if len(self.allItem) >= self.pkgMaxSize:
            return Base.lang('包裹已满!!')
        #如果此位置上有装备
        item = None
        for pos, itemObj in self.allEquiped.iteritems():
            if itemObj.uid == itemId:
                item = itemObj
                del self.allEquiped[pos]
                break
        if not item:
            return Base.lang('此物品无法卸下!!!')
        self.allItem[itemId] = item
        self.setPosition(item)
        if retMsg:
            retMsg.itemIdUnEquip    = itemId
            retMsg.itemIdUnEquipPos = item.position
        DbService.getPlayerService().updateItemPos(player, item)
        player.subModuleProp(item.itemCfg.itemType)
        return None
    #获取装备的某个道具
    def getEquipedItemById(self, itemId):
        for pos, itemObj in self.allEquiped.iteritems():
            if itemObj.uid == itemId:
                return itemObj
        return None
    #爆掉一个装备
    def dropEquip(self):
        player  = self.ownerref()
        allItemPos = [postion for postion, item in self.allEquiped]
        if len(allItemPos) == 0:
            return None
        selectDropPos = allItemPos[random.randint(0, len(allItemPos) - 1)]
        selecItem = self.allEquiped.pop(selectDropPos)
        DbService.getPlayerService().delItemById(player, selecItem.uid)
        #出现在地图上
        player.mapObj.itemEnterMap(selecItem, player.x + random.randint(-2, 2), player.y + random.randint(-2, 2))
    #计算某个道具的数量
    def countItemNumbyCfgId(self, cfgId):
        num = 0
        for k, item in self.allItem.iteritems():
            if item.itemCfg.cfgId == cfgId:
                if item.itemCfg.flagDieJia:
                    num += item.lefttimes
                else:
                    num += 1
        return num
    def countItemNumbyName(self, name):
        num = 0
        for k, item in self.allItem.iteritems():
            if item.itemCfg.name == name:
                if item.itemCfg.flagDieJia:
                    num += item.lefttimes
                else:
                    num += 1
        return num
    def getItemByCfgId(self, cfgId):
        for k, item in self.allItem.iteritems():
            if item.itemCfg.cfgId == cfgId:
                return item
        return None
    #扣除某个道具N个
    def subItemNumByCfgId(self, cfgId, num):
        needDel = []
        player  = self.ownerref()
        for k, item in self.allItem.iteritems():
            if item.itemCfg.cfgId == cfgId:
                if item.itemCfg.flagDieJia:
                    if item.lefttimes <= num:
                        item.lefttimes = 0
                        num -= item.lefttimes
                        needDel.append(k)
                    else:
                        item.lefttimes -= num
                        num = 0
                    DbService.getPlayerService().updateItemLeftTimes(player, item)
                else:
                    needDel.append(k)
                    num -= 1

                if num <= 0:
                    break

        for itemId in needDel:
            self.allItem.pop(itemId, None)
            DbService.getPlayerService().delItemById(player, itemId)
        return len(needDel) == num
    #扣除某个道具N个
    def subItemNumByName(self, name, num):
        needDel = []
        player  = self.ownerref()
        for k, item in self.allItem.iteritems():
            if item.itemCfg.cfgId == name:
                if item.itemCfg.flagDieJia:
                    if item.lefttimes <= num:
                        item.lefttimes = 0
                        num -= item.lefttimes
                        needDel.append(k)
                    else:
                        item.lefttimes -= num
                        num = 0
                    DbService.getPlayerService().updateItemLeftTimes(player, item)
                else:
                    needDel.append(k)
                    num -= 1

                if num <= 0:
                    break

        for itemId in needDel:
            self.allItem.pop(itemId, None)
            DbService.getPlayerService().delItemById(player, itemId)
        return len(needDel) == num



class ItemMgr(Base.BaseObj):
    def __init__(self):
        self.allItemCfg = {}#itemid -> itemcfg
        self.name2Cfg   = {}#name -> itemCfg
        self.allCollect = {}#uid -> collectItem
        self.arenaScoreItem = {} #cfg id -> itemCfg
    def readTable_strengthen_position(self, db):#return job -> equipType -> 属性率
        ret = {
            Base.Job.ZHANSHI : {},
            Base.Job.FASHI   : {},
            Base.Job.SHUSHI  : {},
            Base.Job.YOUXIA  : {},
        }
        sqlQHPos = 'select jobname,position ,positionname ,job ,propname ,propkey ,hp,physic_attack_min ,physic_attack_max ,magic_attack_min ,magic_attack_max ,'\
'physic_defend_min ,physic_defend_max ,magic_defend_min ,magic_defend_max    from strengthen_position '
        retQHPos = db.queryResult(sqlQHPos)
        propHelp = {
            1101: 7,
            1102: 13,
            1103: 11,
            1104: 6,
            1105: 6,
            1106: 7,
            1107: 7,
            1108: 6,

            2101: 9,
            2102: 13,
            2103: 11,
            2104: 6,
            2105: 6,
            2106: 9,
            2107: 9,
            2108: 6,

            3101: 9,
            3102: 13,
            3103: 11,
            3104: 6,
            3105: 6,
            3106: 9,
            3107: 9,
            3108: 6,

            4101: 7,
            4102: 13,
            4103: 11,
            4104: 6,
            4105: 6,
            4106: 7,
            4107: 7,
            4108: 6,
        }
        for k in retQHPos.result:
            job = int(k[3])
            equipType = int(k[1])
            propKey = int(k[5])
            #ffext.dump('readTable_strengthen_position', propKey)
            index = propHelp[propKey]
            propRate= float(k[index])
            ret[job][equipType] = propRate
        return ret
    def readTable_strengthen_equip(self, db, strengthenRateCfg):#return startLevel -> strengthlevel -> cfg
        #等级对应的强化属性具体数值
        sqlQH = 'select minlevel,maxlevel,level,consume_id,consume_num,gold,rate,hp,physic_attack_min ,physic_attack_max,magic_attack_min  ,magic_attack_max  ,physic_defend_min  ,physic_defend_max  ,magic_defend_min  ,'\
'magic_defend_max   from strengthen_equip '
        retQH = db.queryResult(sqlQH)
        tmpQHData = {}
        for k in retQH.result:
            startLevel = int(k[0])
            level = int(k[2])
            tmpDict = tmpQHData.get(startLevel)
            sCfg = StengthenCfg(k)
            sCfg.strengthenRateCfg = strengthenRateCfg
            if tmpDict != None:
                tmpDict[level] = sCfg
            else:
                tmpDict = {}
                tmpDict[level] = sCfg
                tmpQHData[startLevel] = tmpDict
        return tmpQHData
    #读取所有装备
    def readtalbe_item(self, db):
        sql = "select cfgid,name,itemtype,descText,quality,needlevel,bindtype,job,decompose_prize,arena_score,diejia_flag, price from item where cfgid <> ''"
        ret = db.queryResult(sql)
        allItem = {}
        allName = {}
        self.arenaScoreItem = {}
        for k in ret.result:
            itemCfg = ItemCfg()
            itemCfg.cfgId           = int(k[0])
            itemCfg.name            = k[1].strip()
            itemCfg.itemType        = int(k[2])
            itemCfg.desc            = k[3]
            itemCfg.quality         = int(k[4])
            itemCfg.needLevel       = int(k[5])
            itemCfg.bindType        = int(k[6])
            itemCfg.job             = int(k[7])
            itemCfg.decomposePrize  = int(k[8])
            itemCfg.arenaScore      = int(k[9])
            itemCfg.flagDieJia      = int(k[10])
            if k[11]:
                itemCfg.price       = int(k[11])
            else:
                itemCfg.price       = 0
            allItem[itemCfg.cfgId]  = itemCfg
            allName[itemCfg.name]   = itemCfg
            #ffext.dump('readtable_item [%s]'%(itemCfg.name))
            if itemCfg.arenaScore > 0:
                #ffext.dump('arenaScore', itemCfg.name, itemCfg.arenaScore)
                self.arenaScoreItem[itemCfg.cfgId] = (itemCfg, itemCfg.arenaScore)
        self.allItemCfg = allItem
        self.name2Cfg   = allName
        return ret
    def init(self):#读取任务配置
        #位置 对应 强化哪个属性配置
        db = ffext.allocDbConnection('cfg',ffext.getConfig('-cfg'))

        self.readtalbe_item(db)
        strengthenRateCfg         = self.readTable_strengthen_position(db)
        qhPropInfo                = self.readTable_strengthen_equip(db, strengthenRateCfg)
        #装备属性配置
        ffext.dump('begin read item table')
        sql = 'select cfgid,name,itemtype,quality,needlevel,proptype,bindtype ,job ,suitid,base_powerfight as powerfight,base_powerfight,\
hp ,mp ,physic_attack_min ,physic_attack_max ,magic_attack_min ,magic_attack_max ,physic_defend_min ,physic_defend_max ,magic_defend_min ,magic_defend_max ,\
crit,hit ,avoid,attackspeed,attacksing ,attackinterval ,attackdistance ,movespeed  ,hurtabsorb,hpabsorb from equipprop '
        ret = db.queryResult(sql)
        ffext.dump('begin read item end')
        for row in ret.result:
            cfgId = int(row[0])
            itemCfg = self.allItemCfg.get(cfgId)
            if None == itemCfg:
                itemCfg = ItemCfg()
                self.allItemCfg[cfgId] = itemCfg
                self.name2Cfg[row[1]]    = itemCfg
            itemCfg.assignCfg(row)
            startLevel = itemCfg.needLevel - (itemCfg.needLevel % 10)
            if startLevel < 1:
                startLevel = 1
            QHCfgData = qhPropInfo.get(startLevel)
            if not QHCfgData:
                continue
            itemCfg.allStrengthenCfg = QHCfgData
        ffext.dump('load item num=%d %d'%(len(self.allItemCfg), len(self.name2Cfg)))
        self.initCollectPoint()
        return True
    def initCollectPoint(self):
        sql = 'select name,mapid,x,y,num,item from collectpoint'
        db = ffext.allocDbConnection('cfg',ffext.getConfig('-cfg'))
        ret = db.queryResult(sql)
        for row in ret.result:
            itemNameShow = row[0].strip()
            mapName  = row[1].strip()
            x        = int(row[2])
            y        = int(row[3])
            num      = int(row[4])
            itemGive = row[5].strip()
            rangeMax = 1
            item = genItem(mapName, itemNameShow, x, y, num, rangeMax)
            if None == item:
                continue
            cfg = CollectCfg()
            cfg.showName = itemNameShow
            cfg.mapname = mapName
            cfg.x = x
            cfg.y = y
            cfg.itemGive = itemGive
            cfg.itemNum = num
            self.allCollect[item.uid] = cfg
    def getCollectCfgById(self, uid):
        return self.allCollect.get(uid)
    def getCfgByCfgId(self, index):
        return self.allItemCfg.get(index)
    def getCfgByName(self, name):
        return self.name2Cfg.get(name)
gItemMgr = ItemMgr()
def getItemMgr():
    return gItemMgr


def tmpBuildItem(item, itemCfg):
    item.uid = 0
    item.itemCfgId = itemCfg.cfgId
    item.name      = itemCfg.name
    item.strengthenLevel = 0
    item.lefttimes = 1
    #item.propExt = itemObj.propExt
    #item.propStrengthen = itemObj.toStrenthenPropData()
    return item
def genItem(mapName, itemName, x, y, num, rangeMax):
    item = Item()
    #item.ownerref   = self.ownerref
    itemCfg = getItemMgr().getCfgByName(itemName)
    if not itemCfg:
        ffext.error("genItem failed [%s]"%(itemName))
        return None
    item.itemCfg    = itemCfg
    item.uid        = idtool.allocItemId()
    item.createTime = ffext.getTime()
    mapObj   = MapMgr.getMapMgr().allocMap(mapName)
    if not mapObj:
        ffext.error('genItem failed map=%s'%(mapName))
        return None
    if False == mapObj.itemEnterMap(item, x, y):
        return None
    return item


USE_ITEM_FUNC = {}

def UseBind(itemType):
    def genFunc(func_):
        global USE_ITEM_FUNC
        USE_ITEM_FUNC[itemType] = func_
        return func_
    return genFunc

@UseBind(201)
def use201(player, item):#使用血瓶
    ffext.dump('use201....', item.itemCfg.name)
    param = item.itemCfg.desc.split('恢复')[1].split('点')[0]
    param = int(param)
    ffext.dump('use201....', item.itemCfg.name, param)

    playerref = weakref.ref(player)
    refData = [param, 0]
    def cb():
        playerobj = playerref()
        if not playerobj:
            return
        refData[1] += 1
        playerobj.addHPMsg(int(refData[0] / 10))
        if refData[1] < 10:
            ffext.timer(1000, cb)
        ffext.dump('use201 timer recover....', refData[0], refData[1])
        return
    ffext.timer(1000, cb)
    return
@UseBind(202)
def use202(player, item):#使用魔瓶
    ffext.dump('use201....', item.itemCfg.name)
    param = item.itemCfg.desc.split('恢复')[1].split('点')[0]
    param = int(param)
    ffext.dump('use201....', item.itemCfg.name, param)

    playerref = weakref.ref(player)
    refData = [param, 0]

    def cb():
        playerobj = playerref()
        if not playerobj:
            return
        refData[1] += 1
        playerobj.addHPMsg(0, int(refData[0] / 10))
        if refData[1] < 10:
            ffext.timer(1000, cb)
        ffext.dump('use202 timer recover....', refData[0], refData[1])
        return

    ffext.timer(1000, cb)
    return
@UseBind(203)
def use203(player, item):#使用大补丸
    ffext.dump('use201....', item.itemCfg.name)
    param = item.itemCfg.desc.split('回复')[1].split('点')[0]
    param2 = item.itemCfg.desc.split('，')[1].split('点')[0]
    cd = item.itemCfg.desc.split('时间')[1].split('秒')[0]
    param = int(param)
    param2= int(param2)
    cd = int(cd)
    ffext.dump('use201....', item.itemCfg.name, param, param2, cd)

    now = ffext.getTime()
    key = 'LastUse%d'%(item.itemCfg.itemType)
    lastTm = player.tmpInfo.get(key, 0)
    if now - lastTm <= cd:
        return 'CD时间未到'
    player.tmpInfo[key] = now
    player.addHPMsg(param, param2)
    return

@UseBind(402)
def use402(player, item):
    return None



#寄售、拍卖行定时器
def auctionOnTimer():
    def callback(ret):
        if ret:
            for row in ret.result:
                attachNode = MsgDef.MailAttachData()
                attachNode.type = 0
                #itemCfgId
                attachNode.arg1 = int(row[2])
                #lefttimes
                attachNode.arg2 = int(row[3])

                auctionId = int(row[0])
                #角色uid
                uid = int(row[1])

                title = '拍卖行到期'
                msg = "您拍卖的物品已到期！"
                from MailModel import doSendMailToPlayer
                doSendMailToPlayer(None, uid, 2, title, msg, [attachNode])
                DbService.getPlayerService().deleteAuction(auctionId)
    DbService.getPlayerService().queryTimeAuction(ffext.getTime(), callback=callback)
    ffext.dump("!!!!!!!!!!!!!! Timer!!!!!!!!!!!!!", ffext.getTime())
    ffext.timer(Base.AUCTION_TIMER_MS, auctionOnTimer)
