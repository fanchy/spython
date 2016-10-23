# -*- coding: utf-8 -*-
#本文件用于存放组队操作
import ffext
#调用msgtype中的ttypes文件，使用系统中的枚举函数
from msgtype import ttypes as MsgDef
#调用行会信息、组队信息
from model import TeamModel as TeamModel
from handler import SkillHandler
from db import DbService
from base import  Base

#队伍列表获取
@ffext.onLogic(MsgDef.ClientCmd.GET_TEAMLIST, MsgDef.TeamListMsgReq)
def processTeamList(session, msg):
    opstype             = msg.opstype
    ret_msg             = MsgDef.TeamListMsgRet()
    ret_msg.allTeamInfo = []
    ret_msg.opstype        = opstype
    teamID = session.player.teamCtrl.teamID
#获取队伍成员信息
    if opstype == MsgDef.TeamListClientCmd.GET_TEAMLIST:
        if 0 != teamID:
            #遍历allFriend字典，获取好友属性
            for uid, val in TeamModel.getTeamMgr().getTeamById(teamID).getTeamMember().iteritems():
                if teamID == val.uid:
                    leader = True
                else:
                    leader = False
                ret_msg.allTeamInfo.append(processTeamPlayerMsg(val.uid, val.name, val.job, val.gender, val.level, val.hp, val.hpMax, val.mp, val.mpMax, val.anger, val.angerMax,  leader))
        session.sendMsg(MsgDef.ServerCmd.TEAMLIST_MSG, ret_msg)
        return

#组队的操作信息
@ffext.onLogic(MsgDef.ClientCmd.TEAMLIST_OPS, MsgDef.TeamMsgReq)
def processTeamOps(session, msg):
    opstype = msg.opstype
    cmd     = MsgDef.ClientCmd.TEAMLIST_OPS
    uid     = msg.uid
    memberSession  = ffext.getSessionMgr().findByUid(uid)
    #邀请别人进行组队
    if opstype == MsgDef.TeamClientCmd.INVITE_ADD_TEAM:
        if not (processCheckAddTeam(session, memberSession, opstype, cmd) and processCheckMacTeamNum(session, memberSession, opstype, cmd)):
            return
        memberSession.sendMsg(MsgDef.ServerCmd.TEAM_MSG, processTeamPlayerMsgByPlayerRet(opstype, session.player, False))
    #同意别人邀请，进行组队
    if opstype == MsgDef.TeamClientCmd.VERIFY_INVIT_ADD_TEAM:
        if not (processCheckAddTeam(session, memberSession, opstype, cmd) and processCheckMacTeamNum(session, memberSession, opstype, cmd)):
            return
        #判断是加入队伍还是同意别人加入
        if 0 != session.player.teamCtrl.teamID:
            teamID = session.player.teamCtrl.teamID
            #同意别人加入
            memberSession.player.teamCtrl.setTeamID(teamID)
            #将用户信息广播给已有成员
            for key, val in TeamModel.getTeamMgr().getTeamById(teamID).getTeamMember().iteritems():
                teamMemberSession = ffext.getSessionMgr().findByUid(val.uid)
                if None != teamMemberSession:
                     teamMemberSession.sendMsg(MsgDef.ServerCmd.TEAM_MSG, processTeamPlayerMsgByPlayerRet(opstype, memberSession.player, False))
                if val.uid == teamID:
                    leader = True
                else:
                    leader = False
                memberSession.sendMsg(MsgDef.ServerCmd.TEAM_MSG, processTeamPlayerMsgByPlayerRet(opstype, val, leader))
            memberSession.player.teamCtrl.setTeamID(teamID)
            TeamModel.getTeamMgr().getTeamById(teamID).addTeamMember(memberSession.player)
        else:
            if 0 == memberSession.player.teamCtrl.teamID:
                #两人均没有队伍，给对方创建队伍，并任命对方为队长
                TeamModel.getTeamMgr().addTeam(memberSession.player)
                memberSession.player.teamCtrl.setTeamID(memberSession.player.uid)
            teamID = memberSession.player.teamCtrl.teamID
            #同意加入别人
            session.player.teamCtrl.setTeamID(teamID)
            #将用户信息广播给已有成员
            for key, val in TeamModel.getTeamMgr().getTeamById(teamID).getTeamMember().iteritems():
                teamMemberSession = ffext.getSessionMgr().findByUid(val.uid)
                if None != teamMemberSession:
                    teamMemberSession.sendMsg(MsgDef.ServerCmd.TEAM_MSG, processTeamPlayerMsgByPlayerRet(opstype, session.player, False))
                if val.uid == teamID:
                    leader = True
                else:
                    leader = False
                session.sendMsg(MsgDef.ServerCmd.TEAM_MSG, processTeamPlayerMsgByPlayerRet(opstype, val, leader))
            session.player.teamCtrl.setTeamID(teamID)
            TeamModel.getTeamMgr().getTeamById(teamID).addTeamMember(session.player)
        return
    #拒绝别人邀请
    if opstype == MsgDef.TeamClientCmd.REFUSE_INVITT_ADD_TEAM:
        memberSession   = ffext.getSessionMgr().findByUid(uid)
        #session.sendMsg(MsgDef.ServerCmd.TEAM_MSG, processTeamPlayerMsgRet(opstype, uid, '', 0, 0, 0, 0, 0, 0, 0, 0, 0, False))
        if None != memberSession:
            if session.player.uid == session.player.teamCtrl.teamID:
                leader = True
            else:
                leader = False
            memberSession.sendMsg(MsgDef.ServerCmd.TEAM_MSG, processTeamPlayerMsgByPlayerRet(opstype, session.player, leader))
        return
    #删除队友CONFIRM_INVIT_ADD_BROTHER
    if opstype == MsgDef.TeamClientCmd.DEL_TEAMPLAYER:
        teamID = session.player.teamCtrl.teamID
        if  session.player.uid != teamID:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '您不是队长，进行队伍成员操作'))
            return
        if session.player.uid == uid:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '不能对自己进行操作，如想退出队伍，请使用退出队伍选项'))
            return
        #判断用户是否在队伍中(理论上应该客户端判断)
        if None == TeamModel.getTeamMgr().getTeamById(teamID).getTeamMemberByUid(uid):
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '用户不在队伍中，无法删除。'))
            return
        #将队友从session中删除
        TeamModel.getTeamMgr().getTeamById(teamID).delTeamMember(uid)
        if None != memberSession:
            memberSession.player.teamCtrl.setTeamID(0)
            memberSession.sendMsg(MsgDef.ServerCmd.TEAM_MSG, processTeamPlayerMsgByPlayerRet(opstype, session.player, True))
        for key, val in TeamModel.getTeamMgr().getTeamById(teamID).getTeamMember().iteritems():
            teamMemberSession = ffext.getSessionMgr().findByUid(val.uid)
            if None != teamMemberSession:
                teamMemberSession.sendMsg(MsgDef.ServerCmd.TEAM_MSG, processTeamPlayerMsgByPlayerRet(opstype, memberSession.player, False))
        return
