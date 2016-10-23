# -*- coding: utf-8 -*-
#本文件用于存放行会的字典操作

import time
import ffext
import weakref
from mapmgr import MapMgr
#调用msgtype中的ttypes文件，使用系统中的枚举函数
from msgtype import ttypes as MsgDef
from db import DbService
from model.copymap import GuildCopy, CityWarCopy
from model import GlobalRecordModel
import  idtool
#创建行会需要的经验
CREAT_GUILD_GOLD = 1
#创建行会需要的最小等级
MIN_GUILD_LEVEL = 10
#行会成员分布表
MAX_GUILD_USER_LEVEL_RANKING1 = 10 #左将军最大排名
MAX_GUILD_USER_LEVEL_RANKING2 = 20 #右将军最大排名
MAX_GUILD_USER_LEVEL_RANKING3 = 50 #将士最大排名
MAX_GUILD_USER_LEVEL_RANKING4 = 100 #兵士最大排名

SECONDS_PER_DAY = 86400

# 可申请城战时间
CITYWAR_APPLY_TM_LIST = {
    # week_day : [begin_tm, end_tm]
    # 7 : 表示星期天
    1 : [1400, 1430], #周一
    3 : [1400, 1430], #周三
    5 : [1400, 1430], #周五
}

# 城战开始时间
CITYWAR_START_TM_LIST = {
    # week_day : [begin_tm, end_tm]
    # 7 : 表示星期天
    2 : [2030, 2230], #周二
    4 : [2030, 2230], #周四
    6 : [2030, 2230], #周六
}

g_debugCityWar = 0
def isCityWarApplyTime():
    #方便测试
    return True


    if g_debugCityWar == 1:
        return True
    nowTm = ffext.datetime_now()
    weekDay = nowTm.weekday()
    if weekDay == 0:
        weekDay = 7
    if CITYWAR_APPLY_TM_LIST.has_key(weekDay):
        tmSet = CITYWAR_APPLY_TM_LIST[weekDay]
        curHour = nowTm.hour # [0, 24)
        curMin = nowTm.minute # [0, 60)
        curT = curHour * 100 + curMin
        return (curT >= tmSet[0] and curT < tmSet[1])
    return False

#创建一个类，用于保存用户的行会信息
class PersonGuildCtrl:
    def __init__(self, owner):
        self.ownerref               = weakref.ref(owner)
        self.allInviter             = []            #所有邀请加入的行会ID
        #self.lastDateContribution   = 0             #行会最后一日贡献度
        #self.lastDate               = ''           #最后一次日期
        self.guildInfo              = None
    def GuildWarWhenKillOther(self, killedPlayer):
        if self.guildInfo:
            otherGuild = killedPlayer.guildCtrl.guildInfo
            if not otherGuild:
                return False
            guildId = self.guildInfo.guildID
            warInfo = getGuildMgr().getWarVSinfo(guildId)
            if warInfo and warInfo.getAnotherGuild().guildID == otherGuild.guildID:
                warInfo.addGuildScore(guildId)
                return True
        return False

    #行会排名战
    def GuildRankWarWhenKillOther(self, killedPlayer):
        if self.guildInfo:
            otherGuild = killedPlayer.guildCtrl.guildInfo
            if not otherGuild:
                return False
            guildId = self.guildInfo.guildID
            rankWarInfo = getGuildMgr().getRankWarVSinfo(guildId)
            if rankWarInfo and rankWarInfo.getAnotherGuild() == otherGuild.guildID:
                rankWarInfo.addGuildScore(guildId)
                #return True
            dead = 0
            for k, v in rankWarInfo.getAnotherTeam().iteritems():
                if v.hp <= 0:
                    dead += 1
                else:
                    return True
            rankWarInfo.setGuildWin(guildId)
            return True
        return False



    @property
    def lastDateContribution(self):
        if not self.guildInfo:
            return  0
        else:
            m = self.guildInfo.getGuildMemberByUid(self.ownerref().uid)
            if not m:
                return 0
            return  m.daycontribute
    @lastDateContribution.setter
    def lastDateContribution(self, value):
        if self.guildInfo:
            self.guildInfo.getGuildMemberByUid(self.ownerref().uid).daycontribute = value
    @property
    def lastDate(self):
        if not self.guildInfo:
            return 0
        else:
            return self.guildInfo.getGuildMemberByUid(self.ownerref().uid).lastdate

    @lastDateContribution.setter
    def lastDate(self, value):
        if self.guildInfo:
            self.guildInfo.getGuildMemberByUid(self.ownerref().uid).lastdate = value
    #声明一个函数，用于格式化打印
    def __repr__(self):
        L = ['%s=%r' % (key, value)
            for key, value in self.__dict__.iteritems()]
        return '%s(%s)' % (self.__class__.__name__, ', '.join(L))
    #将数据库中查询出的数据，传递至用户对象中
    def fromData(self, result):
        if 0 == len(result):
            self.guildInfo              = None
            self.allInviter             = []
            return
        self.guildInfo              = getGuildMgr().getGuildById(long(result[0][0]))
        self.allInviter             = []
        return
    #获取职位
    def getPost(self):
        return self.guildInfo.getGuildMemberByUid(self.ownerref().uid).post
    #玩家更换行会
    def changeGuild(self, guildID):
        self.guildInfo              = getGuildMgr().getGuildById(guildID)
        self.allInviter             = []
        self.lastDateContribution   = 0
        self.lastDate               = ''
        return
    #玩家升级行会
    def updateGuild(self, lastDateContribution, lastDate):
        self.lastDateContribution   = lastDateContribution
        self.lastDate               = lastDate
        return
    #判断ID是否在allInviter中，返回id在allInviter中出现的次数
    def getInviterById(self, guildID):
        return self.allInviter.count(guildID)
    #获取待验证列表中的行会信息
    def getInviter(self):
        return self.allInviter
    #将队伍信息加入至待验证列表
    def addInviter(self, guildID):
        if 0 == self.getInviterById(guildID):
            self.allInviter.append(guildID)
        return
    #将队伍邀请信息删除
    def delInviter(self, guildID):
        if 0 != self.getInviterById(guildID):
            self.allInviter.remove(guildID)
        return
