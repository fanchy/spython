# -*- coding: utf-8 -*-
import random
import ffext

import msgtype.ttypes as MsgDef
from db import DbService
from model import PlayerModel, MailModel, LoginRewardModel, LogModel
from mapmgr import MapMgr
from base import Base
import idtool
import SkillHandler
import TaskHandler
import ItemHandler
import FriendHandler
import TeamHandler
import GuildHandler
def buildErrMsg(cmd, errMsg):
    return MsgDef.ErrorMsgRet(0, cmd, errMsg)#'cmd=%d,errMsg=%s'%(cmd, errMsg)
@ffext.onLogin(MsgDef.ClientCmd.LOGIN, MsgDef.LoginReq)
def processLogin(session, msg): #session_key,
    print('processLogin', msg)
    #ffext.dump("USERNAME", msg.username[:5])
    if msg.username[:5] == "ceshi" and msg.password != "1234":
        retErr = Base.lang('密码不正确')
        session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.LOGIN, retErr))
        return
    #异步载入数据库数据
    def callback(db):
        session.user = PlayerModel.User()
        session.user.username = msg.username
        reconnectUid = msg.reconnectUid
        retRole = []
        if db.result:
            accountId = long(db.result[0][0])
            def funcToClose(sessOther):
                if sessOther.user.accountid == accountId:
                    ffext.warn('check relogin accountId=%d, name=%s'%(accountId, sessOther.user.username))
                    #if reconnectUid:
                    #    session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.LOGIN, Base.lang('账号在其他地方登录')))
                    #else:
                    #    sessOther.close()
                    # 登出-记录log
                    LogModel.logLoginData(accountId, 0, '', LogModel.LoginOpType.LOGOUT, LogModel.LoginReason.KICKOUT)
                    sessOther.sendMsg(MsgDef.ServerCmd.RELOGIN, MsgDef.ReLoginRet())
                    def cbClose():
                        sessOther.close()
                    ffext.timer(500, cbClose)
                    return True
            ffext.getSessionMgr().foreach_until(funcToClose)
            session.user.accountid =accountId
        else:
            session.user.accountid = idtool.allocUid()
            def cbNewUser(retNew):
                accountId = long(retNew.result[0][0])
                session.user.accountid = accountId
                ffext.dump('cbNewUser', retNew, accountId)
                # 登录（new）-记录log
                LogModel.logLoginData(accountId, 0, '', LogModel.LoginOpType.LOGIN_ACCOUNT, LogModel.LoginReason.NEW_LOGIN)
                return
            DbService.getPlayerService().createUser(msg.username, cbNewUser)
        ffext.dump('load player', db.result)
        for row in db.result:
            roleTmp = PlayerModel.Role(row)
            session.user.addRole(roleTmp)
            tmpRoleMsg = MsgDef.RoleInfo(roleTmp.uid, roleTmp.name, roleTmp.job, roleTmp.gender, roleTmp.level, roleTmp.exp)
            retRole.append(tmpRoleMsg)
        #print(session.user.accountid, session.user.username)
        ffext.checkWebDebug(session, msg, MsgDef)
        retMsg = MsgDef.UserInfoRet(ffext.getTime(), retRole)
        if reconnectUid:#重连
            processSelectRoleReq(session, MsgDef.SelectRoleReq(reconnectUid), msg.x ,msg.y)
        else:
            session.sendMsg(MsgDef.ServerCmd.USER_INFO, retMsg)
        # 登录（old）-记录log-(TODO:ip,geo信息获取接口暂缺)
        LogModel.logLoginData(session.user.accountid, 0, '', LogModel.LoginOpType.LOGIN_ACCOUNT, LogModel.LoginReason.OLD_LOGIN)
    DbService.getPlayerService().loadUser(msg.username, callback)
    return
@ffext.onLogic(MsgDef.ClientCmd.LOGIN, MsgDef.LoginReq)
def processLoginAgain(session, msg):
    processLogin(session, msg)
    
