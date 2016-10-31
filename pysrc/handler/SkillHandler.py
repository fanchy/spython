# -*- coding: utf-8 -*-
import ffext
import msgtype.ttypes as MsgDef
import  weakref
from base import  Base
import MarryHandler
from model import  TeamModel, PlayerModel, ItemModel
from db import DbService

def buildErrMsg(cmd, errMsg):
    return MsgDef.ErrorMsgRet(0, cmd, errMsg)#'cmd=%d,errMsg=%s'%(cmd, errMsg)
@ffext.onLogic(MsgDef.ClientCmd.QUERY_SKILL, MsgDef.EmptyReq)
def processQuerySkill(session, msg = None):
    player = session.player
    retMsg = MsgDef.QuerySkillRet([])
    for skillId, skill in player.skillCtrl.allSkill.iteritems():
        skillInfo = MsgDef.Skill()
        skillInfo.skillId = skillId
        skillInfo.skillLevel = skill.skillLevel
        skillInfo.lastUsedTM = int(skill.lastUsedTmMs / 1000)
        skillInfo.position   = skill.position
        skillInfo.exp = skill.exp
        if skill.skillCfg:
            skillInfo.cd         = skill.skillCfg.cd
            if skillInfo.cd > 30000:
                skillInfo.cd = 0
            elif skillInfo.cd < 0:
                skillInfo.cd = 0
        else:
            skillInfo.cd = 0
        retMsg.allSkill.append(skillInfo)
    session.sendMsg(MsgDef.ServerCmd.QUERY_SKILL, retMsg)
    return

#学习技能
@ffext.onLogic(MsgDef.ClientCmd.LEARN_SKILL, MsgDef.LearnSkillReq)
def processLearnSkill(session, msg):
    ffext.dump('processLearnSkill', msg)
    player = session.player
    if msg.skillId == Base.MAKE_ITEM_ID and player.level < 10:
        session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.LEARN_SKILL, 'Error:人物等级需达到10级！'))
    if msg.skillLevel < 1:
        msg.skillLevel = 1
    retErr = player.skillCtrl.learnSkill(msg.skillId, msg.skillLevel)
    if retErr:
        session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.LEARN_SKILL, 'Error:'+retErr))
        return
    session.sendMsg(MsgDef.ServerCmd.LEARN_SKILL, MsgDef.LearnSkillRet(msg.skillId, msg.skillLevel))
    return


#使用技能
@ffext.onLogic(MsgDef.ClientCmd.USE_SKILL, MsgDef.UseSkillReq)
def processUseSkill(session, msg):
    player = session.player
    skill = player.skillCtrl.getSkillById(msg.skillId)
    if not skill:
        for k , v in player.skillCtrl.allSkill.iteritems():
            if v.skillCfg.skillId == msg.skillId:
                skill = v
                break
            #skill = v
        #session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.USE_SKILL, '%d技能不存在'%(msg.skillId)))
        #return
    #伤血计算 满怒气值 是能放一次无双技能
    #生命值每损失5%增加3点怒气值
    #主动行为：每次普通攻击或释放技能，增加0.5点怒气值
    #怒气值上限为100点

    ffext.dump('skillID', skill.skillCfg.skillId)
    #结义技能和夫妻技能
    if skill.skillCfg.skillId == Base.BRO_SKILL_ID or skill.skillCfg.skillId == MarryHandler.WEDDING_SKILL_ID:
        #ffext.dump("BROSKILLID", Base.BRO_SKILL_ID)
        ffext.dump("WEDDINGSKILLID",MarryHandler.WEDDING_SKILL_ID)
        msg.targetId = player.uid
        ffext.dump('TARGETID', msg.targetId)
        costAnger = player.angerMax
        if player.anger < costAnger:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.USE_SKILL, '怒气未满'))
            return
        player.addAnger(-costAnger)
        ffext.dump('COSTANGER', costAnger)
        objDest = player.mapObj.getObjById(msg.targetId)
    else:
        objDest = player.mapObj.getObjById(msg.targetId)
        if not objDest:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.USE_SKILL, '目标不存在'))
            return
        mp = skill.skillCfg.mp
        if player.mp < mp:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.USE_SKILL, '蓝量不足'))
            return
        player.subMP(mp)
        player.addAnger(Base.ANGER_USE_SKILL)#ANGER_USE_SKILL = 0.5

    #ffext.dump("TARGETUID", msg.targetId)
    #objDest = player.mapObj.getObjById(msg.targetId)
    #if not objDest:
        #session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.USE_SKILL, '目标不存在'))
        #return


    #mp = skill.skillCfg.mp
    #if player.mp < mp:
        #session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.USE_SKILL, '蓝量不足'))
        #return
    #player.subMP(mp)
    #player.addAnger(Base.ANGER_USE_SKILL)#ANGER_USE_SKILL = 0.5

    retMsg = MsgDef.UseSkillRet(player.uid, msg.skillId, msg.targetId, skill.skillCfg.cd, player.hp, player.mp, player.anger, player.angerMax)
    ffext.dump('SKILLLLLLLL', skill.skillCfg.skillId)
    retErr  = player.skillCtrl.useSkill(skill, objDest, msg)
    if retErr:
        session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.USE_SKILL, retErr))
        return
    retMsg.targetX = objDest.x
    retMsg.targetY = objDest.y
    player.broadcast(MsgDef.ServerCmd.USE_SKILL, retMsg)
    return


