# -*- coding: utf-8 -*-
from msgtype import ttypes as MsgDef
import idtool
from db import DbServicePlayer as DbServicePlayer
from db import DbService
from base import Base
import ffext
import json
import weakref

# 恶心就恶心了 :)
def _RankDataNodeComp(ranktype, data):
    if not data:
        return -1
    if ranktype == MsgDef.RankType.FULL_FIGHTPOWER:
        return data.fightpower
    elif ranktype == MsgDef.RankType.LEVEL:
        return data.level
    elif ranktype == MsgDef.RankType.GOLD:
        return data.gold
    elif ranktype == MsgDef.RankType.WUJIANG_FIGHTPOWER:
        return data.fightpower
    elif ranktype == MsgDef.RankType.CESHI_FIGHTPOWER:
        return data.fightpower
    elif ranktype == MsgDef.RankType.GONGJIAN_FIGHTPOWER:
        return data.fightpower
    elif ranktype == MsgDef.RankType.SHUSHI_FIGHTPOER:
        return data.fightpower
    elif ranktype == MsgDef.RankType.JUNTUAN_FIGHTPOWER:
        return data.fightpower
    elif ranktype == MsgDef.RankType.JUNTUAN_LEVEL:
        return data.level
    elif ranktype == MsgDef.RankType.ZHANLING_COUNT:
        return data.count
    elif ranktype == MsgDef.RankType.BROTHER_FIGHTPOWER:
        return data.fightpower
    elif ranktype == MsgDef.RankType.MARRY_FIGHTPOWER:
        return data.fightpower
    return -1

class RankDataInfo:
    def __init__(self):
        self.rankType = MsgDef.RankType.NONE_VALUE  #就是rank的ID：已无力命名
        self.listRank = []                          #MsgDef.RankDataNode
        return

    def getListRank(self):
        return self.listRank

    def addRDNode(self, rdNode):
        self.listRank.append(rdNode)

    def doSort(self):
        self.listRank.sort(key = lambda x:_RankDataNodeComp(self.rankType, x), reverse=True)
        # 设置新的排名rank值（1起始）
        for i in range(0, len(self.listRank)):
            self.listRank[i].rank = i + 1
            pass
        return

    def doUpdateWholeList(self, listR):
        self.listRank = listR
        self.doSort()
        return

    def toDataJsonObj(self):
        retObj = []
        for rankSingle in self.listRank:
            rankSingleObj = {
                'rank': rankSingle.rank,
                'name': rankSingle.name,
                'uid': rankSingle.uid,
                'job': rankSingle.job,
                'level': rankSingle.level,
                'fp': rankSingle.fightpower,
                'gold': rankSingle.gold,
                'count': rankSingle.count,
                'gn': rankSingle.guild_name,
                'gid': rankSingle.guild_id,
            }
            retObj.append(rankSingleObj)
        return retObj

    def toDataJsonStr(self):
        jsonObj = self.toDataJsonObj()
        if not jsonObj:
            return '[]'
        return json.dumps(jsonObj, ensure_ascii=False)

    def saveData(self):
        if self.rankType == MsgDef.RankType.NONE_VALUE:
            return False
        DbService.getPlayerService().updateRank(self.rankType, self.toDataJsonStr())
        return True

    def initRankdDataNodeFromJsonObj(self, rdNode, jsonObj):
        if not rdNode or not jsonObj:
            return False
        rdNode.rank = jsonObj.get('rank', 0)
        rdNode.name = jsonObj.get('name', '').encode('utf-8')
        rdNode.uid = jsonObj.get('uid', 0)
        rdNode.job = jsonObj.get('job', 0)
        rdNode.level = jsonObj.get('level', 0)
        rdNode.fightpower = jsonObj.get('fp', 0)
        rdNode.gold = jsonObj.get('gold', 0)
        rdNode.count = jsonObj.get('count', 0)
        rdNode.guild_name = jsonObj.get('gn', '').encode('utf-8')
        rdNode.guild_id = jsonObj.get('gid', 0)
        return True

    def initFromDbData(self, type, dataStr):
        if type <= MsgDef.RankType.NONE_VALUE or type > MsgDef.RankType.MARRY_FIGHTPOWER:
            return False
        if not dataStr or dataStr == '':
            return False
        #ret = MsgDef.RankDataNode()
        #ffext.dump("init from db data-str:", dataStr)
        dataObj = json.loads(dataStr)
        if not dataObj:
            return False
        if len(dataObj) <= 0:
            return False
        self.rankType = type
        for singleDataObj in dataObj:
            if len(singleDataObj) <= 0:
                continue
            rdNode = MsgDef.RankDataNode()
            if self.initRankdDataNodeFromJsonObj(rdNode, singleDataObj):
                self.listRank.append(rdNode)
        return True