#创建角色
@ffext.onLogic(MsgDef.ClientCmd.CREATE_ROLE, MsgDef.CreateRoleReq)
def processCreateRoleReq(session, msg):
    print('CreateRoleReq', msg)
    if msg.gender != Base.Gender.MALE and msg.gender != Base.Gender.FEMAIL:
        msg.gender = Base.Gender.MALE
    roleTmp = PlayerModel.Role()
    roleTmp.uid = idtool.allocUid()
    if session.isWebDebug:
        msg.name = msg.name.encode('utf-8')
    roleTmp.name= msg.name
    roleTmp.job = msg.job
    roleTmp.gender = msg.gender
    if  roleTmp.gender != Base.Gender.MALE and  roleTmp.gender != Base.Gender.FEMAIL:
         roleTmp.gender = Base.Gender.MALE

    if roleTmp.job <  Base.Job.ZHANSHI or roleTmp.job > Base.Job.YOUXIA:
        roleTmp.job = Base.Job.ZHANSHI
    def callback(db):
        retMsg = MsgDef.CreateRoleRet()
        if db.isOk():
            retMsg.flag = True
            retMsg.uid = roleTmp.uid
            session.user.addRole(roleTmp)
        else:
            retMsg.flag   = False
            retMsg.errMsg = '角色名已经存在'
        session.sendMsg(MsgDef.ServerCmd.CREATE_ROLE_RET, retMsg)
        MailModel.createMailRecrodAtFirstTime(roleTmp.uid)
        # 新增每日活动记录
        DbService.getPlayerService().createDailyLoginAct(session.user.accountid)
        if retMsg.flag == True:
            # 创角（old）-记录log
            LogModel.logLoginData(session.user.accountid, roleTmp.uid, roleTmp.name, LogModel.LoginOpType.CREATE_PLAYER, 0)
    mapName = 10001
    x = 27
    y = 188
    mapObj = MapMgr.getMapMgr().allocMap(mapName)
    if mapObj.cfg.reviveMap != None:
        mapName = mapObj.cfg.reviveMap.mapname
        x       = mapObj.cfg.reviveMap.x
        y       = mapObj.cfg.reviveMap.y

    DbService.getPlayerService().createRole(session.user, roleTmp, mapName, x, y, callback)
    return
#选取角色，发送角色数据给 client
@ffext.onLogic(MsgDef.ClientCmd.DEL_ROLE, MsgDef.DelRoleReq)
def processDelRoleReq(session, msg):
    print('DelRoleReq', msg)
    for k in range(0, len(session.user.allRole)):
        if session.user.allRole[k].uid == msg.uid:
            u_name = session.user.allRole[k].name
            del session.user.allRole[k]
            DbService.getPlayerService().delRole(msg.uid)
            # 删角（old）-记录log
            LogModel.logLoginData(session.user.accountid, msg.uid, u_name, LogModel.LoginOpType.DEL_PLAYER, 0)
            break
    retMsg = MsgDef.DelRoleRet(msg.uid)
    session.sendMsg(MsgDef.ServerCmd.DEL_ROLE, retMsg)
#随机角色名称
@ffext.onLogic(MsgDef.ClientCmd.RAND_NAME, MsgDef.RandNameReq)
def processRandNameReq(session, msg):
    print('processRandNameReq', msg)
    name =  PlayerModel.getPlayerMgr().randName(msg.gender)
    session.sendMsg(MsgDef.ServerCmd.RAND_NAME, MsgDef.RandNameRet(name))