#退出组队（用户下线时也执行相同代码，如）
    if opstype == MsgDef.TeamClientCmd.QUIT_TEAM:
        teamID = session.player.teamCtrl.teamID
        #判断自己是否加入队伍(理论上应该客户端判断teamID=0，不需要给客户端返回语句)
        if 0 == teamID:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG,  processErrorMsgRet(opstype, cmd, '没有队伍，不需要退出。'))
            return
        #判断自己是否为队长(队长退出时默认为队伍解散)
        if  session.player.uid == teamID:
            for key, val in TeamModel.getTeamMgr().getTeamById(teamID).getTeamMember().iteritems():
                teamMemberSession = ffext.getSessionMgr().findByUid(val.uid)
                if None != teamMemberSession:
                    teamMemberSession.player.teamCtrl.setTeamID(0)
                    teamMemberSession.sendMsg(MsgDef.ServerCmd.TEAM_MSG, processTeamPlayerMsgByPlayerRet(opstype, session.player, True))
            TeamModel.getTeamMgr().delTeam(teamID)
        else:
            for key, val in TeamModel.getTeamMgr().getTeamById(teamID).getTeamMember().iteritems():
                teamMemberSession = ffext.getSessionMgr().findByUid(val.uid)
                if None != teamMemberSession:
                    teamMemberSession.sendMsg(MsgDef.ServerCmd.TEAM_MSG, processTeamPlayerMsgByPlayerRet(opstype, session.player, False))
            TeamModel.getTeamMgr().getTeamById(teamID).delTeamMember(session.player.uid)
            session.player.teamCtrl.setTeamID(0)
        return
    #更换队长
    if opstype == MsgDef.TeamClientCmd.REPLACE_TEAMLEADER:
        teamID = session.player.teamCtrl.teamID
        if  session.player.uid != teamID:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '您不是队长，无权进行更换队长操作'))
            return
        if None == TeamModel.getTeamMgr().getTeamById(teamID).getTeamMemberByUid(uid):
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '新任命的队长不在队伍中，无法任命'))
            return
        #向所有队员广播变更队长消息
        for key, val in TeamModel.getTeamMgr().getTeamById(teamID).getTeamMember().iteritems():
            teamMemberSession = ffext.getSessionMgr().findByUid(val.uid)
            if None != teamMemberSession:
                teamMemberSession.player.teamCtrl.setTeamID(uid)
                teamMemberSession.sendMsg(MsgDef.ServerCmd.TEAM_MSG, processTeamPlayerMsgRet(opstype, uid,  '', 0, 0, 0, 0, 0, 0, 0, 0, 0, False))
        #变更session中存储的队长
        TeamModel.getTeamMgr().setTeamLeader(teamID, uid)
        return

def processCheckAddTeam(session, memberSession, opstype, cmd):
    if None == memberSession:
        session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '对方不在线，不能进行邀请组队！'))
        return False
    if  0 != session.player.teamCtrl.teamID and 0 != memberSession.player.teamCtrl.teamID:
        session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '对方和您都拥有队伍，不能进行组队'))
        return False
    if  0 != session.player.teamCtrl.teamID and session.player.uid != session.player.teamCtrl.teamID:
        session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '您不是队长，不能对方进行组队'))
        return False
    if  0 != memberSession.player.teamCtrl.teamID and memberSession.player.uid != memberSession.player.teamCtrl.teamID:
        session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '对方不是队长，如想加入队伍，请联系对方队长'))
        return False
    return True
def processCheckMacTeamNum(session, memberSession, opstype, cmd):
    if  session.player.uid == session.player.teamCtrl.teamID and TeamModel.getTeamMgr().getTeamById(session.player.teamCtrl.teamID).getLenTeamMember() >= TeamModel.MAX_TEAM_NUM:
        session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '您的队伍已满，不能再加入队员'))
        return False
    if  memberSession.player.uid == memberSession.player.teamCtrl.teamID and TeamModel.getTeamMgr().getTeamById(memberSession.player.teamCtrl.teamID).getLenTeamMember() >= TeamModel.MAX_TEAM_NUM:
        session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '对方的队伍已满，不能再加入队员'))
        return False
    return True
