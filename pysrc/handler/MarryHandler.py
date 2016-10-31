# -*- coding: utf-8 -*-
import ffext
import json
import weakref
import idtool
import msgtype.ttypes as MsgDef
from base import Base
from model import  MarryModel, TeamModel, ItemModel
from handler import ItemHandler
from db import DbServicePlayer as DbServicePlayer
from db import DbService

def buildErrMsg(cmd, errMsg):
    return MsgDef.ErrorMsgRet(0, cmd, errMsg)#'cmd=%d,errMsg=%s'%(cmd, errMsg)
def buildMarryItem(item, pos, itemObj):
    item.posid = pos
    item.itemCfgId = itemObj.cfgId
    return True
def buildMarryRoom(room, id1, id2):
    room.roomId = idtool.allocId()
    room.uid1 = id1
    room.uid2 = id2
    return True

# 请帖最大文本长度
WEDDING_SEND_MAX_STR = 256
WEDDING_SEND_MAX_PLAYER = 20
# 结婚任务ID
MARRY_TASK_ID = 10001
#婚禮時間
WEDDING_INTERVAL = 60*2
# 双双和谐离婚最终间隔-暂定60秒
WEDDING_END_INTERVAL = 1#60*60*24*3 # 3 * 24 * 3600
# 夫妻技能ID
WEDDING_SKILL_ID = 2011

def processOffline(session):#MARRY_OFFLINE
    cmd =1
    opstype = 2
    player = session.player
    #ffext.error('111 %d'%(player.uid))
    #ffext.error('111 1 %d'%(player.uid))
    opstype = 17#MsgDef.MarriageClientCmd.MARRY_OFFLINE
    
    #ffext.error('222 %d'%(player.uid))
    marryTotalInfo = player.marriageCtrl.marryTotalInfo
    #ffext.error('333 %d'%(player.uid))
    if not marryTotalInfo:
        marryTotalInfo = player.tmpInfo.get('_marry_task_apply_')
        #ffext.error('111 44 %d'%(player.uid))
    if marryTotalInfo:
        #ffext.error('111 5 %d'%(player.uid))
        anotherInfo = marryTotalInfo.getInfoByAnotherGender(player.gender)
        mateSession = ffext.getSessionMgr().findByUid(anotherInfo.uid)
        if mateSession:
            #ffext.error(' 6 %d'%(player.uid))
            retMsg = processMarryOpsMsgRet(opstype, player, 0, 0, '', 0)
            mateSession.sendMsg(MsgDef.ServerCmd.MARRIAGE_OPS_MSG, retMsg)
            if mateSession.player.tmpInfo.get('_marry_task_apply_') == marryTotalInfo:
                mateSession.player.tmpInfo['_marry_task_apply_'] = None
        return

    