#创建一个类，用于保存系统中所有的行会信息
WAR_SEC_START = 10
WAR_SEC_END   = 60*5
class GuildWarVSInfo:
    def __init__(self):
        self.warId  = 0
        self.guild1 = None
        self.guild2 = None
        self.guildScore1 = 0
        self.guildScore2 = 0
        self.tmWarStart = 0
    def getAnotherGuild(self, guildId):
        if self.guild1.guildID != guildId:
            return self.guild1
        return self.guild2
    def addGuildScore(self, guildId, score = 1):
        if self.guild1.guildID == guildId:
            self.guildScore1 += score
        else:
            self.guildScore2 += score

#创建一个类，用于行会排名战
RANK_WAR_SEC_START = 10
RANK_WAR_SEC_END   = 60*10
class GuildRankWarVSInfo:
    def __init__(self):
        self.warId  = 0
        self.guildId1 = 0
        self.guildId2 = 0
        self.guildTeam1 = {}
        self.guildTeam2 = {}
        self.guildScore1 = 0
        self.guildScore2 = 0
        self.guildWin = 0
        self.tmRankWarStart = 0
    def getAnotherGuild(self, guildId):
        if self.guildId1 != guildId:
            return self.guildId1
        return self.guildId2

    def getAnotherTeam(self, guildId):
        if self.guildId1 != guildId:
            return self.guildTeam1
        return self.guildTeam2

    def addGuildScore(self, guildId, score = 1):
        if self.guildId1 == guildId:
            self.guildScore1 += score
        else:
            self.guildScore2 += score

    def setGuildWin(self, guildId):
        self.guildWin = guildId


def buildGuildInfoMsg(guildInfo):
    val = guildInfo
    ret_msg = MsgDef.GuildInfoMsg()
    ret_msg.guildID = val.guildID  # 行会ID
    ret_msg.guildName = val.guildName  # 行会名称
    ret_msg.guildPlayerNumber = val.getLenGuildMember()  # 行会成员数量
    ret_msg.guildLeaderName = val.guildLeaderName  # 行会长名称
    ret_msg.guildNotice = val.guildNotice  # 行会公告
    ret_msg.levelRanking = val.levelRanking  # 行会等级排名
    ret_msg.guildImage = val.guildImage  # 行会图片
    ret_msg.guildlevel = val.guildLevel  # 行会等级
    ret_msg.copymapEndTm = val.copymapEndTm  # 副本结束时间
    ret_msg.typeCopyMap = val.typeCopyMap  # 副本类型
    return ret_msg


def onCityWarStart():
    # 开始一场攻城战
    citywar_info = GlobalRecordModel.getGlobalRecordMgr().citywar_info
    if citywar_info.copyMap:
        # 已经启动了，先结束了
        if citywar_info.copyMap.copyMapHandler:
            citywar_info.copyMap.copyMapHandler.onEnd(citywar_info.copyMap)
    citywar_info.copyMap = None

    guildId = citywar_info.getFirstGuildPop()
    if guildId <= 0:
        ffext.dump('攻城战队列没有行会，直接退出!')
        return False

    attackGuild = getGuildMgr().getGuildById(guildId)
    if not attackGuild:
        ffext.dump('攻城战行会不存在，直接退出!')
        return False
    if citywar_info.master_guild == 0:
        citywar_info.master_guild = citywar_info.getFirstGuildPop()
    defGuild = getGuildMgr().getGuildById(citywar_info.master_guild)

    mapObj = CityWarCopy.create(attackGuild, defGuild, getGuildMgr())
    if mapObj:
        citywar_info.copyMap = mapObj
        if citywar_info.copyMap.copyMapHandler:
            #执行启动时间（fzz：貌似这个已经集成在框架里）
            citywar_info.copyMap.copyMapHandler.onStart(mapObj)
    else:
        ffext.dump("启动攻城战失败!")
    return True