def processTeamPlayerMsg(uid, name, job, gender, level, hp, hpMax, mp, mpMax, anger, angerMax,  leader):
    ret_msg = MsgDef.TeamPlayerMsg()
    ret_msg.uid         = uid
    ret_msg.name        = name
    ret_msg.job         = job
    ret_msg.gender      = gender
    ret_msg.level       = level
    ret_msg.hp          = hp
    ret_msg.hpMax       = hpMax
    ret_msg.mp          = mp
    ret_msg.mpMax       = mpMax
    ret_msg.anger       = anger
    ret_msg.angerMax    = angerMax
    ret_msg.leader      = leader
    return ret_msg
def processTeamPlayerMsgByPlayerRet(opstype, player, leader):
    ret_msg = MsgDef.TeamMsgRet()
    ret_msg.opstype     = opstype
    ret_msg.uid         = player.uid
    ret_msg.name        = player.name
    ret_msg.job         = player.job
    ret_msg.gender      = player.gender
    ret_msg.level       = player.level
    ret_msg.hp          = player.hp
    ret_msg.hpMax       = player.hpMax
    ret_msg.mp          = player.mp
    ret_msg.mpMax       = player.mpMax
    ret_msg.anger       = player.anger
    ret_msg.angerMax    = player.angerMax
    ret_msg.leader      = leader
    return ret_msg
def processTeamPlayerMsgRet(opstype, uid, name, job, gender, level, hp, hpMax, mp, mpMax, anger, angerMax, leader):
    ret_msg = MsgDef.TeamMsgRet()
    ret_msg.uid         = uid
    ret_msg.name        = name
    ret_msg.job         = job
    ret_msg.gender      = gender
    ret_msg.level       = level
    ret_msg.hp          = hp
    ret_msg.hpMax       = hpMax
    ret_msg.mp          = mp
    ret_msg.mpMax       = mpMax
    ret_msg.anger       = anger
    ret_msg.angerMax    = angerMax
    ret_msg.leader      = leader
    return ret_msg
#用于返回错误信息的函数
def processErrorMsgRet(opstype, cmd, msg):
    ret_msg                 = MsgDef.ErrorMsgRet()
    ret_msg.errType         = opstype                        #错误信息所处位置opstype
    ret_msg.cmd             = cmd                               #错误信息所处位置cmd
    ret_msg.errMsg          = msg                               #错误信息
    return ret_msg

def sendBroList(session, opstype = MsgDef.BrotherClientCmd.GET_BROTHERLIST):
    allBrotherInfo = []
    #先判断用户是否有结义
    brotherInfo = session.player.brotherCtrl.brotherInfo
    if None == brotherInfo:
        session.sendMsg(MsgDef.ServerCmd.BROTHER_OPS_MSG, processBrotherOpsMsgRet(opstype, session.player, [], True, 0))
        return
    for key, val in brotherInfo.getBrotherMember().iteritems():
        memberSession   = ffext.getSessionMgr().findByUid(val.uid)
        if None == memberSession:
            online = False
        else:
            online = True
        allBrotherInfo.append(processBrotherOpsMsg(val, online))
    if brotherInfo.flag:
        delBrotherTime = 0
    else:
        delBrotherTime = brotherInfo.getBrotherExtraByKey('delTime')
    session.sendMsg(MsgDef.ServerCmd.BROTHER_OPS_MSG, processBrotherOpsMsgRet(opstype, session.player, allBrotherInfo, brotherInfo.flag, delBrotherTime))
#结义的操作信息
def checkPlayerCanBeBro(opstype, player, player1, player2):
    cmd = MsgDef.ClientCmd.BROTHER_OPS
    if not player1:
        player.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, 'player1没有在线!'))
        return False
    if not player2:
        player.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, 'player2没有在线!'))
        return False
    if player.brotherCtrl.brotherInfo != None:
        player.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '你当前已经结义!'))
        return False
    if player1.brotherCtrl.brotherInfo != None:
        player.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '%s当前已经结义!'%(player1.name)))
        return False
    if player2.brotherCtrl.brotherInfo != None:
        player.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '%s当前已经结义!' % (player2.name)))
        return False
    return True
