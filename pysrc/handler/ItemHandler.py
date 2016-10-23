# -*- coding: utf-8 -*-
import ffext
import json
import weakref
import idtool
import msgtype.ttypes as MsgDef
from base import Base
from model import  ItemModel, PlayerModel, TeamModel, SkillModel, MailModel
from db import DbService
import random
def buildErrMsg(cmd, errMsg):
    return MsgDef.ErrorMsgRet(0, cmd, errMsg)#'cmd=%d,errMsg=%s'%(cmd, errMsg)
def buildItem(item, itemObj):
    item.uid = itemObj.uid
    itemCfg = itemObj.itemCfg
    item.itemCfgId = itemCfg.cfgId
    item.name      = itemCfg.name
    item.strengthenLevel = itemObj.strengthenLevel
    item.lefttimes = itemObj.lefttimes
    item.propExt = itemObj.propExt
    item.propStrengthen = itemObj.toStrenthenPropData()
    return True
#包裹数据
@ffext.onLogic(MsgDef.ClientCmd.QUERY_PKG, MsgDef.EmptyReq)
def processQueryPkg(session, msg = None):
    player = session.player
    if player.itemCtrl.arrangePkg():
        processQueryPkg(session)
    retMsg = MsgDef.QueryPkgRet({}, player.itemCtrl.pkgMaxSize)
    for itemId, itemObj in player.itemCtrl.allItem.iteritems():
        item = MsgDef.Item()
        buildItem(item, itemObj)
        retMsg.allItem[itemObj.position] = item
    #ffext.dump('processQueryPkg', retMsg)
    session.sendMsg(MsgDef.ServerCmd.QUERY_PKG, retMsg)
    return


#装备数据
@ffext.onLogic(MsgDef.ClientCmd.QUERY_EQUIP, MsgDef.QueryEquipReq)
def processQueryEquip(session, msg = None):
    if not msg:
        player = session.player
        retMsg = MsgDef.QueryEquipRet({})
        for itemId, itemObj in player.itemCtrl.allEquiped.iteritems():
            item = MsgDef.Item()
            buildItem(item, itemObj)
            retMsg.allItem[abs(itemObj.position)] = item
        session.sendMsg(MsgDef.ServerCmd.QUERY_EQUIP, retMsg)
        #ffext.dump('processQueryEquip', retMsg)
        return
    tgt  = ffext.getSessionMgr().findByUid(msg.uid)
    retMsg = MsgDef.QueryEquipRet({},msg.uid)
    for itemId, itemObj in tgt.player.itemCtrl.allEquiped.iteritems():
        item = MsgDef.Item()
        buildItem(item, itemObj)
        retMsg.allItem[abs(itemObj.position)] = item
    session.sendMsg(MsgDef.ServerCmd.QUERY_EQUIP, retMsg)
    #ffext.dump('processQueryEquip', retMsg)
    return
#穿戴装备
@ffext.onLogic(MsgDef.ClientCmd.EQUIP_ITEM, MsgDef.EquipOpsReq)
def processEquipItem(session, msg):
    player  = session.player
    itemCtrl= player.itemCtrl
    item   = itemCtrl.getItem(msg.uid)
    if not item:
        session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.EQUIP_ITEM, Base.lang('物品不存在')))
        return
    retMsg = MsgDef.EquipItemRet()
    retErr = itemCtrl.equipItem(item, retMsg)
    if retErr:
        print(retErr)
        session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.EQUIP_ITEM, retErr))
        return
    session.sendMsg(MsgDef.ServerCmd.EQUIP_ITEM, retMsg)
    ffext.dump('processEquipItem', retMsg)
    PlayerModel.sendPropUpdateMsg(player)
    processQueryEquip(session)
    processQueryPkg(session)

#卸下装备
@ffext.onLogic(MsgDef.ClientCmd.UNEQUIP_ITEM, MsgDef.EquipOpsReq)
def processUnEquipItem(session, msg):
    player  = session.player
    itemCtrl= player.itemCtrl
    retMsg = MsgDef.UnEquipItemRet()
    retErr = itemCtrl.unequipItem(msg.uid, retMsg)
    if retErr:
        print(retErr)
        session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.UNEQUIP_ITEM, retErr))
        return
    session.sendMsg(MsgDef.ServerCmd.UNEQUIP_ITEM, retMsg)
    PlayerModel.sendPropUpdateMsg(player)
    processQueryPkg(session)

#扔装备到地图上
@ffext.onLogic(MsgDef.ClientCmd.THROW_ITEM, MsgDef.EquipOpsReq)
def processThrowItem(session, msg):
    ffext.dump('processThrowItem', msg)
    player  = session.player
    itemCtrl= player.itemCtrl
    retMsg = MsgDef.ThrowItemRet(msg.uid)
    item   = itemCtrl.delItem(msg.uid)
    #if item:
    #    player.mapObj.itemEnterMap(item, player.x, player.y)
    session.sendMsg(MsgDef.ServerCmd.THROW_ITEM, retMsg)
    processQueryPkg(session)

#从地图上捡起道具
@ffext.onLogic(MsgDef.ClientCmd.PICKUP_ITEM, MsgDef.PickUpItemReq)
def processPickupItem(session, msg):
    player  = session.player
    itemCtrl= player.itemCtrl
    mapObj  = player.mapObj
    item = mapObj.getObjByPos(msg.x, msg.y, Base.ITEM)
    mapObj.itemLeaveMap(item)
    if not item:
        return
    retMsg = MsgDef.PickUpItemRet()
    retMsg.item = MsgDef.Item()
    buildItem(retMsg.item, item)
    session.sendMsg(MsgDef.ServerCmd.PICKUP_ITEM, retMsg)
    processQueryPkg(session)

#强化装备
@ffext.onLogic(MsgDef.ClientCmd.STRENGTHEN_ITEM, MsgDef.StrengthenItemReq)
def processStrengthenItem(session, msg):
    player  = session.player
    itemCtrl= player.itemCtrl
    item = itemCtrl.getItem(msg.uid)
    itemEquiped = None
    if not item:
        itemEquiped = itemCtrl.getEquipedItemById(msg.uid)
        item = itemEquiped
    if not item:
        retErr = Base.lang('物品不存在')
        session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.STRENGTHEN_ITEM, retErr))
        return
    curLevel = item.strengthenLevel
    itemCfg = item.itemCfg
    stengthenCfg = itemCfg.allStrengthenCfg.get(curLevel)
    if not stengthenCfg:
        retErr = Base.lang('此物品不能强化!')
        session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.STRENGTHEN_ITEM, retErr))
        return
    if curLevel >= 9:
        retErr = Base.lang('此物品达到最大强化等级，不可强化')
        session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.STRENGTHEN_ITEM, retErr))
        return
    ffext.dump('processStrengthenItem', stengthenCfg)
    consumeItemCfg = ItemModel.getItemMgr().getCfgByCfgId(stengthenCfg.consumeId)
    if not consumeItemCfg:
        retErr = Base.lang('此物品不能强化!!')
        session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.STRENGTHEN_ITEM, retErr))
        return
    if player.gold < stengthenCfg.consumeGold:
        retErr = Base.lang('金币不足:%d'%(stengthenCfg.consumeGold))
        session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.STRENGTHEN_ITEM, retErr))
        return

    haveNum = itemCtrl.countItemNumbyCfgId(stengthenCfg.consumeId)
    needNum = stengthenCfg.consumeNum
    if haveNum < needNum:
        retErr = Base.lang('材料不足,需要:%s*%d'%(consumeItemCfg.name, stengthenCfg.consumeNum))
        session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.STRENGTHEN_ITEM, retErr))
        return
    itemCtrl.subItemNumByCfgId(stengthenCfg.consumeId, needNum)

    #强化成功
    oldPropExt = item.toStrenthenPropData()
    item.strengthenLevel = getStrengthenLevel(item.strengthenLevel)
    newPropExt = item.toStrenthenPropData()
    DbService.getPlayerService().updateStrengthenLevel(player, item)
    retMsg = MsgDef.StrengthenItemRet(msg.uid)
    retMsg.level = item.strengthenLevel
    retMsg.propAdded = {}
    for k, v in newPropExt.iteritems():
        addVal = v - oldPropExt.get(k, 0)
        retMsg.propAdded[k] = addVal
    
    session.sendMsg(MsgDef.ServerCmd.STRENGTHEN_ITEM, retMsg)
    processQueryPkg(session)
    processQueryEquip(session)
    #增加属性
    if itemEquiped:
        propData = item.toAllProp()
        player.addModuleProp(itemCfg.itemType, propData)
        PlayerModel.sendPropUpdateMsg(player)

