# -*- coding: utf-8 -*-
import ffext
import msgtype.ttypes as MsgDef
import  weakref
from base import  Base
from model import  TeamModel, PlayerModel, ItemModel, ArenaModel
from db import DbService

def buildErrMsg(cmd, errMsg):
    return MsgDef.ErrorMsgRet(0, cmd, errMsg)#'cmd=%d,errMsg=%s'%(cmd, errMsg)

#竞技场购买价格
AREANA_BUY_PRICE = [
    [1,	2000],
    [2,	3000],
    [3,	4000],
    [4,	5000],
    [5,	6000],
    [6,	7000],
    [7,	8000],
    [8,	9000],
    [9,	10000],
    [10,11000],
]
#竞技场
@ffext.onLogic(MsgDef.ClientCmd.ARENA_OPS, MsgDef.ArenaOpsReq)
def processArenaReq(session, msg = None):
    player = session.player
    arenaCtrl = player.arenaCtrl
    if msg.opstype == 0 or msg.opstype == 1:#0表示显示竞技场数据
        retMsg = MsgDef.ArenaOpsRet(msg.opstype, arenaCtrl.leftChallengeTimes, arenaCtrl.score, ArenaModel.getArenaMgr().getRankByUid(player.uid), [])
        retMsg.listPlayers = ArenaModel.getArenaMgr().allRank
        session.sendMsg(MsgDef.ServerCmd.ARENA_OPS, retMsg)
    elif msg.opstype == 2:#显示积分兑换
        retMsg = MsgDef.ArenaOpsRet(msg.opstype, arenaCtrl.leftChallengeTimes, arenaCtrl.score, arenaCtrl.rank, [], [])

        for k, itemCfgPair in ItemModel.getItemMgr().arenaScoreItem.iteritems():
            item = MsgDef.Item()
            itemCfg = itemCfgPair[0]
            ItemModel.tmpBuildItem(item, itemCfg)
            retMsg.listItems.append(MsgDef.ArenaScore2Item(itemCfgPair[1], item))
        session.sendMsg(MsgDef.ServerCmd.ARENA_OPS, retMsg)
        return
    elif msg.opstype == 3:#积分兑换
        cfgid = msg.idArg
        destCfg = None
        if msg.numArg < 0:
            msg.numArg = 1
        for k, itemCfgPair in ItemModel.getItemMgr().arenaScoreItem.iteritems():
            itemCfg = itemCfgPair[0]
            if itemCfg.cfgId == cfgid:
                destCfg = itemCfgPair
                break
        if None == destCfg:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.ARENA_OPS, '参数有误'))
            return
        score = destCfg[1] * msg.numArg
        if player.arenaCtrl.score < score:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.ARENA_OPS, '积分不足'))
            return
        needPkgNum = msg.numArg
        if destCfg[0].flagDieJia:
            needPkgNum = 1
        if player.itemCtrl.getFreePkgSize() < needPkgNum:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.ARENA_OPS, '包裹不足'))
            return
        player.AddScoreArena(-1 * score)
        itemObj = player.itemCtrl.addItemByCfgId(cfgid)
        from handler import ItemHandler
        ItemHandler.processQueryPkg(session)
        retMsg = MsgDef.ArenaOpsRet(msg.opstype, arenaCtrl.leftChallengeTimes, arenaCtrl.score, arenaCtrl.rank, [], [])
        session.sendMsg(MsgDef.ServerCmd.ARENA_OPS, retMsg)

        return
    elif msg.opstype == 4:#挑战某人
        if player.arenaCtrl.leftChallengeTimes <= 0:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.ARENA_OPS, '每天最多挑战10次'))
            return
        ArenaModel.getArenaMgr().createArena(session.player, msg.destuid)
    return
