# -*- coding: utf-8 -*-
import ffext
from base import Base
import msgtype.ttypes as MsgDef
from mapmgr import MapMgr
from model import NpcModel
ServerCmd = MsgDef.ServerCmd

def buildErrMsg(cmd, errMsg):
    return MsgDef.ErrorMsgRet(0, cmd, errMsg)#'cmd=%d,errMsg=%s'%(cmd, errMsg)

FuncHelper = {
    0: lambda player, npc, func, funcParam: func(player, npc),
    1: lambda player, npc, func, funcParam: func(player, npc, funcParam[0]),
    2: lambda player, npc, func, funcParam: func(player, npc, funcParam[0], funcParam[1]),
    3: lambda player, npc, func, funcParam: func(player, npc, funcParam[0], funcParam[1], funcParam[2]),
    4: lambda player, npc, func, funcParam: func(player, npc, funcParam[0], funcParam[1], funcParam[2], funcParam[3]),
    5: lambda player, npc, func, funcParam: func(player, npc, funcParam[0], funcParam[1], funcParam[2], funcParam[3], funcParam[4]),
    6: lambda player, npc, func, funcParam: func(player, npc, funcParam[0], funcParam[1], funcParam[2], funcParam[3], funcParam[4], funcParam[5]),
    7: lambda player, npc, func, funcParam: func(player, npc, funcParam[0], funcParam[1], funcParam[2], funcParam[3], funcParam[4], funcParam[5], funcParam[6]),
    8: lambda player, npc, func, funcParam: func(player, npc, funcParam[0], funcParam[1], funcParam[2], funcParam[3], funcParam[4], funcParam[5], funcParam[6], funcParam[7]),
    9: lambda player, npc, func, funcParam: func(player, npc, funcParam[0], funcParam[1], funcParam[2], funcParam[3], funcParam[4], funcParam[5], funcParam[6], funcParam[8], funcParam[9]),
}
@ffext.onLogic(MsgDef.ClientCmd.CLICK_NPC, MsgDef.ClickNpcReq)
def processClickNpc(session, msg):
    playerClickNpc(session.player, msg.uid, msg.link)
#点击npc：
#1没有任务---返回CLICK_NPC，显示你返回的内容和按钮
#2是可接的任务---返回CLICK_NPC，显示内容和xxx任务按钮
#3是可交任务--返回SHOW_TASK_PANEL，显示交面板
def playerClickNpc(player, npcid, link = ''):
    ffext.dump('processClickNpc', link)
    mapObj= player.mapObj
    npc   = mapObj.getNpc(npcid)
    if None == npc:
        player.sendMsg(ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.CLICK_NPC, Base.lang('npc invalid')))
        return
    #判断是不是有任务要触发了
    if link == '' and player.taskCtrl.whenClickNpc(npc):
        return
    npcRet = None

    if link == '':
        npcRet = npc.scriptMod.main(player, npc)
    else:
        args = link.split('&')
        funcName = args[0]
        if funcName == '_call_':
            player.doCallBack(int(args[1]))
            return
        func = getattr(npc.scriptMod, funcName, None)
        if None == func:
            player.sendMsg(ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.CLICK_NPC, Base.lang('func invalid:')+funcName))
            return
        funcParam = []
        if len(args) >= 2:
            for i in range(1, len(args)):
                funcParam.append(args[i])
        npcRet = FuncHelper[len(funcParam)](player, npc, func, funcParam)
    ffext.dump('click npc', npcRet)
    if npcRet != None:
        content = ''
        allButt = []
        if npcRet.__class__ == str:
            content = npcRet
        else:
            content = npcRet[0]
            allButt = npcRet[1]
        npc.speakTo(player, content, allButt)
    return


#传送
@ffext.onLogic(MsgDef.ClientCmd.TRANSFER_OPS, MsgDef.TransferOpsReq)
def transfer(session, msg):
    mapname = msg.cfgid
    mapObj = MapMgr.getMapMgr().allocMap(mapname)
    mapObj.playerEnterMap(session.player, msg.x, msg.y, True)