#选取角色，发送角色数据给 client
@ffext.onLogic(MsgDef.ClientCmd.SELECT_ROLE, MsgDef.SelectRoleReq)
def processSelectRoleReq(session, msg, x = 0, y = 0):
    print('SelectRoleReq', msg)
    if msg.uid == 0:
        msg.uid = session.user.allRole[0].uid
    accountid = session.user.accountid
    role = session.user.getRole(msg.uid)
    if session.player:
        return False
    if not role:
        return False
    def callback(dbSet):
        #异步载入数据库，需要验证session是否仍然有效，有可能下线了
        db = dbSet['player']
        if session.isValid() == False or session.player:
            return False
        
        if len(db.result) == 0:
            ffext.dump('no this role')
            return False
        else:
            player = PlayerModel.Player(db.result[0])
            #ffext.dump(dbSet)
            session.setPlayer(player)
            if x != 0 and y != 0:
                player.x = x
                player.y = y

            #载入数据
            ffext.dump('load player =%s'%(session.player.name))
            session.verify_id(session.player.uid)
            dbTask = dbSet['task']
            dbitem = dbSet['item']
            dbFriend = dbSet['friend']
            dbEnemy = dbSet['enemy']
            dbGuild = dbSet['guild']
            dbPet = dbSet['pet']
            dbMail = dbSet['mail']
            dbLoginAct = dbSet['login_activity']
            if dbTask.isOk():
                player.taskCtrl.fromData(dbTask.result)
            if dbitem.isOk():
                player.itemCtrl.fromData(dbitem.result)
                #TaskHandler.processQueryTask(session)
            #初始化好友信息、仇人信息，屏蔽信息
            if dbFriend.isOk():
                player.friendCtrl.fromDataFriend(dbFriend.result)
            if dbEnemy.isOk():
                player.friendCtrl.fromDataEnemy(dbEnemy.result)
            #初始化行会信息
            if dbGuild.isOk():
                player.guildCtrl.fromData(dbGuild.result)
            player.petCtrl.fromData(dbPet.result)
            if dbMail.isOk():
                player.mailCtrl.fromData(dbMail.result)
            if dbLoginAct.isOk():
                player.loginActCtrl.fromData(dbLoginAct.result)
        # 发送属性数据
        PlayerModel.sendPropUpdateMsg(player)
        #发消息通知,通知上线
        tmpReq = MsgDef.EnterMapReq(player.mapname, player.x, player.y)
        processEnterMapReq(session, tmpReq, True)
        #发送技能数据
        SkillHandler.processQuerySkill(session)
        #发送包裹数据
        ItemHandler.processQueryPkg(session)
        #发送装备数据
        ItemHandler.processQueryEquip(session)
        #发送任务数据
        TaskHandler.processQueryTask(session)
        #发送好友数据
        FriendHandler.processListFriend(session, MsgDef.FriendListMsgReq(MsgDef.FriendListClientCmd.GET_FRIENDLIST))
        #发送行会数据
        GuildHandler.processGuildInfo(session)
        #发送结义数据
        TeamHandler.processBrotherOps(session, MsgDef.BrotherOpsReq(MsgDef.BrotherClientCmd.GET_BROTHERLIST))
        #发送安全码
        processMoneyBankOps(session)
        processQueryPet(session)
        from handler import  MarryHandler
        MarryHandler.processMarryOPS(session, MsgDef.MarriageOpsReq(MsgDef.MarriageClientCmd.MARRY_QUERY_STATUS))
        SkillHandler.processAttackModeReq(session)#发送攻击模式
        from handler import MailHandler
        MailHandler.processMarryOPS(session, MsgDef.MailOpsReq(0))
        #msg = MsgDef.UpdateSkillPosReq({320:1})
        #SkillHandler.processUpdateSkillPosReq(session, msg)
        #结义数据
        # if player.brotherCtrl:
        #     BrotherModel.handleQueryBrother(player)

        player.checkTimeAfterInit()
        # 登录（old）-记录log
        LogModel.logLoginData(accountid, player.uid, player.name, LogModel.LoginOpType.LOGIN_PLAYER, LogModel.LoginReason.OLD_LOGIN)
        return
    #异步载入数据库数据
    DbService.getPlayerService().loadPlayer(msg.uid, accountid, callback)
    return
