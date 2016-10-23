# -*- coding: utf-8 -*-
import  weakref
from base import  Base
import msgtype.ttypes as MsgDef
import os
import ffext
import random
import math
#副本相关的操作
class CopyMapHandler(Base.BaseObj):
    def __init__(self, autoClose = True):
        self.autoClose = autoClose #当没有玩家在副本时，自动析构
        self.createTime = ffext.getTime()
        return
    def onStart(self, mapObj):
        return True
    def onEnd(self, mapObj):
        return True
    def handleTimer(self, mapObj):
        #ffext.dump('CopyMapHandler handleTimer')
        return True
    def handleObjDie(self, mapObj, obj):
        return True
    def handlePlayerRevive(self, mapObj, obj):
        return True
    def handleObjEnter(self, mapObj, obj):
        ffext.dump('CopyMapHandler handleObjEnter', obj.name)
        return True
    def handleObjLeave(self, mapObj, obj):
        ffext.dump('CopyMapHandler handleObjLeave', obj.name)
        return True
    def handleEvent(self, mapObj, obj, event):
        return True
class MapProp:
    TRANSFER_POINT = 1
class MapPos(Base.BaseObj):
    def __init__(self, blockIndex = 0):
        self.obj   = {}
        self.prop  = 0#坐标点属性，是否是传送点
        self.blockIndex = blockIndex
class MapBlock(Base.BaseObj):
    def __init__(self):
        self.players   = {}
        self.all      = {}
    def addObj(self, uid, obj):
        if obj.getType()  == Base.PLAYER:
            self.players[uid] = obj
        self.all[uid] = obj
    def delObj(self, uid):
        self.players.pop(uid, None)
        return  self.all.pop(uid, None)
ObjType2ServerCmd = {
    Base.MONSTER: MsgDef.ServerCmd.MONSTER_ENTER_MAP,
    Base.ITEM: MsgDef.ServerCmd.ITEM_ENTER_MAP,
    Base.NPC: MsgDef.ServerCmd.NPC_ENTER_MAP,
    Base.PLAYER: MsgDef.ServerCmd.ENTER_MAP,
}
class MapObjInfo:
    def __init__(self, player = None):
        self.player = None
        self.x      = 0
        self.y      = 0
        self.blockIndex = 0
        if player:
            self.setPlayer(player)
    def setPlayer(self, player):
        self.player = player
        self.x = player.x
        self.y = player.y
