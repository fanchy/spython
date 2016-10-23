# -*- coding: utf-8 -*-
#本文件用于存放行会操作
import ffext
import datetime
import idtool
import weakref
from base import  Base
from mapmgr import MapMgr
#调用msgopstype中的topstypes文件，使用系统中的枚举函数
from msgtype import ttypes as MsgDef
#调用GuildModel文件
from model import GuildModel, PlayerModel, GlobalRecordModel
#调用DbService文件，使用全局对象gDbServiceFriend
from db import DbService as DbService
#所有行会信息 对应消息类型为GET_GUILDINFO   ->GuildMsgReq           -> server:GUILDINFO_MSG  ->GuildInfoMsgRet
@ffext.onLogic(MsgDef.ClientCmd.GET_GUILDINFO, MsgDef.GuildMsgReq)
def processGuildListInfo(session, msg):
    ret_msg                     = MsgDef.GuildInfoMsgRet()
    ret_msg.opstype                = msg.opstype
    ret_msg.allGuildInfo        = []
    if msg.opstype == MsgDef.GuildInfoClientCmd.GET_GUILD_ALL:
        for guildID, val in GuildModel.getGuildMgr().getGuild().iteritems():
            ret_msg.allGuildInfo.append(processGuildInfoMsg(val.guildID, val.guildName, val.getLenGuildMember(), val.guildLeaderName, val.guildNotice, val.levelRanking, val.guildImage, val.guildLevel, val.copymapEndTm, val.typeCopyMap))
        session.sendMsg(MsgDef.ServerCmd.GUILDINFO_MSG, ret_msg)
        return
    if msg.opstype == MsgDef.GuildInfoClientCmd.GET_GUILD_BY_NAME:
        name = msg.guildname#.encode('utf-8')
        for guildID, val in GuildModel.getGuildMgr().getGuild().iteritems():
            if val.guildName == name:#可以做相似判断
                ret_msg.allGuildInfo.append(processGuildInfoMsg(val.guildID, val.guildName, val.getLenGuildMember(), val.guildLeaderName, val.guildNotice, val.levelRanking, val.guildImage, val.guildLevel, val.copymapEndTm, val.typeCopyMap))
        session.sendMsg(MsgDef.ServerCmd.GUILDINFO_MSG, ret_msg)
        return

#用于传递玩家的行会信息 对应消息类型为GET_USER_GUILD_INFO ->EmptyReq           -> server:GUILD_INFO_LIST_MSG       ->UserGuildListMsgRet
@ffext.onLogic(MsgDef.ClientCmd.GET_USER_GUILD_INFO, MsgDef.EmptyReq)
def processGuildInfo(session, msg = None):
    guildMemberList = []        #行会成员列表
    guildMemberTempList = []    #行会待验证成员列表
    guildInfo = session.player.guildCtrl.guildInfo
    if None == guildInfo:
        session.sendMsg(MsgDef.ServerCmd.GUILD_INFO_LIST_MSG, processUserGuildListMsgRet(0, '', 0, '', 0, 0, '', '', 0, 0, 0, 0, 0, 0, guildMemberList, guildMemberTempList, 0, 0))
        return
    userLastDay                 = session.player.guildCtrl.lastDate
    userLastDateContribution    = session.player.guildCtrl.lastDateContribution
    guildLastDay                = guildInfo.lastDate
    guildLastDateContribution   = guildInfo.lastDateContribution
    guildLevel                  = guildInfo.guildLevel
    #处理用户级别
    user = guildInfo.getGuildMemberByUid(session.player.uid)
    ffext.dump('processGuildInfo', user)
    guildPost = 0
    ranking = 0
    try:
        if user:
            guildPost = user.post
            guildPost = int(guildPost)
            ranking = user.ranking
    except:
        guildPost = 0
    #获取用户当日已贡献值
    userDateContribution = processUserDateContributionRet(userLastDay, userLastDateContribution)
    #玩家当日还可允许贡献值
    maxContribution = processMaxContributionRet(guildLevel, userLastDay, userLastDateContribution, guildLastDay, guildLastDateContribution)
    #print(maxContribution)
    #用户在行会中的等级

    guildUserLevel = processGuildUserLevelRet(guildPost, ranking)
    #行会最大人数
    guildMaxPlayerNumber = GuildModel.getGuildMgr().getGuildLevelCfgByGuildLevel(guildLevel).guildNum
    #行会升级最大值
    if guildLevel <= 5:
        guildUpdateExp = GuildModel.getGuildMgr().getGuildLevelCfgByGuildLevel(guildLevel).guildExp
    #elif guildLevel == 5:
        #guildUpdateExp = GuildModel.getGuildMgr().getGuildLevelCfgByGuildLevel(guildLevel).guildExp
    else:
        session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, '行会已到最大等级')
    for uid, val in guildInfo.getGuildMember().iteritems():
        guildMemberList.append(processUserGuildInfoMsg(val.uid, val.name, val.post, val.contribute, val.ranking, val.level, val.job))
    if MsgDef.GuildPostCmd.GUILD_LEADER == guildPost or  MsgDef.GuildPostCmd.GUILD_SECOND_LEADER == guildPost:
        for uid, val in guildInfo.getGuildMemberTemp().iteritems():
            guildMemberTempList.append(processUserGuildInfoMsg(val.uid, val.name, 0, 0, 0, val.level, val.job))
    warInfo = GuildModel.getGuildMgr().getWarVSinfo(guildInfo.guildID)
    retMsg = processUserGuildListMsgRet(guildInfo.guildID, guildInfo.guildName, guildLevel, guildInfo.guildImage, guildInfo.getLenGuildMember(), guildMaxPlayerNumber, guildInfo.guildLeaderName, guildInfo.guildNotice, guildInfo.guildExp, guildUpdateExp, guildInfo.levelRanking, guildUserLevel, userDateContribution, maxContribution, guildMemberList, guildMemberTempList, guildInfo.copymapEndTm, guildInfo.typeCopyMap)
    if warInfo:
        otherGuild = warInfo.getAnotherGuild(guildInfo.guildID)
        val = otherGuild
        retMsg.warVsGuildInfo = processGuildInfoMsg(val.guildID, val.guildName, val.getLenGuildMember(), val.guildLeaderName, val.guildNotice, val.levelRanking, val.guildImage, val.guildLevel, val.copymapEndTm, val.typeCopyMap)
        retMsg.tmWarStart = warInfo.tmWarStart
    session.sendMsg(MsgDef.ServerCmd.GUILD_INFO_LIST_MSG, retMsg)
    return
#所有行会信息 对应消息类型为GET_GUILDINFO   ->GuildMsgReq           -> server:GUILDINFO_MSG  ->GuildInfoMsgRet
@ffext.onLogic(MsgDef.ClientCmd.GUILD_INFO_OPS, MsgDef.GuildInfoMsgReq)
def processGuildInfoOps(session, msg):
    cmd         = MsgDef.ClientCmd.GUILD_INFO_OPS
    opstype     = 0
    #先判断用户是否有行会
    guildInfo = session.player.guildCtrl.guildInfo
    #判断用户是否拥有行会，判断用户是否拥有修改行会的权限
    if not processUserHaveGuild(session, False, opstype, cmd) or processUserHaveGuildLimit(session, opstype, cmd):
        return
    guildImage  = msg.guildImage#.encode('utf-8')
    guildNotice = msg.guildNotice#.encode('utf-8')
    #修改数据库
    if '' != guildImage:
        DbService.getGuildService().updateGuildImage(guildInfo.guildID, guildImage)
    #if '' != guildNotice:
    ffext.dump("guildNotice", guildNotice)
    DbService.getGuildService().updateGuildNotice(guildInfo.guildID, guildNotice)

    #修改session
    guildImage  = guildInfo.updateGuildImage(guildImage)
    guildNotice = guildInfo.updateGuildNotice(guildNotice)
    ret_msg     = processGuildInfoOpsMsgRet(guildImage, guildNotice)
    for key, val in guildInfo.getGuildMember().iteritems():
        ffext.dump('processGuildInfoOps', key, val)
        memberSession   = ffext.getSessionMgr().findByUid(val.uid)
        if None != memberSession:
            memberSession.sendMsg(MsgDef.ServerCmd.GUILD_INFO_MSG, ret_msg)
    return
