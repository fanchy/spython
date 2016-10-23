# -*- coding: utf-8 -*-
#本文件用于存放好友关系的操作函数
import ffext
from base import Base
from mapmgr import MapMgr as MapMgr
#调用msgtype中的ttypes文件，使用系统中的枚举函数
from msgtype import ttypes as MsgDef
#调用DbService文件，使用全局对象gDbServiceFriend
from db import DbService as DbService

def buildErrMsg(cmd, errMsg):
    return MsgDef.ErrorMsgRet(0, cmd, errMsg)#'cmd=%d,errMsg=%s'%(cmd, errMsg)

#当客户端向服务器发送GET_FRIENDLIST指令时，服务器向客户端反馈好友列表
@ffext.onLogic(MsgDef.ClientCmd.GET_FRIENDLIST, MsgDef.FriendListMsgReq)
def processListFriend(session, msg):
    #声明好友列表以FriendListMsgRet格式传输，客户端识别指令为FRIENDLIST_MSG传输格式
    #print(msg)
    ret_msg                 = MsgDef.FriendListMsgRet()
    ret_msg.opstype         = msg.opstype
    ret_msg.allPlayerInfo   =[]
    ret_msg.allEnemyInfo    =[]
    ret_msg.allShieldInfo   =[]
    if msg.opstype == MsgDef.FriendListClientCmd.GET_FRIENDLIST:
        online = True
        #遍历allFriend字典，获取好友属性
        for uid, val in session.player.friendCtrl.getFriend().iteritems():
            if None == ffext.getSessionMgr().findByUid(val.uid):
                online = False
            else:
                online = True
            #将好友信息赋值，传递给客户端
            ret_msg.allPlayerInfo.append(processFriendPlayerMsg(val.uid, val.name, val.job, val.gender, val.level, online))
        for uid, val in session.player.friendCtrl.getEnemy().iteritems():
            if None == ffext.getSessionMgr().findByUid(val.uid):
                online = False
            else:
                online = True
            #将仇人信息赋值，传递给客户端
            ret_msg.allEnemyInfo.append(processFriendPlayerMsg(val.uid, val.name, val.job, val.gender, val.level, online))
        for uid, val in session.player.friendCtrl.getShieldPerson().iteritems():
            if None == ffext.getSessionMgr().findByUid(val.uid):
                online = False
            else:
                online = True
            #将屏蔽信息赋值，传递给客户端
            ret_msg.allShieldInfo.append(processFriendPlayerMsg(val.uid, val.name, val.job, val.gender, val.level, online))
        session.sendMsg(MsgDef.ServerCmd.FRIENDLIST_MSG, ret_msg)
        return
    # if msg.opstype == MsgDef.FriendListClientCmd.GET_FRIENDLIST_TEMP:
    #     #遍历allFriend字典，获取好友属性
    #     for uid, val in session.player.friendCtrl.getFriendTemp().iteritems():
    #         ret_msg.allPlayerInfo.append(processFriendPlayerMsg(val.uid, val.name))
    #     session.sendMsg(MsgDef.ServerCmd.FRIENDLIST_MSG, ret_msg)
    #     return
    #仇人追击
    if msg.opstype == MsgDef.FriendListClientCmd.GET_ENEMY:
        enemyUid = msg.uid
        for uid, val in session.player.friendCtrl.getEnemy().iteritems():
            if uid == enemyUid:
                enemyPlayer = ffext.getSessionMgr().findByUid(enemyUid).player
                if None == enemyPlayer:
                    online = False
                    retErr = Base.lang('仇人处于离线状态!')
                    session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.FriendListClientCmd.GET_ENEMY, retErr))
                    return
                else:
                    online = True
                    ret_msg.allEnemyInfo.append(processFriendPlayerMsg(val.uid, val.name, val.job, val.gender, val.level, online, enemyPlayer.mapname, enemyPlayer.x, enemyPlayer.y))
                    session.sendMsg(MsgDef.ServerCmd.FRIENDLIST_MSG, ret_msg)
                    return
        else:
            retErr = Base.lang('仇人不存在!')
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.FriendListClientCmd.GET_ENEMY, retErr))
            return
    if msg.opstype == MsgDef.FriendListClientCmd.JUMP_ENEMY:
        enemyUid = msg.uid
        for uid, val in session.player.friendCtrl.getEnemy().iteritems():
            if uid == enemyUid:
                enemyPlayer = ffext.getSessionMgr().findByUid(enemyUid).player
                if None == enemyPlayer:
                    online = False
                    retErr = Base.lang('仇人处于离线状态!')
                    session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.FriendListClientCmd.GET_ENEMY, retErr))
                    return
                else:
                    online = True
                    mapname = enemyPlayer.mapname
                    x = enemyPlayer.x
                    y = enemyPlayer.y
                    mapObj = MapMgr.getMapMgr().allocMap(mapname)
                    if not mapObj:
                        retErr = Base.lang('地图不存在!')
                        session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.FriendListClientCmd.JUMP_ENEMY, retErr))
                        return
                    mapObj.playerEnterMap(session.player, x, y)
                    return
        else:
            retErr = Base.lang('仇人不存在!')
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.FriendListClientCmd.GET_ENEMY, retErr))
            return