class GuildMgr:
    def __init__(self):
        self.allGuild               = {}        #行会成员列表
        self.guildLevelCfg          = {}
        #行会名，对应的行会副本
        self.guildName2CoypMap      = {}
        #行会战相关的数据，谁-》谁
        self.allGuildWarVSInfo      = {}

        #行会排名战相关的数据
        self.allGuildRankWarVSInfo  = {}
    #以下是行会排名战
    def getRankWarVSinfo(self, guildId):
        for a, k in self.allGuildRankWarVSInfo.iteritems():
            if k.guildId1 == guildId or k.guildId2:
                return k
        return None

    def delRankWarVsInfo(self, guildId):
        for i, k in self.allGuildRankWarVSInfo.iteritems():
            if k.guildId1 == guildId or k.guildId2 == guildId:
                self.allGuildRankWarVSInfo.pop(i)
                break
        return self.allGuildRankWarVSInfo


    def addRankWarVsInfo(self, guildId1, guildId2, mapxy):
        rankWarInfo = GuildRankWarVSInfo()
        rankWarId = idtool.allocTmpId()
        rankWarInfo.warId  = rankWarId
        rankWarInfo.guildId1 = guildId1
        rankWarInfo.guildId2 = guildId2
        rankWarInfo.guildTeam1 = {}
        rankWarInfo.guildTeam2 = {}
        rankWarInfo.tmRankWarStart = ffext.getTime() + RANK_WAR_SEC_START
        retMsg = MsgDef.GuildRankWarOpsRet()
        cmd = MsgDef.ClientCmd.GUILD_RANKWAR_OPS
        def cb(ret):
            for row in ret.result:
                memberUid = int(row[0])
                guildId = int(row[1])
                memberSession = ffext.getSessionMgr().findByUid(memberUid)
                if memberSession:
                    member = memberSession.player
                    #询问是否进入地图
                    retMsg.guildId = guildId
                    retMsg.mapname = mapxy[0]
                    retMsg.x = mapxy[1]
                    retMsg.y = mapxy[2]
                    memberSession.sendMsg(cmd, retMsg)
                import time
                time.sleep(10)
                if guildId == rankWarInfo.guildId1 and member.mapname == mapxy[0]:
                    member.modeAttack = MsgDef.EATTACK_MODE.PEACE
                    rankWarInfo.guildTeam1[memberUid] = member
                elif guildId == rankWarInfo.guildId2 and member.mapname == mapxy[0]:
                    member.modeAttack = MsgDef.EATTACK_MODE.PEACE
                    rankWarInfo.guildTeam2[memberUid] = member
            self.allGuildRankWarVSInfo[rankWarInfo.warId] = rankWarInfo
        DbService.getGuildService().queryRankWarTeamMember(1, rankWarInfo.guildId1, rankWarInfo.guildId2, cb)

        #self.allGuildWarVSInfo[rankWarInfo.warId] = rankWarInfo

        def cbStart():
            retMsg = MsgDef.GuildWarOpsRet(MsgDef.GuildRankWarOpsCmd.RANKWAR_START, rankWarInfo.tmRankWarStart)
            for k, v in rankWarInfo.guildTeam1.iteritems():
                v.modeAttack = MsgDef.EATTACK_MODE.GUILD
            for k, v in rankWarInfo.guildTeam2.iteritems():
                v.modeAttack = MsgDef.EATTACK_MODE.GUILD
            pass

        def cbEnd():
            rankWarInfo = self.allGuildRankWarVSInfo.pop(rankWarId, None)
            if not rankWarInfo:
                return
            rankWarInfo.tmRankWarStart = 0
            retMsg = MsgDef.GuildRankWarOpsRet(MsgDef.GuildRankWarOpsCmd.RANKWAR_END, rankWarInfo.tmRankWarStart)
            retMsg.winGuildId = 0
            if rankWarInfo.guildWin:
                retMsg.winGuildId = rankWarInfo.guildWin

            elif rankWarInfo.guildScore1 > rankWarInfo.guildScore2:
                rankWarInfo.guildWin = rankWarInfo.guild1.guildID
                retMsg.winGuildId = rankWarInfo.guild1.guildID
            elif rankWarInfo.guildScore1 < rankWarInfo.guildScore2:
                rankWarInfo.guildWin = rankWarInfo.guild2.guildID
                retMsg.winGuildId = rankWarInfo.guild2.guildID
            elif rankWarInfo.guildScore1 == rankWarInfo.guildScore2:
                allHp1 = 0
                allHp2 = 0
                for k, v in rankWarInfo.guildTeam1.iteritems():
                    memberSession = ffext.getSessionMgr().findByUid(k)
                    if memberSession:
                        member = memberSession.player
                        allHp1 += member.hp
                for k, v in rankWarInfo.guildTeam2.iteritems():
                    memberSession = ffext.getSessionMgr().findByUid(k)
                    if memberSession:
                        member = memberSession.player
                        allHp2 += member.hp
                if allHp1 > allHp2:
                    rankWarInfo.guildWin = rankWarInfo.guild1.guildID
                    retMsg.winGuildId = rankWarInfo.guild1.guildID
                elif allHp1 < allHp2:
                    rankWarInfo.guildWin = rankWarInfo.guild2.guildID
                    retMsg.winGuildId = rankWarInfo.guild2.guildID

            if not retMsg.winGuildId:
                DbService.getGuildService().updateRankWarWin(0, rankWarInfo.guildId1, rankWarInfo.guildId2)
                for k, v in rankWarInfo.guildTeam1.iteritems():
                    memberSession = ffext.getSessionMgr().findByUid(k)
                    memberSession.sendMsg(cmd, retMsg)
                for k, v in rankWarInfo.guildTeam2.iteritems():
                    memberSession = ffext.getSessionMgr().findByUid(k)
                    memberSession.sendMsg(cmd, retMsg)
            else:
                DbService.getGuildService().updateRankWarWin(0, rankWarInfo.getAnotherGuild(retMsg.winGuildId))

            if retMsg.winGuildId == rankWarInfo.guild1.guildID:
                for k, v in rankWarInfo.guildTeam1.iteritems():
                    memberSession = ffext.getSessionMgr().findByUid(k)
                    memberSession.sendMsg(cmd, retMsg)
            elif retMsg.winGuildId == rankWarInfo.guild2.guildID:
                for k, v in rankWarInfo.guildTeam1.iteritems():
                    memberSession = ffext.getSessionMgr().findByUid(k)
                    memberSession.sendMsg(cmd, retMsg)


        ffext.timer(WAR_SEC_START * 1000, cbStart)
        ffext.timer((WAR_SEC_START + WAR_SEC_END) * 1000, cbEnd)
        return rankWarInfo


    #以下是行会战
    def getWarVSinfo(self, guildId):
        for a, k in self.allGuildWarVSInfo.iteritems():
            if k.guild1.guildID == guildId or k.guild2.guildID:
                return k
        return None
    def delWarVsInfo(self, guildId):
        for i, k in self.allGuildWarVSInfo.iteritems():
            if k.guild1.guildID == guildId:
                self.allGuildWarVSInfo.pop(i)
                break
        return self.allGuildWarVSInfo

    def addWarVsInfo(self, guild1, guild2):
        warInfo = GuildWarVSInfo()
        warId = idtool.allocTmpId()
        warInfo.warId  = warId
        warInfo.guild1 = guild1
        warInfo.guild2 = guild2
        warInfo.tmWarStart = ffext.getTime() + WAR_SEC_START
        self.allGuildWarVSInfo[warInfo.warId] = warInfo

        def cbStart():
            retMsg = MsgDef.GuildWarOpsRet(MsgDef.GuildWarOpsCmd.WAR_START, warInfo.tmWarStart)
            retMsg.warApplyGuild = buildGuildInfoMsg(guild1)
            retMsg.warFightGuild = buildGuildInfoMsg(guild2)
            guild1.sendMsg2OnlineMember(MsgDef.ServerCmd.GUILD_WAR_OPS, retMsg)
            guild2.sendMsg2OnlineMember(MsgDef.ServerCmd.GUILD_WAR_OPS, retMsg)
            # 更新颜色
            def updatePlayerColor1(player):
                player.nameColor = MsgDef.ECOLOR.BLUE
                player.SendChangeApprMsg()
                return
            def updatePlayerColor2(player):
                player.nameColor = MsgDef.ECOLOR.YELLOW
                player.SendChangeApprMsg()
                return
            guild1.foreachOnlineMember(updatePlayerColor1)
            guild2.foreachOnlineMember(updatePlayerColor2)
            return

        def cbEnd():
            warInfo = self.allGuildWarVSInfo.pop(warId, None)
            if not warInfo:
                return
            warInfo.tmWarStart = 0
            retMsg = MsgDef.GuildWarOpsRet(MsgDef.GuildWarOpsCmd.WAR_END, warInfo.tmWarStart)
            retMsg.winGuildId = 0
            if warInfo.guildScore1 >= warInfo.guildScore2:
                retMsg.winGuildId = warInfo.guild1.guildID
            else:
                retMsg.winGuildId = warInfo.guild2.guildID
            retMsg.warApplyGuild = buildGuildInfoMsg(guild1)
            retMsg.warFightGuild = buildGuildInfoMsg(guild2)
            guild1.sendMsg2OnlineMember(MsgDef.ServerCmd.GUILD_WAR_OPS, retMsg)
            guild2.sendMsg2OnlineMember(MsgDef.ServerCmd.GUILD_WAR_OPS, retMsg)
            # 更新颜色
            def updatePlayerColor(player):
                player.nameColor = 0
                player.SendChangeApprMsg()
                return
            guild1.foreachOnlineMember(updatePlayerColor)
            guild2.foreachOnlineMember(updatePlayerColor)
            return
        ffext.timer(WAR_SEC_START * 1000, cbStart)
        ffext.timer((WAR_SEC_START + WAR_SEC_END) * 1000, cbEnd)
        return warInfo

    #声明一个函数，用于格式化打印
    def __repr__(self):
        L = ['%s=%r' % (key, value)
            for key, value in self.__dict__.iteritems()]
        return '%s(%s)' % (self.__class__.__name__, ', '.join(L))
    #读取行会列表#初始化行会列表。用于在服务器重启后，将行会信息写入服务器session
    def init(self):
        db = ffext.allocDbConnection('cfg',ffext.getConfig('-cfg'))
        ret = db.queryResult('select guildLevel,guildExp,guildNum, guildDayExp, playerDayExp from guild')
        self.guildLevelCfg = {}
        for row in ret.result:
            levelCfg = guildLevelCfg()
            levelCfg.setGuildLevelCfg(long(row[0]),long(row[1]), long(row[2]), long(row[3]), long(row[4]))
            self.guildLevelCfg[levelCfg.guildLevel] = levelCfg
        def guildInfo(ret):
            if ret.flag == False or len(ret.result) == 0:
                self.allGuild       = {}
                return
            for i in range(0, len(ret.result)):
                guildID = long(ret.result[i][0])
                if None == self.getGuildById(guildID):
                    guildInfo                               = GuildInfo()
                    guildLevel                              = long(ret.result[i][8])
                    guildExp                                = long(ret.result[i][9])            #行会剩余资源
                    levelRanking = 1
                    #遍历现有字典，获取该行会现有排名，并插入
                    for uid, val in self.allGuild.iteritems():
                        if val.guildLevel < guildLevel or (val.guildLevel == guildLevel and val.guildExp < guildExp):
                            val.levelRanking = val.levelRanking + 1
                        else:
                            levelRanking = levelRanking + 1
                    guildInfo.allGuildMemberTemp            = {}                                #申请加入行会成员列表
                    guildInfo.guildID                       = long(ret.result[i][0])            #行会ID
                    guildInfo.guildName                     = str(ret.result[i][5])             #行会名称
                    guildInfo.guildImage                    = str(ret.result[i][6])             #行会名称
                    guildInfo.guildNotice                   = str(ret.result[i][7])             #行会名称
                    guildInfo.guildLevel                    = guildLevel                        #行会等级
                    guildInfo.levelRanking                  = levelRanking                      #行会经验
                    guildInfo.guildExp                      = guildExp
                    guildInfo.guildLeaderName                = str(ret.result[i][10])             #行会名称
                    guildInfo.lastDateContribution          = long(ret.result[i][11])            #行会经验
                    guildInfo.lastDate                      = str(ret.result[i][12])             #行会名称
                    self.allGuild[guildInfo.guildID]        = guildInfo
                else:
                    guildInfo = self.getGuildById(guildID)
                playerGuildInfo = PlayerGuildInfo()
                ranking = 1
                contribute = ret.result[i][4]
                #遍历现有字典，获取该行会现有排名，并插入
                for uid, val in guildInfo.allGuildMember.iteritems():
                    if val.contribute > contribute:
                        ranking = ranking + 1
                    else:
                        val.ranking = val.ranking + 1
                #ffext.dump('ret is!!!!!!!!!!!!!!!!!!!!!!!!! ', ret)
                playerGuildInfo.setPlayerGuildInfo(long(ret.result[i][1]),  str(ret.result[i][2]), long(ret.result[i][3]), contribute, ranking)
                guildInfo.allGuildMember[playerGuildInfo.uid] = playerGuildInfo
            return
        #DbService.getGuildService().syncGetGuildMemberInfoList(guildInfo)
        def loadAllGuild(ret):
            if ret.flag == False or len(ret.result) == 0:
                self.allGuild = {}
                return
            for i in range(0, len(ret.result)):
                guildInfo = GuildInfo()
                levelRanking = i + 1
                #sql = "select guildid, guildname, guildimage, guildnotice, guildlevel, guildExp, guildchiefname, lastdatecontribution, lastdate from guildinfo order by guildlevel desc, guildExp desc"
                guildInfo.guildID = long(ret.result[i][0])  # 行会ID
                guildInfo.guildName = str(ret.result[i][1])  # 行会名称
                guildInfo.guildImage = str(ret.result[i][2])  # 行会名称
                guildInfo.guildNotice = str(ret.result[i][3])  # 行会名称
                guildInfo.guildLevel = long(ret.result[i][4])  # 行会等级
                guildInfo.levelRanking = levelRanking
                guildInfo.guildExp = long(ret.result[i][5])  # 行会经验
                guildInfo.guildLeaderName = str(ret.result[i][6])  # 行会名称
                guildInfo.lastDateContribution = long(ret.result[i][7])  # 行会经验
                guildInfo.lastDate = ffext.str2timestamp(ret.result[i][8])  # 行会名称
                #ffext.dump('loadAllGuild', guildInfo)
                self.allGuild[guildInfo.guildID] = guildInfo
            return
        def loadAllGuildMember(ret):
            for i in range(0, len(ret.result)):
                playerGuildInfo = PlayerGuildInfo()
                row = ret.result[i]

                guildID = long(row[0])
                guildInfo = self.getGuildById(guildID)
                if not guildInfo:
                    return
                #sql = "select guildid, guildmemberinfo.uid as uid1, name2,memberpost3, contribute4 daycontribute5, lastdate6, level7 from guildmemberinfo, player where player.uid = guildmemberinfo.uid and player.delflag = 0"
                playerGuildInfo.setPlayerGuildInfo(long(row[1]), str(row[2]), long(row[3]), long(row[4]), 1, int(row[7]), int(row[8]))
                playerGuildInfo.daycontribute = long(row[5])
                playerGuildInfo.lastdate = ffext.str2timestamp(row[6])
                guildInfo.allGuildMember[playerGuildInfo.uid] = playerGuildInfo
                #ffext.dump('loadAllGuildMember!!!!!!!!!!!!!!!!!!!!!!!!', row, playerGuildInfo)
            return
        DbService.getGuildService().syncGetAllGuildInfo(loadAllGuild)
        DbService.getGuildService().syncGetAllGuildMember(loadAllGuildMember)
        for k , v in self.allGuild.iteritems():
            v.calMemberRank()
        return True
    #启动行会相关定时器
    def initTimer(self):
        nowSec = ffext.getTime()
        secondUtilMiddleNight = SECONDS_PER_DAY - (nowSec % SECONDS_PER_DAY)
        nowTm = ffext.datetime_now()
        weekDay = nowTm.weekday()
        if weekDay == 0:
            weekDay = 7
        nowCompVal = weekDay * 10000 + nowTm.hour * 100 + nowTm.minute
        for wd, tmInfo in CITYWAR_START_TM_LIST.iteritems():
            tmCompVal_1 = wd * 10000 + tmInfo[0]
            tmCompVal_2 = wd * 10000 + tmInfo[1]
            if nowCompVal >= tmCompVal_1:
                # 目前配置时间点已经过了，算到本周日结束的时间
                secondUtilWeekEnd = secondUtilMiddleNight + (7 - weekDay) * SECONDS_PER_DAY
                tm2 = secondUtilWeekEnd + (wd - 1) * SECONDS_PER_DAY + (tmInfo[0] / 100) * 3600 + (tmInfo[0] % 100) * 60
                ffext.timer(tm2 * 1000, onCityWarStart)
            else:
                # 目前配置时间还没来，还可以再打一场
                tm1 = nowSec % SECONDS_PER_DAY
                tm2 = (tmInfo[0] / 100) * 3600 + (tmInfo[0] % 100) * 60
                ffext.timer((tm2 - tm1) * 1000, onCityWarStart)
                pass
        return True

    #将新创建的行会写入行会字典
    def addGuild(self, uid, name, guildID, guildName, level, job):
        guildInfo = GuildInfo()
        guildInfo.creatGuild(uid, name, guildID, guildName, self.getLenGuild() + 1, level, job)
        self.allGuild[guildInfo.guildID] = guildInfo
        return guildInfo
    #解散行会
    def delGuild(self, guildID):
        if None == self.getGuildById(guildID):
            return False
        self.allGuild.pop(guildID)
        return
    #获取服务器中行会的数量
    def getLenGuild(self):
        return len(self.allGuild)
    #获取服务器中所有行会信息
    def getGuild(self):
        return self.allGuild
    #通过ID获取行会
    def getGuildById(self, guildID):
        return self.allGuild.get(guildID)
    #通过行会名字获取行会ID
    def getGuildIdByName(self, guildName):
        for i,k in self.allGuild.iteritems():
            if k.guildName == guildName:
                return i
    #通过guildLevel获取行会
    def getGuildLevelCfgByGuildLevel(self, guildLevel):
        if guildLevel == 0:
            guildLevel = 1
        return self.guildLevelCfg.get(guildLevel)
    #创建副本
    def openCopyMap(self, player):
        guildInfo = player.guildCtrl.guildInfo
        mapObj = self.guildName2CoypMap.get(guildInfo.guildID)
        if mapObj:
            return mapObj
        mapObj = GuildCopy.create(guildInfo)#MapMgr.getMapMgr().allocMap('10002')#
        if mapObj:
            self.guildName2CoypMap[guildInfo.guildID] = mapObj
            guildInfo.copymapEndTm = ffext.getTime() + 30
        return mapObj
    def closeCopyMap(self, guildInfo):
        mapObj = self.guildName2CoypMap.pop(guildInfo.guildID, None)
        guildInfo.copymapEndTm = 0
        guildInfo.typeCopyMap  = 0
        return mapObj
    def getGuildCopyMap(self, guildInfo):
        mapObj = self.guildName2CoypMap.get(guildInfo.guildID)
        if mapObj:
            return mapObj
        return None

    def buildCityWarRetMsg(self, opstype, res=0, startTm=0, notifyMaster=True, notifyList=True):
        return buildGuildCityWarOpsMsgRet(opstype, res, startTm, notifyMaster, notifyList)