#行会列表操作对应消息类型为GUILD_LEVEL_OPS      ->GuildLevelOpsMsgReq-> server:GUILD_LEVEL_MSG              ->GuildLevelOpsMsgRet
@ffext.onLogic(MsgDef.ClientCmd.GUILD_LEVEL_OPS, MsgDef.GuildLevelOpsMsgReq)
def processGuildLevelOps(session, msg):
    opstype                 = msg.opstype
    cmd                     = MsgDef.ClientCmd.GUILD_LEVEL_OPS

    if not session.player:
        session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '无效请求。'))
        return
    #0升级行会
    if msg.opstype == MsgDef.GuildLevelClientCmd.UP_GUILD_LEVEL:
        #先判断用户是否有同意玩家加入行会的权限
        guildInfo = session.player.guildCtrl.guildInfo
        #判断用户是否拥有行会，判断用户是否拥有修改行会的权限，及行会经验是否满足升级要求
        if not processUserHaveGuild(session, False, opstype, cmd) or processUserHaveGuildLimit (session, opstype, cmd) or processGuildHaveEnoughExp (session, opstype, cmd):
            return
        #执行行会升级的数据库操作和session操作
        if guildInfo.guildLevel != 5:
            processUpgradeGuild(guildInfo)
            ffext.dump('guildexp!!!',guildInfo.guildExp)
            ret_msg = processGuildLevelOpsMsgRet(opstype, guildInfo.guildLevel, session.player.uid, session.player.name, 0, guildInfo.levelRanking, [])
            ffext.dump('RET', ret_msg)
            processGuildAllMemberRet(guildInfo, ret_msg, MsgDef.ServerCmd.GUILD_LEVEL_MSG)
            return
   #1贡献行会经验
    if msg.opstype == MsgDef.GuildLevelClientCmd.UP_GUILD_EXP:
        gold                    = msg.gold
        if gold <= 0:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '金币数量错误。'))
            return
        #判断用户是否拥有行会，判断用户金钱值是否满足
        if not processUserHaveGuild(session, False, opstype, cmd) or processUserHaveEnoughGold (session, opstype, cmd, session.player.gold, gold) or processUserGoldOutMaxContribution (session, opstype, cmd, gold):
            return
        guildInfo = session.player.guildCtrl.guildInfo
        processUpgradeGuildExp(session, gold)
        guildMemberList = getMemberList(session)
        ret_msg = processGuildLevelOpsMsgRet(opstype, 1, session.player.uid, session.player.name, gold, guildInfo.levelRanking, guildMemberList)
        ffext.dump('ret_msg', ret_msg)
        processGuildAllMemberRet(guildInfo, ret_msg, MsgDef.ServerCmd.GUILD_LEVEL_MSG)
        return

#函数封装，可以得到行会成员列表的所有信息，返回行会成员信息列表
def getMemberList(session):
    guildMemberList = []
    guildInfo = session.player.guildCtrl.guildInfo
    if guildInfo:
        for uid, val in guildInfo.getGuildMember().iteritems():
            guildMemberList.append(processUserGuildInfoMsg(val.uid, val.name, val.post, val.contribute, val.ranking, val.level, val.job))
    return guildMemberList

#函数封装，可以得到成员退出后行会成员列表的所有信息，返回退出后的行会成员信息列表
def getDelMemberList(session):
    guildDelMemberList = []
    guildInfo = session.player.guildCtrl.guildInfo
    if guildInfo:
        for uid, val in guildInfo.getGuildMember().iteritems():
            if session.player.uid != uid:
                guildDelMemberList.append(processUserGuildInfoMsg(val.uid, val.name, val.post, val.contribute, val.ranking, val.level, val.job))
    return guildDelMemberList

#函数封装，可以得到成员职务升级后的成员列表，返回退出后的行会成员信息列表
def getUpMemberList(session, new_post, memberUid):
    guildUpMemberList = []
    guildInfo = session.player.guildCtrl.guildInfo
    length = len(new_post)
    if guildInfo:
        for uid, val in guildInfo.getGuildMember().iteritems():
            for i in range(0, length):
                if uid == memberUid[i]:
                    guildUpMemberList.append(processUserGuildInfoMsg(val.uid, val.name, new_post[i], val.contribute, val.ranking, val.level, val.job))
            if uid not in memberUid:
                guildUpMemberList.append(processUserGuildInfoMsg(val.uid, val.name, val.post, val.contribute, val.ranking, val.level, val.job))
    return guildUpMemberList

#行会操作
@ffext.onLogic(MsgDef.ClientCmd.GUILD_OPS, MsgDef.GuildMsgReq)
def processGuildOPS(session, msg):
    opstype     = msg.opstype
    cmd         = MsgDef.ClientCmd.GUILD_OPS
    guildMemberList = getMemberList(session)

    #0创建行会
    if msg.opstype == MsgDef.GuildOpsClientCmd.CREATE_GUILD:#已测
        guildName = msg.guildname#.encode('utf-8')
        if guildName == '':
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '行会名不能为空。'))
            return
        if processUserHaveGuild(session, True , opstype, cmd) or processGuildNameRepeat(session, guildName, opstype, cmd):
            return
       #判断用户是否具备创建行会的条件
        if GuildModel.CREAT_GUILD_GOLD > session.player.gold or GuildModel.MIN_GUILD_LEVEL > session.player.level:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype,cmd, '角色达到10级之后，才可创建行会!'))
            return
        #扣除创建行会所需的金钱
        session.player.gold = session.player.gold - GuildModel.CREAT_GUILD_GOLD
        #给出行会ID
        guildID = idtool.allocId()
        #开始创建行会
        guildLeaderName = session.player.name
        memberpost = MsgDef.GuildPostCmd.GUILD_LEADER
        uid = session.player.uid
        level = session.player.level
        job = session.player.job
        #将行会创建信息写入数据库
        DbService.getGuildService().addGuild(guildID, guildName, guildLeaderName)
        DbService.getGuildService().addGuildMember(guildID, uid, memberpost)
        #将数据库创建成功写入session
        GuildModel.getGuildMgr().addGuild(uid, guildLeaderName, guildID, guildName, level, job)
        session.player.guildCtrl.changeGuild(guildID)
        # 数据库操作成功，给用户返回行会创建成功的信息
        session.sendMsg(MsgDef.ServerCmd.GUILD_OPS_MSG, processGuildOpsMsgRet(opstype, guildID, guildName, 0, '', guildMemberList))
        processGuildInfo(session)
        # 发送行会数据

        #发送行会创建成功的文字消息
        session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype,cmd, '行会创建成功！'))
        return
    #1请求加入行会
    if msg.opstype == MsgDef.GuildOpsClientCmd.REQUEST_ADD_GUILD:
        guildID = msg.guildid
        if GuildModel.MIN_GUILD_LEVEL > session.player.level:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype,cmd, '角色达到10级之后才可加入行会'))
            return
        if processUserHaveGuild(session, True, opstype, cmd) or processCheckGuildByID(session, guildID, opstype, cmd):
            return


        playerUid       = session.player.uid
        playerName      = session.player.name
        playerLevel     = session.player.level
        playerJob       = session.player.job
        ffext.dump('LEVEL!!!!!!!!!!!!!!!!!!!!!!!!!', playerLevel)
        ffext.dump('JOB!!!!!!!!!!!!!!!!!!!!!!!!!!!', playerJob)
        guildInfo       = GuildModel.getGuildMgr().getGuildById(guildID)
        #将用户写入临时行会列表，如果不需要，则注释掉下一行
        if None == guildInfo.getGuildMemberTempByUid(playerUid):
            guildInfo.addGuildMemberTemp(playerUid, playerName, playerLevel, playerJob)
            ret_msg = processGuildOpsMsgRet(opstype, guildID, '', playerUid, playerName, guildMemberList)
             #向队伍管理员广播加入队伍请求
            processGuildLimitRet(guildInfo, ret_msg, MsgDef.ServerCmd.GUILD_OPS_MSG)
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '行会申请已发送成功'))
        else:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '您已申请过该工会，请耐心等待!'))
        return
#2同意加入行会申请
    if msg.opstype == MsgDef.GuildOpsClientCmd.VERIFY_REQUEST_ADD_GUILD:
        newMemberUid = msg.uid
        guildInfo = session.player.guildCtrl.guildInfo
        #判断用户是否申请加入session所在的行会（函数中已判断session拥有行会） 判断用户是否有管理行会的权限    判断ID是否拥有行会
        if processUserApplyGuildByID(session, newMemberUid, opstype, cmd) or processGuildNumFull(session, guildInfo, opstype, cmd) or processUserHaveGuildLimit (session, opstype, cmd) or processUserHaveGuildByID(session, newMemberUid, opstype, cmd):
            return
        #修改数据库
        DbService.getGuildService().addGuildMember(guildInfo.guildID, newMemberUid, MsgDef.GuildPostCmd.MEMBER)
        #将用户写入session中行会成员列表
        newMemberSession = ffext.getSessionMgr().findByUid(newMemberUid)
        if None != newMemberSession:
            newMemberSession.player.guildCtrl.guildInfo = guildInfo
        newMemberName = guildInfo.getGuildMemberTempByUid(newMemberUid).name
        newMemberLevel = guildInfo.getGuildMemberTempByUid(newMemberUid).level
        newMemberJob = guildInfo.getGuildMemberTempByUid(newMemberUid).job
        guildInfo.addGuildMember(newMemberUid, newMemberName, newMemberLevel, newMemberJob)
        #将用户信息从临时好友列表中删除(如果没有临时列表，则不需要)
        guildInfo.delGuildMemberTemp(newMemberUid)
        #向行会成员广播加入行会
        guildMemberList = getMemberList(session)
        ret_msg = processGuildOpsMsgRet(opstype, guildInfo.guildID, guildInfo.guildName, newMemberUid, newMemberName, guildMemberList)
        processGuildAllMemberRet(guildInfo, ret_msg, MsgDef.ServerCmd.GUILD_OPS_MSG)
        processGuildInfo(session)  # 发送行会数据 给新成员
        if None != newMemberSession:
            processGuildInfo(newMemberSession)# 发送行会数据 给新成员
        return