#强化装备辅助函数，强化等级
def getStrengthenLevel(strengthenLevel):
    successRate = [1, 0.9, 0.8, 0.7, 0.5, 0.4, 0.25, 0.15, 0.1, 0.08]
    randomRate = random.random()
    ffext.dump('randomRate', randomRate)
    if randomRate < successRate[strengthenLevel]:
        return strengthenLevel + 1
    else:
        if strengthenLevel < 6:
            return strengthenLevel
        elif strengthenLevel < 9:
            return strengthenLevel - 1





#使用道具
@ffext.onLogic(MsgDef.ClientCmd.USE_ITEM, MsgDef.UseItemReq)
def processUseItem(session, msg):
    player  = session.player
    itemCtrl= player.itemCtrl
    item = itemCtrl.getItem(msg.uid)
    if not item:
        retErr = Base.lang('不存在')
        session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.USE_ITEM, retErr))
        return
    func = ItemModel.USE_ITEM_FUNC.get(item.itemCfg.itemType)
    retMsg = MsgDef.UseItemRet(msg.uid, 0)
    if func:
        retErr = func(player, item)
        if retErr.__class__ == str:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.USE_ITEM, retErr))
            return
        if item.itemCfg.flagDieJia:
            item.subLeftTimes(1)
            retMsg.leftTimes = item.lefttimes
            if item.lefttimes <= 0:
                item   = itemCtrl.delItem(msg.uid)
            DbService.getPlayerService().updateItemLeftTimes(player, item)
        else:
            item   = itemCtrl.delItem(msg.uid)

        session.sendMsg(MsgDef.ServerCmd.USE_ITEM, retMsg)
        processQueryPkg(session)
        return
    else:
        retErr = Base.lang('不可使用')
        session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.USE_ITEM, retErr))
        return

    #return

#叠加物品
@ffext.onLogic(MsgDef.ClientCmd.DIEJIA_ITEM, MsgDef.DieJiaItemReq)
def processDieJiaItem(session, msg):
    player  = session.player
    itemCtrl= player.itemCtrl
    itemFrom = itemCtrl.getItem(msg.uidFrom)
    itemTo = itemCtrl.getItem(msg.uidTo)
    if not itemFrom:
        retErr = Base.lang('不存在!')
        session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.DIEJIA_ITEM, retErr))
        return
    if not itemTo:
        retErr = Base.lang('不存在!!')
        session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.DIEJIA_ITEM, retErr))
        return
    if itemFrom.itemCfg.cfgId != itemTo.itemCfg.cfgId or itemFrom.itemCfg.flagDieJia != 1:
        retErr = Base.lang('物品不能叠加!')
        session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.DIEJIA_ITEM, retErr))
        return
    itemTo.lefttimes += itemFrom.lefttimes
    DbService.getPlayerService().updateItemLeftTimes(player, itemTo)
    item   = itemCtrl.delItem(msg.uidFrom)
    session.sendMsg(MsgDef.ServerCmd.DIEJIA_ITEM, MsgDef.DieJiaItemRet(msg.uidFrom, msg.uidTo, itemTo.lefttimes))
    return

#锻造配置
DUANZAO_RATE_CFG = [
    #最低装备等级	最高装备等级	装备品质	概率	合成获得经验
    [1,10,1,1.00 , 1],
    [11,19,1,0.60 ,1],
    [11,19,2,0.25 ,2],
    [11,19,3,0.10 ,3],
    [11,19,4,0.05 ,4],
    [20,29,1,0.75 ,1],
    [20,29,2,0.20 ,2],
    [20,29,3,0.08 ,3],
    [20,29,4,0.02 ,4],
    [30,39,1,0.75 ,1],
    [30,39,2,0.15 ,2],
    [30,39,3,0.08 ,3],
    [30,39,4,0.02 ,4],
    [30,49,1,0.75 ,1],
    [30,49,2,0.15 ,2],
    [30,49,3,0.08 ,3],
    [30,49,4,0.02 ,4],
    [30,59,1,0.75 ,1],
    [30,59,2,0.15 ,2],
    [30,59,3,0.08 ,3],
    [30,59,4,0.02 ,4]
]
#装备锻造合成等级	最高装低备等级	最高装备等级	人物需求等级	升级需求经验
DUANZAO_SKILL_EXP = [
    [1,	1 ,	19,	5 ,	200],
    [2,	20,	29,	20,	250],
    [3,	30,	39,	30,	300],
    [4,	40,	49,	40,	400],
    [5,	50,	59,	50,	100000000]
]
def processDuanZaoSkillExp(player):
    skill = player.skillCtrl.getSkillById(Base.MAKE_ITEM_ID)
    for k in DUANZAO_SKILL_EXP:
        levelCfg = k[0]
        maxExp   = k[4]
        if skill.skillLevel == levelCfg:
            if skill.exp < maxExp:
                break
            skill.exp -= maxExp
            skill.skillLevel += 1
        #else:
            #break
    return True

def getQualityAndExpCfg(level):
    tmpList = []
    for k in DUANZAO_RATE_CFG:
        if level >= k[0] and level <= k[1]:
            tmpList.append(k)
    if not tmpList:
        return None
    rand = random.randint(1, 100)
    curRate = 0
    for k in tmpList:
        rateCfg = int(k[3] * 100)
        curRate += rateCfg
        if rand <= curRate:
            quality = k[2]
            exp = k[4]
            return (quality, exp)
    k = tmpList[0]
    quality = k[2]
    exp = k[4]
    return (quality, exp)