@ffext.onLogic(MsgDef.ClientCmd.BROTHER_OPS, MsgDef.BrotherOpsReq)
def processBrotherOps(session, msg):#0表示邀请别人一起结义
    opstype = msg.opstype
    cmd     = MsgDef.ClientCmd.BROTHER_OPS
    #ffext.dump('processBrotherrOps', msg)
    player = session.player

    uid = player.uid
    uid1 = msg.uid1
    uid2 = msg.uid2

    if opstype == MsgDef.BrotherClientCmd.INVITE_ADD_BROTHER:
        #获取用户邀请结义的ID
        player2 = player.mapObj.getPlayerById(uid1)
        player3 = player.mapObj.getPlayerById(uid2)
        if False == checkPlayerCanBeBro(opstype, player, player2, player3):
            return False
        brotherInfo = TeamModel.BrotherCtrl()
        brotherInfo.addBrotherMember(player, player2, player3)
        player.brotherCtrl.tmpBrotherInfo = brotherInfo
        player2.brotherCtrl.tmpBrotherInfo = brotherInfo
        player3.brotherCtrl.tmpBrotherInfo = brotherInfo
        #将邀请信息发给对方
        allBrotherInfo = []
        allBrotherInfo.append(processBrotherOpsMsg(player, True))
        allBrotherInfo.append(processBrotherOpsMsg(player2, True))
        allBrotherInfo.append(processBrotherOpsMsg(player3, True))
        session.sendMsg(MsgDef.ServerCmd.BROTHER_OPS_MSG, processBrotherOpsMsgRet(opstype, player, allBrotherInfo, True, 0))
        player2.sendMsg(MsgDef.ServerCmd.BROTHER_OPS_MSG, processBrotherOpsMsgRet(opstype, player, allBrotherInfo, True, 0))
        player3.sendMsg(MsgDef.ServerCmd.BROTHER_OPS_MSG, processBrotherOpsMsgRet(opstype, player, allBrotherInfo, True, 0))

        brotherInfo.getMemberInfo(player.uid).status = TeamModel.BrotherStatus.BRO_VERIFY_INVIT #自动确认
        return
    if msg.opstype == MsgDef.BrotherClientCmd.VERIFY_INVIT_ADD_BROTHER:
        brotherInfo = player.brotherCtrl.tmpBrotherInfo
        if not brotherInfo:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '结义状态已经解除。'))
            return
        playerList = brotherInfo.getPlayers()
        player1 = playerList[0]
        player2= playerList[1]
        player3= playerList[2]

        if False == checkPlayerCanBeBro(opstype, player1, player2, player3):
            return False

        brotherInfo.getMemberInfo(player.uid).status = TeamModel.BrotherStatus.BRO_VERIFY_INVIT
        player1.sendMsg(MsgDef.ServerCmd.BROTHER_OPS_MSG, processBrotherOpsMsgRet(opstype, player, [], True, 0))
        player2.sendMsg(MsgDef.ServerCmd.BROTHER_OPS_MSG, processBrotherOpsMsgRet(opstype, player, [], True, 0))
        player3.sendMsg(MsgDef.ServerCmd.BROTHER_OPS_MSG, processBrotherOpsMsgRet(opstype, player, [], True, 0))
        return
    if msg.opstype == MsgDef.BrotherClientCmd.REFUSE_INVITT_ADD_BROTHER:
        brotherInfo = player.brotherCtrl.tmpBrotherInfo
        if not brotherInfo:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '结义状态已经解除。'))
            return
        playerList = brotherInfo.getPlayers()

        for k in playerList:
            if k:
                k.brotherCtrl.tmpBrotherInfo = None
            k.sendMsg(MsgDef.ServerCmd.BROTHER_OPS_MSG, processBrotherOpsMsgRet(opstype, player, [], True, 0))
        return
    #用户确认结义
    if msg.opstype == MsgDef.BrotherClientCmd.CONFIRM_INVIT_ADD_BROTHER:
        brotherInfo = player.brotherCtrl.tmpBrotherInfo
        if not brotherInfo:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '结义状态已经解除。'))
            return
        playerList = brotherInfo.getPlayers()
        player1 = playerList[0]
        player2 = playerList[1]
        player3 = playerList[2]

        brotherInfo.getMemberInfo(player.uid).status = TeamModel.BrotherStatus.BRO_CONFIRM
        player1.sendMsg(MsgDef.ServerCmd.BROTHER_OPS_MSG, processBrotherOpsMsgRet(opstype, player, [], True, 0))
        player2.sendMsg(MsgDef.ServerCmd.BROTHER_OPS_MSG, processBrotherOpsMsgRet(opstype, player, [], True, 0))
        player3.sendMsg(MsgDef.ServerCmd.BROTHER_OPS_MSG, processBrotherOpsMsgRet(opstype, player, [], True, 0))

        allConfirm = True
        for k in playerList:
            if k == None or brotherInfo.getMemberInfo(k.uid).status != TeamModel.BrotherStatus.BRO_CONFIRM:
                allConfirm = False
                break
        if allConfirm:
            bid = TeamModel.getBrotherMgr().addBrotherInfo(brotherInfo)
            player1.brotherCtrl.tmpBrotherInfo = None
            player2.brotherCtrl.tmpBrotherInfo = None
            player3.brotherCtrl.tmpBrotherInfo = None

            player1.brotherCtrl.brotherInfo = brotherInfo
            player2.brotherCtrl.brotherInfo = brotherInfo
            player3.brotherCtrl.brotherInfo = brotherInfo

            sendBroList(player1.session)
            sendBroList(player2.session)
            sendBroList(player3.session)
        return
    #用户强制退出结义
    if opstype == MsgDef.BrotherClientCmd.QUIT_BROTHER:
        #先判断用户是否有结义
        brotherInfo = session.player.brotherCtrl.brotherInfo
        if None == brotherInfo:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '用户没有结义信息。'))
            return
        if session.player.gold < TeamModel.BROTHER_QUIT_GOLD:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '金钱不足，不能强制退出。'))
            return
        #扣除金钱
        session.player.addGold(-1 * TeamModel.BROTHER_QUIT_GOLD)
        bid = brotherInfo.bid
        for key, val in brotherInfo.getBrotherMember().iteritems():
            memberSession   = ffext.getSessionMgr().findByUid(val.uid)
            memberSession.player.skillCtrl.deleteSkill(Base.BRO_SKILL_ID, True)
            SkillHandler.processQuerySkill(memberSession)
            if None != memberSession:
                memberSession.sendMsg(MsgDef.ServerCmd.BROTHER_OPS_MSG, processBrotherOpsMsgRet(opstype, session.player, [], True, 0))
                memberSession.player.brotherCtrl.delBrother(memberSession.player)
                if val.uid == session.player.uid:
                    continue
                else:
                    memberSession.player.addGold(int(TeamModel.BROTHER_QUIT_GOLD/2))
            else:
                DbService.getPlayerService().updateGold(val, int(TeamModel.BROTHER_QUIT_GOLD/2))
        TeamModel.getBrotherMgr().delBrother(bid)

        return
    #发送结义列表

    if opstype == MsgDef.BrotherClientCmd.GET_BROTHERLIST:
        sendBroList(session, opstype)
        return
    #用户协商退出结义（必须三个人同时在线）
    if opstype == MsgDef.BrotherClientCmd.CONSULT_QUIT_BROTHER:
        #先判断用户是否有结义
        brotherInfo = session.player.brotherCtrl.brotherInfo
        if None == brotherInfo:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '用户没有结义信息。'))
            return
        #判断三个人是否同时在线
        for key, val in brotherInfo.getBrotherMember().iteritems():
            memberSession   = ffext.getSessionMgr().findByUid(val.uid)
            if None == memberSession:
                session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '用户协议取消结义时，必须同时在线！'))
                return
        brotherInfo.getMemberInfo(player.uid).status = TeamModel.BrotherStatus.BRO_QUIT
        allQuit = True
        for key, val in brotherInfo.getBrotherMember().iteritems():
            if val.status != TeamModel.BrotherStatus.BRO_QUIT:
                allQuit = False
                break
        delTime = 0
        delTimeSec = 1
        if allQuit:
            delTime = ffext.getTime() + delTimeSec
        for key, val in brotherInfo.getBrotherMember().iteritems():
            memberSession = ffext.getSessionMgr().findByUid(val.uid)
            memberSession.player.skillCtrl.deleteSkill(Base.BRO_SKILL_ID, True)
            SkillHandler.processQuerySkill(memberSession)
            memberSession.sendMsg(MsgDef.ServerCmd.BROTHER_OPS_MSG, processBrotherOpsMsgRet(opstype, player, [], False, delTime))

        if allQuit:
            def cb():
                processBrotherDel(session, opstype)
                return
            ffext.timer(delTimeSec * 1000, cb)
        return
    #用户取消退出结义
    if opstype == MsgDef.BrotherClientCmd.CANCLE_QUIT_BROTHER:
        #先判断用户是否有结义
        brotherInfo = session.player.brotherCtrl.brotherInfo
        if None == brotherInfo:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '用户没有结义信息。'))
            return
        if brotherInfo.getMemberInfo(player.uid).status != TeamModel.BrotherStatus.BRO_QUIT:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '不需要取消。'))
            return
        brotherInfo.getMemberInfo(player.uid).status = TeamModel.BrotherStatus.BRO_OK
        for key, val in brotherInfo.getBrotherMember().iteritems():
            memberSession   = ffext.getSessionMgr().findByUid(val.uid)
            if None != memberSession:
                memberSession.sendMsg(MsgDef.ServerCmd.BROTHER_OPS_MSG, processBrotherOpsMsgRet(opstype, session.player, [], True, 0))
        return
    elif opstype == MsgDef.BrotherClientCmd.LEARN_BRO_SKILL:#9学习结义技能
        brotherInfo = session.player.brotherCtrl.brotherInfo
        if None == brotherInfo:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '用户没有结义信息。'))
            return
        skillLevel = 1
        retErr = player.skillCtrl.learnSkill(Base.BRO_SKILL_ID, skillLevel)#
        if retErr:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '学习技能%d失败，原因:%s!' % (Base.BRO_SKILL_ID, retErr)))
            return
        session.sendMsg(MsgDef.ServerCmd.LEARN_SKILL, MsgDef.LearnSkillRet(Base.BRO_SKILL_ID, skillLevel))
        session.sendMsg(MsgDef.ServerCmd.BROTHER_OPS_MSG, processBrotherOpsMsgRet(opstype, player, [], False, 0))