#3拒绝加入行会申请
    if msg.opstype == MsgDef.GuildOpsClientCmd.REFUSE_REQUEST_ADD_GUILD:
        newMemberUid = msg.uid
        #判断用户是否申请加入session所在的行会（函数中已判断session拥有行会） 判断用户是否有管理行会的权限    
        if processUserApplyGuildByID(session, newMemberUid, opstype, cmd) or processUserHaveGuildLimit (session, opstype, cmd):
            return
        guildInfo = session.player.guildCtrl.guildInfo
        #将用户信息从临时好友列表中删除(如果没有临时列表，则不需要)
        guildInfo.delGuildMemberTemp(newMemberUid)
        #拒绝行会申请成功，将成功信息反馈给客户端
        newMemberSession = ffext.getSessionMgr().findByUid(newMemberUid)
        if None != newMemberSession:
            newMemberSession.sendMsg(MsgDef.ServerCmd.GUILD_OPS_MSG, processGuildOpsMsgRet(opstype, guildInfo.guildID, guildInfo.guildName, session.player.uid, session.player.name, guildMemberList))
        #向行会成员广播加入行会
        ret_msg = processGuildOpsMsgRet(opstype, guildInfo.guildID, guildInfo.guildName, newMemberUid, '',guildMemberList)
        processGuildLimitRet(guildInfo, ret_msg, MsgDef.ServerCmd.GUILD_OPS_MSG)
        return
    #4邀请加入行会
    if msg.opstype == MsgDef.GuildOpsClientCmd.INVITE_ADD_GUILD:
        memberName              = msg.name#.encode('utf-8')
        if processUserHaveGuild(session, False, opstype, cmd) == False or processUserHaveGuildLimit (session, opstype, cmd) :
            return
        guildInfo = session.player.guildCtrl.guildInfo
        memberSession   = ffext.getSessionMgr().getSessionByName(memberName)
        if GuildModel.MIN_GUILD_LEVEL > memberSession.player.level:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype,cmd, '角色达到10级之后才可加入行会'))
            return
        if None != memberSession:
            if 0 == memberSession.player.guildCtrl.getInviterById(guildInfo.guildID):
                memberSession.player.guildCtrl.addInviter(guildInfo.guildID)
            memberSession.sendMsg(MsgDef.ServerCmd.GUILD_OPS_MSG, processGuildOpsMsgRet(opstype, guildInfo.guildID, guildInfo.guildName, session.player.uid, session.player.name, guildMemberList))
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '已向对方发出行会邀请。'))
        else:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '用户不在线，或者用户不存在，不能邀请加入行会。'))
        return
    #5同意加入行会邀请
    if msg.opstype == MsgDef.GuildOpsClientCmd.VERIFY_INVIT_ADD_GUILD:
        guildID = msg.guildid
        #guildID = session.player.guildCtrl.guildInfo.guildID
        guildInfo = GuildModel.getGuildMgr().getGuildById(guildID)
        #先判断自己是否有行会，判断给定的行会是否存在，判断行会成员是否已满、判断行会是否邀请过用户
        if processUserHaveGuild(session, True, opstype, cmd) or processGuildExist(session, guildInfo, opstype, cmd) or \
                processGuildNumFull(session, guildInfo, opstype, cmd) or processGuildInviterByGuildInfo(session, guildInfo, opstype, cmd):
            return
        ffext.dump('MsgDef.GuildOpsClientCmd.VERIFY_INVIT_ADD_GUILD')
        #执行加入行会操作
        uid = session.player.uid
        name = session.player.name
        level = session.player.level
        job = session.player.job
        guildInfo.addGuildMember(uid, name, level, job)
        session.player.guildCtrl.delInviter(guildID)
        session.player.guildCtrl.changeGuild(guildID)
        DbService.getGuildService().addGuildMember(guildID, uid, MsgDef.GuildPostCmd.MEMBER)
        guildMemberList = getMemberList(session)
        ret_msg = processGuildOpsMsgRet(opstype, guildID, guildInfo.guildName, uid, name, guildMemberList)
        processGuildAllMemberRet(guildInfo, ret_msg, MsgDef.ServerCmd.GUILD_OPS_MSG)
        processGuildInfoAllMemberRet(guildInfo)
        # 发送行会数据
        #processGuildInfo(session)

        #发送文字消息
        session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '您已成功加入'+str(guildInfo.guildName)+'行会。'))
        return
    #6拒绝加入行会邀请
    if msg.opstype == MsgDef.GuildOpsClientCmd.REFUSE_INVITT_ADD_GUILD:
        guildID = msg.guildid
        guildInfo = GuildModel.getGuildMgr().getGuildById(guildID)
        #判断给定的行会是否存在，判断行会是否邀请过用户
        if processGuildExist(session, guildInfo, opstype, cmd) or processGuildInviterByGuildInfo(session, guildInfo, opstype, cmd):
            return
        #修改session
        session.player.guildCtrl.delInviter(guildID)
        #将消息进行广播
        ret_msg = processGuildOpsMsgRet(opstype, guildID, guildInfo.guildName, session.player.uid, session.player.name, guildMemberList)
        processGuildLimitRet(guildInfo, ret_msg, MsgDef.ServerCmd.GUILD_OPS_MSG)
        #session.sendMsg(MsgDef.ServerCmd.GUILD_OPS_MSG, processGuildOpsMsgRet(opstype, guildInfo.guildID, guildInfo.guildName, session.player.uid, session.player.name))
        session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '已拒绝了'+str(guildInfo.guildName)+'行会邀请。'))

        return

    #7从行会退出
    if msg.opstype == MsgDef.GuildOpsClientCmd.EXIT_GUILD:
        #先判断给定id是否和用户在同一个行会（内含判定用户是否有行会）、判断用户是否为行会长、判断用户给定ID是否是自己
        if not processUserHaveGuild(session, False, opstype, cmd):
            return
        uid                 = session.player.uid
        #判断用户是否为行会长
        guildInfo           = session.player.guildCtrl.guildInfo
        guildID             = guildInfo.guildID
        guildPost           = guildInfo.getGuildMemberByUid(uid).post
        if MsgDef.GuildPostCmd.GUILD_LEADER == guildPost:
            #用户为行会长，退出行会，该行会自动注销
            DbService.getGuildService().delGuild(guildID)
            ret_msg = processGuildOpsMsgRet(opstype, guildID, guildInfo.guildName, uid, session.player.name, guildMemberList)
            for key, val in guildInfo.getGuildMember().iteritems():
                memberSession = ffext.getSessionMgr().findByUid(val.uid)
                if None != memberSession:
                    memberSession.player.guildCtrl.changeGuild(0)
                    memberSession.sendMsg(MsgDef.ServerCmd.GUILD_OPS_MSG, ret_msg)
            for key, val in GuildModel.getGuildMgr().getGuild().iteritems():
                if guildInfo.levelRanking < val.levelRanking:
                    val.levelRanking = val.levelRanking - 1
            GuildModel.getGuildMgr().delGuild(guildID)
        else:
            guildDelMemberList = getDelMemberList(session)
            #ffext.dump('GuildDelMemberList!!!!!!!!!!!!!!!!!!!!!!!!!!!!', guildDelMemberList)
            ret_msg = processGuildOpsMsgRet(opstype, guildID, guildInfo.guildName, uid, session.player.name, guildDelMemberList)
            session.sendMsg(MsgDef.ServerCmd.GUILD_OPS_MSG, ret_msg)
            processGuildDelMemberByID(session, uid, opstype)
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '您已成功退出行会!'))
        return
    #8将成员从行会中删除
    if msg.opstype == MsgDef.GuildOpsClientCmd.DEL_GUILD_MEMBER:
        uid = msg.uid
        #先判断给定id是否和用户在同一个行会（内含判定用户是否有行会）、判断用户是否有修改行会的权限
        if processGuildUserByUid(session, uid, opstype, cmd ) or processUserHaveGuildLimit (session, opstype, cmd):
            return
        processGuildDelMemberByID(session, uid, opstype)
        return
    #9升级为行会长
    if msg.opstype == MsgDef.GuildOpsClientCmd.UP_GUILD_LEADER:
        memberUid = msg.uid
        #先判断给定id是否和用户在同一个行会（内含判定用户是否有行会）、判断用户是否为行会长、判断用户给定ID是否是自己
        if processGuildUserByUid(session, memberUid, opstype, cmd ) or processUserGuildLeader (session, opstype, cmd) or processGuildUserorUid(session, memberUid, opstype, cmd, '行会长需要通过变更行会长，才能将自己转化成副行会长。'):
            return
        DbService.getGuildService().updateGuildMemberPost(memberUid, MsgDef.GuildPostCmd.GUILD_LEADER)
        DbService.getGuildService().updateGuildMemberPost(session.player.uid, MsgDef.GuildPostCmd.MEMBER)
        guildInfo = session.player.guildCtrl.guildInfo
        playerInfo = guildInfo.getGuildMemberByUid(memberUid)
        memberName = playerInfo.name
        guildInfo.guildLeaderName = memberName
        playerInfo.post = MsgDef.GuildPostCmd.GUILD_LEADER
        guildInfo.getGuildMemberByUid(session.player.uid).post = MsgDef.GuildPostCmd.MEMBER
        new_post = [playerInfo.post, guildInfo.getGuildMemberByUid(session.player.uid).post]
        ffext.dump('new_post!!!!!!!!!!!!!!!', new_post)
        memberUidList = [memberUid, session.player.uid]
        ffext.dump('memberUidList!!!!!!!!!!!!!!!!!!!!!!', memberUidList)
        guildUpMemberListFirst = getUpMemberList(session, new_post, memberUidList)
        ffext.dump('MemberlistFirst!!!!!!!!!!!!!!!!!', guildUpMemberListFirst)
        ret_msg = processGuildOpsMsgRet(opstype, guildInfo.guildID, guildInfo.guildName, memberUid, playerInfo.name, guildUpMemberListFirst)
        processGuildAllMemberRet(guildInfo, ret_msg, MsgDef.ServerCmd.GUILD_OPS_MSG)
        return
    #10升级为副行会长
    if msg.opstype == MsgDef.GuildOpsClientCmd.UP_GUILD_SECOND_LEADER:
        memberUid = msg.uid
        #先判断给定id是否和用户在同一个行会（内含判定用户是否有行会）、判断用户是否为行会长、判断用户给定ID是否是自己
        if processGuildUserByUid(session, memberUid, opstype, cmd ) or processUserGuildLeader (session, opstype, cmd) or processGuildUserorUid(session, memberUid, opstype, cmd, '行会长需要通过变更行会长，才能将自己转化成副行会长。'):
            return
        guildInfo = session.player.guildCtrl.guildInfo
        playerInfo = guildInfo.getGuildMemberByUid(memberUid)
        if MsgDef.GuildPostCmd.GUILD_SECOND_LEADER == playerInfo.post:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '用户已经为副行会长，不需要重新任命。'))
            return
        #遍历，查询行会中有几个副行会长
        if processGuildsecondLeaderNum(session) >= 2:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '副行会长数量超过要求，不能再进行任命。'))
            return
        DbService.getGuildService().updateGuildMemberPost(memberUid, MsgDef.GuildPostCmd.GUILD_SECOND_LEADER)
        playerInfo.post = MsgDef.GuildPostCmd.GUILD_SECOND_LEADER
        guildUpMemberListSecond = getUpMemberList(session, [playerInfo.post], [memberUid])
        ret_msg = processGuildOpsMsgRet(opstype, guildInfo.guildID, guildInfo.guildName, memberUid, playerInfo.name, guildUpMemberListSecond)
        processGuildAllMemberRet(guildInfo, ret_msg, MsgDef.ServerCmd.GUILD_OPS_MSG)
        return
    #11升级为普通成员
    if msg.opstype == MsgDef.GuildOpsClientCmd.UP_MEMBER:
        memberUid = msg.uid
        #先判断给定id是否和用户在同一个行会（内含判定用户是否有行会）、判断用户是否为行会长、判断用户给定ID是否是自己
        if processGuildUserByUid(session, memberUid, opstype, cmd ) or processUserGuildLeader (session, opstype, cmd) or processGuildUserorUid(session, memberUid, opstype, cmd, '行会长需要通过变更行会长，才能将自己转化成普通用户。'):
            return
        guildInfo = session.player.guildCtrl.guildInfo
        playerInfo = guildInfo.getGuildMemberByUid(memberUid)
        DbService.getGuildService().updateGuildMemberPost(memberUid, MsgDef.GuildPostCmd.MEMBER)
        playerInfo.post = MsgDef.GuildPostCmd.MEMBER
        guildUpMemberListThird = getUpMemberList(session, [playerInfo.post], [memberUid])
        ret_msg = processGuildOpsMsgRet(opstype, guildInfo.guildID, guildInfo.guildName, memberUid, playerInfo.name, guildUpMemberListThird)
        processGuildAllMemberRet(guildInfo, ret_msg, MsgDef.ServerCmd.GUILD_OPS_MSG)
    #12 开启行会副本
    if msg.opstype == MsgDef.GuildOpsClientCmd.OPEN_COPY_MAP:
        # 军团副本只有军团长或副军团长才能开启
        if processUserHaveGuild(session, False, opstype, cmd) == False or processUserHaveGuildLimit(session, opstype, cmd):
            return
        GuildModel.getGuildMgr().openCopyMap(session.player)
        guildInfo = session.player.guildCtrl.guildInfo
        guildInfo.typeCopyMap = msg.typeCopyMap
        guildMemberList = getMemberList(session)
        ret_msg = processGuildOpsMsgRet(opstype, guildInfo.guildID, guildInfo.guildName, session.player.uid, session.player.name, guildMemberList, guildInfo)
        #ret_msg = processGuildInfoMsg(guildInfo.guildID, guildInfo.guildName, guildInfo.getLenGuildMember(), guildInfo.guildLeaderName, guildInfo.guildNotice, guildInfo.levelRanking, guildInfo.guildImage, guildInfo.guildLevel, guildInfo.copymapEndTm, guildInfo.typeCopyMap)
        processGuildAllMemberRet(guildInfo, ret_msg, MsgDef.ServerCmd.GUILD_OPS_MSG)
    if msg.opstype == MsgDef.GuildOpsClientCmd.ENTER_COPY_MAP:
        # 军团副本只有军团长或副军团长才能开启
        if processUserHaveGuild(session, False, opstype, cmd) == False:
            return
        guildInfo = session.player.guildCtrl.guildInfo
        mapObj = GuildModel.getGuildMgr().getGuildCopyMap(guildInfo)
        if not mapObj:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '副本已经关闭。'))
            return
        nowTm = ffext.getTime()
        if nowTm >= guildInfo.copymapEndTm:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '副本已经关闭。'))
            return
        mapObj.playerEnterMap(session.player, 78, 67)