#锻造合成物品
@ffext.onLogic(MsgDef.ClientCmd.MAKE_ITEM, MsgDef.MakeItemReq)
def processMakeItem(session, msg):
    player  = session.player
    itemCtrl= player.itemCtrl
    skillCtrl = player.skillCtrl
    destItemCfg = ItemModel.getItemMgr().getCfgByCfgId(msg.itemCfgId)
    if not destItemCfg:
        retErr = Base.lang('此物品不能合成!!')
        session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.MAKE_ITEM, retErr))
        return
    if itemCtrl.getFreePkgSize() <= 0:
        retErr = Base.lang('包裹空间不足!')
        session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.MAKE_ITEM, retErr))
        return
    if player.level < destItemCfg.needLevel:
        session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.MAKE_ITEM, Base.lang('等级不足!')))
        return
    #if player.job != destItemCfg.job:
        #session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.MAKE_ITEM, Base.lang('职业不符!')))
        #return
    db = ffext.allocDbConnection('cfg', ffext.getConfig('-cfg'))
    sql = 'select needitemid1,neednum1,needitemid2,neednum2,needitemid3,neednum3,needitemid4,neednum4 from itemmake \
         where itemlevelmin <= %d and itemlevelmax >= %d and job in (%d, 0) and itemtype = %d' % \
          (destItemCfg.needLevel, destItemCfg.needLevel, destItemCfg.job, destItemCfg.itemType)
    ffext.dump('processMakeItem sql', sql)
    def cb(ret):
        if len(ret.result) == 0:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.MAKE_ITEM, Base.lang('服务器忙!')))
            return
        row = ret.result[0]
        ffext.dump('processMakeItem', row)
        needItemCfg = {}
        for i in range(0, 4):
            if row[i*2] == '':
                continue
            needItemId = int(row[i*2])
            needItemNum= int(row[i*2 + 1])
            needItemCfg[needItemId] = needItemNum
            haveNum = itemCtrl.countItemNumbyCfgId(needItemId)
            if haveNum < needItemNum:
                consumeItemCfg = ItemModel.getItemMgr().getCfgByCfgId(needItemId)
                retErr = Base.lang('材料不足,需要:%s*%d'%(consumeItemCfg.name, needItemNum))
                session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.MAKE_ITEM, retErr))
                return
        #套装名 概率 1 50% 2 33% 3 17 %
        strItemCfgId = str(msg.itemCfgId)
        #3051 1 1 3 8
        #3051 2 1 1 8

        rateCfg = getQualityAndExpCfg(destItemCfg.needLevel)
        if not rateCfg:
            retErr = Base.lang('人物等级不够!!')
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.MAKE_ITEM, retErr))
            return
        qualityRand = rateCfg[0]
        addExp = rateCfg[1]
        pinzhi = qualityRand
        ffext.dump('NEEDLEVEL', destItemCfg.needLevel)


        for k, v in skillCtrl.allSkill.iteritems():
            if skillCtrl.getSkillById(Base.MAKE_ITEM_ID) == v: #or skillCtrl.getSkillById(210) == v:
                break
        else:
            retErr = Base.lang('未学习锻造技能！')
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.MAKE_ITEM, retErr))
            return 0
        makeItemSkill = skillCtrl.getSkillById(Base.MAKE_ITEM_ID)
        #makeItemSkill = skillCtrl.getSkillById(210)
        exp = makeItemSkill.exp + addExp
        level = makeItemSkill.skillLevel
        # 等级		可制作内容		锻造技能等级
        # 制作材料（初级）		用于制作1－19级装备		    1
        # 制作材料（中级）		用于制作20级-29级装备		2
        # 制作材料（高级）		用于制作30级-39级装备		3
        # 制作材料（名匠）		用于制作40级-49级装备		4
        bCanDuanZao = False
        if level <= 1 and player.level >= 5:
            if destItemCfg.needLevel <= 19:
                bCanDuanZao = True
        elif level <= 2 and player.level >= 20:
            if destItemCfg.needLevel <= 29:
                bCanDuanZao = True
        elif level <= 3 and player.level >= 30:
            if destItemCfg.needLevel <= 39:
                bCanDuanZao = True
        elif level <= 4 and player.level >= 40:
            if destItemCfg.needLevel <= 49:
                bCanDuanZao = True
        elif level <= 5 and player.level >= 50:
            if destItemCfg.needLevel <= 59:
                bCanDuanZao = True
        if False == bCanDuanZao:
            retErr = Base.lang('锻造技能等级不足或者人物等级不足！')
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.MAKE_ITEM, retErr))
            return 0

    # if destItemCfg.needLevel <= 10:
        #     result = makeItemSkillExp(exp, level, player)
        #     if result:
        #         exp = result[0]
        #         level = result[1]
        #     else:
        #         retErr = Base.lang('人物等级不够')
        #         session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.MAKE_ITEM, retErr))
        #     pinzhi = 1
        # elif destItemCfg.needLevel < 20:
        #     successRate = [0.6, 0.25, 0.1, 0.05]
        #     result = makeItemSkillExp(exp, level, player, successRate)
        #     if result:
        #         exp = result[0]
        #         level = result[1]
        #     else:
        #         retErr = Base.lang('人物等级不够')
        #         session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.MAKE_ITEM, retErr))
        #     pinzhi = success(successRate)
        # elif destItemCfg.needLevel < 30:
        #     successRate = [0.75, 0.2, 0.08, 0.02]
        #     result = makeItemSkillExp(exp, level, player, successRate)
        #     if result:
        #         exp = result[0]
        #         level = result[1]
        #     else:
        #         retErr = Base.lang('人物等级不够')
        #         session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.MAKE_ITEM, retErr))
        #     pinzhi = success(successRate)
        # elif destItemCfg.needLevel < 40:
        #     successRate = [0.75, 0.15, 0.08, 0.02]
        #     result = makeItemSkillExp(exp, level, player, successRate)
        #     if result:
        #         exp = result[0]
        #         level = result[1]
        #     else:
        #         retErr = Base.lang('人物等级不够')
        #         session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.MAKE_ITEM, retErr))
        #     pinzhi = success(successRate)
        # elif destItemCfg.needLevel < 50:
        #     successRate = [0.75, 0.15, 0.08, 0.02]
        #     result = makeItemSkillExp(exp, level, player, successRate)
        #     if result:
        #         exp = result[0]
        #         level = result[1]
        #     else:
        #         retErr = Base.lang('人物等级不够')
        #         session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.MAKE_ITEM, retErr))
        #     pinzhi = success(successRate)
        # elif destItemCfg.needLevel < 60:
        #     successRate = [0.75, 0.15, 0.08, 0.02]
        #     result = makeItemSkillExp(exp, level, player, successRate)
        #     if result:
        #         exp = result[0]
        #         level = result[1]
        #     else:
        #         retErr = Base.lang('人物等级不够')
        #         session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.MAKE_ITEM, retErr))
        #     pinzhi = success(successRate)

        skillCtrl.getSkillById(Base.MAKE_ITEM_ID).exp = exp
        #skillCtrl.getSkillById(210).exp = exp
        skillCtrl.getSkillById(Base.MAKE_ITEM_ID).skillLevel = level
        processDuanZaoSkillExp(player)
        #skillCtrl.getSkillById(210).level = level
        ffext.dump('EXPPPPPPPPP', exp)
        ffext.dump('LEVELLLLLLL', level)

        #taoshu = 1
        rand = random.randint(1, 100)
        randcfg = [50, 33, 17]
        if rand < randcfg[0]:
            taoshu = 1
        elif rand < randcfg[0] + randcfg[1]:
            taoshu = 2
        else:
            taoshu = 3
        strItemCfgId = strItemCfgId[0:4] + str(pinzhi) + strItemCfgId[5] + str(taoshu) + strItemCfgId[7:] #strItemCfgId[4] = 2 #品质 strItemCfgId[6] = 2  # 套
        ffext.dump('铸造', strItemCfgId, msg.itemCfgId, rand, taoshu, pinzhi)
        if ItemModel.getItemMgr().getCfgByCfgId(int(strItemCfgId)):
            msg.itemCfgId = int(strItemCfgId)

        for consumeId, needNum in needItemCfg.iteritems():
            itemCtrl.subItemNumByCfgId(consumeId, needNum)
        itemObj = itemCtrl.addItemByCfgId(msg.itemCfgId, 1)
        if not itemObj:
            return 
        retMsg = MsgDef.MakeItemRet()
        retMsg.itemMaked = MsgDef.Item()
        retMsg.exp = exp
        retMsg.level = level
        buildItem(retMsg.itemMaked, itemObj)
        processQueryPkg(session)
        session.sendMsg(MsgDef.ServerCmd.MAKE_ITEM, retMsg)
        return
    db.query(sql, cb)
    return

#锻造成功的函数调用
def success(successRate):
    rate = random.random()
    if successRate:
        length = len(successRate)
    else:
        return 1
    for i in range(0, length)[::-1]:
        if rate <= successRate[i]:
            return i+1
        else:
            continue
    else:
        return 0

#锻造辅助函数，锻造经验值增加与技能升级
def makeItemSkillExp(oldExp, oldLevel, player, successRate=None):
    addExp = success(successRate)
    curExp = oldExp + addExp
    #playerNeedLevel = [5, 20, 30, 40]
    if oldLevel == 1 and player.level >= 5:
        needExp = 200
    elif oldLevel == 2 and player.level >= 20:
        needExp = 250
    elif oldLevel == 3 and player.level >= 30:
        needExp = 300
    elif oldLevel == 4 and player.level >= 40:
        needExp = 400
    elif oldLevel == 5:
        return curExp, oldLevel
    else:
        return

    if curExp >= needExp:
        newLevel = oldLevel + 1
        curExp -= needExp
        return curExp, newLevel
    else:
        return curExp, oldLevel