#地图类，封装一个地图的属性和操作
class MapObj(Base.BaseObj):
    def  __init__(self, cfg, mapname, width, height, allPos, keyName = None):
        self.cfg      = cfg
        #self.keyName  = mapname#唯一性地图名
        self.showName = ''
        self.mapname  = mapname
        self.tmxFilePath = ''#地图文件名
        if keyName != None:
            self.mapname = str(keyName)
        self.width    = width
        self.height   = height
        self.allPos   = allPos#地图上所有点，index = Y * width + X
        self.allMovePos = []#所有可以移动的点，方便随机
        self.allBlock  = [] #地图被分成大格子，方便广播
        self.copyMapHandler = None#副本处理事件的对象

        #先生成block点
        self.blockWidth  = int(math.ceil(self.width*1.0 / Base.MAP_BLOCK_SIZE))
        self.blockHeight = int(math.ceil(self.height*1.0 / Base.MAP_BLOCK_SIZE))
        for y in range(self.blockHeight):
            for x in range(self.blockWidth):
                self.allBlock.append(MapBlock())
        def calBlockIndex(x, y):
            blockX = int(math.ceil(x * 1.0 / Base.MAP_BLOCK_SIZE))
            if blockX > 0:
                blockX -= 1
            blockY = int(math.ceil(y * 1.0 / Base.MAP_BLOCK_SIZE))
            if blockY > 0:
                blockY -= 1
            return blockY * self.blockWidth + blockX
        #整理一下数据结构
        for y in range(self.height):
            for x in range(self.width):
                index = y * width + x

                if index >= len(self.allPos):
                    ffext.dump('MapObj init out range', x, y)
                    continue
                val   = self.allPos[index]
                # if x == 85 and y == 165:
                #     ffext.dump('MapObj init x, y, val',x, y, val)
                # if x == 27 and y == 4:
                #     ffext.dump('MapObj init x, y, val',x, y, val)

                if val == 0:
                    self.allPos[index] = None
                else:
                    self.allMovePos.append((x, y))
                    self.allPos[index] = MapPos(calBlockIndex(x, y))#存储id-> obj

        #上次更新怪物的时间
        self.lastMonsterUpdateMs = 0
    @property
    def allMonter(self):
        return ffext.ff.get_obj_by_type(self.mapname, Base.MONSTER)
    @property
    def allPlayer(self):
        return ffext.ff.get_obj_by_type(self.mapname, Base.PLAYER)
    #清理数据
    def cleanup(self):
        self.copyMapHandler = None
        for pos in self.allPos:
            if None != pos:
                pos.obj = {}
        return True
    def canMove(self, x, y):
        return ffext.ff.can_move(self.mapname, x, y)
    def getObjById(self, uid):
        return ffext.ff.get_obj_by_id(self.mapname, uid)
    def getPlayerById(self, uid):
        obj = self.getObjById(uid)
        if obj and obj.getType() == Base.PLAYER:
            return obj
        return None
    #获取索引id
    def getIndex(self, x, y):
        return y * self.width + x
    #获取随即点
    def getRandMovePos(self):
        rand = self.allMovePos[random.randint(0, len(self.allMovePos) - 1)]
        return self.allPos[rand[1] * self.width + rand[0]]
    def getRandMoveXY(self):
        rand = self.allMovePos[random.randint(0, len(self.allMovePos) - 1)]
        return rand
    def getPlayerNum(self):
        return  ffext.ff.get_num_by_type(self.mapname, Base.PLAYER)
    def getObjByPos(self, x, y, objType):
        allobj = ffext.ff.get_objs_by_xy(self.mapname, x, y)
        for v in allobj:
            if v.getType() == objType:
                return v
        return None

    def getAliveObjByPos(self, x, y):
        allobj = ffext.ff.get_objs_by_xy(self.mapname, x, y)
        for v in allobj:
            if v.getType() == Base.PLAYER or v.getType() == Base.MONSTER:
                if v.isDeath() == False:
                    return v
        return None
    #第一次进入地图
    def playerEnterMap(self, player, x = None, y = None, msgToSelf = True):
        if player.mapObj:
            player.mapObj.playerLeaveMap(player, msgToSelf)

        player.mapObj = self
        player.mapname = self.mapname
        player.x = x
        player.y = y
        ret = ffext.ff.obj_enter(player, player.uid, self.mapname, x, y, player.direction, msgToSelf, player.session.nameGate, player.session.getSocketId())
        if ret == 0:
            player.mapObj = self
            player.x = x
            player.y = y
            if self.copyMapHandler:
                self.copyMapHandler.handleObjEnter(self, player)
            return True
        return False
    def playerLeaveMap(self, player, msgToSelf = True):
        #ffext.dump('playerLeaveMap', player.name)
        ret = ffext.ff.obj_leave(player, player.uid, msgToSelf)
        if ret != 0:
            return False
        player.mapObj = None
        if ret == 0 and self.copyMapHandler:
            try:
                self.copyMapHandler.handleObjLeave(self, player)
            except:
                ffext.error('self.copyMapHandler.handleObjLeave failed mapname=%s player=%s'%(self.mapname, player.name))
        return True
    def movePlayer(self, player, x, y, msgFlag = True):
        player.x  = x
        player.y  = y
        ret = ffext.ff.obj_move(player, player.uid, x, y, player.direction)
        if ret == 0:
            player.x  = x
            player.y  = y
            return True
        return False
    def monsterEnterMap(self, monster, x, y, msgToSelf = True):#怪物出现
        #ffext.dump('monsterEnterMap', monster.name)
        if monster.mapObj:
            monster.mapObj.monsterLeaveMap(monster)

        monster.mapObj = self
        monster.x = x
        monster.y = y
        ret = ffext.ff.obj_enter(monster, monster.uid, self.mapname, x, y, monster.direction, msgToSelf, '', 0)
        if ret == 0:
            monster.mapObj = self
            monster.x = x
            monster.y = y
            return True
        return True
    def moveObj(self, obj, x, y, msgFlag = True):
        if obj.getType() == Base.PLAYER:
            return self.movePlayer(obj, x, y, msgFlag)
        else:
            return self.moveMonster(obj, x, y, msgFlag)
    def monsterLeaveMap(self, monster):#怪物消失
        if monster.mapObj:
            ffext.dump('monsterLeaveMap', monster.name, monster.x, monster.y)
        ret = ffext.ff.obj_leave(monster, monster.uid, True)
        if ret != 0:
            return False
        monster.mapObj = None
        return monster
    def moveMonster(self, monster, x, y, msgFlag = True):
        ret = ffext.ff.obj_move(monster, monster.uid, x, y, monster.direction)
        if ret == 0:
            monster.x  = x
            monster.y  = y
            return True
        return True
    #获取一定范围内的玩家对象
    def getPlayerInRange(self, x, y, n):
        ret = []
        def cb(obj):
            if obj and obj.getType() == Base.PLAYER and Base.distance(x, y, obj.x, obj.y) <= n:
                ret.append(obj)
            return
        self.foreachInRange(x, y, cb)
        return ret
    #获取一定范围内的怪对象
    def getMonsterInRange(self, x, y, n):
        def cb(obj):
            if obj and obj.getType() == Base.MONSTER and Base.distance(x, y, obj.x, obj.y) <= n:
                func(obj)
            return
        self.foreachInRange(x, y, cb)
    #获取一定范围内的怪对象
    def foreachObjInRange(self, x, y, n, func):
        def cb(obj):
            if obj and Base.distance(x, y, obj.x, obj.y) <= n:
                func(obj)
            return
        self.foreachInRange(x, y, cb)
    def itemEnterMap(self, item, x, y):#道具出现
        if item.mapObj:
            item.mapObj.itemLeaveMap(item)
        #ffext.dump('itemEnterMap', item.itemCfg.name)

        item.mapObj = self
        item.x = x
        item.y = y
        ret = ffext.ff.obj_enter(item, item.uid, self.mapname, x, y, 0, True, '', 0)
        if ret == 0:
            item.mapObj = self
            item.x = x
            item.y = y
            return True
        return True
    def itemLeaveMap(self, item):#道具消失
        ret = ffext.ff.obj_leave(item, item.uid, True)
        if ret != 0:
            return None
        item.mapObj = None
        return item
    def npcEnterMap(self, npc, x, y):#NPC出现
        #ffext.dump('npcEnterMap', npc.name)
        if npc.mapObj:
            npc.mapObj.npcLeaveMap(npc)

        npc.mapObj = self
        npc.x = x
        npc.y = y
        ret = ffext.ff.obj_enter(npc, npc.uid, self.mapname, x, y, npc.direction, True, '', 0)
        if ret == 0:
            npc.mapObj = self
            npc.x = x
            npc.y = y
            return True
        return True
    def npcLeaveMap(self, npc):#npc消失
        ret = ffext.ff.obj_leave(npc, npc.uid, True)
        if ret != 0:
            return None
        npc.mapObj = None
        return npc
    def getNpc(self, uid):#获取NPC
        npc = self.getObjById(uid)
        if npc and npc.getType() == Base.NPC:
            return  npc
        return None
    def broadcast(self, x, y, cmd, msg, excludePlayer = None):
        #ffext.dump('broadcast', x, y, cmd, msg)
        excludeUid = 0
        if excludePlayer:
            excludeUid = excludePlayer.uid
        ffext.ff.broadcast(self.mapname, x, y, cmd, ffext.encodeMsg(msg), excludeUid)
        return True
        def cb(obj):
            if obj.getType() == Base.PLAYER and obj.uid != excludeUid:
                obj.sendMsg(cmd, msg)
            return
        self.foreachInRange(x, y, cb)
        return  True
    def foreachInRange(self, x, y, func):
        return ffext.ff.foreach_in_range(self.mapname, x, y, func)