#结婚操作过程
@ffext.onLogic(MsgDef.ClientCmd.MARRIAGE_OPS, MsgDef.MarriageOpsReq)
def processMarryOPS(session, msg):
    #ffext.dump('processMarryOPS', msg)
    opstype = msg.opstype
    cmd     = MsgDef.ClientCmd.MARRIAGE_OPS
    player  = session.player

    if opstype == MsgDef.MarriageClientCmd.MARRY_QUERY_STATUS:#查询结婚状态
        retMsg = processMarryOpsMsgRet(opstype, player, player.marriageCtrl.marryFlag, 0, '', 0)
        #print(retMsg)
        session.sendMsg(MsgDef.ServerCmd.MARRIAGE_OPS_MSG, retMsg)
        return
    elif opstype == MsgDef.MarriageClientCmd.MARRY_APPLY_TASK:
        marryTotalInfo = player.marriageCtrl.marryTotalInfo
        nextTaskId = MARRY_TASK_ID
        # if marryTotalInfo:#直接接任务
        #     if session.player.marriageCtrl.getStatus() != MsgDef.MarryStatusCmd.MARRY_STATUS_NOT:
        #         session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '不能领取任务！'))
        #         return
        #     session.player.marriageCtrl.setStatus(MsgDef.MarryStatusCmd.MARRY_STATUS_TASK_GO)
        #
        #     for taskid, task in session.player.taskCtrl.allTask.iteritems():
        #         session.player.taskCtrl.delTaskById(taskid)
        #         newTask = session.player.taskCtrl.addTaskById(nextTaskId, False)
        #         if newTask:
        #             DbService.getPlayerService().replaceTask(session.player, newTask, taskid)
        #         break
        #     from handler import  TaskHandler
        #     TaskHandler.processQueryTask(session)
        #     session.sendMsg(MsgDef.ServerCmd.MARRIAGE_OPS_MSG, processMarryOpsMsgRet(opstype, session.player, MsgDef.MarryStatusCmd.MARRY_STATUS_TASK_GO))
        #     DbService.getPlayerService().updateMarry(marryTotalInfo)
        #     return
        team = TeamModel.getTeamMgr().getTeamById(session.player.teamCtrl.teamID)
        if not team:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '请先组队！'))
            return
        if len(team.getTeamMember()) != 2:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '请先组队2人！'))
            return
        if player.isMarry():
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '你已经结婚！'))
            return
        destPlayer = None
        mateSession = None
        marryTotalInfo = None
        for key, valdata in team.getTeamMember().iteritems():
            mateSession = ffext.getSessionMgr().findByUid(valdata.uid)
            if not mateSession:
                session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '队伍异常:%d'%(valdata.uid)))
                continue
            val = mateSession.player
            if val.uid != session.player.uid:
                if val.gender == player.gender:
                    session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '性别不符！'))
                    return
                mateUid = val.uid
                destPlayer = val
                if destPlayer.isMarry():
                    session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '对方已经结婚！'))
                    return
                husbend = player
                wife    = val
                if player.gender == Base.Gender.FEMAIL:
                    husbend = val
                    wife    = player
                strFlag = player.tmpInfo.get('_marry_task_apply_')
                marryTotalInfo = None
                if strFlag == None:
                    flag2 = destPlayer.tmpInfo.get('_marry_task_apply_')
                    if flag2 != None:
                        marryTotalInfo = flag2
                    else:
                        marryTotalInfo = MarryModel.getMarryMgr().allocMarryTotalInfo(husbend, wife)
                    player.tmpInfo['_marry_task_apply_'] = marryTotalInfo
                    session.player.marriageCtrl.setStatus(MsgDef.MarryStatusCmd.MARRY_STATUS_TASK_GO)

                if destPlayer.tmpInfo.get('_marry_task_apply_')  == None:
                    session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '等待对方确认！'))
                    husbend.sendMsg(MsgDef.ServerCmd.MARRIAGE_OPS_MSG, processMarryOpsMsgRet(opstype, session.player,
                                                                                             MsgDef.MarryStatusCmd.MARRY_STATUS_TASK_GO, 0, '',0, 0, marryTotalInfo))
                    wife.sendMsg(MsgDef.ServerCmd.MARRIAGE_OPS_MSG, processMarryOpsMsgRet(opstype, session.player,
                                                                                             MsgDef.MarryStatusCmd.MARRY_STATUS_TASK_GO,
                                                                                             0, '', 0, 0,
                                                                                             marryTotalInfo))
                    return

                # marryTotalInfo = MarryModel.allockMarryInfo()

                #wife.marriageCtrl.setStatus(MsgDef.MarryStatusCmd.MARRY_STATUS_TASK_GO)
                ffext.dump('dump marry', marryTotalInfo)
                break
        #领取结婚任务         | 未婚-结婚进行中任务
        nextTaskId = MARRY_TASK_ID
        for taskid, task in session.player.taskCtrl.allTask.iteritems():
            session.player.taskCtrl.delTaskById(taskid)
            newTask = session.player.taskCtrl.addTaskById(nextTaskId, False)
            if newTask:
                DbService.getPlayerService().replaceTask(session.player, newTask, taskid)
            break
        for taskid, task in destPlayer.taskCtrl.allTask.iteritems():
            destPlayer.taskCtrl.delTaskById(taskid)
            newTask = destPlayer.taskCtrl.addTaskById(nextTaskId, False)
            if newTask:
                DbService.getPlayerService().replaceTask(destPlayer, newTask, taskid)
            break
        from handler import  TaskHandler
        TaskHandler.processQueryTask(session)
        TaskHandler.processQueryTask(destPlayer.session)

        session.sendMsg(MsgDef.ServerCmd.MARRIAGE_OPS_MSG, processMarryOpsMsgRet(opstype, session.player, MsgDef.MarryStatusCmd.MARRY_STATUS_TASK_GO))
        destPlayer.sendMsg(MsgDef.ServerCmd.MARRIAGE_OPS_MSG, processMarryOpsMsgRet(opstype, session.player, MsgDef.MarryStatusCmd.MARRY_STATUS_TASK_GO))

        DbService.getPlayerService().addMarry(player, player.marriageCtrl.marryId, mateSession.player.uid, ffext.getTime())
        DbService.getPlayerService().updateMarry(marryTotalInfo)
        player.tmpInfo['_marry_task_apply_'] = None
        destPlayer.tmpInfo['_marry_task_apply_'] = None
        return

    elif opstype == MsgDef.MarriageClientCmd.MARRY_GIVEUP_TASK:#13:放弃结婚任务
        if not player.marriageCtrl:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, 'CTRL错误！'))
            return
        marryTotalInfo = player.marriageCtrl.marryTotalInfo
        if not marryTotalInfo or marryTotalInfo.coupleData[0].status != MsgDef.MarryStatusCmd.MARRY_STATUS_TASK_GO:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '未领取任务！'))
            return
        anotherInfo = marryTotalInfo.getInfoByAnotherGender(player.gender)
        destPlayer  = player.mapObj.getPlayerById(anotherInfo.uid)
        mateSession = None
        if destPlayer:
            mateSession = destPlayer.session

        marryTotalInfo.getInfoByGender(player.gender).status = MsgDef.MarryStatusCmd.MARRY_STATUS_NOT
        marryTotalInfo.getInfoByAnotherGender(player.gender).status = MsgDef.MarryStatusCmd.MARRY_STATUS_NOT

        MarryModel.getMarryMgr().delMarryById(marryTotalInfo.marryId)
        DbService.getPlayerService().updateMarryDivorce(marryTotalInfo.marryId)
        DbService.getPlayerService().updateMarryDivorcePlayer(player.uid)
        DbService.getPlayerService().updateMarryDivorcePlayer(anotherInfo.uid)


        # 提交任务             | 结婚进行中任务 - 已婚
        task = session.player.taskCtrl.getTask(MARRY_TASK_ID)
        if task:
            from model import TaskModel
            task.status = TaskModel.TaskStatus.FINISH
            session.player.taskCtrl.checkNewTask(task)
            from handler import  TaskHandler
            TaskHandler.processQueryTask(session)

            ffext.dump('dump marry', marryTotalInfo)

        player.marriageCtrl.divorceForce()
        player.tmpInfo['_marry_task_apply_'] = None
        # 发送回包
        ret_msg = processMarryOpsMsgRet(opstype, session.player, MsgDef.MarryStatusCmd.MARRY_STATUS_NOT)
        session.sendMsg(MsgDef.ServerCmd.MARRIAGE_OPS_MSG, ret_msg)

        if destPlayer:
            task2 = destPlayer.taskCtrl.getTask(MARRY_TASK_ID)
            if task2:
                from model import TaskModel
                task2.status = TaskModel.TaskStatus.FINISH
                destPlayer.taskCtrl.checkNewTask(task2)
                from handler import  TaskHandler
                TaskHandler.processQueryTask(mateSession)

            destPlayer.marriageCtrl.divorceForce()
            # 发送回包
            ret_msg = processMarryOpsMsgRet(opstype, destPlayer, MsgDef.MarryStatusCmd.MARRY_STATUS_NOT)
            mateSession.sendMsg(MsgDef.ServerCmd.MARRIAGE_OPS_MSG, ret_msg)
            
            destPlayer.tmpInfo['_marry_task_apply_'] = None

        return
    elif opstype == MsgDef.MarriageClientCmd.MARRY_COMMIT_TASK:
        if not player.marriageCtrl:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, 'CTRL错误！'))
            return
        marryTotalInfo = player.marriageCtrl.marryTotalInfo
        if not marryTotalInfo:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '未领取任务！'))
            return
        anotherInfo = marryTotalInfo.getInfoByAnotherGender(player.gender)
        destPlayer  = player.mapObj.getPlayerById(anotherInfo.uid)
        #ffext.dump('MARRRRRRRRRRRRR!')
        task = player.taskCtrl.getTask(MARRY_TASK_ID)
        ffext.dump('MARRYTASK', task)
        if task:
            from model import TaskModel
            task.status = TaskModel.TaskStatus.FINISH
            player.taskCtrl.checkNewTask(task)
            from handler import  TaskHandler
            TaskHandler.processQueryTask(session)

            ffext.dump('dump marry', marryTotalInfo)
            marryTotalInfo.getInfoByGender(player.gender).status = MsgDef.MarryStatusCmd.MARRY_STATUS_TASK_FINISH

        mateSession = None
        if destPlayer:
            mateSession = destPlayer.session

        status1 = marryTotalInfo.getInfoByGender(player.gender).status
        status2 = marryTotalInfo.getInfoByAnotherGender(player.gender).status
        #ffext.dump('STATUS1',status1)
        #ffext.dump('STATUS2',status2)
        #ffext.dump('MARRRRRRRRRRRRR!')
        if status1 == MsgDef.MarryStatusCmd.MARRY_STATUS_TASK_FINISH and status1 == status2:
            marryTotalInfo.getInfoByGender(player.gender).status = MsgDef.MarryStatusCmd.MARRY_STATUS_MARRIED
            marryTotalInfo.getInfoByAnotherGender(player.gender).status = MsgDef.MarryStatusCmd.MARRY_STATUS_MARRIED
        DbService.getPlayerService().updateMarry(marryTotalInfo)
        session.sendMsg(MsgDef.ServerCmd.MARRIAGE_OPS_MSG, processMarryOpsMsgRet(opstype, destPlayer, MsgDef.MarryStatusCmd.MARRY_STATUS_TASK_FINISH))
        destPlayer.sendMsg(MsgDef.ServerCmd.MARRIAGE_OPS_MSG, processMarryOpsMsgRet(opstype, destPlayer, MsgDef.MarryStatusCmd.MARRY_STATUS_TASK_FINISH))

        return
    elif opstype == MsgDef.MarriageClientCmd.MARRY_SEND:
        # 发请帖
        friends = session.player.friendCtrl.getFriend()
        friends_lst = []
        for k, v in friends.iteritems():
            friends_lst.append(v.name)
        #ffext.dump('Friends_lst', friends_lst)
        msg.visitors = friends_lst
        ffext.dump('QINGTIEMSG', msg)
        if msg.visitors == None:
            return
        if len(msg.visitors) > WEDDING_SEND_MAX_PLAYER:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '邀请人数太多了！'))
            return
        if len(msg.msg) > WEDDING_SEND_MAX_STR:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '请帖文字太长了！'))
            return
        marryTotalInfo = session.player.marriageCtrl.marryTotalInfo
        marryTotalInfo.flagXiTie += 1
        hasSend = []
        for k in msg.visitors:
            if k in hasSend:
                continue
            hasSend.append(k)
            #查找所有的被邀请者的“姓名”
            otherSession = ffext.getSessionMgr().getSessionByName(k)
            if otherSession:
                toPlayer = otherSession.player
                msg = msg.msg + '\n\n\n\n' + '系统提醒:请去结婚界面确认是否参加婚礼!'
                title = None
                #ffext.dump('喜帖!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
                session.player.mailCtrl.sendMail(toPlayer.uid, 0, title, msg)
                otherSession.sendMsg(MsgDef.ServerCmd.MARRIAGE_OPS_MSG, processMarryOpsMsgRet(opstype,session.player, MsgDef.MarryStatusCmd.MARRY_STATUS_MARRIED, 0, msg.msg))
        #状态变化，更新数据库
        DbService.getPlayerService().updateMarry(marryTotalInfo)
        session.sendMsg(MsgDef.ServerCmd.MARRIAGE_OPS_MSG, processMarryOpsMsgRet(opstype,session.player, MsgDef.MarryStatusCmd.MARRY_STATUS_MARRIED, 0, msg.msg))
        return
    elif opstype == MsgDef.MarriageClientCmd.MARRY_APPLY_WEDDING:#申请结婚
        marryTotalInfo = player.marriageCtrl.marryTotalInfo
        if not marryTotalInfo:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '先完成結婚任務！'))
            return
        if marryTotalInfo.flagWeding != MsgDef.WeddingFlagCmd.WEDDING_NOT_APPLY and marryTotalInfo.flagWeding != MsgDef.WeddingFlagCmd.WEDDING_FAIL:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '已经申请过！'))
            return

        mate = marryTotalInfo.getInfoByAnotherGender(player.gender)
        otherPlayer = player.mapObj.getPlayerById(mate.uid)
        if not otherPlayer:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '配有没有在线！'))
            return
        strFlag = player.tmpInfo.get('_wedding_apply_')
        if strFlag == None:
            player.tmpInfo['_wedding_apply_'] = True
        strFlag2 = otherPlayer.tmpInfo.get('_wedding_apply_')
        if strFlag2 == None:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '等待配偶确认！'))
            ret_msg = processMarryOpsMsgRet(opstype, player)
            session.sendMsg(MsgDef.ServerCmd.MARRIAGE_OPS_MSG, ret_msg)
            ret_msg = processMarryOpsMsgRet(opstype, otherPlayer)
            otherPlayer.sendMsg(MsgDef.ServerCmd.MARRIAGE_OPS_MSG, ret_msg)
            return
        player.tmpInfo['_wedding_apply_'] = None
        otherPlayer.tmpInfo['_wedding_apply_'] = None
        
        marryTotalInfo.flagWeding = MsgDef.WeddingFlagCmd.WEDDING_APPLYED
        leftSec = WEDDING_INTERVAL
        marryTotalInfo.tmWedding  = ffext.getTime() + leftSec #1 分钟后开始

        marryId = marryTotalInfo.marryId
        def cb():
            MarryModel.handleTimerWedding(marryId)
        ffext.timer(leftSec*1000, cb)
        ret_msg = processMarryOpsMsgRet(opstype, player)
        session.sendMsg(MsgDef.ServerCmd.MARRIAGE_OPS_MSG, ret_msg)
        #状态变化，更新数据库
        DbService.getPlayerService().updateMarry(marryTotalInfo)

        if mate:
            marryPlayer = ffext.getSessionMgr().findByUid(mate.uid)
            if marryPlayer:
                marryPlayer.sendMsg(MsgDef.ServerCmd.MARRIAGE_OPS_MSG, ret_msg)
        return
    elif opstype == MsgDef.MarriageClientCmd.MARRY_QUERY_ALL_MARRIAGE:##12:查询所有夫妻，方便参加婚礼
        allMarriage = MarryModel.getAllMarriage()
        ret_msg = processMarryOpsMsgRet(opstype, None)
        ret_msg.allMarriageInfo = []
        num = 0
        for k, marryTotalInfo in allMarriage.iteritems():
            num += 1
            if num >= 100:
                break
            if marryTotalInfo.flagWeding != MsgDef.WeddingFlagCmd.WEDDING_APPLYED:
                continue
            baseInfo = MsgDef.MarriageBaseInfo(marryTotalInfo.marryId, [], [])
            for k in marryTotalInfo.coupleData:
                num += 1
                if num >= 100:
                    break
                tmpmsg = MsgDef.MarriagePlayerMsg()
                tmpmsg.uid                     = k.uid
                tmpmsg.name                    = k.name
                tmpmsg.job                     = k.job
                tmpmsg.gender                  = k.gender
                tmpmsg.level                   = k.level
                tmpmsg.status                   = k.status
                baseInfo.coupleData.append(tmpmsg)
            for k in marryTotalInfo.listAttends:
                num += 1
                if num >= 100:
                    break
                tmpmsg = MsgDef.MarriagePlayerMsg()
                tmpmsg.uid                     = k.uid
                tmpmsg.name                    = k.name
                tmpmsg.job                     = k.job
                tmpmsg.gender                  = k.gender
                tmpmsg.level                   = k.level
                tmpmsg.status                   = k.status
                baseInfo.listAttends.append(tmpmsg)
            ret_msg.allMarriageInfo.append(baseInfo)
        session.sendMsg(MsgDef.ServerCmd.MARRIAGE_OPS_MSG, ret_msg)
    elif opstype == MsgDef.MarriageClientCmd.MARRY_ATTEND_WEEDING:
        # 参加婚礼，扣礼金，发道具
        marryTotalInfo = MarryModel.getMarryMgr().getMarryTotalInfo(msg.marryId)
        #marryPlayer = ffext.getSessionMgr().findByUid(msg.marryUid)
        if not marryTotalInfo:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, "对方还未结婚!"))
            return
        gold = 500
        item1 = 1040188
        item2 = 1040189
        if player.gold < gold:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, "金币不足500!"))
            return
        for k in marryTotalInfo.listAttends:
            if k.uid == player.uid:
                session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '不可重复报名!'))
                return
        player.addGold(gold * -1, True)
        itemObj = player.itemCtrl.addItemByCfgId(item1)
        if not itemObj:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '系统忙!'))
           # return
        itemObj2 = player.itemCtrl.addItemByCfgId(item2)
        if not itemObj2:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '系统忙!'))
            #return

        ItemHandler.processQueryPkg(session)
        # 增加总礼金，添加到列表
        marryTotalInfo.totalGold += gold
        #playerTmpInfo = MarryModel.PlayerMarryInfo()
        #playerTmpInfo.setPlayerMarryInfo(player)
        playerTmpInfo = MsgDef.MarriagePlayerMsg(player.uid, player.name, player.job, player.gender, player.level)
        marryTotalInfo.listAttends.append(playerTmpInfo)
        DbService.getPlayerService().updateMarry(marryTotalInfo)

        #(opstype, player, flag = 0, delTime = 0, msg = '', gold = 0, skillId = 0, marryTotalInfo = None):
        ret_msg = processMarryOpsMsgRet(opstype,session.player, MsgDef.MarryStatusCmd.MARRY_STATUS_MARRIED, 0, '', gold, 0, marryTotalInfo)
        addItem2MarryPlayerMsg(ret_msg, itemObj, 1)
        addItem2MarryPlayerMsg(ret_msg, itemObj2, 1)

        session.sendMsg(MsgDef.ServerCmd.MARRIAGE_OPS_MSG, ret_msg)
        return
    elif opstype == MsgDef.MarriageClientCmd.MARRY_NEW_LIST:
        # 新房列表
        retMsg = processMarryOpsMsgRet(opstype, session.player, MsgDef.MarryStatusCmd.MARRY_STATUS_MARRIED, 0, '', 0)
        allMarriage = MarryModel.getAllMarriage()
        for k, marryTotalInfo in allMarriage.iteritems():
            #if marryTotalInfo.flagWeding != MsgDef.WeddingFlagCmd.WEDDING_APPLYED and marryTotalInfo.flagWeding != MsgDef.WeddingFlagCmd.WEDDING_FINISH:
            #    continue
            if len(marryTotalInfo.coupleData) == 2 and marryTotalInfo.coupleData[0].status == MsgDef.MarryStatusCmd.MARRY_STATUS_MARRIED:
                marryMsg = processMarriageVisitListBaseInfo(marryTotalInfo.marryId, marryTotalInfo.coupleData[0], marryTotalInfo.coupleData[1], marryTotalInfo.tmWedding)
                retMsg.listVisitHouseInfo.append(marryMsg)
            pass
        session.sendMsg(MsgDef.ServerCmd.MARRIAGE_OPS_MSG, retMsg)
        return
    elif opstype == MsgDef.MarriageClientCmd.MARRY_VISIT_HOUSE:
        # 我要参观其他新房
        mId = msg.marryId
        allMarriage = MarryModel.getAllMarriage()
        marryInfo = allMarriage.get(mId)
        if not marryInfo:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '结婚ID:%d不存在！'%(mId)))
            return
        mItems = []
        for k, xItem in marryInfo.listSetItems.iteritems():
            #mItems.append(xItem)
            mItems.append(MsgDef.MarriageItem(k, xItem.get('itemCfgId', 0)))
        marryMsg = processMarriageVisitListBaseInfo(mId, marryInfo.coupleData[0], marryInfo.coupleData[1], marryInfo.tmWedding, mItems)

        retMsg = processMarryOpsMsgRet(opstype,session.player, MsgDef.MarryStatusCmd.MARRY_STATUS_MARRIED, 0, '', 0)
        retMsg.otherHouseInfo = marryMsg
        session.sendMsg(MsgDef.ServerCmd.MARRIAGE_OPS_MSG, retMsg)
        ffext.dump('xxx', retMsg)
        return
    elif opstype == MsgDef.MarriageClientCmd.MARRY_SET_HOUSE_ITEM:
        # 装点新房
        if not player.isMarry():
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, "请先结婚!"))
            return
        if msg.housePos < MsgDef.MarriageHousePos.MARRY_HOUSE_POS_1 or \
            msg.housePos > MsgDef.MarriageHousePos.MARRY_HOUSE_POS_6:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, "位置错误!"))
            return

        itemToSetCfgId = 0
        item = player.itemCtrl.getItem(msg.houseItemId)
        if item:
            itemToSetCfgId = item.itemCfg.cfgId
            player.itemCtrl.delItem(msg.houseItemId)
        else:
            itemToSetCfgId = msg.houseItemId
            setItemCfg = ItemModel.getItemMgr().getCfgByCfgId(itemToSetCfgId)
            if not setItemCfg:
                session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, "Item Id not exists! %d"%(msg.houseItemId)))
                return
            setItemHaveNum = player.itemCtrl.countItemNumbyCfgId(itemToSetCfgId)
            if setItemHaveNum < 1:
                session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, "You do not have Item!"))
                return
            # 删除道具
            player.itemCtrl.subItemNumByCfgId(itemToSetCfgId, 1)
        # 设置到marriageCtl.marryTotalInfo
        player.marriageCtrl.marryTotalInfo.addSetItem(msg.housePos, itemToSetCfgId)


        ret_msg = processMarryOpsMsgRet(opstype, session.player, MsgDef.MarryStatusCmd.MARRY_STATUS_MARRIED, 0, '', 0)
        #addItem2MarryPlayerMsgEx(ret_msg, msg.housePos, itemToSetCfgId)
        session.sendMsg(MsgDef.ServerCmd.MARRIAGE_OPS_MSG, ret_msg)

        #更新数据库
        itemStr = player.marriageCtrl.marryTotalInfo.toJson4SetItems()
        extraStr = player.marriageCtrl.marryTotalInfo.toJson4Extra()
        DbService.getPlayerService().updateMarryItem(player.uid, player.marriageCtrl.marryId, itemStr, extraStr)
        return
    elif opstype == MsgDef.MarriageClientCmd.MARRY_LEARN_COUPLE_SKILL:
        # 学习夫妻技能
        skillLevel = 1
        retErr = player.skillCtrl.learnSkill(WEDDING_SKILL_ID, skillLevel)
        if retErr:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '学习技能%d失败，原因:%s!' % (WEDDING_SKILL_ID, retErr)))
            return
        session.sendMsg(MsgDef.ServerCmd.LEARN_SKILL, MsgDef.LearnSkillRet(WEDDING_SKILL_ID, skillLevel))
        retMsg = processMarryOpsMsgRet(opstype, session.player, MsgDef.MarryStatusCmd.MARRY_STATUS_MARRIED, 0, '', 0, WEDDING_SKILL_ID)
        session.sendMsg(MsgDef.ServerCmd.MARRIAGE_OPS_MSG, retMsg)
        return
    elif opstype == MsgDef.MarriageClientCmd.MARRY_DIVORCE_NORMAL:
        # 和谐离婚             | 已婚-离婚中-（update消息）-未婚
        if player.marriageCtrl.marryFlag != MsgDef.MarryStatusCmd.MARRY_STATUS_MARRIED:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '不可以离婚!'))
            return
        marryTotalInfo = player.marriageCtrl.marryTotalInfo
        myMarryInfo = player.marriageCtrl.marryTotalInfo.getInfoByGender(player.gender)
        if not myMarryInfo:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '未知错误!'))
            return
        mateMarryInfo = player.marriageCtrl.marryTotalInfo.getInfoByAnotherGender(player.gender)
        if not mateMarryInfo:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '未知错误!!'))
            return
        matePlayer = player.mapObj.getPlayerById(mateMarryInfo.uid)
        #ffext.dump('mateplayer', matePlayer)
        if not matePlayer:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '配偶没有在线!'))
            return
        player.tmpInfo['_marry_divorce_apply_'] = True
        if matePlayer.tmpInfo.get('_marry_divorce_apply_') == None:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '等待配偶确认!'))
            ret_msg = processMarryOpsMsgRet(opstype, session.player, MsgDef.MarryStatusCmd.MARRY_STATUS_DIVORCING, 0,'', 0)
            if ret_msg.baseInfo.coupleData[0].uid == player.uid:
                ret_msg.baseInfo.coupleData[0].status = MsgDef.MarryStatusCmd.MARRY_STATUS_DIVORCING
            else:
                ret_msg.baseInfo.coupleData[1].status = MsgDef.MarryStatusCmd.MARRY_STATUS_DIVORCING
            #if ret_msg.baseInfo.coupleData[0].statu != ret_msg.baseInfo.coupleData[1].statu:
                #ret_msg.baseInfo.coupleData[0].status = MsgDef.MarryStatusCmd.MARRY_STATUS_MARRIED
                #ret_msg.baseInfo.coupleData[1].status = MsgDef.MarryStatusCmd.MARRY_STATUS_MARRIED
            session.sendMsg(MsgDef.ServerCmd.MARRIAGE_OPS_MSG, ret_msg)
            matePlayer.sendMsg(MsgDef.ServerCmd.MARRIAGE_OPS_MSG, ret_msg)
            return

        player.tmpInfo['_marry_divorce_apply_'] = None
        matePlayer.tmpInfo['_marry_divorce_apply_'] = None

        myMarryInfo.status = MsgDef.MarryStatusCmd.MARRY_STATUS_DIVORCING
        mateMarryInfo.status = MsgDef.MarryStatusCmd.MARRY_STATUS_DIVORCING

        allFlag = True
        delTime = ffext.getTime() + WEDDING_END_INTERVAL
        # 发送回包
        ret_msg = processMarryOpsMsgRet(opstype, session.player, MsgDef.MarryStatusCmd.MARRY_STATUS_DIVORCING, 0, '', 0)
        if allFlag:
            ret_msg.delTime = delTime
        player.skillCtrl.deleteSkill(WEDDING_SKILL_ID, True)
        matePlayer.skillCtrl.deleteSkill(WEDDING_SKILL_ID, True)
        from handler import SkillHandler
        SkillHandler.processQuerySkill(session)
        SkillHandler.processQuerySkill(matePlayer.session)
        session.sendMsg(MsgDef.ServerCmd.MARRIAGE_OPS_MSG, ret_msg)
        matePlayer.sendMsg(MsgDef.ServerCmd.MARRIAGE_OPS_MSG, ret_msg)

        #离婚确定定时器
        def divorceCB():
            MarryModel.handleTimerDivorce(marryTotalInfo.marryId)
        if allFlag:
            # 对方也和谐离婚， 定时器开始
            if WEDDING_END_INTERVAL == 1:
                ffext.timer(WEDDING_END_INTERVAL * 100, divorceCB)
            else:
                ffext.timer(WEDDING_END_INTERVAL * 1000, divorceCB)
            marryTotalInfo.tmEndWedding = delTime
            DbService.getPlayerService().updateMarry(player.marriageCtrl.marryTotalInfo)
    elif opstype == MsgDef.MarriageClientCmd.MARRY_DIVORCE_QUIT:#取消离婚
        myMarryInfo = player.marriageCtrl.marryTotalInfo.getInfoByGender(player.gender)
        if myMarryInfo.status != MsgDef.MarryStatusCmd.MARRY_STATUS_DIVORCING:
            if player.tmpInfo.get('_marry_divorce_apply_') != None:
                player.tmpInfo['_marry_divorce_apply_'] = None
                ret_msg = processMarryOpsMsgRet(opstype, session.player, MsgDef.MarryStatusCmd.MARRY_STATUS_MARRIED, 0, '')
                session.sendMsg(MsgDef.ServerCmd.MARRIAGE_OPS_MSG, ret_msg)

                mateInfo = player.marriageCtrl.marryTotalInfo.getInfoByAnotherGender(player.gender)
                matePlayer = player.mapObj.getPlayerById(mateInfo.uid)
                if  matePlayer:
                    matePlayer.sendMsg(MsgDef.ServerCmd.MARRIAGE_OPS_MSG, ret_msg)
                return
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '未申请和谐离婚!'))
            return
        myMarryInfo.status = MsgDef.MarryStatusCmd.MARRY_STATUS_MARRIED
        mateInfo = player.marriageCtrl.marryTotalInfo.getInfoByAnotherGender(player.gender)
        mateInfo.status = MsgDef.MarryStatusCmd.MARRY_STATUS_MARRIED
        DbService.getPlayerService().updateMarry(player.marriageCtrl.marryTotalInfo)
        # 发送回包
        ret_msg = processMarryOpsMsgRet(opstype, session.player, MsgDef.MarryStatusCmd.MARRY_STATUS_MARRIED, 0, '')
        session.sendMsg(MsgDef.ServerCmd.MARRIAGE_OPS_MSG, ret_msg)
        return
    elif opstype == MsgDef.MarriageClientCmd.MARRY_DIVORCE_FORCE:
        # 强制离婚             | 已婚-未婚
        if player.marriageCtrl.marryFlag != MsgDef.MarryStatusCmd.MARRY_STATUS_MARRIED:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '不可以离婚!'))
            return
        needGold = 1000000
        if player.gold < needGold:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, "金币不足!"))
            return
        marryTotalInfo = player.marriageCtrl.marryTotalInfo
        if not marryTotalInfo:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, '未领取任务！'))
            return
        oldMarryId = marryTotalInfo.marryId
        anotherInfo = marryTotalInfo.getInfoByAnotherGender(player.gender)
        oldMateId = anotherInfo.uid
        matePlayer  = player.mapObj.getPlayerById(anotherInfo.uid)
        player.addGold(needGold * -1, True)
        matePlayer.addGold(needGold, True)
        MarryModel.getMarryMgr().delMarryById(marryTotalInfo.marryId)

        mateSession = None
        from handler import SkillHandler
        if matePlayer:
            mateSession = matePlayer.session
            matePlayer.marriageCtrl.divorceForce()
            matePlayer.skillCtrl.deleteSkill(WEDDING_SKILL_ID, True)
            SkillHandler.processQuerySkill(mateSession)
        player.marriageCtrl.divorceForce()

        player.skillCtrl.deleteSkill(WEDDING_SKILL_ID, True)
        SkillHandler.processQuerySkill(session)

        # 发送回包
        ret_msg = processMarryOpsMsgRet(opstype, session.player, MsgDef.MarryStatusCmd.MARRY_STATUS_NOT, 0, '', needGold)
        session.sendMsg(MsgDef.ServerCmd.MARRIAGE_OPS_MSG, ret_msg)

        if mateSession:
            #up_msg = processMarriageUpdateRet(opstype, player, MsgDef.MarryStatusCmd.MARRY_STATUS_NOT, None)
            mateSession.sendMsg(MsgDef.ServerCmd.MARRIAGE_OPS_MSG, ret_msg)
            return

        # 更新数据库
        DbService.getPlayerService().updateMarryDivorce(oldMarryId)
        DbService.getPlayerService().updateMarryDivorcePlayer(player.uid)
        DbService.getPlayerService().updateMarryDivorcePlayer(oldMateId)
        return