#覆盖道具，继承属性
@ffext.onLogic(MsgDef.ClientCmd.INHERIT_ITEM, MsgDef.InheritItemReq)
def processFuGaiItem(session, msg):
    ffext.dump('processFuGaiItem', msg)
    player  = session.player
    itemCtrl= player.itemCtrl
    itemFrom = itemCtrl.getItem(msg.uidFrom)
    itemTo = itemCtrl.getItem(msg.uidTo)
    bEquiped = False
    bFromEquiped = False
    if not itemTo:
        itemTo = itemCtrl.getEquipedItemById(msg.uidTo)
        bEquiped = True
    if not itemFrom:
        itemFrom = itemCtrl.getEquipedItemById(msg.uidFrom)
        bFromEquiped = True
    if not itemFrom:
        retErr = Base.lang('不存在!')
        session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.INHERIT_ITEM, retErr))
        return
    if not itemTo:
        retErr = Base.lang('不存在!!')
        session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.INHERIT_ITEM, retErr))
        return
    if itemFrom.itemCfg.itemType != itemTo.itemCfg.itemType:
        retErr = Base.lang('物品不同不能覆盖!')
        session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.INHERIT_ITEM, retErr))
        return
    if itemFrom.itemCfg.quality != itemTo.itemCfg.quality:
        retErr = Base.lang('物品品质不同不能覆盖!')
        session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.INHERIT_ITEM, retErr))
        return
    if itemTo.itemCfg.itemType >= 101 and itemTo.itemCfg.itemType <= 108:
        pass
    else:
        retErr = Base.lang('必须是装备!')
        session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.INHERIT_ITEM, retErr))
        return
    #只覆盖基础属性，如果基础属性没有任何比目标道具高的，不能覆盖
    ffext.dump("inherit", itemFrom.itemCfg.cfgId, itemTo.itemCfg.cfgId, itemTo.itemCfg)
    # propDataOld = itemFrom.itemCfg.toPropData()
    # propDataNew = itemTo.itemCfg.toPropData()
    # ffext.dump("inherit", msg, propDataOld, propDataNew)
    # genNewProp = {}
    # for k, v in propDataOld.iteritems():
    #     curVal = propDataNew.get(k, 0)
    #
    #     if v > curVal:
    #         genNewProp[k] = v - curVal
    # if len(genNewProp) == 0:
    #     retErr = Base.lang('%s覆盖%s失败,没有更高的属性可以覆盖!'%(itemFrom.itemCfg.name, itemTo.itemCfg.name))
    #     session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.INHERIT_ITEM, retErr))
    #     retErr = Base.lang('%s!' % (str(propDataOld)))
    #     session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.INHERIT_ITEM, retErr))
    #     retErr = Base.lang('%s!' % (str(propDataNew)))
    #     session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.INHERIT_ITEM, retErr))
    #     return
    if bFromEquiped:#先放回到包裹
        retMsg = MsgDef.UnEquipItemRet()
        retErr = itemCtrl.unequipItem(msg.uidFrom, retMsg)
        if retErr:
            print(retErr)
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.UNEQUIP_ITEM, retErr))
            return
        session.sendMsg(MsgDef.ServerCmd.UNEQUIP_ITEM, retMsg)
        PlayerModel.sendPropUpdateMsg(player)
    item   = itemCtrl.delItem(msg.uidFrom)
    fromCfg= item.itemCfg
    # if item.strengthenLevel > 0:
    #     #strengthenCfg = fromCfg.allStrengthenCfg.get(item.strengthenLevel)
    #     oldPropExt = item.toStrenthenPropData()
    #     if oldPropExt:
    #         for k, v in oldPropExt.iteritems():#strengthenCfg.toPropData(item.itemCfg.job*1000 + item.itemCfg.itemType).iteritems():
    #             if itemTo.propExt.get(k) != None:
    #                 itemTo.propExt[k] += v
    #             else:
    #                 itemTo.propExt[k] = v
    #######################################################################
    # for k, v in genNewProp.iteritems():
    #     if itemTo.propExt.get(k) != None:
    #         itemTo.propExt[k] += v
    #     else:
    #         itemTo.propExt[k] = v
    itemTo.strengthenLevel = item.strengthenLevel
    DbService.getPlayerService().updateItem(player, itemTo)
    itemData = MsgDef.Item()
    buildItem(itemData, itemTo)
    session.sendMsg(MsgDef.ServerCmd.INHERIT_ITEM, MsgDef.InheritItemRet(msg.uidFrom, msg.uidTo, itemData))
    ffext.dump("arrange!------------------------------")
    processQueryPkg(session)
    #属性变化
    if bEquiped:
        #增加属性
        propData = itemTo.toAllProp()
        player.addModuleProp(itemTo.itemCfg.itemType, propData)
        PlayerModel.sendPropUpdateMsg(player)
    if bFromEquiped:
        retMsg = MsgDef.EquipItemRet()
        retErr = itemCtrl.equipItem(itemTo, retMsg)
        if retErr:
            print(retErr)
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.EQUIP_ITEM, retErr))
            return
        session.sendMsg(MsgDef.ServerCmd.EQUIP_ITEM, retMsg)
        ffext.dump('processFuGaiItem', retMsg)
        PlayerModel.sendPropUpdateMsg(player)
        processQueryEquip(session)
    return

#采集
@ffext.onLogic(MsgDef.ClientCmd.COLLECT_OPS, MsgDef.CollectOpsReq)
def processCollect(session, msg):#操作类型，0表示请求开始采集 1表示采集完成（进度表播完）
    ffext.dump('processCollect', msg)
    retMsg = MsgDef.CollectOpsRet(msg.opstype, msg.uid, 3)
    player = session.player
    itemObj = player.mapObj.getObjById(msg.uid)
    if itemObj == None or itemObj.getType() != Base.ITEM:
        retErr = Base.lang('采集点无效!')
        session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.COLLECT_OPS, retErr))
        return
    retMsg.cfgid = itemObj.itemCfg.cfgId
    if msg.opstype == 0:
        retMsg.item = MsgDef.Item()
        collectCfg = ItemModel.getItemMgr().getCollectCfgById(itemObj.uid)
        if not collectCfg:
            retErr = Base.lang('采集点无效!')
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.COLLECT_OPS, retErr))
            return
        itemName = collectCfg.itemGive#'生铁'#14011
        destItemCfg = ItemModel.getItemMgr().getCfgByName(itemName)
        if destItemCfg:
            retMsg.item.itemCfgId = destItemCfg.cfgId       
        
        session.sendMsg(MsgDef.ServerCmd.COLLECT_OPS, retMsg)
    elif msg.opstype == 1:
        collectCfg = ItemModel.getItemMgr().getCollectCfgById(itemObj.uid)
        if not collectCfg:
            retErr = Base.lang('采集点无效!')
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.COLLECT_OPS, retErr))
            return
        
        itemName = collectCfg.itemGive#'生铁'#14011
        itemObjNew = session.player.itemCtrl.addItemByName(itemName, collectCfg.itemNum)
        retMsg.item = MsgDef.Item()
        if itemObjNew:
            buildItem(retMsg.item, itemObjNew)
            player.taskCtrl.trigger(Base.Action.COLLECT, itemObjNew.itemCfg.cfgId, 1)
        processQueryPkg(session)
        session.sendMsg(MsgDef.ServerCmd.COLLECT_OPS, retMsg)
        mapObj = itemObj.mapObj
        x = itemObj.x
        y =  itemObj.y
        mapObj.itemLeaveMap(itemObj)
        def onTimer():
            mapObj.itemEnterMap(itemObj, x, y)
        ffext.timer(5*1000, onTimer)

