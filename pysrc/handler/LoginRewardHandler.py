# -*- coding: utf-8 -*-
import ffext
import json
import weakref
import idtool
import msgtype.ttypes as MsgDef
from base import Base
from model import  LoginRewardModel, ItemModel
from db import DbServicePlayer as DbServicePlayer
from db import DbService

DAILY_AWARD_CFG = [
    "经验（1倍）",
    "金币（1倍）",
    "大补丸（1倍）",
    "强化石+1",
    "经验（2倍）",
    "金币（1.5倍）",
    "宠物蛋（初级）",
    "经验（3倍）",
    "金币（2倍）",
    "大补丸（2倍）",
    "强化石+2",
    "经验（4倍）",
    "金币（2.5倍）",
    "熟铁",
    "经验（5倍）",
    "金币（3倍）",
    "大补丸（3倍）",
    "强化石+3",
    "经验（6倍）",
    "金币（1.6倍）",
    "宠物蛋（中级）",
    "经验（7倍）",
    "金币（4倍）",
    "大补丸（4倍）",
    "强化石+4",
    "经验（8倍）",
    "金币（2.6倍）",
    "钢铁",
    #额外
    "宠物食物-初级",
    "制作卷轴2",
    "宠物食物-中级",
    "制作卷轴4",
]
def getDailyAwardId(index):
    cfg = DAILY_AWARD_CFG[index]
    args = cfg.split('（')
    if args[0] == '经验':
        itemCfg = ItemModel.getItemMgr().getCfgByName('经验')
        if itemCfg:
            return itemCfg.cfgId
    elif args[0] == '金币':
        itemCfg = ItemModel.getItemMgr().getCfgByName('金币')
        if itemCfg:
            return itemCfg.cfgId
    elif args[0] == '大补丸':
        itemCfg = ItemModel.getItemMgr().getCfgByName('大补丸（小）')
        if itemCfg:
            return itemCfg.cfgId
    else:
        itemCfg = ItemModel.getItemMgr().getCfgByName(cfg)
        if itemCfg:
            return  itemCfg.cfgId
        return 2060121
    
BASE_EXP = 100
BASE_GOLD= 10
def giveDailyAwardByIndex(player, index):
    cfg = DAILY_AWARD_CFG[index]
    args = cfg.split('（')
    ffext.dump('args', args[0])
    if args[0] == '经验':
        param = args[1].split('倍')
        timesstr = param[0]
        val = int(BASE_EXP * float(timesstr))
        player.addExp(val, True)
        return 0
    elif args[0] == '金币':
        param = args[1].split('倍')
        timesstr = param[0]
        val = int(BASE_GOLD * float(timesstr))
        player.addGold(val, True)
        return 1
    elif args[0] == '大补丸':
        ffext.dump('args 11', args[0])
        itemCfg = ItemModel.getItemMgr().getCfgByName('大补丸（小）')
        if itemCfg:
            ffext.dump('args 22', args[0])
            player.itemCtrl.getItemByCfgId(itemCfg.cfgId)
            from handler import  ItemHandler
            ItemHandler.processQueryPkg(player.session)
            return itemCfg.cfgId
    else:
        itemCfg = ItemModel.getItemMgr().getCfgByName(cfg)
        if itemCfg:
            player.itemCtrl.getItemByCfgId(itemCfg.cfgId)
            from handler import  ItemHandler
            ItemHandler.processQueryPkg(player.session)
            return itemCfg.cfgId
        return 2060121