#玩家跳地图
@ffext.onLogic(MsgDef.ClientCmd.ENTER_MAP, MsgDef.EnterMapReq)
def processEnterMapReq(session, msg, flagLogin = False):
    print('processEnterMapReq', msg)

    player     = session.player

    player.mapname = msg.mapname
    #添加player到地图管理器中
    mapObj = MapMgr.getMapMgr().allocMap(player.mapname)
    if not mapObj:
        mapObj = MapMgr.getMapMgr().getDefaultMap(player)
    mapObj.playerEnterMap(player, msg.x, msg.y)

    return
@ffext.onLogic(MsgDef.ClientCmd.MOVE, MsgDef.MoveReq)
def processMoveReq(session, msg):
    #ffext.dump('processMoveReq ', msg)
    player = session.player
    #if player.hp <= 0:
    #    return
    player.direction = msg.direction
    player.mapObj.movePlayer(player, msg.x, msg.y)

@ffext.onLogout
def processLogout(session):
    print(__name__, session.player)
    player = session.player
    if not player:
        return
    #发消息通知
    mapObj = player.mapObj
    if mapObj:
        mapObj.playerLeaveMap(player)
        #如果地图属性配置了下线后踢到某地图，那么改一下地图和坐标
        cfg = mapObj.cfg
        if cfg.offlineMap != None:
            player.mapname = cfg.offlineMap.mapname
            player.x       = cfg.offlineMap.x
            player.y       = cfg.offlineMap.y
            ffext.info('logout name=%s, offlineMap=%s, x=%d, y=%d'%(player.name, player.mapname, player.x, player.y))
        elif player.isDeath() and cfg.reviveMap != None:
            player.mapname = cfg.reviveMap.mapname
            player.x       = cfg.reviveMap.x
            player.y       = cfg.reviveMap.y
            ffext.info('logout name=%s, reviveMap=%s, x=%d, y=%d'%(player.name, player.mapname, player.x, player.y))
    #下线计算本次在线时长
    player.gametime = player.gametime + (ffext.getTime() - player.logintime)
    player.last_logout = ffext.getTime()

    DbService.getPlayerService().updatePlayer(player)
    #DbService.getPlayerService().updatePlayer(player)

    from handler import MarryHandler
    MarryHandler.processOffline(session)#MARRY_OFFLINE
    TeamHandler.processTeamOps(session, MsgDef.TeamMsgReq(MsgDef.TeamClientCmd.QUIT_TEAM, 0))
    TeamHandler.processBrotherDownline(session)
    

#@ffext.onEnter(msg_def.input_req_t)
def processEnter(session, msg):
    print('processEnter', session, msg)
    print('processEnter', msg, session)

@ffext.onLogic(MsgDef.ClientCmd.SERVER_CALLBACK, MsgDef.ServerCallBackReq)
def processServerCallback(session, msg):
    player= session.player
    player.doCallBack(msg.callbackId)

#玩家传送点传送
@ffext.onLogic(MsgDef.ClientCmd.TRANSFER_POINT_OPS, MsgDef.TransferPointOpsReq)
def processTransferPointOpsReq(session, msg):
    print('processTransferPointOpsReq', msg)
    player     = session.player
    destCfg = MapMgr.getMapMgr().getTransferPointCfg(msg.cfgid)
    if not destCfg:
        session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.TRANSFER_POINT_OPS, Base.lang('传送点不存在')))
        return
    #添加player到地图管理器中
    mapObj = MapMgr.getMapMgr().allocMap(destCfg.tomapid)
    if not mapObj:
        ffext.error('processTransferPointOpsReq %s not exist'%(str(destCfg.tomapid)))
        session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.TRANSFER_POINT_OPS, Base.lang('传送点不存在！')))
        return
    # if msg.cfgid == 7:#TODO
    #     from model.copymap import TestCopy
    #     mapObj = TestCopy.create(destCfg.tomapid)
    ffext.dump('transfer ', mapObj.mapname, mapObj.showName)
    if mapObj.showName.find('副本') >= 0:
        player.taskCtrl.trigger(Base.Action.COPY_MAP, int(mapObj.mapname), 1)
    mapObj.playerEnterMap(player, destCfg.tox, destCfg.toy)
    return