#声明一个函数，用于操作在删除用户时的session和数据操作
def processGuildDelMemberByID(session, uid, opstype):
    #将成员从数据库中删除
    DbService.getGuildService().delGuildMember(uid)
    #修改行会排名
    guildInfo = session.player.guildCtrl.guildInfo
    playerInfo = guildInfo.getGuildMemberByUid(uid)
    ranking = playerInfo.ranking
    for memberUid, val in guildInfo.getGuildMember().iteritems():
        if ranking < val.ranking:
            val.ranking = val.ranking - 1
    guildInfo.delGuildMember(uid)
    if ffext.getSessionMgr().findByUid(uid):
        ffext.getSessionMgr().findByUid(uid).player.guildCtrl.changeGuild(0)
    guildMemberList = getMemberList(session)
    ret_msg = processGuildOpsMsgRet(opstype, guildInfo.guildID, guildInfo.guildName, uid, playerInfo.name, guildMemberList)
    processGuildAllMemberRet(guildInfo, ret_msg, MsgDef.ServerCmd.GUILD_OPS_MSG)
    return True
#声明一个函数，用于判断给定行会是否邀请用户
def processGuildInviterByGuildInfo(session, guildInfo, opstype, cmd):
    if 0 == session.player.guildCtrl.getInviterById(guildInfo.guildID):
        session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '该行会没有邀请您，不能加入。'))
        return True
    return False
#声明一个函数，用于判断给定行会是否存在
def processGuildExist(session, guildInfo, opstype, cmd):
    ffext.dump('processGuildExist')
    if None == guildInfo:
        session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '行会ID不正确，指令错误。'))
        return True
    return False
#声明一个函数，用于判断行会是否满员
def processGuildNumFull(session, guildInfo, opstype, cmd):
    ffext.dump('processGuildNumFull')
    guildNumber = guildInfo.getLenGuildMember()
    guildMaxNumber = GuildModel.getGuildMgr().getGuildLevelCfgByGuildLevel(guildInfo.guildLevel).guildNum
    if guildNumber >= guildMaxNumber:
        session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '行会已满。'))
        return True
    return False
#声明一个函数，用于判断给定ID是否申请加入自己的行会（前提是session拥有行会）
def processUserApplyGuildByID(session, memberUid, opstype, cmd):
    if not processUserHaveGuild(session, False, opstype, cmd):
        return True
    #判断用户是否发送申请，如没有发送申请，则提示错误
    if None == session.player.guildCtrl.guildInfo.getGuildMemberTempByUid(memberUid):
        session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '用户没有申请加入行会，或其他管理员已操作。'))
        return True
    return False