class RankMgr:
    def __init__(self):
        self.allRankInfo = {} #rankTypeId(MsgDef.RankType.MARRY_FIGHTPOWER) -> RankDataInfo
        return

    def getAllRankInfo(self):
        return self.allRankInfo
    def getRankInfo(self, id):
        return self.allRankInfo.get(id)
    def addRankInfo(self, id, info):
        self.allRankInfo[id] = info
    def delRankById(self, id):
        self.allRankInfo.pop(id, None)

    def genRankDataInfo(self, id, data):
        retInfo = RankDataInfo()
        retInfo.initFromDbData(id, data)
        ffext.dump("get data from db type:", MsgDef.RankType._VALUES_TO_NAMES[id], " and data:", `retInfo`)
        return retInfo

    def genRDNodeFromDbResult1(self, i, rdNode, dbRow):
        #select uid,username,job,level,fightpower,gold
        rdNode.rank = i + 1
        rdNode.name = str(dbRow[1])
        rdNode.uid = long(dbRow[0])
        rdNode.job = int(dbRow[2])
        rdNode.level = int(dbRow[3])
        rdNode.fightpower = long(dbRow[4])
        rdNode.gold = int(dbRow[5])
        rdNode.count = 0
        rdNode.guild_name = ''
        rdNode.guild_id = 0
        return True

    def dataFromDailyRefresh(self, ranktype, db):
        ffext.dump("refresh db data type:", MsgDef.RankType._VALUES_TO_NAMES[ranktype])
        if not db or not db.result:
            ffext.dump("refresh db data get empty ......")
            return False
        dbResult = db.result

        rankInfoRefreshed = RankDataInfo()
        rankInfoRefreshed.rankType = ranktype

        #select uid,username,job,level,fightpower,gold from player order by fightpower desc,uid   limit 100
        if ranktype == MsgDef.RankType.FULL_FIGHTPOWER:
            for i in range(0, len(dbResult)):
                rdNode = MsgDef.RankDataNode()
                self.genRDNodeFromDbResult1(i, rdNode, dbResult[i])

                #ffext.dump("refresh db data type:", MsgDef.RankType._VALUES_TO_NAMES[ranktype], " and data:", `rdNode`)

                rankInfoRefreshed.addRDNode(rdNode)
                pass
            pass
        #select uid,username,job,level,fightpower,gold from player order by level desc,uid limit 100
        elif ranktype == MsgDef.RankType.LEVEL:
            for i in range(0, len(dbResult)):
                rdNode = MsgDef.RankDataNode()
                self.genRDNodeFromDbResult1(i, rdNode, dbResult[i])

                ffext.dump("refresh db data type:", MsgDef.RankType._VALUES_TO_NAMES[ranktype], " and data:", `rdNode`)

                rankInfoRefreshed.addRDNode(rdNode)
                pass
            pass
        #select uid,username,job,level,fightpower,gold from player order by gold desc,uid limit 100
        elif ranktype == MsgDef.RankType.GOLD:
            for i in range(0, len(dbResult)):
                rdNode = MsgDef.RankDataNode()
                self.genRDNodeFromDbResult1(i, rdNode, dbResult[i])

                ffext.dump("refresh db data type:", MsgDef.RankType._VALUES_TO_NAMES[ranktype], " and data:", `rdNode`)

                rankInfoRefreshed.addRDNode(rdNode)
                pass
            pass
        #select uid,username,job,level,fightpower,gold from player where job=1 order by fightpower desc,uid   limit 100
        elif ranktype == MsgDef.RankType.WUJIANG_FIGHTPOWER:
            for i in range(0, len(dbResult)):
                rdNode = MsgDef.RankDataNode()
                self.genRDNodeFromDbResult1(i, rdNode, dbResult[i])

                ffext.dump("refresh db data type:", MsgDef.RankType._VALUES_TO_NAMES[ranktype], " and data:", `rdNode`)

                rankInfoRefreshed.addRDNode(rdNode)
                pass
            pass
        #select uid,username,job,level,fightpower,gold from player where job=2 order by fightpower desc,uid   limit 100
        elif ranktype == MsgDef.RankType.CESHI_FIGHTPOWER:
            for i in range(0, len(dbResult)):
                rdNode = MsgDef.RankDataNode()
                self.genRDNodeFromDbResult1(i, rdNode, dbResult[i])

                ffext.dump("refresh db data type:", MsgDef.RankType._VALUES_TO_NAMES[ranktype], " and data:", `rdNode`)

                rankInfoRefreshed.addRDNode(rdNode)
                pass
            pass
        #select uid,username,job,level,fightpower,gold from player where job=4 order by fightpower desc,uid   limit 100
        elif ranktype == MsgDef.RankType.GONGJIAN_FIGHTPOWER:
            for i in range(0, len(dbResult)):
                rdNode = MsgDef.RankDataNode()
                self.genRDNodeFromDbResult1(i, rdNode, dbResult[i])

                ffext.dump("refresh db data type:", MsgDef.RankType._VALUES_TO_NAMES[ranktype], " and data:", `rdNode`)

                rankInfoRefreshed.addRDNode(rdNode)
                pass
            pass
        #select uid,username,job,level,fightpower,gold from player where job=3 order by fightpower desc,uid   limit 100
        elif ranktype == MsgDef.RankType.SHUSHI_FIGHTPOER:
            for i in range(0, len(dbResult)):
                rdNode = MsgDef.RankDataNode()
                self.genRDNodeFromDbResult1(i, rdNode, dbResult[i])

                ffext.dump("refresh db data type:", MsgDef.RankType._VALUES_TO_NAMES[ranktype], " and data:", `rdNode`)

                rankInfoRefreshed.addRDNode(rdNode)
                pass
            pass
        #select a.guildid,a.guildname,a.guildlevel, "[会长]" as gname, sum(c.fightpower) as total_fight from guildinfo as a, guildmemberinfo as b,
        #  player as c where a.guildid = b.guildid and b.uid = c.uid group by a.guildid order by total_fight desc,a.guildid limit 100
        elif ranktype == MsgDef.RankType.JUNTUAN_FIGHTPOWER:
            for i in range(0, len(dbResult)):
                rdNode = MsgDef.RankDataNode()
                # self.genRDNodeFromDbResult1(i, rdNode, dbResult[i])
                rdNode.rank = i + 1
                rdNode.name = str(dbResult[i][3])
                rdNode.uid = 0
                rdNode.job = 0
                rdNode.level = int(dbResult[i][2])
                rdNode.fightpower = long(dbResult[i][4])
                rdNode.gold = 0
                rdNode.count = 0
                rdNode.guild_name = str(dbResult[i][1])
                rdNode.guild_id = long(dbResult[i][0])

                ffext.dump("refresh db data type:", MsgDef.RankType._VALUES_TO_NAMES[ranktype], " and data:", `rdNode`)

                rankInfoRefreshed.addRDNode(rdNode)
                pass
            pass
        #select guildid,guildname,guildlevel from guildinfo order by guildlevel desc,guildid limit 100
        elif ranktype == MsgDef.RankType.JUNTUAN_LEVEL:
            for i in range(0, len(dbResult)):
                rdNode = MsgDef.RankDataNode()
                # self.genRDNodeFromDbResult1(i, rdNode, dbResult[i])
                rdNode.rank = i + 1
                rdNode.name = ''
                rdNode.uid = 0
                rdNode.job = 0
                rdNode.level = int(dbResult[i][2])
                rdNode.fightpower = ''
                rdNode.gold = 0
                rdNode.count = 0
                rdNode.guild_name = str(dbResult[i][1])
                rdNode.guild_id = long(dbResult[i][0])

                ffext.dump("refresh db data type:", MsgDef.RankType._VALUES_TO_NAMES[ranktype], " and data:", `rdNode`)

                rankInfoRefreshed.addRDNode(rdNode)
                pass
            pass
        elif ranktype == MsgDef.RankType.ZHANLING_COUNT:
            #TODO
            return True
        #select a.bid, group_concat(b.username) as  bro_names, sum(b.fightpower) as total_fight from brother as a, player as b
        #  where b.uid in (a.uid1, a.uid2, a.uid3) group by a.bid order by total_fight desc,a.bid limit 100
        elif ranktype == MsgDef.RankType.BROTHER_FIGHTPOWER:
            for i in range(0, len(dbResult)):
                rdNode = MsgDef.RankDataNode()
                # self.genRDNodeFromDbResult1(i, rdNode, dbResult[i])
                rdNode.rank = i + 1
                rdNode.name = str(dbResult[i][1])
                rdNode.uid = long(dbResult[i][0])
                rdNode.job = 0
                rdNode.level = 0
                rdNode.fightpower = long(dbResult[i][2])
                rdNode.gold = 0
                rdNode.count = 0
                rdNode.guild_name = ''
                rdNode.guild_id = 0

                ffext.dump("refresh db data type:", MsgDef.RankType._VALUES_TO_NAMES[ranktype], " and data:", `rdNode`)

                rankInfoRefreshed.addRDNode(rdNode)
                pass
            pass
        #select a.marryid, group_concat(b.username) as  m_names, sum(b.fightpower) as total_fight from marryinfo as a, player as b
        #  where b.uid in (a.uid1, a.uid2) group by a.marryid order by total_fight desc,a.marryid limit 100
        elif ranktype == MsgDef.RankType.MARRY_FIGHTPOWER:
            for i in range(0, len(dbResult)):
                rdNode = MsgDef.RankDataNode()
                # self.genRDNodeFromDbResult1(i, rdNode, dbResult[i])
                rdNode.rank = i + 1
                rdNode.name = str(dbResult[i][1])
                rdNode.uid = long(dbResult[i][0])
                rdNode.job = 0
                rdNode.level = 0
                rdNode.fightpower = long(dbResult[i][2])
                rdNode.gold = 0
                rdNode.count = 0
                rdNode.guild_name = ''
                rdNode.guild_id = 0

                ffext.dump("refresh db data type:", MsgDef.RankType._VALUES_TO_NAMES[ranktype], " and data:", `rdNode`)

                rankInfoRefreshed.addRDNode(rdNode)
                pass
            pass

        #替换原来的排行榜
        self.addRankInfo(ranktype, rankInfoRefreshed)
        rankInfoRefreshed.saveData()
        return True

    def broadcastToAllClientNewRank(self):
        #TODO
        return True

    #每日排行榜数据刷新
    def dailyRefresh(self):
        def callback(dbSet):
            # 命名很难看，意义好理解 :)
            # init one by one, if not exists, make empty one

            db_FULL_FIGHTPOWER = dbSet['FULL_FIGHTPOWER']
            if db_FULL_FIGHTPOWER.isOk():
                getRankMgr().dataFromDailyRefresh(MsgDef.RankType.FULL_FIGHTPOWER, db_FULL_FIGHTPOWER)
            db_LEVEL = dbSet['LEVEL']
            if db_LEVEL.isOk():
                getRankMgr().dataFromDailyRefresh(MsgDef.RankType.LEVEL, db_LEVEL)
            db_GOLD = dbSet['GOLD']
            if db_GOLD.isOk():
                getRankMgr().dataFromDailyRefresh(MsgDef.RankType.GOLD, db_GOLD)
            db_WUJIANG_FIGHTPOWER = dbSet['WUJIANG_FIGHTPOWER']
            if db_WUJIANG_FIGHTPOWER.isOk():
                getRankMgr().dataFromDailyRefresh(MsgDef.RankType.WUJIANG_FIGHTPOWER, db_WUJIANG_FIGHTPOWER)
            db_CESHI_FIGHTPOWER = dbSet['CESHI_FIGHTPOWER']
            if db_CESHI_FIGHTPOWER.isOk():
                getRankMgr().dataFromDailyRefresh(MsgDef.RankType.CESHI_FIGHTPOWER, db_CESHI_FIGHTPOWER)
            db_GONGJIAN_FIGHTPOWER = dbSet['GONGJIAN_FIGHTPOWER']
            if db_GONGJIAN_FIGHTPOWER.isOk():
                getRankMgr().dataFromDailyRefresh(MsgDef.RankType.GONGJIAN_FIGHTPOWER, db_GONGJIAN_FIGHTPOWER)
            db_SHUSHI_FIGHTPOER = dbSet['SHUSHI_FIGHTPOER']
            if db_SHUSHI_FIGHTPOER.isOk():
                getRankMgr().dataFromDailyRefresh(MsgDef.RankType.SHUSHI_FIGHTPOER, db_SHUSHI_FIGHTPOER)
            db_JUNTUAN_FIGHTPOWER = dbSet['JUNTUAN_FIGHTPOWER']
            if db_JUNTUAN_FIGHTPOWER.isOk():
                getRankMgr().dataFromDailyRefresh(MsgDef.RankType.JUNTUAN_FIGHTPOWER, db_JUNTUAN_FIGHTPOWER)
            db_JUNTUAN_LEVEL = dbSet['JUNTUAN_LEVEL']
            if db_JUNTUAN_LEVEL.isOk():
                getRankMgr().dataFromDailyRefresh(MsgDef.RankType.JUNTUAN_LEVEL, db_JUNTUAN_LEVEL)
            db_BROTHER_FIGHTPOWER = dbSet['BROTHER_FIGHTPOWER']
            if db_BROTHER_FIGHTPOWER.isOk():
                getRankMgr().dataFromDailyRefresh(MsgDef.RankType.BROTHER_FIGHTPOWER, db_BROTHER_FIGHTPOWER)
            db_MARRY_FIGHTPOWER = dbSet['MARRY_FIGHTPOWER']
            if db_MARRY_FIGHTPOWER.isOk():
                getRankMgr().dataFromDailyRefresh(MsgDef.RankType.MARRY_FIGHTPOWER, db_MARRY_FIGHTPOWER)

            #广播更新新的排行榜数据
            getRankMgr().broadcastToAllClientNewRank()
            return

        DbService.getPlayerService().loadAllRankOnDailyRefresh(callback)
        pass

    def doInitRankRecordWithExcept(self, exceptList):
        for i in range(MsgDef.RankType.FULL_FIGHTPOWER, MsgDef.RankType.MAX_VALUE):
            if exceptList != None and i not in exceptList:
                DbService.getPlayerService().addRank(i, MsgDef.RankRefreshType.DAILY)
        return True

    def init(self):
        def cb(ret):
            exceptList = [] #不需要初始化的type列表
            for rankRow in ret.result:
                rankId = int(rankRow[0])
                rankType = int(rankRow[1])
                rankData = rankRow[2]
                exceptList.append(rankId)
                if rankType == MsgDef.RankRefreshType.DAILY:
                    rankInfo = getRankMgr().genRankDataInfo(rankId, rankData)
                    if rankInfo:
                        getRankMgr().addRankInfo(rankId, rankInfo)
                else:
                    ffext.dump("not support")
            getRankMgr().doInitRankRecordWithExcept(exceptList)
            return

        DbService.getPlayerService().loadAllRankOnInit(cb)
        return True

gRMgr = RankMgr()
def getRankMgr():
    return gRMgr