#当客户端向服务器发送FRIENDLIST_OPS指令时，服务器执行如下操作，并将处理结果反馈给客户端
@ffext.onLogic(MsgDef.ClientCmd.FRIENDLIST_OPS, MsgDef.FriendMsgReq)
def processFriendListOps(session, msg):
    friendUid           = msg.uid
    opstype             = msg.opstype
    friendSession       = ffext.getSessionMgr().findByUid(friendUid)
    uid                 = session.player.uid
    #用户申请添加别人为好友的语句
    if opstype == MsgDef.FriendOpsClientCmd.INVITE_ADD_LISTFRIEND:
        #如果好友不在线，提示用户，好友不在线，不能添加（此处由客户端判断，理论上是有用户面对面才可以添加好友）
        if None == friendSession:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, MsgDef.ClientCmd.FRIENDLIST_OPS,'对方不在线，无法添加'))
            return
        #判断是否已经为好友（此处由客户端判断，已经为好友的不能再次添加）
        if None != session.player.friendCtrl.getFriendByUid(friendUid):
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, MsgDef.ClientCmd.FRIENDLIST_OPS, '双方已是好友，无法再次添加'))
            return
        #判断是否发送过好友申请如未发送，则在对方临时好友列表中添加个人信息
        # if None == friendSession.player.friendCtrl.getFriendTempByUid(uid):
        #     #将用户信息添加至好友的临时好友表中
        #     friendSession.player.friendCtrl.addFriendTemp(session.player)
        #将好友邀请发送给对方客户端
        friendSession.sendMsg(MsgDef.ServerCmd.FRIEHND_MSG, processFriendPlayerMsgRet(opstype, uid, session.player.name, session.player.job, session.player.gender, session.player.level, True))
        return
    #用户确认添加别人为好友的语句
    if opstype == MsgDef.FriendOpsClientCmd.VERIFY_ADD_LISTFRIEND:
        #判断是否在临时好友列表中
        # if None == session.player.friendCtrl.getFriendTempByUid(friendUid):
        #     session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, MsgDef.ClientCmd.FRIENDLIST_OPS, '不在待验证好友列表中，无法进行确认'))
        #     return.
        if None == friendSession:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, MsgDef.ClientCmd.FRIENDLIST_OPS,'对方不在线，无法确认添加好友'))
            return
        #将好友关系写入数据库
        DbService.getFriendService().addFriend(uid, friendUid)
        session.player.friendCtrl.addFriend(friendSession.player)
        session.sendMsg(MsgDef.ServerCmd.FRIEHND_MSG, processFriendPlayerMsgRet(opstype, friendUid, friendSession.player.name, friendSession.player.job, friendSession.player.gender, friendSession.player.level, True))
        if None != friendSession:
            friendSession.player.friendCtrl.addFriend(session.player)
            friendSession.sendMsg(MsgDef.ServerCmd.FRIEHND_MSG, processFriendPlayerMsgRet(opstype, uid, session.player.name, session.player.job, session.player.gender, session.player.level, True))
        return
    #用户拒绝添加别人为好友的语句
    if opstype == MsgDef.FriendOpsClientCmd.REFUSE_ADD_LISTFRIEND:
        #判断是否在临时好友列表中
        # if None == session.player.friendCtrl.getFriendTempByUid(friendUid):
        #     session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, MsgDef.ClientCmd.FRIENDLIST_OPS, '不在待验证好友列表中，无法进行拒绝'))
        #     return
        #忽略好友申请成功，将成功信息反馈给客户端
        session.sendMsg(MsgDef.ServerCmd.FRIEHND_MSG, processFriendPlayerMsgRet(opstype, friendUid, '', 0, 0, 0, True))
        if None != friendSession:
            friendSession.sendMsg(MsgDef.ServerCmd.FRIEHND_MSG, processFriendPlayerMsgRet(opstype, uid, session.player.name, session.player.job, session.player.gender, session.player.level, True))
        return
    #用户删除好友的语句
    if opstype == MsgDef.FriendOpsClientCmd.DEL_LISTFRIEND:
        #判断是否为好友
        # if None == session.player.friendCtrl.getFriendByUid(friendUid):
        #     session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, MsgDef.ClientCmd.FRIENDLIST_OPS, '不是好友，无法进行删除'))
        #     return
        #从数据库中将好友关系删除
        DbService.getFriendService().delFriend(uid, friendUid)
        session.player.friendCtrl.delFriend(friendUid)
        session.sendMsg(MsgDef.ServerCmd.FRIEHND_MSG, processFriendPlayerMsgRet(opstype, friendUid, '', 0, 0, 0, True))
        #数据库操作成功，给用户返回删除好友正常的信息
        if None         != friendSession:
            #如果好友在线，则将好友删除信息反馈给好友
            friendSession.player.friendCtrl.delFriend(uid)
            friendSession.sendMsg(MsgDef.ServerCmd.FRIEHND_MSG, processFriendPlayerMsgRet(opstype, uid, '', 0, 0, 0, True))
        return
        #将ID加入仇人列表中
    #将ID加入仇人列表中
    if opstype == MsgDef.FriendOpsClientCmd.ADD_ENEMY:
        #如果对方不在线，提示用户，对方不在线，不能添加
        if None == friendSession:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, MsgDef.ClientCmd.FRIENDLIST_OPS, '对方不在线，无法添加'))
            return
        if checkUserEnemy(session, friendUid):
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, MsgDef.ClientCmd.FRIENDLIST_OPS, '对方已在您的仇人列表中'))
            return
        #将好友关系写入数据库
        DbService.getFriendService().addEnemy(uid, friendUid, 0)
        session.player.friendCtrl.addEnemy(friendSession.player)
        session.sendMsg(MsgDef.ServerCmd.FRIEHND_MSG, processFriendPlayerMsgRet(opstype, friendUid, friendSession.player.name, friendSession.player.job, friendSession.player.gender, friendSession.player.level, True))
        return
    #将ID从仇人列表中删除
    if opstype == MsgDef.FriendOpsClientCmd.DEL_ENEMY:
        if not checkUserEnemy(session, friendUid):
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, MsgDef.ClientCmd.FRIENDLIST_OPS, '对方不在您的仇人列表中'))
            return
        #将好友关系写入数据库
        DbService.getFriendService().delEnemy(uid, friendUid, 0)
        session.player.friendCtrl.delEnemyByUid(friendUid)
        session.sendMsg(MsgDef.ServerCmd.FRIEHND_MSG, processFriendPlayerMsgRet(opstype, friendUid, '', 0, 0, 0, True))
        return
    #将ID加入屏蔽列表中
    if opstype == MsgDef.FriendOpsClientCmd.ADD_SHIELD:
        #如果对方不在线，提示用户，对方不在线，不能添加
        if None == friendSession:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, MsgDef.ClientCmd.FRIENDLIST_OPS, '对方不在线，无法添加'))
            return
        if checkUserShieldPerson(session, friendUid):
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, MsgDef.ClientCmd.FRIENDLIST_OPS, '对方已在您的屏蔽列表中'))
            return
        #将好友关系写入数据库
        DbService.getFriendService().addEnemy(uid, friendUid, 1)
        session.player.friendCtrl.addShieldPerson(friendSession.player)
        session.sendMsg(MsgDef.ServerCmd.FRIEHND_MSG, processFriendPlayerMsgRet(opstype, friendUid, friendSession.player.name, friendSession.player.job, friendSession.player.gender, friendSession.player.level, True))
        return
    #将ID从仇人列表中删除
    if opstype == MsgDef.FriendOpsClientCmd.DEL_SHIELD:
        if not checkUserShieldPerson(session, friendUid):
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, MsgDef.ClientCmd.FRIENDLIST_OPS, '对方不在您的屏蔽列表中'))
            return
        #将好友关系写入数据库
        DbService.getFriendService().delEnemy(uid, friendUid, 1)
        session.player.friendCtrl.deShieldPersonByUid(friendUid)
        session.sendMsg(MsgDef.ServerCmd.FRIEHND_MSG, processFriendPlayerMsgRet(opstype, friendUid, '', 0, 0, 0, True))
        return


        