#声明一个函数，用于判断给定ID是否拥有行会
def processUserHaveGuildByID(session, memberUid, opstype, cmd):
    #判断用户是否拥有行会
    newMemberSession = ffext.getSessionMgr().findByUid(memberUid)
    if None != newMemberSession:
        if None != newMemberSession.player.guildCtrl.guildInfo:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '已有行会。'))
            return True
    else:
        #用户不在线，需要查询数据库判断用户是否拥有行会
        for keyGuild, valGuild in GuildModel.getGuildMgr().getGuild().iteritems():
            for key, val in valGuild.getGuildMember().iteritems():
                if memberUid == val.uid:
                    session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '已有行会。'))
                    return True
    return False
#声明一个函数，用于查询行会中有几个副会长
def processGuildsecondLeaderNum(session):
    secondLeaderNum = 0
    for key, val in session.player.guildCtrl.guildInfo.getGuildMember().iteritems():
        if MsgDef.GuildPostCmd.GUILD_SECOND_LEADER == val.post:
            secondLeaderNum = secondLeaderNum + 1
    return secondLeaderNum
#声明一个函数，判断给定的用户是否是用户自己
def processGuildUserorUid(session, memberUid, opstype, cmd, ret_msg):
    ffext.dump('processGuildUserorUid', memberUid, opstype, cmd, ret_msg)
    if memberUid == session.player.uid:
        session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, ret_msg))
        return True
    return False
#声明一个函数，判断给定的用户是否和自己在同一个行会
def processGuildUserByUid(session, memberUid, opstype, cmd ):
    #先判断自己是否有行会
    if not processUserHaveGuild(session, False, opstype, cmd):
        return True
    guildInfo = session.player.guildCtrl.guildInfo
    playerInfo = guildInfo.getGuildMemberByUid(memberUid)
    if None == playerInfo:
        session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '用户不在此行会，不能修改。'))
        return True
    return  False
#声明一个函数，通过玩家行会排名返回玩家行会等级
def processGuildUserLevelRet(guildPost, guildUserRanking):
    if MsgDef.GuildPostCmd.GUILD_LEADER == guildPost:
        guildUserLevel = MsgDef.GuildLevelCmd.GUILD_LEVRL_1
    elif MsgDef.GuildPostCmd.GUILD_SECOND_LEADER == guildPost:
        guildUserLevel = MsgDef.GuildLevelCmd.GUILD_LEVRL_2
    else:
        if guildUserRanking > GuildModel.MAX_GUILD_USER_LEVEL_RANKING4:
            guildUserLevel = MsgDef.GuildLevelCmd.GUILD_LEVRL_7
        elif guildUserRanking > GuildModel.MAX_GUILD_USER_LEVEL_RANKING3:
            guildUserLevel = MsgDef.GuildLevelCmd.GUILD_LEVRL_6
        elif guildUserRanking > GuildModel.MAX_GUILD_USER_LEVEL_RANKING2:
            guildUserLevel = MsgDef.GuildLevelCmd.GUILD_LEVRL_5
        elif guildUserRanking > GuildModel.MAX_GUILD_USER_LEVEL_RANKING1:
            guildUserLevel = MsgDef.GuildLevelCmd.GUILD_LEVRL_4
        else:
            guildUserLevel = MsgDef.GuildLevelCmd.GUILD_LEVRL_3
    return  guildUserLevel
#声明一个函数，用户获取玩家本次可允许贡献行会的最大值
def processMaxContributionRet(guildLevel, userLastDay, userLastDateContribution, guildLastDay, guildLastDateContribution):
    thisDay = str(datetime.date.today())
    print(guildLevel)
    guildLevelCfg = GuildModel.getGuildMgr().getGuildLevelCfgByGuildLevel(guildLevel)
    print(guildLevelCfg)
    userMaxContribution = guildLevelCfg.playerDayExp
    userDateContribution = 0
    if thisDay == userLastDay:
        userDateContribution = userLastDateContribution
    guildDateContribution = 0
    if thisDay == guildLastDay:
        guildDateContribution = guildLastDateContribution
    guildMaxContribution = guildLevelCfg.guildDayExp - guildDateContribution + userDateContribution
    if guildMaxContribution > userMaxContribution:
        maxContribution = userMaxContribution
    else:
        maxContribution = guildMaxContribution
    return  maxContribution
#声明一个函数，用于获取用户当日贡献值
def processUserDateContributionRet(userLastDay, userLastDateContribution):
    thisDay = str(datetime.date.today())
    userDateContribution = 0
    if thisDay == userLastDay:
        userDateContribution = userLastDateContribution
    return  userDateContribution
#声明一个函数，用于判断玩家是否拥有行会
def processUserHaveGuild(session, flag, opstype, cmd):

    if None == session.player.guildCtrl.guildInfo:
        if False == flag:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '用户没有行会，指令错误。'))
        ffext.dump('processUserHaveGuild', session.player.guildCtrl.guildInfo, False)
        return False
    else:
        if True == flag:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '用户已有行会。'))
        return  True
#声明一个函数，用于判断行会是否有重名
def processGuildNameRepeat(session, guildName, opstype, cmd):
    for id, val in GuildModel.getGuildMgr().getGuild().iteritems():
        if guildName == val.guildName:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '行会名称重名，请重新选择行会名称。'))
            return True
    return False
#声明一个函数，用于判断用户是否拥有修改行会的权限
def processUserHaveGuildLimit (session, opstype, cmd):
    if not session.player.guildCtrl.guildInfo:
        session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '用户没有权限。'))
        return True
    m = session.player.guildCtrl.guildInfo.getGuildMemberByUid(session.player.uid)
    if not m:
        session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '用户没有权限。'))
        return True
    guildPost = m.post
    if MsgDef.GuildPostCmd.GUILD_LEADER != guildPost and MsgDef.GuildPostCmd.GUILD_SECOND_LEADER != guildPost:
        session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '用户没有权限。'))
        return True
    return  False
#声明一个函数，用于判断用户是否拥有修改成员级别的权限
def processUserGuildLeader (session, opstype, cmd):
    guildPost = session.player.guildCtrl.guildInfo.getGuildMemberByUid(session.player.uid).post
    if MsgDef.GuildPostCmd.GUILD_LEADER != guildPost:
        session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '用户没有权限。'))
        return True
    return  False
#声明一个函数，用于判断用户行会经验数目是否满足升级行会的要求
def processGuildHaveEnoughExp (session, opstype, cmd):
    guildInfo = session.player.guildCtrl.guildInfo
    #获取行会升级需要的经验值
    if guildInfo.guildLevel < 5:
        levelExp = GuildModel.getGuildMgr().getGuildLevelCfgByGuildLevel(guildInfo.guildLevel).guildExp
    elif guildInfo.guildLevel == 5:
        levelExp = GuildModel.getGuildMgr().getGuildLevelCfgByGuildLevel(guildInfo.guildLevel).guildExp
        return
    else:
        session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '已达到行会最大等级'))
        return
    guildExp = guildInfo.guildExp
    if levelExp > guildExp:
        session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '行会经验值不满足升级条件。'))
        return True
    return  False
#升级行会时的session和数据库操作
def processUpgradeGuild(guildInfo):
    #guildLevel = guildInfo.guildLevel + 1
    if guildInfo.guildLevel < 5:
        levelExp = GuildModel.getGuildMgr().getGuildLevelCfgByGuildLevel(guildInfo.guildLevel).guildExp
        guildInfo.guildLevel += 1
    elif guildInfo.guildLevel == 5:
        levelExp = GuildModel.getGuildMgr().getGuildLevelCfgByGuildLevel(guildInfo.guildLevel).guildExp
        return
    else:
        return
    guildExp = guildInfo.guildExp - levelExp
    levelRanking = guildInfo.levelRanking
    guildLevel = guildInfo.guildLevel
    #修改数据库
    DbService.getGuildService().updateGuild(guildInfo.guildID, guildExp, guildLevel)
    #修改session
    guildInfo.guildExp = guildExp
    guildInfo.guildLevel = guildLevel
    for key, val in GuildModel.getGuildMgr().getGuild().iteritems():
        if val == guildInfo:
            continue
        if guildLevel > val.guildLevel or \
            (guildLevel == val.guildLevel and guildExp > val.guildExp):
            if val.levelRanking < levelRanking:
                levelRanking = val.levelRanking
            val.levelRanking = val.levelRanking +1
    ffext.dump('LEVELRANKING', levelRanking)
    guildInfo.levelRanking = levelRanking
    return
#向行会中所有成员广播
def processGuildAllMemberRet(guildInfo, ret_msg, format):
    for key, val in guildInfo.getGuildMember().iteritems():
        ffext.dump('VAL.UID',val.uid)
        memberSession   = ffext.getSessionMgr().findByUid(val.uid)
        if None != memberSession:
            memberSession.sendMsg(format, ret_msg)
    return