#更新技能位置
@ffext.onLogic(MsgDef.ClientCmd.UPDATE_SKILL_POS, MsgDef.UpdateSkillPosReq)
def processUpdateSkillPosReq(session, msg):
    ffext.dump('processUpdateSkillPosReq', msg)
    player = session.player
    for pos,skillId in msg.skill2pos.iteritems():
        skill = player.skillCtrl.getSkillById(skillId)
        if not skill:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.UPDATE_SKILL_POS, '技能不存在'))
            continue
        skill.position = pos
    session.sendMsg(MsgDef.ServerCmd.UPDATE_SKILL_POS, MsgDef.UpdateSkillPosRet(msg.skill2pos))
    return
def buildPlayerInfo(retMsg, player):
    retMsg.uid = player.uid
    retMsg.name = player.name
    retMsg.level = player.level
    retMsg.gender = player.gender
    retMsg.job = player.job
    return retMsg
#切磋
def winQieCuo(player):
    if player:
        if player.ctrlQieCuo.startMap != player.mapname:
            return
        playerInfo = MsgDef.BrotherPlayerMsg()
        buildPlayerInfo(playerInfo, player)
        retMsg = MsgDef.QieCuoRet(3, playerInfo, player.uid)#0表示请求切磋 1表示同意 2表示拒绝 3表示 切磋状态消失
        player.sendMsg(MsgDef.ServerCmd.QIECUO_OPS, retMsg)

        destPlayer = player.ctrlQieCuo.playerRefQieCuo()
        if destPlayer:
            destPlayer.sendMsg(MsgDef.ServerCmd.QIECUO_OPS, retMsg)
    return