#用于返回错误信息的函数
def processErrorMsgRet(opstype, cmd, msg):
    ret_msg                 = MsgDef.ErrorMsgRet()
    ret_msg.errType         = opstype                        #错误信息所处位置opstype
    ret_msg.cmd             = cmd                               #错误信息所处位置cmd
    ret_msg.errMsg          = msg                               #错误信息
    return ret_msg

#结婚操作时，服务器给客户端广播的信息格式
def processMarryOpsMsgRet(opstype, player, flag = 0, delTime = 0, msg = '', gold = 0, skillId = 0, marryTotalInfo = None):
    ret_msg                         = MsgDef.MarriageOpsMsgRet(opstype, MsgDef.MarriageBaseInfo())
    ret_msg.opstype                 = opstype
    if not marryTotalInfo:
        if player and player.marriageCtrl.marryTotalInfo:
            marryTotalInfo = player.marriageCtrl.marryTotalInfo
    if marryTotalInfo:
        ret_msg.delTime                 = marryTotalInfo.tmEndWedding
        #ffext.dump('self.listSetItems', marryTotalInfo.listSetItems)
        ret_msg.baseInfo.marryId                     = marryTotalInfo.marryId
        ret_msg.baseInfo.flagXiTie = marryTotalInfo.flagXiTie
        ret_msg.baseInfo.flagWeding = marryTotalInfo.flagWeding
        ret_msg.baseInfo.tmWedding = marryTotalInfo.tmWedding
        ret_msg.baseInfo.coupleData         = []
        ret_msg.baseInfo.listAttends         = []
        for k in marryTotalInfo.coupleData:
            tmpmsg = MsgDef.MarriagePlayerMsg()
            tmpmsg.uid                     = k.uid
            tmpmsg.name                    = k.name
            tmpmsg.job                     = k.job
            tmpmsg.gender                  = k.gender
            tmpmsg.level                   = k.level
            tmpmsg.status                   = k.status
            tmpmsg.online = False
            if ffext.getSessionMgr().findByUid(k.uid):
                tmpmsg.online = True
            ret_msg.baseInfo.coupleData.append(tmpmsg)
        for k in marryTotalInfo.listAttends:
            tmpmsg = MsgDef.MarriagePlayerMsg()
            tmpmsg.uid                     = k.uid
            tmpmsg.name                    = k.name
            tmpmsg.job                     = k.job
            tmpmsg.gender                  = k.gender
            tmpmsg.level                   = k.level
            tmpmsg.status                   = k.status
            tmpmsg.online = False
            if ffext.getSessionMgr().findByUid(k.uid):
                tmpmsg.online = True
            ret_msg.baseInfo.listAttends.append(tmpmsg)
        ret_msg.setupItems              = []
        for k, v in marryTotalInfo.listSetItems.iteritems():
            #ret_msg.setupItems.append(v)
            ret_msg.setupItems.append(MsgDef.MarriageItem(k, v.get('itemCfgId', 0)))
    #ret_msg.allMarriageInfo         = allMarriageInfo
    ret_msg.flag                    = flag
    if delTime != 0:
        ret_msg.delTime                 = delTime
    ret_msg.msg                     = msg
    ret_msg.gold                    = gold
    ret_msg.getItems                = []
    #ret_msg.setupItems              = []
    ret_msg.weddingSkillId          = skillId
    ret_msg.listVisitHouseInfo      = []
    #ret_msg.otherHouseInfo          = {}
    return ret_msg