#向行会长、副会长广播
def processGuildLimitRet(guildInfo, ret_msg, format):
    for key, val in guildInfo.getGuildMember().iteritems():
        if MsgDef.GuildPostCmd.GUILD_LEADER  == val.post or MsgDef.GuildPostCmd.GUILD_SECOND_LEADER  == val.post:
            LeaderSession  = ffext.getSessionMgr().findByUid(val.uid)
            if None != LeaderSession:
                LeaderSession.sendMsg(format, ret_msg)
    return

#向行会中所有成员广播行会信息
def processGuildInfoAllMemberRet(guildInfo):
    for key, val in guildInfo.getGuildMember().iteritems():
        memberSession   = ffext.getSessionMgr().findByUid(val.uid)
        if None != memberSession:
            processGuildInfo(memberSession)
    return

#声明一个函数，用于判断用户金钱数是否满足本次贡献数额
def processUserHaveEnoughGold (session, opstype, cmd, userGold, gold):
    if userGold < gold:
        session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '用户金钱不足。'))
        return True
    return  False
#声明一个函数，用于判断用户本次贡献是否超过当日贡献值
def processUserGoldOutMaxContribution (session, opstype, cmd, gold):
    guildInfo = session.player.guildCtrl.guildInfo
    userLastDay     = session.player.guildCtrl.lastDate
    userLastDateContribution = session.player.guildCtrl.lastDateContribution
    guildLastDay    = guildInfo.lastDate
    guildLastDateContribution = guildInfo.lastDateContribution
    guildLevel      = guildInfo.guildLevel
    userMaxContribution = processMaxContributionRet(guildLevel, userLastDay, userLastDateContribution, guildLastDay, guildLastDateContribution) - processUserDateContributionRet(userLastDay, userLastDateContribution)
    if userMaxContribution < gold:
        session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '金钱已超过当日贡献最大值。'))
        return True
    return  False
#贡献行会时的session和数据库操作
def processUpgradeGuildExp(session, gold):
    nowtm = ffext.getTime()
    #thisDay = str(datetime.date.today()).replace('-','')
    #先扣除用户session中的金钱
    #session.player.gold =  session.player.gold - gold
    session.player.addGold(-1 * gold, True)
    guildInfo = session.player.guildCtrl.guildInfo
    guildExp = guildInfo.guildExp + gold
    userLastDay     = session.player.guildCtrl.lastDate
    ffext.dump("USERLASTDAY", userLastDay)
    if ffext.tmIsSameDay(nowtm, userLastDay):#userLastDay == thisDay:
        userDateContribution = session.player.guildCtrl.lastDateContribution + gold
    else:
        userDateContribution = gold
    guildLastDay    = guildInfo.lastDate
    if ffext.tmIsSameDay(nowtm, guildLastDay):#guildLastDay == thisDay:
        lastDateContribution = guildInfo.lastDateContribution + gold
    else:
        lastDateContribution = gold
    userContribution = long(guildInfo.getGuildMemberByUid(session.player.uid).contribute) + gold
    #修改数据库中信息
    DbService.getGuildService().contributionGuild(session.player.uid, guildInfo.guildID,  nowtm, userContribution, userDateContribution, guildExp, lastDateContribution)
    #将贡献信息写入session
    session.player.guildCtrl.lastDateContribution = userDateContribution
    session.player.guildCtrl.lastDate = nowtm
    guildInfo.lastDateContribution = nowtm
    guildInfo.lastDate             = nowtm
    guildInfo.guildExp             = guildExp
    guildLevel = guildInfo.guildLevel
    levelRanking = guildInfo.levelRanking
    #修改行会排名
    for key, val in GuildModel.getGuildMgr().getGuild().iteritems():
        if val == guildInfo:
            continue
        if guildLevel > val.guildLevel or \
            (guildLevel == val.guildLevel and guildExp > val.guildExp):
            if val.levelRanking < levelRanking:
                levelRanking = val.levelRanking
            val.levelRanking = val.levelRanking +1
    guildInfo.levelRanking = levelRanking
    playerInfo = guildInfo.getGuildMemberByUid(session.player.uid)
    playerInfo.contribute = userContribution
    ranking = playerInfo.ranking
    #修改用户排名
    userGuildInfo = []
    for memberUid, val in guildInfo.getGuildMember().iteritems():
        if userContribution > val.contribute or ranking > val.ranking:
            if ranking > 0:
                ranking = ranking - 1
                val.ranking = val.ranking +1
        userGuildInfo.append(processUserGuildInfoMsg(val.uid, val.name, val.post, val.contribute, val.ranking, val.level, val.job))
    playerInfo.ranking = ranking
    return userGuildInfo




#通过行会ID，判断行会是否存在
def processCheckGuildByID(session, guildID, opstype, cmd):
    guildInfo = GuildModel.getGuildMgr().getGuildById(guildID)
    if None == guildInfo:
        session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '行会不存在。'))
        return True
    return False
#以下为返回客户端信息的格式函数。
# 用于返回行会信息的函数。
def processGuildInfoMsg(guildID, guildName, guildPlayerNumber, guildLeaderName, guildNotice, levelRanking, guildImage, guildLevel, copymapEndTm, typeCopyMap):
    ret_msg                     = MsgDef.GuildInfoMsg()
    ret_msg.guildID             = guildID                   #行会ID
    ret_msg.guildName           = guildName                 #行会名称
    ret_msg.guildPlayerNumber   = guildPlayerNumber         #行会成员数量
    ret_msg.guildLeaderName     = guildLeaderName           #行会长名称
    ret_msg.guildNotice         = guildNotice               #行会公告
    ret_msg.levelRanking        = levelRanking              #行会等级排名
    ret_msg.guildImage          = guildImage                #行会图片
    ret_msg.guildlevel          = guildLevel                #行会等级
    ret_msg.copymapEndTm        = copymapEndTm              #副本结束时间
    ret_msg.typeCopyMap         = typeCopyMap               #副本类型
    return ret_msg
#用于返回错误信息的函数
def processErrorMsgRet(opstype, cmd, msg):
    ret_msg                 = MsgDef.ErrorMsgRet()
    ret_msg.erropstype      = opstype                        #错误信息所处位置opstype
    ret_msg.cmd             = cmd                               #错误信息所处位置cmd
    ret_msg.errMsg          = msg                               #错误信息
    return ret_msg
#行会操作时，给行会返回数据的格式函数
def processGuildOpsMsgRet(opstype, guildid, guildname, userid, username, guildMemberList, guildInfo = None):
    ret_msg                 = MsgDef.GuildOpsMsgRet()
    ret_msg.opstype      = opstype
    ret_msg.guildid         = guildid                           #行会ID
    ret_msg.guildname       = guildname                         #行会名称
    ret_msg.userid          = userid                            #用户ID
    ret_msg.username        = username                          #用户名称
    ret_msg.guildMemberList = guildMemberList                   #行会成员信息
    if guildInfo:
        ret_msg.copymapEndTm = guildInfo.copymapEndTm
        ret_msg.typeCopyMap  = guildInfo.typeCopyMap
    return ret_msg
#返回行会成员列表时，将成员信息打包，成员信息打包的格式
def processUserGuildInfoMsg(uid, name, post, contribute, ranking, level ,job):
    if post == '':
        post = 0
    if contribute == '':
        contribute = 0
    if ranking == '':
        ranking = 0
    ret_msg                     = MsgDef.UserGuildInfoMsg()
    ret_msg.uid                 = uid                           #用户ID
    ret_msg.name                = name                          #用户名称
    ret_msg.post                = post                          #用户级别
    ret_msg.contribute          = contribute                    #用户总贡献值
    ret_msg.ranking             = ranking                       #用户贡献值排名
    ret_msg.level               = level                         #用户等级
    ret_msg.job                 = job                           #用户职业
    return ret_msg
#用户上线时，服务器给客户端发送的用户行会信息的格式
def processUserGuildListMsgRet(guildID, guildName, guildLevel, guildImage, guildPlayerNumber, guildMaxPlayerNumber, guildLeaderName, guildNotice, guildExp, guildUpdateExp, levelRanking, guildPost, dateContribution, maxContribution, guildMemberList, guildMemberTempList, copymapEndTm, typeCopyMap):
    ret_msg                         = MsgDef.UserGuildListMsgRet()
    ret_msg.guildID                 = guildID                       #行会ID
    ret_msg.guildName               = guildName                     #行会名称
    ret_msg.guildLevel              = guildLevel                    #行会等级
    ret_msg.guildImage              = guildImage                    #行会图片
    ret_msg.guildPlayerNumber       = guildPlayerNumber             #行会成员数量
    ret_msg.guildMaxPlayerNumber    = guildMaxPlayerNumber          #行会最大成员数量
    ret_msg.guildLeaderName         = guildLeaderName               #行会长名称
    ret_msg.guildNotice             = guildNotice                   #行会公告
    ret_msg.guildExp                = guildExp                      #行会现有资源
    ret_msg.guildUpdateExp          = guildUpdateExp                #升级需要资源
    ret_msg.levelRanking            = levelRanking                  #行会排名
    ret_msg.guildPost               = guildPost                    #职务
    ret_msg.dateContribution        = dateContribution             #当日贡献值
    ret_msg.maxContribution         = maxContribution              #每日贡献值限额
    ret_msg.guildMemberList         = guildMemberList              #行会成员列表
    ret_msg.guildMemberTempList     = guildMemberTempList          #待验证行会成员信息
    ret_msg.copymapEndTm            = copymapEndTm                 #副本结束时间
    ret_msg.typeCopyMap             = typeCopyMap                  #副本类型
    #ffext.dump(ret_msg)
    return ret_msg
