# -*- coding: utf-8 -*-
import random
from base   import Base
from mapmgr import MapMgr
import msgtype.ttypes as MsgDef
ServerCmd = MsgDef.ServerCmd
import weakref
import ffext
import json
import idtool

class NpcCfg(Base.BaseObj):
    def __init__(self):
        self.cfgid        = 0#配置id
        self.name         = ''#唯一的名称
        self.appr         = 0 #显示的外形
        self.mapname      = ''#地图
        self.x            = 0
        self.y            = 0
        self.direction    = 0
        self.script       = ''#使用的脚本
        self.defaultDuiBai= ''#默认对白

class Npc(Base.BaseObj):
    def __init__(self):
        self.uid          = idtool.allocTmpId()
        self.name         = ''#唯一的名称
        self.appr         = 0 #显示的外形
        self.mapname      = ''#地图
        self.script       = ''#使用的脚本
        self.x            = 0
        self.y            = 0
        self.direction    = 0
        self.mapObj       = None
        self.scriptMod    = None
        self.cfg          = None
    def getType(self):#类型
        return Base.NPC
    def getDefaultDuiBai(self):
        return self.cfg.defaultDuiBai
    def buildEnterMapMsg(self, flag = False):
        retMsg = MsgDef.NpcEnterMapRet(self.appr, self.uid, self.name, self.x, self.y, self.direction, self.cfg.cfgid)
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
        if flag:
            retMsg = ffext.encodeMsg(retMsg)#, flag, flag
        return retMsg
    def speakTo(self, player, content, buttons = None):
        retMsg = MsgDef.ClickNpcRet(self.uid, content)
        if buttons:
            retMsg.buttons = []
            for k in buttons:
                if len(k) == 2:
                    npcButt = MsgDef.NpcButton(k[1], k[0])
                    retMsg.buttons.append(npcButt)
            player.npcInfo.lastChatContstent = {}
            for k in retMsg.buttons:
                 player.npcInfo.lastChatContstent[k.clickCallbackArg] = k.showText
        else:
            player.npcInfo.lastChatContstent = {}
        player.session.sendMsg(ServerCmd.CLICK_NPC, retMsg)
    def showPlay(self, player, playId, callback = None, args = None):
        callbackId =0
        if callback:
            callbackId = player.addCallBack(callback, args)
        player.session.sendMsg(ServerCmd.SHOW_PLAY, MsgDef.ShowPlayRet(playId, callbackId))
    def showNpcPlay(self, player, playId, strArg = None):
        callbackId =0
        if strArg != None:
            args = (self.uid, strArg)
            callbackId = player.addCallBack(npcClickCallback, args)
        player.session.sendMsg(ServerCmd.SHOW_PLAY, MsgDef.ShowPlayRet(playId, callbackId))
def npcClickCallback(player, args):
    uid = args[0]
    link= args[1]
    from handler import  NpcHandler
    NpcHandler.playerClickNpc(player, uid, link)
    return
def genNpc(name, x, y, appr):
    return
class NpcMgr(Base.BaseObj):
    def __init__(self):
        self.allCfg       = {}
        self.allNpcById   = {} #name -> npc obj
        self.allNpcByName = {} #name -> npc obj
    def getNpcByName(self, name):
        return self.allNpcByName.get(name)
    def getNpcById(self, uid):
        return self.allNpcById.get(uid)
    def init(self):#读取任务配置
        name2DuiBai = self.readdNpcDuibaiCfg()
        db = ffext.allocDbConnection('cfg',ffext.getConfig('-cfg'))
        ret = db.queryResult('select name,appr,mapid,x,y,script,direction,cfgid from npc')
        self.allCfg = {}
        for row in ret.result:
            npcCfg = NpcCfg()
            npcCfg.name = row[0]
            npcCfg.appr = int(row[1])
            npcCfg.mapname  = row[2]
            npcCfg.x        = int(row[3])
            npcCfg.y        = int(row[4])
            npcCfg.script   = row[5]
            npcCfg.direction= int(row[6])
            npcCfg.cfgid    = int(row[7])
            npcCfg.defaultDuiBai = name2DuiBai.get(npcCfg.name, '勇士你好！我是%s'%(npcCfg.name))
            self.allCfg[npcCfg.cfgid] = npcCfg
            mapObj = MapMgr.getMapMgr().allocMapByFile(npcCfg.mapname)
            if not mapObj:
                ffext.warn('gen npc failed name=%s, script=%s, map=%s not in this gs'%(npcCfg.name, npcCfg.script,npcCfg.mapname))
            #ffext.dump('load npc ', npcCfg)
            npc = Npc()
            npc.name  = npcCfg.name
            npc.appr  = npcCfg.appr
            npc.mapname= npcCfg.mapname
            npc.script= npcCfg.script
            npc.direction = npcCfg.direction
            npc.cfg       = npcCfg
            try:
                npc.scriptMod = __import__('npc.'+npc.script, fromlist=[npc.script])

            except:
                ffext.error('gen npc failed name=%s, script=%s map=%s,%d,%d'%(npc.name, npc.script, npcCfg.mapname, npcCfg.x, npcCfg.y))
            try:
                mapObj.npcEnterMap(npc, npcCfg.x, npcCfg.y)
            except:
                ffext.error('gen npc failed2 name=%s, script=%s map=%s,%d,%d'%(npc.name, npc.script, npcCfg.mapname, npcCfg.x, npcCfg.y))
        ffext.dump('load npc num=%d'%(len(self.allCfg)))
        return True
    def readdNpcDuibaiCfg(self):
        db = ffext.allocDbConnection('cfg',ffext.getConfig('-cfg'))
        ret = db.queryResult('select npc,duibai from npcduibai')
        name2DuiBai = {}
        for row in ret.result:
            name2DuiBai[row[0]] = row[1]
        return name2DuiBai
    def genNpc(self, name, x, y, appr):
        return
gNpcMgr = NpcMgr()
def getNpcMgr():
    return gNpcMgr