#每日奖励操作
@ffext.onLogic(MsgDef.ClientCmd.DAILY_LOGIN_OPS, MsgDef.DailyLoginOpsReq)
def processDailyLoginOPS(session, msg):
    ffext.dump('processDailyLoginOPS', msg)
    opstype = msg.opstype
    cmd     = MsgDef.ClientCmd.DAILY_LOGIN_OPS
    player  = session.player

    reward_id = msg.reward_id
    def genmsg():
        onlineSec = player.getGameTime()
        dailyInfo = MsgDef.DailyLoginInfo(player.loginActCtrl.seven_login_days, player.loginActCtrl.seven_login_mask,
                                          onlineSec, player.loginActCtrl.online_reward_mask,
                                          player.loginActCtrl.invite_reward)
        retMsg = MsgDef.DailyLoginOpsRet(opstype, dailyInfo, [], 0)
        if opstype == MsgDef.DailyLoginOpsCmd.DAILY_OP_ALL_INFO:
            #from handler import ItemHandler
            for i in range(0, 32):
                item = MsgDef.Item()
                #ItemHandler.buildItem(retItem, k)
                #item.uid = itemObj.uid
                #itemCfg = itemObj.itemCfg
                item.itemCfgId = getDailyAwardId(i)
                item.name = DAILY_AWARD_CFG[i]
                #item.strengthenLevel = itemObj.strengthenLevel
                item.lefttimes = 1
                #item.propExt = itemObj.propExt
                #item.propStrengthen = itemObj.toStrenthenPropData()
                retMsg.items.append(item)
            for i in range(0, len(LoginRewardModel.ONLINE_AWARD_CFG)):
                item = MsgDef.Item()
                # ItemHandler.buildItem(retItem, k)
                needSec = LoginRewardModel.ONLINE_AWARD_CFG[i][0]
                item.uid = int(needSec / 60)
                # itemCfg = itemObj.itemCfg
                item.itemCfgId = 1020101
                item.name = '血瓶（小）'
                # item.strengthenLevel = itemObj.strengthenLevel
                item.lefttimes = i + 1
                # item.propExt = itemObj.propExt
                # item.propStrengthen = itemObj.toStrenthenPropData()
                retMsg.items.append(item)
        return  retMsg
    if opstype == MsgDef.DailyLoginOpsCmd.DAILY_OP_ALL_INFO:
        # 获取个人所有每日登录信息
        # TODO
        ffext.dump(player.uid, opstype, reward_id)
        retMsg = genmsg()
        session.sendMsg(MsgDef.ServerCmd.DAILY_LOGIN_OPS_MSG, retMsg)
        pass

    elif opstype == MsgDef.DailyLoginOpsCmd.DAILY_OP_SEVEN_REWARD:
        # 获取七日登录奖励
        ffext.dump(player.uid, opstype, reward_id)
        day = -1
        for k in range(0, 32):
            if player.loginActCtrl.seven_login_days <= k:
                break
            if player.loginActCtrl.seven_login_mask & (1 << k):
                continue
            day = k
            break
        if day == -1 and msg.reward_id >= 28 and msg.reward_id <= 32:
            k = msg.reward_id - 1
            if player.loginActCtrl.seven_login_mask & (1 << k):
                session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '奖励已经领过！'))
                return
            day = k
        if day == -1:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '无奖可领！'))
            return
        giveDailyAwardByIndex(player, day)
        player.loginActCtrl.seven_login_mask |= (1 << day)
        session.player.loginActCtrl.updateData()
        retMsg = genmsg()
        session.sendMsg(MsgDef.ServerCmd.DAILY_LOGIN_OPS_MSG, retMsg)
        pass

    elif opstype == MsgDef.DailyLoginOpsCmd.DAILY_OP_ONLINE_REWARD:
        # 获取每日在线奖励
        ffext.dump(player.uid, opstype, reward_id)
        prizeIndex = -1
        for k in range(0, len(LoginRewardModel.ONLINE_AWARD_CFG)):
            if player.loginActCtrl.online_reward_mask & (1 << k):
                continue
            needSec = LoginRewardModel.ONLINE_AWARD_CFG[k][0]
            onlineSec = player.getGameTime()
            if onlineSec < needSec:
                session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '需要在线%d分钟才能领取！'%(needSec/60)))
                return
                break
            prizeIndex = k
            break
        if prizeIndex == -1:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '无奖可领！'))
            return
        player.loginActCtrl.online_reward_mask |= (1 << prizeIndex)
        session.player.loginActCtrl.updateData()

        retMsg = genmsg()
        session.sendMsg(MsgDef.ServerCmd.DAILY_LOGIN_OPS_MSG, retMsg)
        pass

    elif opstype == MsgDef.DailyLoginOpsCmd.DAILY_OP_INVITE_REWARD:
        player.loginActCtrl.invite_reward = 1
        session.player.loginActCtrl.updateData()
        # 获取邀请奖励
        ffext.dump(player.uid, opstype, reward_id)
        ffext.dump(player.uid, opstype, reward_id)
        dailyInfo = MsgDef.DailyLoginInfo()
        retMsg = MsgDef.DailyLoginOpsRet(opstype, dailyInfo)
        session.sendMsg(MsgDef.ServerCmd.DAILY_LOGIN_OPS_MSG, retMsg)
        pass

    pass


# # 发送邮件附件中的道具、奖励等
# def mailAttachToPlayer(player, attachNode, opstype, cmd):
#     if not attachNode or not player:
#         return
#     if attachNode.type == MsgDef.MailAttachType.MAIL_ATTACH_ITEM:
#         itemObj = player.itemCtrl.addItemByCfgId(attachNode.arg1, attachNode.arg2)
#         if not itemObj:
#             player.sendMsg(MsgDef.ServerCmd.ERROR_MSG, MailModel.processErrorMsgRet(opstype, cmd, '系统忙!'))
#         pass
#     elif attachNode.type == MsgDef.MailAttachType.MAIL_ATTACH_EXP:
#         player.addExp(attachNode.arg1)
#         pass
#     elif attachNode.type == MsgDef.MailAttachType.MAIL_ATTACH_GOLD:
#         player.addGold(attachNode.arg1)
#         pass
#     return

#用于返回错误信息的函数
def processErrorMsgRet(opstype, cmd, msg):
    ret_msg                 = MsgDef.ErrorMsgRet()
    ret_msg.errType         = opstype                           #错误信息所处位置opstype
    ret_msg.cmd             = cmd                               #错误信息所处位置cmd
    ret_msg.errMsg          = msg                               #错误信息
    return ret_msg