#判断是否为仇人
def checkUserEnemy(session, eid):
    if None == session.player.friendCtrl.getEnemyByUid(eid):
        return False
    return True
#判断是否屏蔽
def checkUserShieldPerson(session, eid):
    if None == session.player.friendCtrl.getShieldPersonByUid(eid):
        return False
    return True
#用于返回错误信息的函数
def processErrorMsgRet(opstype, cmd, msg):
    ret_msg                 = MsgDef.ErrorMsgRet()
    ret_msg.errType         = opstype                        #错误信息所处位置opstype
    ret_msg.cmd             = cmd                               #错误信息所处位置cmd
    ret_msg.errMsg          = msg                               #错误信息
    return ret_msg

def processFriendPlayerMsg(uid, name, job, gender, level, online, mapname=None, x=None , y=None):
    ret_msg                 = MsgDef.FriendPlayerMsg()
    ret_msg.uid             = uid
    ret_msg.name            = name
    ret_msg.job             = job
    ret_msg.gender          = gender
    ret_msg.level           = level
    ret_msg.online          = online
    ret_msg.mapname         = mapname
    ret_msg.x               = x
    ret_msg.y               = y
    return ret_msg
def processFriendPlayerMsgRet(opstype, uid, name, job, gender, level, online):
    ret_msg                 = MsgDef.FriendMsgRet()
    ret_msg.opstype         = opstype
    ret_msg.uid             = uid
    ret_msg.name            = name
    ret_msg.job             = job
    ret_msg.gender          = gender
    ret_msg.level           = level
    ret_msg.online          = online
    return ret_msg