#@ffext.onLogic(MsgDef.ClientCmd.BROTHER_OPS, MsgDef.BrotherOpsReq)
def processBrotherOps2(session, msg):#0表示邀请别人一起结义
    opstype = msg.opstype
    cmd     = MsgDef.ClientCmd.BROTHER_OPS
    #ffext.dump('processBrotherrOps', msg)
    if opstype == MsgDef.BrotherClientCmd.INVITE_ADD_BROTHER:
        #获取用户邀请结义的ID
        uid1                = msg.uid1
        uid2                = msg.uid2
        uid                 = session.player.uid
        memberSession1      = ffext.getSessionMgr().findByUid(uid1)
        memberSession2      = ffext.getSessionMgr().findByUid(uid2)
        #判断用户是否满足结义条件
        if not processCheckAddBrother(session, memberSession1, memberSession2, opstype, cmd):
            return
        if TeamModel.BrotherFlag.flag1 != session.player.brotherCtrl.brotherFlag or TeamModel.BrotherFlag.flag1 != memberSession1.player.brotherCtrl.brotherFlag or TeamModel.BrotherFlag.flag1 != memberSession2.player.brotherCtrl.brotherFlag:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '用户不满足结义条件。'))
            return
        #执行邀请代码，将用户加入至待验证列表
        session.player.brotherCtrl.AddBrotherInviter(uid1,  uid2)
        memberSession1.player.brotherCtrl.AddBrotherInviter(uid,  uid2)
        memberSession2.player.brotherCtrl.AddBrotherInviter(uid1,  uid)
        #将邀请信息发给对方
        allBrotherInfo = []
        allBrotherInfo.append(processBrotherOpsMsg(session.player, True))
        allBrotherInfo.append(processBrotherOpsMsg(memberSession1.player, True))
        allBrotherInfo.append(processBrotherOpsMsg(memberSession2.player, True))
        session.sendMsg(MsgDef.ServerCmd.BROTHER_OPS_MSG, processBrotherOpsMsgRet(opstype, session.player, allBrotherInfo, True, 0))
        memberSession1.sendMsg(MsgDef.ServerCmd.BROTHER_OPS_MSG, processBrotherOpsMsgRet(opstype, session.player, allBrotherInfo, True, 0))
        memberSession2.sendMsg(MsgDef.ServerCmd.BROTHER_OPS_MSG, processBrotherOpsMsgRet(opstype, session.player, allBrotherInfo, True, 0))
        #15秒后如果用户未确定结义状态改变，则将结义状态初始化（以后添加）
        def cb():
            processBrotherDelay(session, TeamModel.BrotherFlag.flag2, opstype, cmd, '存在用户未及时同意结义，所有结义归零')
            return
        #ffext.timer(15 * 1000, cb)
        return
    if msg.opstype == MsgDef.BrotherClientCmd.VERIFY_INVIT_ADD_BROTHER:
        #判断用户是否满足结义条件
        memberSession1      = ffext.getSessionMgr().findByUid(session.player.brotherCtrl.inviter[0])
        memberSession2      = ffext.getSessionMgr().findByUid(session.player.brotherCtrl.inviter[1])
        if not processCheckAddBrother(session, memberSession1, memberSession2, opstype, cmd):
            return
        #同意结义
        session.player.brotherCtrl.verifyBrotherInviter()
        session.sendMsg(MsgDef.ServerCmd.BROTHER_OPS_MSG, processBrotherOpsMsgRet(opstype, session.player, [], True, 0))
        memberSession1.sendMsg(MsgDef.ServerCmd.BROTHER_OPS_MSG, processBrotherOpsMsgRet(opstype, session.player, [], True, 0))
        memberSession2.sendMsg(MsgDef.ServerCmd.BROTHER_OPS_MSG, processBrotherOpsMsgRet(opstype, session.player, [], True, 0))
        #15秒后如果用户未确定结义状态改变，则将结义状态初始化（以后添加）
        def cb():
            processBrotherDelay(session, TeamModel.BrotherFlag.flag3, opstype, cmd, '存在用户未及时确认结义，所有结义归零')
            return
        #ffext.timer(15 * 1000, cb)
        return
    if msg.opstype == MsgDef.BrotherClientCmd.REFUSE_INVITT_ADD_BROTHER:
        #此处应判断是否满足同意结义的条件
        #拒绝结义
        memberSession1      = ffext.getSessionMgr().findByUid(session.player.brotherCtrl.inviter[0])
        memberSession2      = ffext.getSessionMgr().findByUid(session.player.brotherCtrl.inviter[1])
        session.player.brotherCtrl.refuseBrotherInviter()
        session.sendMsg(MsgDef.ServerCmd.BROTHER_OPS_MSG, processBrotherOpsMsgRet(opstype, session.player, [], True, 0))
        memberSession1.player.brotherCtrl.refuseBrotherInviter()
        memberSession1.sendMsg(MsgDef.ServerCmd.BROTHER_OPS_MSG, processBrotherOpsMsgRet(opstype, session.player, [], True, 0))
        memberSession2.player.brotherCtrl.refuseBrotherInviter()
        memberSession2.sendMsg(MsgDef.ServerCmd.BROTHER_OPS_MSG, processBrotherOpsMsgRet(opstype, session.player, [], True, 0))
        return
    #用户确认结义
    if msg.opstype == MsgDef.BrotherClientCmd.CONFIRM_INVIT_ADD_BROTHER:
        #判断用户是否满足结义条件
        memberSession1      = ffext.getSessionMgr().findByUid(session.player.brotherCtrl.inviter[0])
        memberSession2      = ffext.getSessionMgr().findByUid(session.player.brotherCtrl.inviter[1])
        if not processCheckAddBrother(session, memberSession1, memberSession2, opstype, cmd):
            return
        if TeamModel.BrotherFlag.flag4 != session.player.brotherCtrl.brotherFlag:
            session.player.brotherCtrl.confirmBrotherInviter()
            session.sendMsg(MsgDef.ServerCmd.BROTHER_OPS_MSG, processBrotherOpsMsgRet(opstype, session.player, [], True, 0))
            memberSession1.sendMsg(MsgDef.ServerCmd.BROTHER_OPS_MSG, processBrotherOpsMsgRet(opstype, session.player, [], True, 0))
            memberSession2.sendMsg(MsgDef.ServerCmd.BROTHER_OPS_MSG, processBrotherOpsMsgRet(opstype, session.player, [], True, 0))
        if TeamModel.BrotherFlag.flag4 == memberSession1.player.brotherCtrl.brotherFlag and TeamModel.BrotherFlag.flag4 == memberSession2.player.brotherCtrl.brotherFlag:
            bid = TeamModel.getBrotherMgr().addBrotherList(session.player, memberSession1.player, memberSession2.player)
            session.player.brotherCtrl.AddBrother(bid)
            memberSession1.player.brotherCtrl.AddBrother(bid)
            memberSession2.player.brotherCtrl.AddBrother(bid)
            sendBroList(session)
            sendBroList(memberSession1)
            sendBroList(memberSession2)
        return
    #用户强制退出结义
    if opstype == MsgDef.BrotherClientCmd.QUIT_BROTHER:
        #先判断用户是否有结义
        brotherInfo = session.player.brotherCtrl.brotherInfo
        if None == brotherInfo:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '用户没有结义信息。'))
            return
        if session.player.gold < TeamModel.BROTHER_QUIT_GOLD:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '金钱不足，不能强制退出。'))
            return
        #扣除金钱
        session.player.addGold(- TeamModel.BROTHER_QUIT_GOLD)
        bid = brotherInfo.bid
        for key, val in brotherInfo.getBrotherMember().iteritems():
            memberSession   = ffext.getSessionMgr().findByUid(val.uid)
            if None != memberSession:
                memberSession.sendMsg(MsgDef.ServerCmd.BROTHER_OPS_MSG, processBrotherOpsMsgRet(opstype, session.player, [], True, 0))
                memberSession.player.brotherCtrl.delBrother(memberSession.player)
                if val.uid == session.player.uid:
                    continue
                else:
                    memberSession.player.addGold(TeamModel.BROTHER_QUIT_GOLD/2)
            else:
                DbService.getPlayerService().updateGold(val, TeamModel.BROTHER_QUIT_GOLD/2)
        TeamModel.getBrotherMgr().delBrother(bid)
        return
    #发送结义列表

    if opstype == MsgDef.BrotherClientCmd.GET_BROTHERLIST:
        sendBroList(session, opstype)
        return
    #用户协商退出结义（必须三个人同时在线）
    if opstype == MsgDef.BrotherClientCmd.CONSULT_QUIT_BROTHER:
        #先判断用户是否有结义
        brotherInfo = session.player.brotherCtrl.brotherInfo
        if None == brotherInfo:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '用户没有结义信息。'))
            return
        #判断三个人是否同时在线
        for key, val in brotherInfo.getBrotherMember().iteritems():
            memberSession   = ffext.getSessionMgr().findByUid(val.uid)
            if None == memberSession:
                session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '用户协议取消结义时，必须同时在线！'))
                return
        if TeamModel.BrotherFlag.flag5 != session.player.brotherCtrl.brotherFlag:
            session.player.brotherCtrl.consultBrotherQuit()
            for key, val in brotherInfo.getBrotherMember().iteritems():
                memberSession   = ffext.getSessionMgr().findByUid(val.uid)
                memberSession.sendMsg(MsgDef.ServerCmd.BROTHER_OPS_MSG, processBrotherOpsMsgRet(opstype, session.player, [], False, 0))
        for key, val in brotherInfo.getBrotherMember().iteritems():
            memberSession   = ffext.getSessionMgr().findByUid(val.uid)
            if TeamModel.BrotherFlag.flag5 != memberSession.player.brotherCtrl.brotherFlag:
                return
        delTimeSec = 1
        #修改结义状态
        time = ffext.getTime() + delTimeSec
		#time = ffext.getTime() + 2 * 3600 * 24
        session.player.brotherCtrl.brotherInfo.addTime(time)
        for key, val in brotherInfo.getBrotherMember().iteritems():
            memberSession   = ffext.getSessionMgr().findByUid(val.uid)
            memberSession.sendMsg(MsgDef.ServerCmd.BROTHER_OPS_MSG, processBrotherOpsMsgRet(opstype, session.player, [], False, time))
        def cb():
            processBrotherDel(session, opstype)
            return
        ffext.timer(1 * 1000, cb)
		#ffext.timer(2 * 3600 * 24 * 1000, cb)
        return
    #用户取消退出结义
    if opstype == MsgDef.BrotherClientCmd.CANCLE_QUIT_BROTHER:
        #先判断用户是否有结义
        brotherInfo = session.player.brotherCtrl.brotherInfo
        if None == brotherInfo:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '用户没有结义信息。'))
            return
        #判断是否需要取消
        if brotherInfo.flag:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '用户没有协议解除结义信息。'))
            return
        brotherInfo.flag = True
        for key, val in brotherInfo.getBrotherMember().iteritems():
            memberSession   = ffext.getSessionMgr().findByUid(val.uid)
            if None != memberSession:
                memberSession.sendMsg(MsgDef.ServerCmd.BROTHER_OPS_MSG, processBrotherOpsMsgRet(opstype, session.player, [], True, 0))
                memberSession.player.brotherCtrl.brotherFlag = TeamModel.BrotherFlag.flag4
        #将倒计时数据从数据库中和session中删除
        brotherInfo.delTime()
        return