class MapPosData(Base.BaseObj):
    def __init__(self):
        self.mapname = ''
        self.x = 0
        self.y = 0

class MapCfg(Base.BaseObj):
    def __init__(self):
        self.reviveMap = None#复活后的地图
        self.offlineMap= None #下线后踢到地图
        self.allPos    = None#所有坐标点

def chekcCopyMap():
    ffext.timer(Base.COPY_MAP_TIMER_MS, chekcCopyMap)
    getMapMgr().chekcCopyMap()
class TransferPoint(Base.BaseObj):
    def __init__(self):
        self.cfgid  = 0#坐标点属性，是否是传送点
        self.mapid  = 0
        self.x      = 0
        self.y      = 0
        self.tomapid= 0
        self.tox    = 0
        self.toy    = 0
#地图管理类，封装所有的地图
class MapMgr(object):
    def  __init__(self):
        self.id2map     = {}#地图id 对应的地图对象
        self.allMap     = {}#地图id str(id)对应的地图对象
        self.file2map   = {}
        self.allCopyMap = {}#地图 str(id) 对应的地图对象
        self.cacheCopyMap = {} #缓存用过的副本地图
        self.allTransfeerPoint = {}#所有传送点
    def allocMap(self, mapname):
        mapname = str(mapname)
        ret = self.allMap.get(mapname)
        if ret == None:
            if mapname.__class__ == str and  mapname.find('_') > 0:
                mapname = mapname.split('_')[0]
                ret = self.allMap.get(mapname)
                if ret:
                    return ret
            ret = self.id2map.get(int(mapname))
        return ret
    def allocMapByFile(self, fileName):
        for k, v in self.allMap.iteritems():
            if v.mapname == fileName:
                return v
        return None
    def getDefaultMap(self, player):
        for k, v in self.allMap.iteritems():
            return v
    def init(self, TopDir):
        subdir     = TopDir + '/cfg/map'
        allMapFile = os.listdir(subdir)
        file2data  = {}
        for k in allMapFile:
            fileName = k[0:-4]
            fileNameStr = '%s/%s'%(subdir, k)
            width, height, mapPos = ffext.readTMCMap(fileNameStr)
            #ffext.dump('MapMgr init k =', k, width, height, len(mapPos), width * height)
            file2data[fileName] = (width, height, mapPos, fileNameStr)
            ffext.ff.create_map(fileName, fileNameStr)
        sql = 'select name, id,revivemap,offlinemap from map'
        db = ffext.allocDbConnection('cfg',ffext.getConfig('-cfg'))
        ret = db.queryResult(sql)
        for row in ret.result:
            showName = row[0]
            fileName= row[1]

            ffext.info('mapmgr %s %s'%(showName, fileName))
            data = file2data.get(fileName)
            if None == data:
                continue
            mapCfg = MapCfg()
            reviveMap = row[2]
            args = reviveMap.split(';')
            if len(args) >= 3:
                mapCfg.reviveMap = MapPosData()
                mapCfg.reviveMap.mapname = args[0]
                mapCfg.reviveMap.x       = int(args[1])
                mapCfg.reviveMap.y       = int(args[2])

            offlineMap= row[3]
            args = offlineMap.split(';')
            if len(args) >= 3:
                mapCfg.offlineMap = MapPosData()
                mapCfg.offlineMap.mapname = args[0]
                mapCfg.offlineMap.x       = int(args[1])
                mapCfg.offlineMap.y       = int(args[2])
            #ffext.dump('mapCfg', mapCfg)
            mapCfg.allPos = data[2]
            mapObj = MapObj(mapCfg, fileName, data[0], data[1], mapCfg.allPos)
            mapObj.showName = showName
            mapObj.tmxFilePath = data[3]
            self.allMap[showName] = mapObj
            self.allMap[fileName] = mapObj
            self.id2map[int(fileName)] = mapObj
        self.readCfgTransferPoint()
        return True
    # 创建副本
    def createCopyMap(self, fromName, copyHandler):
        fromName = str(fromName)
        cacheName = copyHandler.__class__.__name__ + '#' + fromName
        ffext.dump('createCopyMap begin', cacheName)
        mapObj = self.cacheCopyMap.get(cacheName)
        if mapObj:
            ffext.dump('createCopyMap end ok use cache', cacheName, mapObj.mapname)
            newName = mapObj.mapname
            self.allMap[newName] = mapObj
            self.allCopyMap[newName] = mapObj
            mapObj.copyMapHandler = copyHandler
            return mapObj
        if copyHandler == None:
            copyHandler = CopyMapHandler()
        mapObjOld = self.allocMap(fromName)
        if None == mapObjOld:
            return None
        newName = fromName + '_%d' % (ffext.allocId())
        ffext.ff.create_map(newName, mapObjOld.tmxFilePath)
        mapObj = MapObj(mapObjOld.cfg, mapObjOld.mapname, mapObjOld.width, mapObjOld.height, mapObjOld.cfg.allPos, newName)
        mapObj.showName = mapObjOld.showName
        mapObj.copyMapHandler = copyHandler
        self.allMap[newName] = mapObj
        self.allCopyMap[newName] = mapObj
        self.cacheCopyMap[cacheName] = mapObj
        ffext.dump('createCopyMap end ok', fromName)
        return mapObj
    def getTransferPointCfg(self, cfgid):
        return self.allTransfeerPoint.get(cfgid)
    def readCfgTransferPoint(self):
        sql = 'select cfgid, mapid,x,y,tomapid,tox,toy from transferpoint'
        db = ffext.allocDbConnection('cfg',ffext.getConfig('-cfg'))
        ret = db.queryResult(sql)
        self.allTransfeerPoint = {}
        for row in ret.result:
            tp = TransferPoint()
            tp.cfgid = int(row[0])
            tp.mapid = int(row[1])
            tp.x     = int(row[2])
            tp.y     = int(row[3])
            tp.tomapid = int(row[4])
            tp.tox   = int(row[5])
            tp.toy   = int(row[6])
            self.allTransfeerPoint[tp.cfgid] = tp
        #ffext.dump( self.allTransfeerPoint)
        return True
    def initTimer(self):
        ffext.timer(Base.COPY_MAP_TIMER_MS, chekcCopyMap)
    #把所有人踢到某地图
    def kickoutTo(self, mapObj, newName = None, x = None, y = None):
        if mapObj.getPlayerNum() > 0:#踢人
            allPlayer = [v for k, v in mapObj.allPlayer.iteritems()]
            if newName == None:
                newName = '10001'
            newMapObj = self.allocMap(newName)
            ffext.dump('kickoutTo', newName, type(newMapObj))
            if None == newMapObj:
                newMapObj = self.getDefaultMap(allPlayer[0])
            for player in allPlayer:
                mapObj.playerLeaveMap(player)
                newMapObj.playerEnterMap(player, x, y)
        return True

    def closeCopyMap(self, mapname, kickpoutMap = None, x = None, y = None):
        def doOps():
            mapObj = self.allMap.pop(mapname, None)
            if None == mapObj:
                return None
            self.allCopyMap.pop(mapname, None)
            #如果地图上有人，那么踢人
            self.kickoutTo(mapObj, kickpoutMap, x, y)
            #如果有怪，那么把怪给释放掉, 这个时候已经没有人了，不用广播消息了,直接把怪物释放掉即可
            mapObj.cleanup()
            ffext.dump('closeCopyMap', mapname)
        ffext.timer(1, doOps)#立即释放掉
        return True
    def chekcCopyMap(self):
        l = []
        for k, v in self.allCopyMap.iteritems():
            h = v.copyMapHandler
            if h.autoClose and v.getPlayerNum() == 0:
                self.closeCopyMap(v.mapname)

            h.handleTimer(v)
            #ffext.error('copyMapHandler.handleTimer exception keyname=%s'% v.mapname)

gMapMgr = MapMgr()
def getMapMgr():
    return gMapMgr
