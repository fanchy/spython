# -*- coding: utf-8 -*-
import ffext
import json
import weakref
import idtool
import msgtype.ttypes as MsgDef
from base import Base
from model import  RankModel, TeamModel, ItemModel
from db import DbServicePlayer as DbServicePlayer
from db import DbService

#排行榜操作
@ffext.onLogic(MsgDef.ClientCmd.RANK_OPS, MsgDef.RankOpsReq)
def processRankOPS(session, msg):
    ffext.dump('processRankOPS', msg)
    opstype = msg.opstype
    cmd     = MsgDef.ClientCmd.RANK_OPS
    player  = session.player

    ranktype = msg.ranktype

    if opstype == MsgDef.RankOpsCmd.GET_RANK_INFO:
        rankInfo = RankModel.getRankMgr().getRankInfo(ranktype)
        if not rankInfo:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, "请求排行榜不存在!"))
            return

        session.sendMsg(MsgDef.ServerCmd.RANK_OPS_MSG, processRankOpsRet(opstype, ranktype, rankInfo.getListRank()))
    pass

#排行榜数据，服务器给客户端广播的信息格式
def processRankOpsRet(opstype, ranktype, listRank = []):
    ret_msg = MsgDef.RankOpsRet()
    ret_msg.opstype = opstype
    ret_msg.ranktype = ranktype
    ret_msg.listRank = listRank
    return  ret_msg

#用于返回错误信息的函数
def processErrorMsgRet(opstype, cmd, msg):
    ret_msg                 = MsgDef.ErrorMsgRet()
    ret_msg.errType         = opstype                           #错误信息所处位置opstype
    ret_msg.cmd             = cmd                               #错误信息所处位置cmd
    ret_msg.errMsg          = msg                               #错误信息
    return ret_msg