#仓库
@ffext.onLogic(MsgDef.ClientCmd.REPO_ITEM_OPS, MsgDef.RepoItemOpsReq)
def processRepoItemOps(session, msg):#0表示查询（服务器同步一遍列表）， 1表示存入 2表示取出 3 表示整理
    player = session.player
    retMsg = MsgDef.RepoItemOpsRet(msg.opstype, msg.itemid, msg.destPos, player.itemCtrl.repoMaxSize, {})
    ret = False
    if msg.opstype == 0:
        ret = True
    elif msg.opstype == 1:
        if player.isSetPasswd and not player.isVerified:
            def cb(ret):
                safePasswd = ret.result[0][0]
                if msg.passwd != safePasswd:
                    retErr = Base.lang('安全密码错误!')
                    session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.MONEY_BANK_OPS, retErr))
                else:
                    player.isVerified = True
                    retMsg.opstype = 7
                    session.sendMsg(MsgDef.ServerCmd.REPO_ITEM_OPS, retMsg)
            DbService.getPlayerService().querySafePasswd(player, cb)
            return
        #ffext.dump('1111111111111111111111111111')
        #ret = player.itemCtrl.movePkgToRepo(msg.itemid, msg.destPos)
        ret = player.itemCtrl.movePkgToRepo(msg.itemid, msg.itemNum)
        if ret:
            retMsg.destPos = ret.position
            retMsg.itemNum = msg.itemNum
        processQueryPkg(session)
        if player.itemCtrl.arrangeRepo():
            player.itemCtrl.arrangeRepo()
    elif msg.opstype == 2:
        if player.isSetPasswd and not player.isVerified:
            def cb(ret):
                safePasswd = ret.result[0][0]
                if msg.passwd != safePasswd:
                    retErr = Base.lang('安全密码错误!')
                    session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.MONEY_BANK_OPS, retErr))
                else:
                    player.isVerified = True
                    retMsg.opstype = 7
                    session.sendMsg(MsgDef.ServerCmd.REPO_ITEM_OPS, retMsg)
            DbService.getPlayerService().querySafePasswd(player, cb)
            return
        #ret = player.itemCtrl.moveRepoToPkg(msg.itemid, msg.destPos)
        ret = player.itemCtrl.moveRepoToPkg(msg.itemid, msg.itemNum)
        if ret:
            retMsg.destPos = ret.position
            retMsg.itemNum = msg.itemNum
        processQueryPkg(session)
        if player.itemCtrl.arrangeRepo():
            player.itemCtrl.arrangeRepo()
    elif msg.opstype == 3:
        ret = player.itemCtrl.arrangeRepo()
    elif msg.opstype == 4:  # 包裹开一个格子
        #if player.itemCtrl.pkgMaxSize >= Base.MAX_PKG_SIZE:
        oldPkgMaxSize = player.itemCtrl.pkgMaxSize
        newPkgMaxSize = oldPkgMaxSize + msg.destNum
        if newPkgMaxSize > 125:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG,
                            buildErrMsg(MsgDef.ClientCmd.REPO_ITEM_OPS, Base.lang('已到最大包裹数量!')))
            return

        oldPrice = sizePrice(oldPkgMaxSize)
        newPrice = sizePrice(newPkgMaxSize)
        price = newPrice - oldPrice
        #if pkgMaxSize < 25:
            #price = Base.OPEN_PKG_SLOT_PRICE * pkgMaxSize
        #elif player.itemCtrl.pkgMaxSize < 50:
            #price = 1000
        #elif player.itemCtrl.pkgMaxSize < 75:
            #price = 2000
        #elif player.itemCtrl.pkgMaxSize < 100:
            #price = 5000
        #elif player.itemCtrl.pkgMaxSize < 125:
            #price = 10000
        if player.gold < price:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG,
                            buildErrMsg(MsgDef.ClientCmd.REPO_ITEM_OPS, Base.lang('金币不足')))
            return
        ffext.dump('PRICE', price)
        player.addGold(-1 * price, True)
        player.itemCtrl.pkgMaxSize += msg.destNum
        DbService.getPlayerService().updatePkgRepoSize(player)
        retMsg.repoMaxSize = player.itemCtrl.pkgMaxSize
        ret = True
    elif msg.opstype == 5:#开一个格子
        if player.itemCtrl.repoMaxSize >= Base.MAX_REPO_SIZE:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG,
                            buildErrMsg(MsgDef.ClientCmd.REPO_ITEM_OPS, Base.lang('已到最大包裹数量!')))
            return
        if player.gold < Base.OPEN_PKG_SLOT_PRICE * msg.destNum:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.REPO_ITEM_OPS, Base.lang('金币不足!')))
            return
        player.addGold(-msg.destNum * Base.OPEN_PKG_SLOT_PRICE, True)
        destNum = msg.destNum
        if destNum <= 0:
            destNum = 1
        player.itemCtrl.repoMaxSize += destNum
        DbService.getPlayerService().updatePkgRepoSize(player)
        retMsg.repoMaxSize = player.itemCtrl.repoMaxSize
        ret = True
    elif msg.opstype == 6:#设置密码
        DbService.getPlayerService().updateSafePasswd(player, msg.passwd)
        #数据库增加个安全码字段
        retMsg.opstype = 6
        ret = True
    if not ret:
        session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.REPO_ITEM_OPS, Base.lang('无效操作!')))
        return
    for itemId, itemObj in player.itemCtrl.allRepo.iteritems():
        item = MsgDef.Item()
        buildItem(item, itemObj)
        retMsg.allItem[itemObj.position] = item
    session.sendMsg(MsgDef.ServerCmd.REPO_ITEM_OPS, retMsg)
    return


#包裹扩容辅助函数
def sizePrice(size):
    eachPageNum = 25#每页签 25 个
    pagePrice   = [500, 1000, 2000, 5000, 10000]
    maxPageIndex= int(size / eachPageNum)
    if maxPageIndex == 5:
        maxPageIndex = 4
    price    = 0
    for k in range(maxPageIndex):
        price += pagePrice[k] * eachPageNum
    leftNum = int(size % eachPageNum)
    price += pagePrice[maxPageIndex] * leftNum
    #
    # if size >= 100:
    #     price = (size - 100 + 1) * 10000 + (5000 + 2000 + 1000 + 500) * 25
    # elif size >= 75:
    #     price = (size - 75 + 1) * 5000 + (2000 + 1000 + 500) * 25
    # elif size >= 50:
    #     price = (size - 50 + 1) * 2000 + (1000 + 500) * 25
    # elif size >= 25:
    #     price = (size - 25 + 1) * 1000 + 500 * 25
    # elif size >= 0:
    #     price = (size - 0 + 1) * 500
    return price