#创建一个类，用于存放行会等级信息
class guildLevelCfg:
    def __init__(self):
        self.guildLevel     = 0
        self.guildExp       = 0
        self.guildNum       = 0
        self.guildDayExp    = 0
        self.playerDayExp   = 0
    def setGuildLevelCfg(self, guildLevel, guildExp, guildNum, guildDayExp, playerDayExp):
        self.guildLevel     = guildLevel
        self.guildExp       = guildExp
        self.guildNum       = guildNum
        self.guildDayExp    = guildDayExp
        self.playerDayExp   = playerDayExp
        return
    #声明一个函数，用于格式化打印
    def __repr__(self):
        L = ['%s=%r' % (key, value)
            for key, value in self.__dict__.iteritems()]
        return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

#初始化行会类。声明一个函数，用于存储全局对象GuildCtrl并进行数据初始化
gGuildMgr = GuildMgr()
def getGuildMgr():
    return gGuildMgr


#创建一个类，用于保存单个行会的信息
class GuildInfo:
    def __init__(self):
        self.allGuildMember         = {}            #行会成员列表
        self.allGuildMemberTemp     = {}            #申请加入行会成员列表
        self.guildID                = 0             #行会ID
        self.guildName              = ''            #行会名称
        self.guildImage             = ''            #行会图片
        self.guildNotice            = ''            #行会公告
        self.guildLevel             = 1             #行会等级
        self.guildExp               = 0             #行会剩余资源
        self.levelRanking           = 0             #行会等级排名
        self.guildLeaderName        = ''            #行会老大
        self.lastDateContribution   = 0             #行会最后一日贡献度
        self.lastDate               = ''            #最后一次日期
        self.copymapEndTm           = 0             #行会副本结束时间
        self.typeCopyMap            = 0             #行会副本类型
    #声明一个函数，用于格式化打印
    def __repr__(self):
        L = ['%s=%r' % (key, value)
            for key, value in self.__dict__.iteritems()]
        return '%s(%s)' % (self.__class__.__name__, ', '.join(L))
    #创建行会
    def creatGuild(self, uid, name, guildID, guildName, levelRanking, level, job):
        guildMember = PlayerGuildInfo()
        guildMember.setPlayerGuildInfo(uid, name, MsgDef.GuildPostCmd.GUILD_LEADER, 0, 1,level, job)
        self.allGuildMember[guildMember.uid] = guildMember
        self.allGuildMemberTemp     = {}
        self.guildID                = guildID
        self.guildName              = guildName         #行会名称
        self.guildImage             = ''                #行会图片
        self.guildNotice            = ''                #行会公告
        self.guildLevel             = 1                 #行会经验
        self.guildExp                = 0                 #行会经验
        self.levelRanking           = levelRanking      #行会等级排名
        self.guildLeaderName         = name              #行会老大
        self.lastDateContribution   = 0                 #行会最后一日贡献度
        self.lastDate               = ''                #最后一次日期
        return
    #获取行会成员数量
    def getLenGuildMember(self):
        return len(self.allGuildMember)
    #获取行会成员信息
    def getGuildMember(self):
        return self.allGuildMember
    def sendMsg2OnlineMember(self, cmd, msg):
        for key, val in self.getGuildMember().iteritems():
            tmpSession = ffext.getSessionMgr().findByUid(val.uid)
            if None != tmpSession:
                tmpSession.sendMsg(cmd, msg)

    def foreachOnlineMember(self, callback):
        for key, val in self.getGuildMember().iteritems():
            tmpSession = ffext.getSessionMgr().findByUid(val.uid)
            if None != tmpSession and None != tmpSession.player:
                callback(tmpSession.player)
    #通过字典key获取行会成员信息
    def getGuildMemberByUid(self, uid):
        return self.allGuildMember.get(uid)
    #将新成员信息加入至行会列表
    def addGuildMember(self, uid, name, level, job):
        guildMember = PlayerGuildInfo()
        guildMember.setPlayerGuildInfo(uid, name, MsgDef.GuildPostCmd.MEMBER, 0, self.getLenGuildMember() + 1, level, job)
        self.allGuildMember[guildMember.uid] = guildMember
        return
    #将成员信息从行会中删除
    def delGuildMember(self, uid):
        if None == self.getGuildMemberByUid(uid):
            return False
        ranking = self.getGuildMemberByUid(uid).ranking
        for uid, val in self.getGuildMember().iteritems():
            if ranking < val.ranking:
                val.ranking = val.ranking -1
        self.allGuildMember.pop(uid)
        return True
    #获取申请加入行会人员信息
    def getGuildMemberTemp(self):
        return self.allGuildMemberTemp
    #通过Uid获取申请加入行会人员信息
    def getGuildMemberTempByUid(self, uid):
        return self.allGuildMemberTemp.get(uid)
    #将成员信息加入至申请加入行会待验证成员列表
    def addGuildMemberTemp(self, uid, name, level, job):
        guildMember = PlayerGuildInfo()
        guildMember.setPlayerGuildInfo(uid, name, MsgDef.GuildPostCmd.MEMBER, 0, 0, level, job)
        self.allGuildMemberTemp[guildMember.uid] = guildMember
        ffext.dump(self.allGuildMemberTemp)
        return
    #将成员信息从待验证行会成员中删除
    def delGuildMemberTemp(self, uid):
        if None == self.getGuildMemberTempByUid(uid):
            return False
        self.allGuildMemberTemp.pop(uid)
        return True
    #修改行会图片
    def updateGuildImage(self, guildImage):
        if '' == guildImage:
            guildImage = self.guildImage
        else:
            self.guildImage = guildImage
        return guildImage
    #修改行会名称
    def updateGuildName(self, name):
        if '' == name:
            name = self.name
        else:
            self.name = name
        return name
    #修改行会公告
    def updateGuildNotice(self, guildNotice):
        if '' == guildNotice:
            guildNotice = self.guildNotice
        else:
            #self.name = guildNotice
            self.guildNotice = guildNotice
        return guildNotice
    #计算行会成员贡献值排名
    def calMemberRank(self):
        playerList = [v for k, v in self.allGuildMember.iteritems()]
        def cmpFunc(e1, e2):
            if e1.contribute > e2.contribute:
                return  1
            elif e1.contribute == e2.contribute:
                if e1.lastdate < e2.lastdate:
                    return 1
                elif e1.lastdate > e2.lastdate:
                    return -1
                return 0
            else:
                return -1
        sorted(playerList, cmp=cmpFunc, reverse=True)
        for k in range(0, len(playerList)):
            playerList[k].ranking = k + 1
        return True
    def closeCopyMap(self):
        return getGuildMgr().closeCopyMap(self)
