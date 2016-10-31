# -*- coding: utf-8 -*-
import ffext
import msgtype.ttypes as MsgDef
from model import TaskModel
def buildErrMsg(cmd, errMsg):
    return MsgDef.ErrorMsgRet(0, cmd, errMsg)#'cmd=%d,errMsg=%s'%(cmd, errMsg)
@ffext.onLogic(MsgDef.ClientCmd.QUERY_TASK_LIST, MsgDef.EmptyReq)
def processQueryTask(session, msg = None):
    TaskModel.sendTaskList(session.player)

#任务操作
@ffext.onLogic(MsgDef.ClientCmd.UPDATE_TASK_STATUS, MsgDef.UpdateTaskStatusReq)
def processUpdateTaskStatusReq(session, msg):
    player = session.player
    status = msg.status
    if status == MsgDef.TaskStatus.ACCEPT:
        retErr = player.taskCtrl.acceptTask(msg.taskId)
        if retErr:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.UPDATE_TASK_STATUS, 'Error:'+retErr))
            return
    elif status == MsgDef.TaskStatus.FINISH:
        retErr = player.taskCtrl.finishTask(msg.taskId)
        if retErr and retErr.__class__ == str:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.UPDATE_TASK_STATUS, 'Error:'+retErr))
            return
    return