@ffext.onLogic(MsgDef.ClientCmd.EXCHANGE_OPS, MsgDef.ExchangeOpsReq)
def processExchangeOps(session, msg):#0表示请求交易 1表示同意开始交易 2表示拒绝开始交易 3表示更新交易的价格和道具 4标示确认交易 5表示取消交易
    ffext.dump('processExchangeOps',  msg)
    player = session.player
    if msg.opstype == 0:
        destObj = player.mapObj.getObjById(msg.destuid)
        if not destObj:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.EXCHANGE_OPS, Base.lang('目标不在线!')))
            return
        if destObj.tmpInfo.get('exchangeTmp') != None:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.EXCHANGE_OPS, Base.lang('对方忙!')))
            return
        retMsg = MsgDef.ExchangeOpsRet(0, player.uid,player.name, 0, [], 0, [])

        destObj.sendMsg(MsgDef.ServerCmd.EXCHANGE_OPS, retMsg)
        destObj.tmpInfo['exchangeTmp'] = [{'price':0, 'items':[],'confirm':0}, weakref.ref(player)]
        player.tmpInfo['exchangeTmp']  = [{'price':0, 'items':[],'confirm':0}, weakref.ref(destObj)]

        return
    elif msg.opstype == 1:
        tmpInfoArg = player.tmpInfo['exchangeTmp']
        tmpInfo = tmpInfoArg[0]
        srcPlayer = tmpInfoArg[1]()
        if not srcPlayer:
            player.tmpInfo.pop('exchangeTmp', None)
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.EXCHANGE_OPS, Base.lang('对方下线，交易失败!')))
            return
        tmpInfoArg2 = srcPlayer.tmpInfo['exchangeTmp']
        tmpInfo2 = tmpInfoArg2[0]
        ffext.dump(msg.opstype, tmpInfo, tmpInfo2)

        retMsg = MsgDef.ExchangeOpsRet(1, srcPlayer.uid,srcPlayer.name, 0, [], 0, [])
        session.sendMsg(MsgDef.ServerCmd.EXCHANGE_OPS, retMsg)
        retMsg.destuid = player.uid
        retMsg.name    = player.name
        srcPlayer.sendMsg(MsgDef.ServerCmd.EXCHANGE_OPS, retMsg)
        return
    elif msg.opstype == 3:
        tmpInfoArg = player.tmpInfo['exchangeTmp']
        tmpInfo = tmpInfoArg[0]
        srcPlayer = tmpInfoArg[1]()
        if not srcPlayer:
            player.tmpInfo.pop('exchangeTmp', None)
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.EXCHANGE_OPS, Base.lang('对方下线，交易失败!')))
            return
        tmpInfoArg2 = srcPlayer.tmpInfo['exchangeTmp']
        tmpInfo2 = tmpInfoArg2[0]
        ffext.dump(msg.opstype, tmpInfo, tmpInfo2)

        if player.gold < msg.price or msg.price < 0:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.EXCHANGE_OPS, Base.lang('金币不足!')))
            return
        retMsg = MsgDef.ExchangeOpsRet(1, player.uid,player.name, msg.price, [], tmpInfo2['price'], tmpInfo2['items'])
        if not msg.items:
            msg.items = {}
        for itemid, num in msg.items.iteritems():
            itemObj = player.itemCtrl.getItem(itemid)
            if not itemObj:
                ffext.dump('not this item %d'%(itemid))
                continue
            if num <=0:
                continue
            if itemObj.lefttimes < num:
                session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.EXCHANGE_OPS, Base.lang('数量不足!')))
                return
            item = MsgDef.Item()
            buildItem(item, itemObj)
            item.lefttimes = num
            retMsg.items.append(item)
        tmpInfo['price'] = msg.price
        tmpInfo['items'] = retMsg.items
        srcPlayer.sendMsg(MsgDef.ServerCmd.EXCHANGE_OPS, retMsg)

        retMsg.destuid = srcPlayer.uid
        retMsg.name    = srcPlayer.name
        retMsg.price   = tmpInfo2['price']
        retMsg.items   = tmpInfo2['items']
        retMsg.priceSelf = tmpInfo['price']
        retMsg.itemsSelf = tmpInfo['items']
        session.sendMsg(MsgDef.ServerCmd.EXCHANGE_OPS, retMsg)
        return
    elif msg.opstype == 4:
        tmpInfoArg = player.tmpInfo['exchangeTmp']
        tmpInfo = tmpInfoArg[0]
        srcPlayer = tmpInfoArg[1]()
        if not srcPlayer:
            player.tmpInfo.pop('exchangeTmp', None)
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.EXCHANGE_OPS, Base.lang('对方下线，交易失败!')))
            return
        tmpInfo['confirm'] = 1
        tmpInfoArg2 = srcPlayer.tmpInfo['exchangeTmp']
        tmpInfo2 = tmpInfoArg2[0]
        ffext.dump(msg.opstype, tmpInfo, tmpInfo2)

        if tmpInfo2['confirm'] != 1:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.EXCHANGE_OPS, Base.lang('等待对方确认!')))
            srcPlayer.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.EXCHANGE_OPS, Base.lang('对方已确认!')))
            return
        if player.gold < tmpInfo['price']:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.EXCHANGE_OPS, Base.lang('金币不足!')))
            return
        for itemTmp in tmpInfo['items']:
            itemObj = player.itemCtrl.getItem(itemTmp.uid)
            if not itemObj:
                session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.EXCHANGE_OPS, Base.lang('无效道具!')))
                return
            if itemObj.lefttimes < itemTmp.lefttimes:
                session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.EXCHANGE_OPS, Base.lang('道具数量不足!')))
                return
        if srcPlayer.gold < tmpInfo2['price']:
            srcPlayer.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.EXCHANGE_OPS, Base.lang('金币不足!')))
            return
        for itemTmp in tmpInfo2['items']:
            itemObj = srcPlayer.itemCtrl.getItem(itemTmp.uid)
            if not itemObj:
                srcPlayer.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.EXCHANGE_OPS, Base.lang('无效道具!')))
                return
            if itemObj.lefttimes < itemTmp.lefttimes:
                srcPlayer.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.EXCHANGE_OPS, Base.lang('道具数量不足!')))
                return
        if player.itemCtrl.getFreePkgSize() < len(tmpInfo2['items']):
            player.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.EXCHANGE_OPS, Base.lang('包裹空间不足!')))
            return
        if srcPlayer.itemCtrl.getFreePkgSize() < len(tmpInfo['items']):
            srcPlayer.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.EXCHANGE_OPS, Base.lang('包裹空间不足!')))
            return

        itemList = []
        for itemTmp in tmpInfo['items']:
            #item = player.itemCtrl.delItem(itemTmp.uid, False)
            item = player.itemCtrl.getItem(itemTmp.uid)
            if item.lefttimes == itemTmp.lefttimes:
                item = player.itemCtrl.delItem(itemTmp.uid)
            else:
                item = ItemModel.splitItem(player, item, itemTmp.lefttimes)
            itemList.append(item)
        player.addGold(-1*tmpInfo['price'], True)

        itemList2 = []
        for itemTmp in tmpInfo2['items']:
            item = srcPlayer.itemCtrl.getItem(itemTmp.uid)
            if item.lefttimes == itemTmp.lefttimes:
                item = srcPlayer.itemCtrl.delItem(itemTmp.uid)
            else:
                item = ItemModel.splitItem(srcPlayer, item, itemTmp.lefttimes)
            itemList2.append(item)
        srcPlayer.addGold(-1*tmpInfo2['price'], True)

        player.addGold(tmpInfo2['price'], True)
        srcPlayer.addGold(tmpInfo['price'], True)

        for k in itemList:
            srcPlayer.itemCtrl.moveItemToPkg(k)
        for k in itemList2:
            player.itemCtrl.moveItemToPkg(k)

        srcPlayer.sendMsg(MsgDef.ServerCmd.EXCHANGE_OPS, MsgDef.ExchangeOpsRet(2, player.uid, player.name, tmpInfo['price'], tmpInfo['items'], tmpInfo2['price'], tmpInfo2['items']))
        player.sendMsg(MsgDef.ServerCmd.EXCHANGE_OPS, MsgDef.ExchangeOpsRet(2, srcPlayer.uid, srcPlayer.name, tmpInfo2['price'], tmpInfo2['items'], tmpInfo['price'], tmpInfo['items']))
        if len(itemList) > 0:
            processQueryPkg(srcPlayer.session)
        if len(itemList2) > 0:
            processQueryPkg(session)
        player.tmpInfo.pop('exchangeTmp', None)
        srcPlayer.tmpInfo.pop('exchangeTmp', None)
        return
    elif msg.opstype == 2 or msg.opstype == 5:
        tmpInfoArg = player.tmpInfo['exchangeTmp']
        tmpInfo = tmpInfoArg[0]
        srcPlayer = tmpInfoArg[1]()
        if not srcPlayer:
            player.tmpInfo.pop('exchangeTmp', None)
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.EXCHANGE_OPS, Base.lang('对方下线，交易失败!')))
            return
        tmpInfoArg2 = srcPlayer.tmpInfo['exchangeTmp']
        tmpInfo2 = tmpInfoArg2[0]
        ffext.dump(msg.opstype, tmpInfo, tmpInfo2)

        player.tmpInfo.pop('exchangeTmp', None)
        srcPlayer.tmpInfo.pop('exchangeTmp', None)

        srcPlayer.sendMsg(MsgDef.ServerCmd.EXCHANGE_OPS, MsgDef.ExchangeOpsRet(3, player.uid, player.name, 0, [], 0, []))
        player.sendMsg(MsgDef.ServerCmd.EXCHANGE_OPS, MsgDef.ExchangeOpsRet(3, srcPlayer.uid, srcPlayer.name, 0, [], 0, []))

        return

@ffext.onLogic(MsgDef.ClientCmd.ITEM_EXTRA_OPS, MsgDef.ItemExtraOpsReq)
def processExchangeOps(session, msg):#0表示请求交易 1表示同意开始交易 2表示拒绝开始交易 3表示更新交易的价格和道具 4标示确认交易 5表示取消交易
    ffext.dump('processExchangeOps',  msg)
    player = session.player
    gold = 0
    if msg.opstype == 0:#丢弃
        item = player.itemCtrl.delItem(msg.uid)
        if  not item:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.ITEM_EXTRA_OPS, Base.lang('物品不存在，丢弃失败!')))
            return
    elif msg.opstype == 1:#售卖
        item = player.itemCtrl.delItem(msg.uid)
        if  not item:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.ITEM_EXTRA_OPS, Base.lang('物品不存在，售卖失败!')))
            return
        gold = item.itemCfg.decomposePrize
        player.addGold(gold, True)
    session.sendMsg(MsgDef.ServerCmd.ITEM_EXTRA_OPS, MsgDef.ItemExtraOpsRet(msg.opstype, msg.uid, gold))
    processQueryPkg(session)
    return
