# -*- coding: utf-8 -*-
#本页面存放一个DbServiceGuild类，用于存放本游戏中行会操作的增删查的SQL操作。使用该类时，请调用DbService文件中的getGuildService()函数
#引用数据库初始化页面，用于调用getDB()函数
import ffext
from db import DbServiceBase as DbServiceBase


class DbServiceGuild:
    # #获取数据库中各个行会信息。
    # def getGuildInfoList(self, callback):
    #     sql = "select guildid, guildname, guildimage, guildnotice, guildlevel, guildexp, guildchiefname, lastdatecontribution, lastdate from guildinfo"
    #     DbServiceBase.getDB().query(sql, callback)
    #     return
    # #获取数据库中某个行会中的成员信息。
    # def getGuildMemberInfoList(self, guildid, callback):
    #     sql = "select guildid, guildmemberinfo.uid as uid, name, memberpost, contribute, daycontribute, lastdate from guildmemberinfo, player where player.uid = guildmemberinfo.uid and guildid = %d" % (guildid)
    #     DbServiceBase.getDB().query(sql, callback)
    #     return
    #获取数据库中某个行会中的成员信息。
    def getGuildMemberInfoList(self, callback):
        sql = "select guildinfo.guildid as guildid, guildmemberinfo.uid as uid, name, memberpost, contribute, guildname, guildimage, guildnotice, guildlevel, guildexp, guildchiefname, lastdatecontribution, guildinfo.lastdate as guildinfolastdate from guildmemberinfo, player, guildinfo where player.uid = guildmemberinfo.uid and guildinfo.guildid = guildmemberinfo.guildid"
        DbServiceBase.getDB().query(sql, callback)
        return

    def syncGetAllGuildInfo(self, callback):
        sql = "select guildid, guildname, guildimage, guildnotice, guildlevel, guildExp, guildchiefname, lastdatecontribution, lastdate from guildinfo order by guildlevel desc, guildExp desc"
        ret = DbServiceBase.getDB().queryResult(sql)
        callback(ret)
        return
    def syncGetAllGuildMember(self, callback):
        sql = "select guildid, guildmemberinfo.uid as uid, name,memberpost, contribute, daycontribute, lastdate,level, job  from guildmemberinfo, player where player.uid = guildmemberinfo.uid and player.delflag = 0"
        ret = DbServiceBase.getDB().queryResult(sql)
        #ffext.dump('syncGetAllGuildMember', sql)
        callback(ret)
        return
    def syncGetGuildMemberInfoList(self, callback):
        sql = "select guildinfo.guildid as guildid, guildmemberinfo.uid as uid, name, memberpost, contribute, guildname, guildimage, guildnotice, guildlevel, guildexp, guildchiefname, \
            lastdatecontribution, guildinfo.lastdate as guildinfolastdate from guildmemberinfo, player, guildinfo where player.uid = guildmemberinfo.uid and guildinfo.guildid = guildmemberinfo.guildid"
        ret = DbServiceBase.getDB().queryResult(sql)
        callback(ret)
        return

    def syncGetGuildMemberInfoList(self, callback):
        sql = "select guildinfo.guildid as guildid, guildmemberinfo.uid as uid, name, memberpost, contribute, guildname, guildimage, guildnotice, guildlevel, guildexp, guildchiefname, \
            lastdatecontribution, guildinfo.lastdate as guildinfolastdate from guildmemberinfo, player, guildinfo where player.uid = guildmemberinfo.uid and guildinfo.guildid = guildmemberinfo.guildid"
        ret = DbServiceBase.getDB().queryResult(sql)
        callback(ret)
        return
    #获取数据库中某个行会贡献值的详细信息。
    def getGuildContributeInfoList(self, guildid, callback):
        sql = "select guildid, guildcontributeinfo.uid as uid, name, thiscontribute, contributedate from guildcontributeinfo, player where player.uid = guildcontributeinfo.uid and guildid = %d" % (guildid)
        DbServiceBase.getDB().query(sql, callback)
        return
    #创建行会
    def addGuild(self, guildid, guildname, guildchiefname):
        now = ffext.datetime_to_str(ffext.datetime_from_time(ffext.getTime()))
        sql  = "insert into guildinfo (guildid, guildname, guildimage, guildnotice, guildlevel, guildexp, guildchiefname, lastdatecontribution, lastdate) \
                values ('%d', '%s', '', '', 1, 0, '%s', 0, '%s') " % (guildid, guildname, guildchiefname, now)
        DbServiceBase.getDB().query(sql)
        return True
    #解散行会
    def delGuild(self, guildid):
        sql  = "delete from guildmemberinfo where guildid = %d"    % (guildid)
        sql2 = "delete from guildinfo where guildid = %d limit 1"  % (guildid)
        DbServiceBase.getDB().query(sql)
        DbServiceBase.getDB().query(sql2)
        return True
    #贡献行会
    def contributionGuild(self, uid, guildID, tm, userContribution, userDateContribution, guildExp, lastDateContribution):
        now = ffext.datetime_to_str(ffext.datetime_from_time(tm))
        sql1 = "update guildinfo set guildexp = %d, lastdatecontribution = %d, lastdate = '%s' where guildid = %d limit 1" % (guildExp, lastDateContribution, now, guildID)
        sql2 = "update guildmemberinfo set contribute = %d, daycontribute = %d, lastdate = '%s' where uid = %d limit 1" % (userContribution, userDateContribution, now, uid)
        print(sql1)
        print(sql2)

        DbServiceBase.getDB().query(sql1)
        DbServiceBase.getDB().query(sql2)
        return True
    #升级行会
    def updateGuild(self, guildid, guildExp, guildlevel):
        sql1 = "update guildinfo set guildexp = %d, guildlevel = %d   where guildid = %d limit 1" % (guildExp, guildlevel, guildid)
        DbServiceBase.getDB().query(sql1)
        return True
    #更该行会名称
    def updateGuildName(self, guildid, guildName):
        sql  = "update guildinfo set guildname = %s where guildid = %d limit 1" % (guildName, guildid)
        DbServiceBase.getDB().query(sql)
        return True
    #更该行会图片
    def updateGuildImage(self, guildid, guildImage):
        sql  = "update guildinfo set guildimage = '%s' where guildid = %d limit 1" % (guildImage, guildid)
        DbServiceBase.getDB().query(sql)
        return True
    #更该行会公告
    def updateGuildNotice(self, guildid, guildNotice):
        sql  = "update guildinfo set guildnotice = '%s' where guildid = %d limit 1" % (guildNotice, guildid)
        ffext.dump("sql", sql)
        DbServiceBase.getDB().query(sql)
        return True
    #加入行会
    def addGuildMember(self, guildid, uid, memberpost):
        now = ffext.datetime_to_str(ffext.datetime_from_time(ffext.getTime()))
        sql  = "insert into guildmemberinfo (guildid, uid, memberpost, contribute, daycontribute, lastdate) values (%d, %d, %d, 0, 0, '%s') " % (guildid, uid, memberpost, now)
        DbServiceBase.getDB().query(sql)
        return True
    #退出行会
    def delGuildMember(self, uid):
        sql  = "delete from guildmemberinfo where uid = %d limit 1"  % (uid)
        DbServiceBase.getDB().query(sql)
        return True
    #更该行会内人员职务
    def updateGuildMemberPost(self, uid, memberPost):
        sql  = "update guildmemberinfo set memberpost = %d where uid = %d limit 1" % (memberPost, uid)
        DbServiceBase.getDB().query(sql)
        return True
    #结义
    def loadAllBrother(self):
        sql = 'select bid, uid1, uid2, uid3,extra from brother'
        return  DbServiceBase.getDB().queryResult(sql)
    def loadPlayerDetail(self, idList, cb):
        sql = 'select uid,name,job,gender,,level from player where uid in ('
        for k in range(len(idList)):
            if k == 0:
                sql += str(k)
            else:
                sql += ',' + str(k)
        sql += ')'
        DbServiceBase.getDB().query(sql, cb)
        return True
    def getBrotherMemberInfoList(self, callback):
        sql = "select bid, brother.extra, uid, name, job, gender, level from player, brother where brother.uid1 = player.uid or brother.uid2 = player.uid or brother.uid3 = player.uid order by bid"
        DbServiceBase.getDB().query(sql, callback)
        return
    def syncGetBrotherMemberInfoList(self, callback):
        sql = "select bid, brother.extra, uid, name, job, gender, level from player, brother where brother.uid1 = player.uid or brother.uid2 = player.uid or brother.uid3 = player.uid order by bid"
        ret = DbServiceBase.getDB().queryResult(sql)
        callback(ret)
        return
    def addBrother(self, bid, uid1, uid2, uid3):
        sql = "insert into brother (bid, uid1, uid2, uid3, extra) values (%d, %d, %d, %d, '') " % (bid, uid1, uid2, uid3)
        ffext.dump(sql)
        DbServiceBase.getDB().query(sql)
        sql  = 'update player set brotherid =%d where uid in (%d,%d,%d)'%(bid, uid1, uid2, uid3)
        DbServiceBase.getDB().query(sql)
        ffext.dump(sql)
        return True
    def delBrother(self, brotherCtrl):
        sql = "delete from brother where bid=%d"%(brotherCtrl.bid)
        DbServiceBase.getDB().query(sql)
        for key, val in brotherCtrl.getBrotherMember().iteritems():
            sql  = 'update player set brotherid =%d where uid = %d'%(0, val.uid)
            DbServiceBase.getDB().query(sql)
        return True
    def updateBrotherExtra(self, bid, extra):
        sql  = "update brother set extra = '%s' where bid = %d"%(extra, bid)
        DbServiceBase.getDB().query(sql)
        return True

    #以下是行会排名战相关

    def queryGuildRankWarInvitedMember(self, guildId, nowTime, callback=None):
        sql = "select uid from guildmemberinfo where guildid = %d and rankWarInvitedTime >= %d and rankWarAgreed < 2 " %(guildId, nowTime)
        ffext.dump("sql", sql)
        DbServiceBase.getDB().query(sql, callback)
        return True

    def updateGuildRankWarInvitedOverTime(self, memberUid, overTime, callback=None):
        sql = "update guildmemberinfo set rankWarInvitedOverTime = %d where uid = %d " %(overTime, memberUid)
        ffext.dump("sql", sql)
        DbServiceBase.getDB().query(sql, callback)
        return True

    def updateGuildRankWarInvited(self, memberUid, status, callback=None):
        sql = "update guildmemberinfo set rankWarInvited = %d where uid = %d " %(status, memberUid)
        ffext.dump("sql", sql)
        DbServiceBase.getDB().query(sql, callback)
        return True

    def queryRankWarMember(self, memberUid, callback=None):
        sql = "select rankWarInvitedOverTime from guildmemberinfo where uid = %d " %(memberUid)
        ffext.dump("sql", sql)
        DbServiceBase.getDB().query(sql, callback)
        return True

    def queryGuildApply(self, guildStatus, callback=None):
        sql = "select guildid from guildinfo where rankWarApplied = %d " %(guildStatus)
        ffext.dump("sql", sql)
        DbServiceBase.getDB().query(sql, callback)
        return True

    def updateGuildRankWarApply(self, guildStatus, guildId, callback=None):
        sql = "update guildinfo set rankWarApplied = %d where guildid = %d " %(guildStatus, guildId)
        ffext.dump("sql", sql)
        DbServiceBase.getDB().query(sql, callback)
        return True

    def queryRankWarAllFightPower(self, guildId, status, callback=None):
        sql = "select fightpower from player, guildmemberinfo where guildmemberinfo.guildid = %d and guildmemberinfo.rankWarInvited = %d " \
              "and player.uid = guildmemberinfo.uid " %(guildId, status)
        ffext.dump("sql", sql)
        DbServiceBase.getDB().query(sql, callback)
        return True

    def queryRankWarWinTeam(self, status, callback=None):
        sql = "select guildId from player where rankWarApplied = 1 and rankWarWin = %d" %(status)
        ffext.dump("sql", sql)
        DbServiceBase.getDB().query(sql, callback)
        return True

    def queryRankWarTeamMember(self, status, team1, team2, callback=None):
        sql = "select uid, guildid from guildmemberinfo where rankWarInvited = %d and guildid = %d or guildid = %d " %(status, team1, team2)
        ffext.dump("sql", sql)
        DbServiceBase.getDB().query(sql, callback)
        return True

    def updateRankWarWin(self, status, guildId1, guildId2=0, callback=None):
        sql = "update guildinfo set rankWarWin = %d where guildid = %d or guildid = %d" %(status, guildId1, guildId2)
        ffext.dump("sql", sql)
        DbServiceBase.getDB().query(sql, callback)
        return True