#宠物信息
@ffext.onLogic(MsgDef.ClientCmd.PET_QUERY, MsgDef.EmptyReq)
def processQueryPet(session, msg = None):
    player = session.player
    petCtrl= player.petCtrl
    petEgg = petCtrl.petEgg
    retMsg = MsgDef.PetInfoRet()
    retMsg.allPet = []
    retMsg.petEgg = MsgDef.PetEgg(petEgg.eggItemCfgId, petEgg.starttm, petEgg.needsec)
    for uid, pet in petCtrl.allPet.iteritems():
        status = 0
        if uid == petCtrl.outPetUid:
            status = 1
        petMsg = MsgDef.Pet(uid, status, pet.level, pet.exp, pet.cfg.expMax, pet.cfg.petType, pet.cfg.cfgid)
        petMsg.propExt = {}
        for k, v in pet.cfg.toPropData().iteritems():
            petMsg.propExt[k] = v
        retMsg.allPet.append(petMsg)
    session.sendMsg(MsgDef.ServerCmd.PET_QUERY, retMsg)
    return
#开始孵化宠物蛋
@ffext.onLogic(MsgDef.ClientCmd.PET_EGG_START, MsgDef.PetEggStartReq)
def processPetEggStartReq(session, msg):
    player = session.player
    petCtrl= player.petCtrl
    petEgg = petCtrl.petEgg
    item = player.itemCtrl.getItem(msg.uid)
    if not item:
        retErr = Base.lang('道具不存在!')
        session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.PET_EGG_START, retErr))
        return
    item   = player.itemCtrl.delItem(msg.uid)

    petEgg.eggItemCfgId = item.itemCfg.cfgId
    petEgg.starttm      = ffext.getTime()
    petEgg.needsec      = 10

    processQueryPet(session)
    return
#开始孵化宠物蛋
@ffext.onLogic(MsgDef.ClientCmd.PET_EGG_COMPLETE, MsgDef.EmptyReq)
def processPetEggCompleteReq(session, msg):
    player = session.player
    petCtrl= player.petCtrl
    if False == petCtrl.completeEgg():
        pass
        #retErr = Base.lang('孵化未完成!')
        #session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.PET_EGG_COMPLETE, retErr))
        #return
    
    processQueryPet(session)
    return
#喂养宠物
@ffext.onLogic(MsgDef.ClientCmd.PET_FEED, MsgDef.FeedPetReq)
def processPetEggStartReq(session, msg):
    addExp = 10
    player = session.player
    itemCtrl = player.itemCtrl
    if msg.item == None:
        msg.item = []
    pet = player.petCtrl.getPet(msg.uid)
    if None == pet:
        retErr = Base.lang('请选择宠物!')
        session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.PET_FEED, retErr))
        return
    for itemid in msg.item:
        item = itemCtrl.delItem(itemid)
        if item:
            addExp += 10
        else:
            retErr = Base.lang('itemid=%s无效!'%(str(itemid)))
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.PET_FEED, retErr))
    pet.addExp(addExp, True)
    processQueryPet(session)
    return
#释放宠物
@ffext.onLogic(MsgDef.ClientCmd.PET_OUT, MsgDef.PetOpsReq)
def processPetOutReq(session, msg):
    player = session.player
    if not player.petCtrl.petOut(msg.uid):
        retErr = Base.lang('召唤失败!')
        session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.PET_OUT, retErr))
        return
    session.sendMsg(MsgDef.ServerCmd.PET_OUT, MsgDef.PetOpsRet(msg.uid, 1))
    return
#收回宠物
@ffext.onLogic(MsgDef.ClientCmd.PET_IN, MsgDef.PetOpsReq)
def processPetInReq(session, msg):
    player = session.player
    if not player.petCtrl.petIn(msg.uid):
        retErr = Base.lang('收回失败!')
        session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.PET_IN, retErr))
        return
    session.sendMsg(MsgDef.ServerCmd.PET_IN, MsgDef.PetOpsRet(msg.uid, 0))