#结婚时，结婚player对象赋值
def processMarryPlayerMsg(player, online):
    ret_msg                         = MsgDef.MarriagePlayerMsg()
    ret_msg.uid                     = player.uid
    ret_msg.name                    = player.name
    ret_msg.job                     = player.job
    ret_msg.gender                  = player.gender
    ret_msg.level                   = player.level
    ret_msg.online                  = online
    return ret_msg

def addItem2MarryPlayerMsg(msg, item, num):
    if not msg:
        return None
    itemMsg = processMarriageItem(item, num)
    msg.getItems.append(itemMsg)
    return itemMsg

def addItem2MarryPlayerMsgEx(msg, pos, itemId):
    if not msg:
        return None
    itemMsg = MsgDef.MarriageItem()
    itemMsg.pos = pos
    itemMsg.itemCfgId = itemId
    msg.setupItems.append(itemMsg)
    return msg

#结婚相关的主动推送协议
def processMarriageUpdateRet(opstype, mateP, st, goldP):
    ret_msg = MsgDef.MarriageUpdateRet()
    ret_msg.opstype = opstype
    if mateP:
        ret_msg.matePlayer = processMarryPlayerMsg(mateP, ffext.getSessionMgr().isPlayerOnline(mateP.uid))
    else:
        ret_msg.matePlayer = {}
    ret_msg.status = st
    if goldP:
        ret_msg.goldPlayer = processMarryPlayerMsg(goldP, ffext.getSessionMgr().isPlayerOnline(goldP.uid))
    else:
        ret_msg.goldPlayer = {}
    return ret_msg

# #参加婚礼道具
def processMarriageItem(itemObj, num):
    ret_msg                         = MsgDef.Item()
    from handler import ItemHandler
    ItemHandler.buildItem(ret_msg, itemObj)
    return ret_msg
def tmpBuild(k):
    tmpmsg = MsgDef.MarriagePlayerMsg()
    tmpmsg.uid                     = k.uid
    tmpmsg.name                    = k.name
    tmpmsg.job                     = k.job
    tmpmsg.gender                  = k.gender
    tmpmsg.level                   = k.level
    tmpmsg.status                   = k.status
    return tmpmsg
#MARRY_NEW_LIST/MARRY_VISIT_HOUSE 的独立节点结构
def processMarriageVisitListBaseInfo(mId, mMsg1, mMsg2, time = 0, items = []):
    ret_msg = MsgDef.MarriageVisitListBaseInfo()
    ret_msg.marryId = mId
    ret_msg.coupleData = []
    ret_msg.coupleData.append(tmpBuild(mMsg1))
    ret_msg.coupleData.append(tmpBuild(mMsg2))
    ret_msg.tmWedding = time
    ret_msg.setupItems = items
    return ret_msg