#创建一个类，用于保存行会中用户的信息
class PlayerGuildInfo:
    def __init__(self):
        self.uid        = 0             #玩家ID
        self.name       = ''            #玩家姓名
        self.post       = 0             #玩家行会职务
        self.contribute = 0             #玩家贡献值
        self.ranking    = 0             #贡献值排名
        self.level      = 0
        self.daycontribute = 0          #日贡献值
        self.lastdate      = 0          #上次贡献时间
        self.job           = 0
    #声明一个函数，用于格式化打印
    def __repr__(self):
        L = ['%s=%r' % (key, value)
            for key, value in self.__dict__.iteritems()]
        return '%s(%s)' % (self.__class__.__name__, ', '.join(L))
    def setPlayerGuildInfo(self, uid, name, post, contribute, ranking, level , job):
        self.uid        = uid
        self.name       = name
        self.post       = post
        self.contribute = contribute
        self.ranking    = ranking
        self.level      = level
        self.job        = job
        return

def buildGuildCityWarOpsMsgRet(opstype, res = 0, startTm = 0, notifyMaster = True, notifyList = True):
    ret_msg = MsgDef.GuildCityWarOpsMsgRet()
    ret_msg.opstype = opstype
    ret_msg.attack_result = res
    ret_msg.tmStart = startTm
    if ret_msg.curApplyList == None:
        ret_msg.curApplyList = []
    city_war_info = GlobalRecordModel.getGlobalRecordMgr().citywar_info
    if notifyMaster == True:
        if city_war_info.master_guild > 0:
            # build master guild info
            masterGuild = getGuildMgr().getGuildById(city_war_info.master_guild)
            if masterGuild:
                ret_msg.curMaster = buildGuildInfoMsg(masterGuild)
            pass
    if notifyList == True:
        if city_war_info.queue_guild:
            # build all queued guilds info
            for qGuildId in city_war_info.queue_guild:
                qGuildInfo = getGuildMgr().getGuildById(qGuildId)
                if qGuildInfo:
                    ret_msg.curApplyList.append(buildGuildInfoMsg(qGuildInfo))
                    pass
                pass

    return ret_msg