#拍卖相关的，搜索、寄售 AUCTION_OPS -> AuctionOpsReq -> server:AUCTION_OPS  ->AuctionOpsRet
@ffext.onLogic(MsgDef.ClientCmd.AUCTION_OPS, MsgDef.AuctionOpsReq)
def processAuctionOps(session, msg):
    msg.name = msg.name#.encode('utf-8')
    ffext.dump('processAuctionOps',  msg)

    player = session.player
    retMsg = MsgDef.AuctionOpsRet(msg.opstype, [])
    def cbQueryMine(ret):
        #ffext.dump('RRRRRRRR', ret.result)
        for row in ret.result:
            data = MsgDef.AuctionData(long(row[0]))
            cfgid = int(row[1])
            cfg = ItemModel.getItemMgr().getCfgByCfgId(cfgid)
            if not cfg:
                continue
            data.name = cfg.name
            data.level = cfg.needLevel
            data.sellPrice = int(row[2])
            data.sellTime = int(row[3])
            if row[8] != '':
                data.itemType = int(row[8])
            if row[9] != '':
                data.quality = int(row[9])
            if row[10] != '':
                data.job = int(row[10])
            data.item = MsgDef.Item()
            itemObj = ItemModel.Item()

            itemObj = ItemModel.Item()
            itemObj.ownerref   = weakref.ref(player)
            itemObj.itemCfg    = cfg
            itemObj.uid        = 0
            itemObj.createTime = ffext.getTime()
            itemObj.lefttimes = int(row[4])
            if row[8] != '':
                itemObj.itemType = int(row[8])
            if row[9] != '':
                itemObj.quality = int(row[9])
            if row[10] != '':
                itemObj.job = int(row[10])
            buildItem(data.item, itemObj)
            retMsg.auctionData.append(data)
        session.sendMsg(MsgDef.ServerCmd.AUCTION_OPS, retMsg)
    if msg.opstype == 0:#0表示搜索 1表示查询寄售列表 2表示寄售
        def cb(ret):
            ffext.dump('RESULT', ret.result)
            for row in ret.result:
                data = MsgDef.AuctionData(long(row[0]))
                #ffext.dump('DATA', row)
                cfgid = int(row[1])
                cfg = ItemModel.getItemMgr().getCfgByCfgId(cfgid)
                if not cfg:
                    continue
                data.name = cfg.name
                data.level = cfg.needLevel
                data.sellPrice = int(row[2])
                data.sellTime = int(row[3])
                #不要改！这是防止为空的！
                if row[8] != '':
                    data.itemType = int(row[8])
                if row[9] != '':
                    data.quality = int(row[9])
                if row[10] != '':
                    data.job = int(row[10])
                data.owner = row[11]
                data.item = MsgDef.Item()
                itemObj = ItemModel.Item()

                itemObj = ItemModel.Item()
                itemObj.ownerref   = weakref.ref(player)
                itemObj.itemCfg    = cfg
                itemObj.uid        = 0
                itemObj.createTime = ffext.getTime()
                itemObj.lefttimes = int(row[4])
                if row[8] != '':
                    itemObj.itemType = int(row[8])
                if row[9] != '':
                    itemObj.quality = int(row[9])
                if row[10] != '':
                    itemObj.job = int(row[10])
                itemObj.owner = row[11]
                buildItem(data.item, itemObj)
                #ffext.dump('DATA', data)
                retMsg.auctionData.append(data)
            session.sendMsg(MsgDef.ServerCmd.AUCTION_OPS, retMsg)

        DbService.getPlayerService().queryOtherAuction(player, name=msg.name, job=msg.job,itemType=msg.itemType,
                                                       quality=msg.quality, minLevel=msg.minLevel, maxLevel=msg.maxLevel, callback=cb)
        return
    elif msg.opstype == 1:#0表示搜索 1表示查询寄售列表 2表示寄售
        DbService.getPlayerService().queryPlayerAuction(player, cbQueryMine)
        return
    elif msg.opstype == 2:#寄售
        item = player.itemCtrl.getItem(msg.itemSellId)
        #ffext.dump('ITEMTYPE', item.itemCfg.itemType)
        if  not item:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.AUCTION_OPS, Base.lang('物品不存在，售卖失败!')))
            return
        if item.lefttimes < msg.sellNum or msg.sellNum <= 0:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.AUCTION_OPS, Base.lang('输入数量有误!')))
            return
        if item.lefttimes == msg.sellNum:
            player.itemCtrl.delItem(msg.itemSellId)
        else:
            item.subLeftTimes(msg.sellNum)
            DbService.getPlayerService().updateItemLeftTimes(player, item)
        autionId = idtool.allocId()
        #ffext.dump("NAME", player.name)
        DbService.getPlayerService().addAuction(player, item, autionId, msg.sellNum, msg.sellPrice, msg.sellTime + ffext.getTime(), item.itemCfg.itemType,
                                                item.itemCfg.quality, item.itemCfg.job)
        DbService.getPlayerService().queryPlayerAuction(player, cbQueryMine)
        processQueryPkg(session)
        return
    elif msg.opstype == 3:#购买
        def cb(ret):
            ffext.dump('ret', ret.result)
            if 1 != len(ret.result):
                session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.AUCTION_OPS, Base.lang('购买失败!')))
                return
            row = ret.result[0]
            ffext.dump(row)
            sellTime = int(row[3])
            cfgid = int(row[1])
            sellPrice = int(row[2])
            lefttimes =  int(row[4])
            strengthen_level = int(row[6])
            propext = row[7]
            owner_name = row[8]
            uid = int(row[9])
            buyTime = ffext.getTime()
            name = row[10]
            price = sellPrice * lefttimes
            tax = int(price * 0.01)
            afterTaxPrice = price - tax
            if tax < 1:
                tax = 1
            ffext.dump("price", price)
            if player.gold < price:
                session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.AUCTION_OPS, Base.lang('金币不足!')))
                return
            if player.itemCtrl.getFreePkgSize() < 1:
                session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.AUCTION_OPS, Base.lang('包裹不足!')))
                return
            player.addGold(price * -1, True)
            if ffext.getSessionMgr().findByUid(uid):
                customSession = ffext.getSessionMgr().findByUid(uid)
                customSession.player.addGold(afterTaxPrice, True)
            else:
                DbService.getPlayerService().updateGoldById(uid, afterTaxPrice)

            itemObj = player.itemCtrl.addItemByCfgId(cfgid)
            if not itemObj:
                session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.AUCTION_OPS, Base.lang('系统忙!')))
                return
            itemObj.lefttimes = lefttimes
            itemObj.strengthenLevel = strengthen_level
            if propext != '':
                itemObj.propext = json.dumps(propext)

            mailTitle = "拍卖行卖出提醒"
            mailMsg = "您的物品" + str(name) + "已售出！"
            player.mailCtrl.sendMail(uid, 2, mailTitle,mailMsg )

            DbService.getPlayerService().updateItem(player, itemObj)
            #DbService.getPlayerService().delAuction(msg.auctionId)
            DbService.getPlayerService().updateCustomer(msg.auctionId, player, buyTime)
            DbService.getPlayerService().queryPlayerAuction(player, cbQueryMine)
            processQueryPkg(session)
            return
        DbService.getPlayerService().queryAuction(msg.auctionId, cb)
        return
    elif msg.opstype == 4:#交易明细
        def cb(ret):
            ffext.dump("RESULT------", ret.result)
            for row in ret.result:
                data = MsgDef.AuctionData(long(row[0]))
                #ffext.dump('DATA', row)
                cfgid = int(row[1])
                cfg = ItemModel.getItemMgr().getCfgByCfgId(cfgid)
                if not cfg:
                    continue
                data.name = cfg.name
                data.level = cfg.needLevel
                data.sellPrice = int(row[2])
                data.sellTime = int(row[3])
                data.lefttimes = int(row[4])
                data.itemType = int(row[8])
                data.quality = int(row[9])
                data.job = int(row[10])
                data.owner = row[11]
                data.uid = int(row[12])
                data.customUid = int(row[13])
                data.customName = row[14]
                if row[15]:
                    data.buyTime = int(row[15])
                else:
                    data.buyTime = row[15]
                data.item = MsgDef.Item()
                itemObj = ItemModel.Item()

                itemObj = ItemModel.Item()
                itemObj.ownerref   = weakref.ref(player)
                itemObj.itemCfg    = cfg
                itemObj.sellPrice = int(row[2])
                itemObj.uid        = int(row[12])
                itemObj.createTime = ffext.getTime()
                itemObj.lefttimes = int(row[4])
                itemObj.itemType = int(row[8])
                itemObj.quality = int(row[9])
                itemObj.job = int(row[10])
                itemObj.owner = row[11]
                if row[13]:
                    itemObj.customUid = int(row[13])
                else:
                    itemObj.customUid = row[13]
                itemObj.customName = row[14]
                if row[15]:
                    itemObj.buyTime = int(row[15])
                else:
                    itemObj.buyTime = row[15]
                buildItem(data.item, itemObj)
                #ffext.dump('CUSTOMNAME', row[14])
                #ffext.dump('DATA', data)
                if len(retMsg.auctionData) <= 8:
                    retMsg.auctionData.append(data)
                else:
                    retMsg.auctionData.pop(0)
                    retMsg.auctionData.append(data)
            session.sendMsg(MsgDef.ServerCmd.AUCTION_OPS, retMsg)
        DbService.getPlayerService().queryTrade(player, cb)
    if msg.opstype == 5:
        def cb(ret):
            ffext.dump("retResult!!!!!!!!!!!!", ret.result )
            auctionId = int(ret.result[0][0])
            cfgId = int(ret.result[0][1])
            num = int(ret.result[0][4])
            player.itemCtrl.addItemByCfgId(cfgId, num)
            processQueryPkg(session)
            DbService.getPlayerService().deletePlayerUndoAuction(player, auctionId)
        DbService.getPlayerService().queryPlayerUndoAuction(player, msg.auctionId, cb)
    session.sendMsg(MsgDef.ServerCmd.AUCTION_OPS, retMsg)
    #processQueryPkg(session)
    return