@ffext.onLogic(MsgDef.ClientCmd.QIECUO_OPS, MsgDef.QieCuoReq)
def processQieCuoReq(session, msg):
    player = session.player
    if msg.opstype == 0:#0表示请求切磋 1表示同意 2表示拒绝
        destPlayer = player.mapObj.getPlayerById(msg.uidarg)
        if not destPlayer:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.QIECUO_OPS, '对手不在线'))
            return
        playerInfo = MsgDef.BrotherPlayerMsg()
        buildPlayerInfo(playerInfo, player)
        retMsg = MsgDef.QieCuoRet(msg.opstype, playerInfo)#0表示请求切磋 1表示同意 2表示拒绝 3表示 切磋状态消失
        destPlayer.sendMsg(MsgDef.ServerCmd.QIECUO_OPS, retMsg)
    elif  msg.opstype == 1:
        destPlayer = player.mapObj.getPlayerById(msg.uidarg)
        if not destPlayer:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.QIECUO_OPS, '对手不在线'))
            return
        playerInfo = MsgDef.BrotherPlayerMsg()
        buildPlayerInfo(playerInfo, player)
        retMsg = MsgDef.QieCuoRet(msg.opstype, playerInfo)#0表示请求切磋 1表示同意 2表示拒绝 3表示 切磋状态消失
        destPlayer.sendMsg(MsgDef.ServerCmd.QIECUO_OPS, retMsg)

        playerInfo = MsgDef.BrotherPlayerMsg()
        buildPlayerInfo(playerInfo, destPlayer)
        retMsg = MsgDef.QieCuoRet(msg.opstype, playerInfo)#0表示请求切磋 1表示同意 2表示拒绝 3表示 切磋状态消失
        session.sendMsg(MsgDef.ServerCmd.QIECUO_OPS, retMsg)

        player.ctrlQieCuo.setQieCuoPlayer(destPlayer)
        destPlayer.ctrlQieCuo.setQieCuoPlayer(player)
        ref1 = player.ctrlQieCuo.playerRefQieCuo
        ref2 = destPlayer.ctrlQieCuo.playerRefQieCuo

        def cb():
            player1 = ref1()
            player2 = ref2()
            if player1 and player1.mapObj != None:
                if not player2 or player2.mapObj == None:#player1 win
                    winQieCuo(player1)
                    return
                if player2.ctrlQieCuo.startMap != player2.mapname:
                    winQieCuo(player1)
                    return
                dist = Base.distance(player2.x, player2.y, player2.ctrlQieCuo.startX, player2.ctrlQieCuo.startY)
                if dist >  Base.QIECUO_MAX_RANGE:
                    if player2.ctrlQieCuo.warnTimes == 0:
                        player2.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.QIECUO_OPS, '警告!切磋出界3秒后将会被判输!'))
                    player2.ctrlQieCuo.warnTimes += 1
                    if player2.ctrlQieCuo.warnTimes == 4:
                        winQieCuo(player1)
                        return
                else:
                    player2.ctrlQieCuo.warnTimes = 0
                if player2.hp == 1:
                    winQieCuo(player1)
                    return
                if player1.ctrlQieCuo.startMap != player1.mapname:
                    winQieCuo(player2)
                    return
                dist = Base.distance(player1.x, player1.y, player1.ctrlQieCuo.startX, player1.ctrlQieCuo.startY)
                if dist > Base.QIECUO_MAX_RANGE:
                    if player1.ctrlQieCuo.warnTimes == 0:
                        player1.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.QIECUO_OPS, '警告!出界3秒后将会被判输!'))
                    player1.ctrlQieCuo.warnTimes += 1
                    if player1.ctrlQieCuo.warnTimes == 4:
                        winQieCuo(player2)
                        return
                else:
                    player1.ctrlQieCuo.warnTimes = 0
                if player1.hp == 1:
                    winQieCuo(player2)
                    return
                ffext.dump('check win ...')
                ffext.timer(1000, cb)
            else:
                if player2:
                    winQieCuo(player2)
                    return
            return
        ffext.timer(1000, cb)
    elif  msg.opstype == 2:
        destPlayer = player.mapObj.getPlayerById(msg.uidarg)
        if not destPlayer:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.QIECUO_OPS, '对手不在线'))
            return
        playerInfo = MsgDef.BrotherPlayerMsg()
        buildPlayerInfo(playerInfo, player)
        retMsg = MsgDef.QieCuoRet(msg.opstype, playerInfo)#0表示请求切磋 1表示同意 2表示拒绝 3表示 切磋状态消失
        destPlayer.sendMsg(MsgDef.ServerCmd.QIECUO_OPS, retMsg)
    return