def processBrotherDownline(session):
    #先判断用户是否有结义,没有结义，要判断用户是否有结义申请。有结义申请，调用结义申请归置函数
    brotherInfo = session.player.brotherCtrl.brotherInfo
    if None == brotherInfo:
        brotherInfo = session.player.brotherCtrl.tmpBrotherInfo
        allPlayers = brotherInfo.getPlayers()
        for k in allPlayers:
            if k:
                k.brotherCtrl.tmpBrotherInfo = None
                k.sendMsg(MsgDef.ServerCmd.BROTHER_OPS_MSG, processBrotherOpsMsgRet(MsgDef.BrotherClientCmd.DOWN_LINE_BROTHER, session.player, [], True, 0))
                k.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(MsgDef.BrotherClientCmd.DOWN_LINE_BROTHER, MsgDef.ServerCmd.BROTHER_OPS_MSG, '%s下线，结义状态解除。'%(session.player.name)))
        return
    #用户有结义信息，在下线的时候，刷新session中存储的用户信息
    for key, val in brotherInfo.getBrotherMember().iteritems():
        if session.player.uid == val.uid:
            val.level = session.player.level
        else:
            memberSession1      = ffext.getSessionMgr().findByUid(val.uid)
            if memberSession1:
                memberSession1.sendMsg(MsgDef.ServerCmd.BROTHER_OPS_MSG, processBrotherOpsMsgRet(MsgDef.BrotherClientCmd.DOWN_LINE_BROTHER, session.player, [], False, 0))
            