#行会长更改行会信息后，服务器给相关客户端反馈信息的格式
def processGuildInfoOpsMsgRet(guildImage, guildNotice):
    ret_msg                         = MsgDef.GuildInfoOpsMsgRet()
    ret_msg.guildImage              = guildImage                        #行会图片
    ret_msg.guildNotice             = guildNotice                       #行会公告
    return ret_msg
#行会等级操作时，服务器给客户端广播的信息格式
def processGuildLevelOpsMsgRet(opstype, guildLevel, uid, name, gold, ranking, guildMemberList):
    ret_msg                         = MsgDef.GuildLevelOpsMsgRet()
    ret_msg.opstype                 = opstype
    ret_msg.guildLevel              = guildLevel                        #行会等级
    ret_msg.uid                     = uid                               #操作人ID
    ret_msg.name                    = name                              #操作人名称
    ret_msg.gold                    = gold                              #操作人贡献的金币值
    ret_msg.ranking                 = ranking                           #行会排名
    ret_msg.guildMemberList           = guildMemberList                     #行会成员信息
    return ret_msg
#以上为返回客户端信息的格式函数。
def buildErrMsg(cmd, errMsg):
    return MsgDef.ErrorMsgRet(0, cmd, errMsg)#'cmd=%d,errMsg=%s'%(cmd, errMsg)

@ffext.onLogic(MsgDef.ClientCmd.GUILD_WAR_OPS, MsgDef.GuildWarOpsReq)
def processGuildWarOps(session, msg):
    ffext.dump('processGuildWarOps', msg)
    opstype = msg.opstype
    cmd = MsgDef.ClientCmd.GUILD_WAR_OPS
    guildInfo = session.player.guildCtrl.guildInfo
    otherGuildId = GuildModel.getGuildMgr().getGuildIdByName(msg.guildName)
    if not guildInfo:
        session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '请先加入行会。'))
        return
    guildId = guildInfo.guildID
    retMsg = MsgDef.GuildWarOpsRet(msg.opstype)
    if opstype == MsgDef.GuildWarOpsCmd.APPLY_WAR:
        warInfo = GuildModel.getGuildMgr().getWarVSinfo(guildId)
        if warInfo:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '已经申请过了。'))
            return
        otherGuild = GuildModel.getGuildMgr().getGuildById(otherGuildId)
        if not otherGuild:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '输入行会错误。'))
            return
        if otherGuildId == guildId:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '申请目标行会不正确。'))
            return
        warInfo = GuildModel.getGuildMgr().addWarVsInfo(guildInfo, otherGuild)
        retMsg.tmWarStart = warInfo.tmWarStart
        retMsg.warApplyGuild = GuildModel.buildGuildInfoMsg(guildInfo)
        retMsg.warFightGuild = GuildModel.buildGuildInfoMsg(otherGuild)
        guildInfo.sendMsg2OnlineMember(MsgDef.ServerCmd.GUILD_WAR_OPS, retMsg)
        otherGuild.sendMsg2OnlineMember(MsgDef.ServerCmd.GUILD_WAR_OPS, retMsg)
    elif opstype == MsgDef.GuildWarOpsCmd.WAR_LIST:
        warListInfo = GuildModel.getGuildMgr().allGuildWarVSInfo
        ffext.dump('warListInfo',warListInfo)
        retMsg.warListInfo = []
        for i,k in warListInfo.iteritems():
            tmpInfo = MsgDef.GuildWarOtherInfo()
            tmpInfo.warApplyGuild = GuildModel.buildGuildInfoMsg(k.guild1)
            tmpInfo.warFightGuild = GuildModel.buildGuildInfoMsg(k.guild2)
            tmpInfo.tmWarStart = k.tmWarStart
            retMsg.warListInfo.append(tmpInfo)
        ffext.dump('retMsg', retMsg)
        session.sendMsg(MsgDef.ServerCmd.GUILD_WAR_OPS, retMsg)
    elif opstype == MsgDef.GuildWarOpsCmd.WAR_CANCEL_APPLY:
        warListInfo = GuildModel.getGuildMgr().delWarVsInfo(guildId)
        retMsg.warListInfo = []
        for i,k in warListInfo.iteritems():
            tmpInfo = MsgDef.GuildWarOtherInfo()
            tmpInfo.warApplyGuild = GuildModel.buildGuildInfoMsg(k.guild1)
            tmpInfo.warFightGuild = GuildModel.buildGuildInfoMsg(k.guild2)
            tmpInfo.tmWarStart = k.tmWarStart
            retMsg.warListInfo.append(tmpInfo)
        ffext.dump('retMsg', retMsg)
        session.sendMsg(MsgDef.ServerCmd.GUILD_WAR_OPS, retMsg)

@ffext.onLogic(MsgDef.ClientCmd.GUILD_CITYWAR_OPS, MsgDef.GuildCityWarOpsMsgReq)
def processGuildCityWarOps(session, msg):
    ffext.dump('processGuildCityWarOps', msg)
    opstype = msg.opstype
    cmd = MsgDef.ClientCmd.GUILD_CITYWAR_OPS
    guildInfo = session.player.guildCtrl.guildInfo
    # retMsg = MsgDef.GuildCityWarOpsMsgRet(msg.opstype)
    if not guildInfo:
        session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '请先加入行会。'))
        return
    if opstype == MsgDef.GuildCityWarOpsCmd.APPLY_CITYWAR:
        ffext.dump('申请攻城战')
        if guildInfo.guildLevel < 5 and GuildModel.g_debugCityWar == False:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '需要行会5级。'))
            return
        # 会长才能操作
        if guildInfo.getGuildMemberByUid(session.player.uid).post != MsgDef.GuildPostCmd.GUILD_LEADER:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '会长才能申请城战。'))
            return
        # 判断时间是否满足
        if False == GuildModel.isCityWarApplyTime():
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '时间不对。'))
            return
        city_war_info = GlobalRecordModel.getGlobalRecordMgr().citywar_info
        if city_war_info.isInCityWarQueue(guildInfo.guildID):
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '已经在城战排队了。'))
            return

        if guildInfo.guildExp < 100000 and GuildModel.g_debugCityWar == False:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '军团资源不足100000。'))
            return

        guildInfo.guildExp -= 100000
        if guildInfo.guildExp < 0:
            guildInfo.guildExp = 0
        # 修改数据库
        DbService.getGuildService().updateGuild(guildInfo.guildID, guildInfo.guildExp, guildInfo.guildLevel)

        city_war_info.addCityWarQueue(guildInfo.guildID)
        GlobalRecordModel.getGlobalRecordMgr().updateCityWarInfo()

        retMsg = GuildModel.getGuildMgr().buildCityWarRetMsg(opstype)
        session.sendMsg(MsgDef.ClientCmd.GUILD_CITYWAR_OPS, retMsg)
        pass
    elif opstype == MsgDef.GuildCityWarOpsCmd.CITYWAR_LIST:
        ffext.dump('攻城战排队列表')
        retMsg = GuildModel.getGuildMgr().buildCityWarRetMsg(opstype, 0, 0, False, True)
        session.sendMsg(cmd, retMsg)
        pass
    elif opstype == MsgDef.GuildCityWarOpsCmd.CITYWAR_INFO:
        ffext.dump('城主信息等')
        retMsg = GuildModel.getGuildMgr().buildCityWarRetMsg(opstype, 0, 0, True, False)
        session.sendMsg(cmd, retMsg)
        pass
    elif opstype == MsgDef.GuildCityWarOpsCmd.CITYWAR_CANCEL:
        ffext.dump('取消申请')
        # 会长才能操作
        if guildInfo.getGuildMemberByUid(session.player.uid).post != MsgDef.GuildPostCmd.GUILD_LEADER:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '会长才能申请城战。'))
            return
        city_war_info = GlobalRecordModel.getGlobalRecordMgr().citywar_info
        if not city_war_info.isInCityWarQueue(guildInfo.guildID):
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '不在城战排队中。'))
            return

        city_war_info.removeCityWarQueue(guildInfo.guildID)
        GlobalRecordModel.getGlobalRecordMgr().updateCityWarInfo()

        retMsg = GuildModel.getGuildMgr().buildCityWarRetMsg(opstype)
        session.sendMsg(cmd, retMsg)
        pass
    return