#切换攻击模式
@ffext.onLogic(MsgDef.ClientCmd.ATTACK_MODE_OPS, MsgDef.AttackModeReq)
def processAttackModeReq(session, msg = None):
    player = session.player
    typeVal = 0
    if msg != None:
        typeVal = msg.opstype
        if msg.opstype == 0:
            player.modeAttack = msg.modeAttack
    session.sendMsg(MsgDef.ServerCmd.ATTACK_MODE_OPS, MsgDef.AttackModeRet(typeVal, player.modeAttack))
    return


#求救功能
@ffext.onLogic(MsgDef.ClientCmd.HELP_ATTACK_OPS, MsgDef.HelpAttackReq)
def processHelpAttackReq(session, msg = None):
    player = session.player
    if msg.opstype == 0:
        playerInfo = MsgDef.BrotherPlayerMsg()
        buildPlayerInfo(playerInfo, player)
        retMsg = MsgDef.HelpAttackRet(0, playerInfo)
        #结婚的
        hasSendUids = {}
        if player.isMarry():
            marryTotalInfo = player.marriageCtrl.marryTotalInfo
            other = marryTotalInfo.getInfoByAnotherGender(player.gender)
            ffext.dump('help', player.gender, other)
            if other:
                #otherPlayer = player.mapObj.getPlayerById(other.uid)
                otherSession = ffext.getSessionMgr().findByUid(other.uid)
                if otherSession:
                    hasSendUids[other.uid] = True
                    otherPlayer = otherSession.player
                    otherPlayer.sendMsg(MsgDef.ServerCmd.HELP_ATTACK_OPS, retMsg)
        #
        brotherInfo = player.brotherCtrl.brotherInfo
        if None != brotherInfo:
            # 判断三个人是否同时在线
            for key, val in brotherInfo.getBrotherMember().iteritems():
                memberSession = ffext.getSessionMgr().findByUid(val.uid)
                if None != memberSession:
                    memberSession.sendMsg(MsgDef.ServerCmd.HELP_ATTACK_OPS, retMsg)
                    return
        # team = TeamModel.getTeamMgr().getTeamById(player.teamCtrl.teamID)
        # if team:
        #     for key, valdata in team.getTeamMember().iteritems():
        #         if hasSendUids.get(valdata.uid) == True or valdata.uid == player.uid:
        #             continue
        #         else:
        #             hasSendUids[other.uid] = True
        #         otherSession = ffext.getSessionMgr().findByUid(valdata.uid)
        #         if otherSession:
        #             otherPlayer = otherSession.player
        #             playerInfo = MsgDef.BrotherPlayerMsg()
        #             buildPlayerInfo(playerInfo, player)
        #             otherPlayer.sendMsg(MsgDef.ServerCmd.HELP_ATTACK_OPS, MsgDef.HelpAttackRet(0, playerInfo))
    elif msg.opstype == 1:
        otherSession = ffext.getSessionMgr().findByUid(msg.uidArg)
        if otherSession:
            otherPlayer = otherSession.player
            otherPlayer.mapObj.playerEnterMap(player, otherPlayer.x, otherPlayer.y)
    return

#洗白
@ffext.onLogic(MsgDef.ClientCmd.XIBAI_OPS, MsgDef.XibaiReq)
def processXibaiReq(session, msg = None):
    player = session.player
    if msg.opstype == 0:
        if player.pkSinValue >= 100 and player.pkSinValue < 300:#橙：(100<=罪恶值<300)时显示，被人杀死后3%掉落身上任一装备。
            pass
        else:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.QIECUO_OPS, '只有橙色罪恶值才能洗白'))
            return
        gold = 500
        if player.gold < gold:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.QIECUO_OPS, '金币不足:%d'%(gold)))
            return
        player.addGold(gold, True)
        retMsg = MsgDef.XibaiRet(msg.opstype)
        session.sendMsg(MsgDef.ServerCmd.XIBAI_OPS, retMsg)

        def cb():
            player.pkSinValue = 0
            #更新pk罪恶值
            session.broadcast(MsgDef.ServerCmd.PK_SIN_UPDATE_OPS, MsgDef.PkSinUpdateRet(0, player.pkSinValue, player.uid))
            return
        ffext.timer(1000*10, cb)
        return
    return