def processBrotherDownline2(session):
    #先判断用户是否有结义,没有结义，要判断用户是否有结义申请。有结义申请，调用结义申请归置函数
    brotherInfo = session.player.brotherCtrl.brotherInfo
    if None == brotherInfo:
        if TeamModel.BrotherFlag.flag1 == session.player.brotherCtrl.brotherFlag:
            return
        memberSession1      = ffext.getSessionMgr().findByUid(session.player.brotherCtrl.inviter[0])
        memberSession2      = ffext.getSessionMgr().findByUid(session.player.brotherCtrl.inviter[1])
        memberSession1.player.brotherCtrl.refuseBrotherInviter()
        memberSession1.sendMsg(MsgDef.ServerCmd.BROTHER_OPS_MSG, processBrotherOpsMsgRet(MsgDef.BrotherClientCmd.DOWN_LINE_BROTHER, session.player, [], True, 0))
        memberSession2.player.brotherCtrl.refuseBrotherInviter()
        memberSession2.sendMsg(MsgDef.ServerCmd.BROTHER_OPS_MSG, processBrotherOpsMsgRet(MsgDef.BrotherClientCmd.DOWN_LINE_BROTHER, session.player, [], True, 0))
        return
    #用户有结义信息，在下线的时候，刷新session中存储的用户信息
    for key, val in brotherInfo.getBrotherMember().iteritems():
        if session.player.uid == val.uid:
            val.level = session.player.level
            return