#行会排名战
@ffext.onLogic(MsgDef.ClientCmd.GUILD_RANKWAR_OPS, MsgDef.GuildRankWarOpsReq)
def processGuildRankWar(session, msg):
    """
    rankWarInvited字段 0表示被邀请，1表示接受邀请，2表示拒绝邀请，3表示未被邀请，小于2的均表示还在接受邀请，属于5人里面
    rankWarApplied字段 0表示未申请，1表示已申请
    rankWarWin字段 0表示输，1表示赢，2,3,4表示第1,2,3名

    """

    opstype = msg.opstype
    cmd = MsgDef.ClientCmd.GUILD_RANKWAR_OPS
    player = session.player
    guildPost = player.guildCtrl.guildInfo.getGuildMemberByUid(player.uid).post
    retMsg = MsgDef.GuildRankWarOpsRet()

    if msg.opstype == MsgDef.GuildRankWarOpsCmd.RANKWAR_INVITE: #邀请成员
        if guildPost != MsgDef.GuildPostCmd.GUILD_LEADER:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '只有军团长才能邀请成员！'))
            return False
        def cb(ret):
            if not ret.result:
                return
            invitedNum = len(ret.result)
            if invitedNum >= 5:
                session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '只能邀请5个人！'))
                return False
            memberUid = msg.memberUid
            #更新邀请到期时间
            DbService.getGuildService().updateGuildRankWarInvitedOverTime(memberUid, ffext.getTime() + 24*60*60*1000)
            DbService.getGuildService().updateGuildRankWarInvited(memberUid, 0)
            memberSession = ffext.getSessionMgr().findByUid(memberUid)
            if memberSession:
                member = memberSession.player
                # 发送的消息包括 人物的职业，等级，战斗力和邀请状态
                retMsg.uid = member.uid
                retMsg.job = member.job
                retMsg.level = member.level
                retMsg.fightPower = member.fightPower
                retMsg.invitedStatus = 0
                session.sendMsg(cmd, retMsg)
            else:
                title = "军团排名战邀请"
                mailMsg = "军团长邀请您参加本周的行会排名战，您是否希望参加？是 否"
                player.mailCtrl.sendMail(memberUid, 1, title, mailMsg)
        DbService.getGuildService().queryGuildRankWarInvitedMember(player.guildCtrl.guildInfo.guildID, ffext.getTime(), cb)


    elif msg.opstype == MsgDef.GuildRankWarOpsCmd.RANKWAR_AGREE: #同意邀请
        if guildPost != MsgDef.GuildPostCmd.GUILD_LEADER:
            def cb(ret):
                if not ret.result:
                    return
                #比较时间
                invitedOverTime = ret.result[0][0]
                if invitedOverTime  < ffext.getTime():
                    session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '邀请超时！'))
                    DbService.getGuildService().updateGuildRankWarInvited(player.uid, 3)
                    return False
                DbService.getGuildService().updateGuildRankWarInvited(player.uid, 1)
                #发送的消息为同意
                retMsg.uid = player.uid
                retMsg.invitedStatus = 1
                session.sendMsg(cmd, retMsg)
            DbService.getGuildService().queryRankWarMember(player.uid, cb)


    elif msg.opstype == MsgDef.GuildRankWarOpsCmd.RANKWAR_REFUSE: #拒绝邀请
        if guildPost != MsgDef.GuildPostCmd.GUILD_LEADER:
            def cb(ret):
                if not ret.result:
                    return
                #比较时间
                invitedOverTime = ret.result[0][0]
                if invitedOverTime  < ffext.getTime():
                    session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '邀请超时！'))
                    DbService.getGuildService().updateGuildRankWarInvited(player.uid, 3)
                    return False
                DbService.getGuildService().updateGuildRankWarInvited(player.uid, 2)
                #发送的消息为拒绝
                retMsg.uid = player.uid
                retMsg.invitedStatus = 2
                session.sendMsg(cmd, retMsg)
            DbService.getGuildService().queryRankWarMember(player.uid, cb)


    elif msg.opstype == MsgDef.GuildRankWarOpsCmd.RANKWAR_DELETE: #删除成员
        if guildPost != MsgDef.GuildPostCmd.GUILD_LEADER:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '只有军团长才能删除参战成员！'))
            return False
        memberUid = msg.memberUid
        def cb(ret):
            if not ret.result:
                return
            DbService.getGuildService().updateGuildRankWarInvited(memberUid, 3)
            #发送的消息为邀请状态为3
            retMsg.uid = memberUid
            retMsg.invitedStatus = 3
            session.sendMsg(cmd, retMsg)
        DbService.getGuildService().queryRankWarMember(memberUid, cb)


    elif msg.opstype == MsgDef.GuildRankWarOpsCmd.RANKWAR_APPLY: #申请
        if guildPost != MsgDef.GuildPostCmd.GUILD_LEADER:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '只有军团长才能申请行会排名战！'))
            return False
        def cb(ret):
            if not ret.result:
                return
            guildRankWarNum = len(ret.result)
            if guildRankWarNum >= 32:
                session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '申请军团已达到上限！'))
                return False
            DbService.getGuildService().updateGuildRankWarApply(1, session.player.guildCtrl.guildInfo.guildID) #1表示已申请
            retMsg.applyStatus = 1
            retMsg.guildId = session.player.guildCtrl.guildInfo.guildID
        DbService.getGuildService().queryGuildApply(1, cb) #1表示已申请，0表示未申请


    elif msg.opstype == MsgDef.GuildRankWarOpsCmd.RANKWAR_START: #开始战斗

        #每次战斗最多10分钟，要设个定时器,完成以后timesleep2分钟

        def cb(ret):
            if not ret.result:
                return
            mapxy = [] #要传搜到的坐标集合 (mapname, x, y)
            teams = ret.result[0]
            new_teams = []
            i = 0
            while len(teams) > 1:
                team1 = teams.pop(0)
                team2 = teams.pop(0)
                mxy = mapxy[i]
                i += 1
                new_teams.append((team1, team2, mxy))
            if teams:
                team1 = teams.pop(0)
                team2 = None
                mxy = mapxy[i]
                new_teams.append((team1, team2, mxy))

            if len(new_teams) == 2:
                for team_pair in new_teams:
                    team1 = team_pair[0]
                    team2 = team_pair[1]
                    mxy = team_pair[2]
                    if not team2:
                        retMsg.winGuildId = team1
                        DbService.getGuildService().updateRankWarWin(1, team1)
                    else:
                        rankWarInfo = GuildModel.getGuildMgr().addRankWarVsInfo(team1, team2, mxy)
                        DbService.getGuildService().updateRankWarWin(4, rankWarInfo.getAnotherGuild(rankWarInfo.guildWin))
                return

            if len(new_teams) == 1:
                team_pair = new_teams[0]
                team1 = team_pair[0]
                team2 = team_pair[1]
                mxy = team_pair[2]
                if not team2:
                    retMsg.winGuildId = team1
                    DbService.getGuildService().updateRankWarWin(2, team1)
                else:
                    rankWarInfo = GuildModel.getGuildMgr().addRankWarVsInfo(team1, team2, mxy)
                    if rankWarInfo.guildWin:
                        DbService.getGuildService().updateRankWarWin(2, rankWarInfo.guildWin)
                        DbService.getGuildService().updateRankWarWin(3, rankWarInfo.getAnotherGuild(rankWarInfo.guildWin))
                    else:
                        DbService.getGuildService().updateRankWarWin(3, team1, team2)
                return

            for team_pair in new_teams:
                team1 = team_pair[0]
                team2 = team_pair[1]
                mxy = team_pair[2]
                if not team2:
                    retMsg.winGuildId = team1
                    DbService.getGuildService().updateRankWarWin(1, team1)
                else:
                    rankWarInfo = GuildModel.getGuildMgr().addRankWarVsInfo(team1, team2, mxy)

        DbService.getGuildService().queryRankWarWinTeam(1, cb) #win字段0表示输，1表示赢


    elif msg.opstype == MsgDef.GuildRankWarOpsCmd.RANKWAR_ENTER: #成员同意进入地图
        mapname = msg.cfgid
        mapObj = MapMgr.getMapMgr().allocMap(mapname)
        mapObj.playerEnterMap(session.player, msg.x, msg.y, True)


    elif msg.opstype == MsgDef.GuildRankWarOpsCmd.RANKWAR_FIGTHPOWER: #统计军团总战力
        def cb(ret):
            allFightPower = 0
            if not ret.result:
                return
            for row in ret.result:
                allFightPower += int(row[0])
            retMsg.guildId = msg.guildId
            retMsg.allFightPower = allFightPower
            session.sendMsg(cmd, retMsg)
        DbService.getGuildService().queryRankWarAllFightPower(msg.guildId, 1)