#装备购买与贩卖 SALE_OPS -> SaleOpsReq -> server:SALE_OPS  ->SaleOpsRet
@ffext.onLogic(MsgDef.ClientCmd.ITEM_SALE_OPS, MsgDef.ItemSaleOpsReq)
def processSale(session, msg):
    player = session.player
    itemUid = msg.itemId
    toSellItems = player.itemCtrl.toSellItems
    #选择出售物品
    if msg.opstype == 0:
        item = player.itemCtrl.allItem.get(itemUid, None)
        if not item:
            #session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.ITEM_SALE_OPS, Base.lang('物品不存在')))
            return
        count = len(toSellItems)
        if count >= 16:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.ITEM_SALE_OPS, Base.lang('物品选择不能超过16个！')))
        price = 0
        for k, v in toSellItems.iteritems():
            price += v.itemCfg.decomposePrize * v.lefttimes
        item.toSell = True
        if item.itemCfg.flagDieJia:
            ffext.dump("NUM", msg.num)
            item.toSellNum = msg.num
            if item.toSellNum > item.lefttimes:
                session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.ITEM_SALE_OPS, Base.lang('物品叠加数量错误!')))
            else:
                item.lefttimes -= item.toSellNum
        else:
            item.toSellNum = 1
            #processQueryPkg(session)
        ffext.dump("toSellNUM", item.toSellNum)
        player.itemCtrl.toSellItems[itemUid] = item
        price += item.itemCfg.decomposePrize * item.toSellNum

        #消息发送
        new_item = MsgDef.Item()
        buildItem(new_item, item)
        itemData = MsgDef.ItemData(item.toSell, item.toSellNum, new_item)
        retMsg = MsgDef.ItemSaleOpsRet(price, itemData, {}, msg.opstype)
        session.sendMsg(MsgDef.ServerCmd.ITEM_SALE_OPS, retMsg)

    #取消出售物品
    elif msg.opstype == 1:
        item = player.itemCtrl.toSellItems.pop(itemUid, None)
        if not item:
            #session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.ITEM_SALE_OPS, Base.lang('物品不存在')))
            return
        price = 0
        for k, v in toSellItems.iteritems():
            price += v.itemCfg.decomposePrize * v.lefttimes
        item.toSell = False
        if item.itemCfg.flagDieJia:
            item.lefttimes += item.toSellNum
        item.toSellNum = 0

        #消息发送
        new_item = MsgDef.Item()
        buildItem(new_item, item)
        itemData = MsgDef.ItemData(item.toSell, item.toSellNum, new_item)
        retMsg = MsgDef.ItemSaleOpsRet(price, itemData, {}, msg.opstype)
        session.sendMsg(MsgDef.ServerCmd.ITEM_SALE_OPS, retMsg)

    #出售物品
    elif msg.opstype == 2:
        price = 0
        for k, v in player.itemCtrl.toSellItems.iteritems():
            if not v.itemCfg.flagDieJia or v.lefttimes == 0:
                player.itemCtrl.delItem(v.uid)
            else:
                DbService.getPlayerService().updateItemLeftTimes(player, v)
            price += v.itemCfg.decomposePrize * v.toSellNum
        player.addGold(price, True)
        processQueryPkg(session)
        player.itemCtrl.toSellItems = {}
        retMsg = MsgDef.ItemSaleOpsRet(price, MsgDef.ItemData(), {}, msg.opstype)
        session.sendMsg(MsgDef.ServerCmd.ITEM_SALE_OPS, retMsg)

    #查询
    elif msg.opstype == 3:
        #item = player.itemCtrl.toSellItems.get(itemUid, None)
        price = 0
        allSaleData = {}
        for k, v in player.itemCtrl.toSellItems.iteritems():
            price += v.itemCfg.decomposePrize * v.toSellNum
            new_item = MsgDef.Item()
            buildItem(new_item, v)
            itemData = MsgDef.ItemData(v.toSell, v.toSellNum, new_item)
            allSaleData[v.uid] = itemData
        retMsg = MsgDef.ItemSaleOpsRet(price, MsgDef.ItemData() , allSaleData , msg.opstype)
        session.sendMsg(MsgDef.ServerCmd.ITEM_SALE_OPS, retMsg)

    #购买
    elif msg.opstype == 4:
        itemCfg = ItemModel.getItemMgr().getCfgByCfgId(msg.itemCfgId)
        ffext.dump("CFFFFFFFFFFFFFFFFFFGID", msg.itemCfgId)
        ffext.dump("itemcfg", itemCfg)
        #购买价格
        price = itemCfg.price * msg.num
        ffext.dump("PRICEEEEE", itemCfg.price)
        if price > player.gold:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.ITEM_SALE_OPS, Base.lang('金币不足!')))
            return
        else:
            player.itemCtrl.addItemByCfgId(msg.itemCfgId, msg.num)
            player.addGold(-price, True)
            processQueryPkg(session)
            retMsg = MsgDef.ItemSaleOpsRet(0, MsgDef.ItemData() , {} , msg.opstype)
            session.sendMsg(MsgDef.ServerCmd.ITEM_SALE_OPS, retMsg)

    #清空待售列表
    elif msg.opstype == 5:
        player.itemCtrl.toSellItems = {}
        retMsg = MsgDef.ItemSaleOpsRet(0, MsgDef.ItemData() , {} , msg.opstype)
        session.sendMsg(MsgDef.ServerCmd.ITEM_SALE_OPS, retMsg)


    return



#人民币支付接口, 买G
@ffext.onLogic(MsgDef.ClientCmd.GOLD_BUY_OPS, MsgDef.GoldBuyOpsReq)
def processGoldBuy(session, msg):
    player = session.player

    opstype = msg.opstype
    price = msg.price


    if opstype == 0:
        player.addGold(price, True)
        retMsg = MsgDef.GoldBuyOpsRet(0, price)
        session.sendMsg(MsgDef.ServerCmd.GOLD_BUY_OPS, retMsg)

    return





