#当用户没有及时同意结义时相应的代码VERIFY_INVIT_ADD_BROTHER
def processBrotherDelay(session, flag, opstype, cmd, ret_msg):
    #先判断用户是否及时同意结义（三个用户，存在有人结义状态仍然为1）
    #获取结义中三个玩家的session
    memberSession1      = ffext.getSessionMgr().findByUid(session.player.brotherCtrl.inviter[0])
    memberSession2      = ffext.getSessionMgr().findByUid(session.player.brotherCtrl.inviter[1])
    if flag == session.player.brotherCtrl.brotherFlag or flag == memberSession1.player.brotherCtrl.brotherFlag or flag == memberSession2.player.brotherCtrl.brotherFlag:
        session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, ret_msg))
        memberSession1.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, ret_msg))
        memberSession2.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, ret_msg))
        session.player.brotherCtrl.refuseBrotherInviter()
        memberSession1.player.brotherCtrl.refuseBrotherInviter()
        memberSession2.player.brotherCtrl.refuseBrotherInviter()
    return

#当用户没有及时同意结义时相应的代码VERIFY_INVIT_ADD_BROTHER
def processBrotherDel(session, opstype):
    brotherInfo = session.player.brotherCtrl.brotherInfo
    #if brotherInfo.flag:
    #    return
    for key, val in brotherInfo.getBrotherMember().iteritems():
            memberSession   = ffext.getSessionMgr().findByUid(val.uid)
            if None != memberSession:
                memberSession.player.brotherCtrl.delBrother(memberSession.player)
                memberSession.sendMsg(MsgDef.ServerCmd.BROTHER_OPS_MSG, processBrotherOpsMsgRet(opstype, memberSession.player, [], True, 0))
                sendBroList(memberSession)
    TeamModel.getBrotherMgr().delBrother(brotherInfo.bid)
    #此处为及时自行数据库删除操作
    #########
    #########
    #########
    #########
    #########
    return
def processCheckBrotherFlag(session, brotherFlag, opstype, cmd, ret_msg):
    #判断是否在队伍中
    flag = session.player.brotherCtrl.brotherFlag
    if brotherFlag != flag:
        session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, ret_msg))
        return False
    return True



def processCheckAddBrother(session, memberSession1, memberSession2, opstype, cmd):
    #判断用户是否在线
    if None == memberSession1 or None == memberSession2:
        session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '用户不在线，不能进行结义！'))
        return False
    #判断是否在队伍中
    teamID = session.player.teamCtrl.teamID
    if teamID != memberSession1.player.teamCtrl.teamID or teamID != memberSession2.player.teamCtrl.teamID:
        session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '用户不在一个队伍中，不能进行结义！'))
        return False
    return True


#结义操作时，服务器给客户端广播的信息格式
def processBrotherOpsMsgRet(opstype, player, allBrotherInfo, flag, delBrotherTime):
    ret_msg                         = MsgDef.BrotherOpsMsgRet()
    ret_msg.opstype                 = opstype
    ret_msg.uid                     = player.uid
    ret_msg.name                    = player.name
    ret_msg.job                     = player.job
    ret_msg.gender                  = player.gender
    ret_msg.level                   = player.level
    ret_msg.allBrotherInfo          = []
    ret_msg.allBrotherInfo          = allBrotherInfo
    ret_msg.flag                    = flag
    ret_msg.delTime                 = delBrotherTime
    return ret_msg
#结义操作时，服务器给客户端广播的信息格式
def processBrotherOpsMsg(player, online):
    ret_msg                         = MsgDef.BrotherPlayerMsg()
    ret_msg.uid                     = player.uid
    ret_msg.name                    = player.name
    ret_msg.job                     = player.job
    ret_msg.gender                  = player.gender
    ret_msg.level                   = player.level
    ret_msg.online                  = online
    return ret_msg