@ffext.onLogic(MsgDef.ClientCmd.MONEY_BANK_QUERY, MsgDef.EmptyReq)
def processMoneyBankQuery(session, msg = None):#0表示请求交易 1表示同意交易 2表示拒绝
    player = session.player
    retMsg = MsgDef.MoneyBankQueryRet(player.moneyBankCtrl.gold)
    session.sendMsg(MsgDef.ServerCmd.MONEY_BANK_QUERY, retMsg)

#钱庄
@ffext.onLogic(MsgDef.ClientCmd.MONEY_BANK_OPS, MsgDef.MoneyBankOpsReq)
def processMoneyBankOps(session, msg=None):#0存入 1取出 2设置密码
    player = session.player
    if not msg:
        retMsg = MsgDef.MoneyBankOpsRet(0, 0, player.isSetPasswd)
        processMoneyBankQuery(session)
        session.sendMsg(MsgDef.ServerCmd.MONEY_BANK_OPS, retMsg)
        return
    if  msg.opstype == 0:
        #ffext.dump("ISSETPASSWD", player.isSetPasswd)
        if player.isSetPasswd and not player.isVerified:
            def cb(ret):
                safePasswd = ret.result[0][0]
                if msg.passwd != safePasswd:
                    retErr = Base.lang('安全密码错误!')
                    session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.MONEY_BANK_OPS, retErr))
                else:
                    player.isVerified = True
                    verify_retMsg = MsgDef.MoneyBankOpsRet(3, 0, player.isSetPasswd)
                    session.sendMsg(MsgDef.ServerCmd.MONEY_BANK_OPS, verify_retMsg)
            DbService.getPlayerService().querySafePasswd(player, cb)
            return
        if player.gold < msg.num:
            retErr = Base.lang('金币不足!')
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.MONEY_BANK_OPS, retErr))
            return
        player.addGold(msg.num * -1, True)
        player.moneyBankCtrl.gold += msg.num
        processMoneyBankQuery(session)
        retMsg = MsgDef.MoneyBankOpsRet(0, msg.num, player.isSetPasswd)
        session.sendMsg(MsgDef.ServerCmd.MONEY_BANK_OPS, retMsg)
        #processMoneyBankQuery(session)
    elif  msg.opstype == 1:
        if player.isSetPasswd and not player.isVerified:
            def cb(ret):
                safePasswd = ret.result[0][0]
                if msg.passwd != safePasswd:
                    retErr = Base.lang('安全密码错误!')
                    session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.MONEY_BANK_OPS, retErr))
                else:
                    player.isVerified = True
                    verify_retMsg = MsgDef.MoneyBankOpsRet(3, 0, player.isSetPasswd)
                    session.sendMsg(MsgDef.ServerCmd.MONEY_BANK_OPS, verify_retMsg)
                DbService.getPlayerService().querySafePasswd(player, cb)
                return
        if player.moneyBankCtrl.gold < msg.num:
            retErr = Base.lang('钱庄金币不足!')
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.MONEY_BANK_OPS, retErr))
            return
        player.addGold(msg.num, True)
        player.moneyBankCtrl.gold -= msg.num
        retMsg = MsgDef.MoneyBankOpsRet(1, msg.num, player.isSetPasswd)
        processMoneyBankQuery(session)
        session.sendMsg(MsgDef.ServerCmd.MONEY_BANK_OPS, retMsg)
        #processMoneyBankQuery(session)
    elif  msg.opstype == 2:
        DbService.getPlayerService().updateSafePasswd(player, msg.passwd)
        #数据库增加个安全码字段
        retMsg = MsgDef.MoneyBankOpsRet(2, 0, player.isSetPasswd)
        session.sendMsg(MsgDef.ServerCmd.MONEY_BANK_OPS, retMsg)


@ffext.onLogic(MsgDef.ClientCmd.HEART_BEAT, MsgDef.HeartBeatReq)
def processHeartBeatReq(session, msg):
    session.sendMsg(MsgDef.ServerCmd.HEART_BEAT, MsgDef.HeartBeatRet(msg.arg))


