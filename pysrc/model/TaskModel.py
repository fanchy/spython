# -*- coding: utf-8 -*-
import random
from base   import Base
from mapmgr import MapMgr
from db import DbService
import msgtype.ttypes as MsgDef
ServerCmd = MsgDef.ServerCmd
import  weakref
import ffext
import time
from model import MonsterModel, ItemModel

class TaskType:
    MAIN_TASK   = 0#主线任务
    DAILY_TASK  = 1#日常任务
    BRANCH_TASK = 2# 支线任务
    SPECIAL_TASK= 1000
class TaskStatus:
    INIT   = 0#初始化状态
    ACCEPT = 1#已经接受
    DONE   = 2#完成
    FINISH = 3#领奖完毕
class TaskCfg:
    def __init__(self):
        self.taskType  = 0#任务类型
        self.taskId= 0#任务唯一ID
        self.action= 0#怎么做
        self.object= 0#做什么
        self.value = 0#做多少
        self.name  = ''
        self.desc  = ''
        self.nextTaskId = 0#下一个任务的任务ID
        self.acceptNpc  = 0#接受任务的npc nam
        self.finishNpc  = 0#领取任务奖励的npc name
        self.flag       = 0#标记是否是删除
        self.needLevel  = 0#所需等级

        self.acceptshow     = ''#接任务NPC面板显示
        self.finishshow     = ''#交任务NPC面板显示
        self.acceptdialog   = 0 #接任务剧情对白id
        self.completedialog = 0 #目标完成剧情对白id
        self.acceptplay     = 0 #接任务插入剧情id
        self.completeplay   = 0 #条件达成剧情id
        self.finishdialog   = 0 #交任务剧情对白id
        self.finishplay     = 0 #交任务插入剧情id
        self.exp            = 0 #经验奖励
        self.gold           = 0 #金币奖励
        self.itemGiveAccept = ''#接取时给的任务道具

class Task(Base.BaseObj):
    def __init__(self):
        self.taskCfg      = None
        self.status       = TaskStatus.INIT
        self.value        = 0#做多少
        self.acceptTm     = 0#创建时间
        self.action       = 0
        self.object       = 0
        self.destValue    = 0
    def setCfg(self, cfg):
        self.taskCfg      = cfg
        self.taskType     = cfg.taskType
        self.taskId       = cfg.taskId
        self.action       = cfg.action
        self.object       = cfg.object
        self.destValue    = cfg.value
    def getType(self):
        return self.taskType
    def getTaskId(self):
        return self.taskCfg.taskId
    # @property
    # def taskId(self):
    #     return self.taskCfg.taskId
    # @property
    # def action(self):
    #     return self.taskCfg.action
    # @property
    # def object(self):
    #     return self.taskCfg.object
    @property
    def desc(self):
        return self.taskCfg.desc
    def inc(self, action, object, val = 1):
        if self.status != TaskStatus.ACCEPT:
            return  -1
        if  action != self.action or (object != self.object and self.object != 0):
            return -1
        ffext.dump('OBJECT',self.object)
        self.value += val
        if self.value >= self.destValue:
            self.value = self.destValue
            self.status= TaskStatus.DONE
            return 1
        return  0
def mergeAction(action, object):
    return action * 1000000 + object
class TaskCtrl(Base.BaseObj):
    def __init__(self, owner):
        self._owner      = weakref.ref(owner)
        self.allTask     = {}   #Taskid -> Task
        self.action2task = {}
        self.npc2task    = {} #npc name -> [task weakref]
        return
    @property
    def owner(self):
        return self._owner()
    def getTask(self, taskId):
        return self.allTask.get(taskId)
    def addTask(self, task, saveFlag = True):
        self.allTask[task.taskId] = task
        taskCfg = task.taskCfg
        owner   = self.owner
        if task.status == TaskStatus.INIT or task.status == TaskStatus.ACCEPT:
            actionTmp = mergeAction(task.action, task.object)
            dest = self.action2task.get(actionTmp)
            if dest:
                dest.append(weakref.ref(task))
            else:
                self.action2task[actionTmp] = [weakref.ref(task)]
        if saveFlag:
            DbService.getPlayerService().addTask(self.owner, task)
        return task
    def addTaskById(self, taskId, saveFlag = True, status = 0):
        taskCfg = getTaskMgr().getCfgById(taskId)
        if not taskCfg:
            ffext.error('not found taskId=%d'%(taskId))
            return None

        task = Task()
        task.setCfg(taskCfg)
        task.status = status

        acceptNpc = taskCfg.acceptNpc
        finishNpc = taskCfg.finishNpc
        npcData = self.npc2task.get(acceptNpc)
        if npcData == None:
            self.npc2task[acceptNpc] = {taskId: weakref.ref(task)}
        else:
            npcData[taskId] = weakref.ref(task)
        npcData = self.npc2task.get(finishNpc)
        if npcData == None:
            self.npc2task[finishNpc] = {taskId: weakref.ref(task)}
        else:
            npcData[taskId] = weakref.ref(task)
        return self.addTask(task, saveFlag)
    def delTaskById(self, taskId):
        dest = self.allTask.pop(taskId, None)
        if dest:
            for k, v in self.npc2task.iteritems():
                for m, n in v.iteritems():
                    if m == taskId:
                        del  v[m]
                        return
            return True
        else:
            return  False
    def fromData(self, result):
        ffext.dump(result)
        for row in result:
            taskId = int(row[0])
            status = int(row[1])
            value  = int(row[2])
            tmArg  = ffext.str2timestamp(row[3])
            task = self.addTaskById(taskId, False, status)
            if None == task:
                continue
            task.value  = value
            task.acceptTm= tmArg
            if status == TaskStatus.FINISH:#任务结束，检查是否有新的配置
                self.checkNewTask(task)
        getTaskMgr().checkNewTask(self.owner)
        ffext.dump(self.allTask)

        return True
    def acceptTask(self, taskId):
        task = self.allTask.get(taskId)
        if not task:
            return Base.lang( '任务不存在')
        if task.status != TaskStatus.INIT:
            return Base.lang('无法接受任务')
        task.status = TaskStatus.ACCEPT
        task.acceptTm= ffext.getTime()
        #for k, item in self.owner.itemCtrl.allItem.iteritems():
            #if task.object == item.itemCfg.cfgId:
                #task.value = self.owner.itemCtrl.countItemNumbyCfgId(task.object)
                #ffext.dump('Value', task.value)
        self.owner.sendMsg(ServerCmd.UPDATE_TASK_STATUS, MsgDef.UpdateTaskStatusRet(task.taskId, task.status, task.value))
        if task.taskCfg.action == Base.Action.CHAT_NPC:
            task.status = TaskStatus.DONE
        DbService.getPlayerService().updateTask(self.owner, task)
        return None
    def finishTask(self, taskId):
        task = self.allTask.get(taskId)
        if not task:
            return Base.lang('任务不存在')
        if task.status != TaskStatus.DONE:
            return Base.lang('无法交任务')
        task.status = TaskStatus.FINISH
        player = self.owner
        player.addExp(task.taskCfg.exp, True)
        player.addGold(task.taskCfg.gold, True)
        DbService.getPlayerService().updateTask(player, task)
        newTask = self.checkNewTask(task)
        msg = MsgDef.UpdateTaskStatusRet(task.taskId, task.status, task.value)
        if newTask and newTask.__class__ != str:
            msg.nextTask = buildTaskMsg(newTask)
        self.owner.sendMsg(ServerCmd.UPDATE_TASK_STATUS, msg)
        return newTask
    def checkNewTask(self, task):
        #如果任务完成，检查是否有新的任务可以做
        if task.status != TaskStatus.FINISH:
            return None
        nextTaskId = task.taskCfg.nextTaskId
        if nextTaskId <= 0:
            return None
        newTask = self.addTaskById(nextTaskId, False)
        if not newTask:
            return None
        oldTaskId = task.taskId
        self.delTaskById(oldTaskId)
        DbService.getPlayerService().replaceTask(self.owner, newTask, oldTaskId)
        return newTask
    def getTaskByType(self, taskType):
        for taskId, task in self.allTask.iteritems():
            if task.getType() == taskType:
                return task
        return None
    def trigger(self, action, object, value = 1):
        actionTmp = mergeAction(action, object)
        dest = self.action2task.get(actionTmp)
        player = self.owner
        if not dest:
            actionTmp = mergeAction(action, 0)
            dest = self.action2task.get(actionTmp)
            if not dest:
                ffext.dump('trigger2', action, object, value, actionTmp, self.action2task)
                return 0
        ret    = None
        ffext.dump('trigger', action, object, value, actionTmp, self.action2task, dest)
        for taskref in dest:
            task = taskref()
            ffext.dump('trigger', action, object, value, actionTmp, task)
            if not task:
                continue
            #ffext.dump(event)
            r = task.inc(action, object, value)
            if r == 1:#完成任务
                cfg = task.taskCfg
                if ret == None:
                    ret = []
                ret.append(task.taskId)
                DbService.getPlayerService().updateTask(player, task)
                player.sendMsg(ServerCmd.UPDATE_TASK_STATUS, MsgDef.UpdateTaskStatusRet(task.taskId, task.status, task.value))
                if cfg.completedialog:
                    player.sendMsg(MsgDef.ServerCmd.SHOW_PLAY, MsgDef.ShowPlayRet(cfg.completedialog))
                elif cfg.completeplay:
                    player.sendMsg(MsgDef.ServerCmd.SHOW_PLAY, MsgDef.ShowPlayRet(cfg.completeplay))
            elif r == 0:#有进展
                DbService.getPlayerService().updateTask(self.owner, task)
                self.owner.sendMsg(ServerCmd.UPDATE_TASK_STATUS, MsgDef.UpdateTaskStatusRet(task.taskId, task.status, task.value))
        #ffext.dump(ret)
        if ret:
            sendTaskList(player)
            return len(ret)
        return 0
    def whenClickNpc(self, npc):
        npcName = npc.name
        npccfgid = npc.cfg.cfgid
        ffext.dump('whenClickNpc npccfgid', npcName, npccfgid, self.npc2task)
        taskList = self.npc2task.get(npccfgid)
        
        if None == taskList:
            return False
        ffext.dump('whenClickNpc taskList', len(taskList))
        owner = self._owner()
        allAboutTsk1 = []
        allAboutTsk2 = []
        for tid, taskref in taskList.iteritems():
            ffext.dump('whenClickNpc tid', tid)
            task = taskref()
            if None == task:
                continue
            cfg = task.taskCfg
            if cfg.taskType == TaskType.SPECIAL_TASK:
                continue
            if owner.level < cfg.needLevel:
                if cfg.taskType == TaskType.MAIN_TASK:
                    allAboutTsk2.append(task)
            else:
                if task.status == TaskStatus.DONE or task.status == TaskStatus.INIT:
                    allAboutTsk1.insert(0, task)
                else:
                    allAboutTsk1.append(task)
            continue
        if len(allAboutTsk1) == 0:
            allAboutTsk1 = allAboutTsk2
        for task in allAboutTsk1:
            cfg = task.taskCfg
            #ffext.dump('whenClickNpc', task)
            if task.status == TaskStatus.INIT:#弹出接受任务的面板
                callbackId = owner.addCallBack(showPreAcceptTaskCallback, (npc.uid, task.taskId))

                #owner.sendMsg(ServerCmd.SHOW_TASK_PANEL, MsgDef.ShowTaskPanelRet(task.status, task.taskId, cfg.acceptshow, callbackId))
                buttons = [('%s任务'%(cfg.name), '_call_&%d'%(callbackId))]
                if cfg.taskType >= TaskType.BRANCH_TASK and  cfg.taskType <= TaskType.BRANCH_TASK  + 10:
                    callbackId2 = owner.addCallBack(showPreAcceptTaskCallback, (npc.uid, 0))
                    buttons.append(('我要放弃未完成任务', '_call_&%d'%(callbackId2)))
                ffext.dump('whenClickNpc buttons', buttons)
                npc.speakTo(owner, cfg.desc, buttons)#, ('我要放弃未完成的任务', '_call_&%d'%(callbackId))
                return True
            elif task.status == TaskStatus.DONE:
                try:
                    if task.taskCfg.finishNpc != npccfgid:
                        continue
                except:
                    pass
                callbackId = owner.addCallBack(finishTaskCallback, (task.taskId, npccfgid))
                owner.sendMsg(ServerCmd.SHOW_TASK_PANEL, MsgDef.ShowTaskPanelRet(task.status, task.taskId, cfg.finishshow, callbackId))
                return True
        return False
#点击npc：
#1没有任务---返回CLICK_NPC，显示你返回的内容和按钮
#2是可接的任务---返回CLICK_NPC，显示内容和xxx任务按钮
#3是可交任务--返回SHOW_TASK_PANEL，显示交面板
def showPreAcceptTaskCallback(player, args):
    npcid = args[0]
    npc   = player.mapObj.getNpc(npcid)
    taskId = args[1]
    if taskId == 0:#放弃未完成的任务
        npc.speakTo(player, '当前没有任务需要放弃!')
        return
    ffext.dump('showPreAcceptTaskCallback', taskId)
    task = player.taskCtrl.getTask(taskId)
    cfg = task.taskCfg
    callbackId = player.addCallBack(acceptTaskCallback, task.taskId)
    player.sendMsg(ServerCmd.SHOW_TASK_PANEL, MsgDef.ShowTaskPanelRet(task.status, task.taskId, cfg.acceptshow, callbackId))
    return True
def acceptTaskCallback(player, taskId):

    task = player.taskCtrl.getTask(taskId)
    if not task:
        player.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.UPDATE_TASK_STATUS, '任务参数错误'))
        return
    cfg = task.taskCfg
    ffext.dump('acceptTaskCallback', taskId, cfg.needLevel, player.level)
    if player.level < cfg.needLevel:
        player.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.UPDATE_TASK_STATUS, '勇士，请达到%d级再来接取此任务!'%(cfg.needLevel)))
        return
    ret = player.taskCtrl.acceptTask(taskId)
    if ret == None and cfg.itemGiveAccept != '':
        player.itemCtrl.addItemByName(cfg.itemGiveAccept, 1)
    if cfg.action == Base.Action.COLLECT:
        num = player.itemCtrl.countItemNumbyCfgId(cfg.object)
        ffext.dump('collect task:', cfg.action, cfg.object, num)
        if num > 0:
            player.taskCtrl.trigger(cfg.action, cfg.object, num)
    sendTaskList(player)
    #task = player.taskCtrl.getTask(taskId)
    #if task.status == TaskStatus.DONE:
        #from handler import NpcHandler
        #NpcHandler.playerClickNpc(player, )
        #player.taskCtrl.whenClickNpc(task.taskCfg.finishNpc)


    if cfg.acceptdialog:
        player.sendMsg(MsgDef.ServerCmd.SHOW_PLAY, MsgDef.ShowPlayRet(cfg.acceptdialog))
    elif cfg.acceptplay:
        player.sendMsg(MsgDef.ServerCmd.SHOW_PLAY, MsgDef.ShowPlayRet(cfg.acceptplay))
    return
def buildErrMsg(cmd, errMsg):
    return MsgDef.ErrorMsgRet(0, cmd, errMsg)#'cmd=%d,errMsg=%s'%(cmd, errMsg)
def finishTaskCallback(player, arg):
    ffext.dump('finishTaskCallback', arg[0], arg[1])
    taskId = arg[0]
    npccfgid= arg[1]
    taskCtrl = player.taskCtrl
    task = taskCtrl.getTask(taskId)
    cfg = task.taskCfg
    try:
        if cfg.action == Base.Action.COLLECT:
            num = player.itemCtrl.countItemNumbyCfgId(cfg.object)
            if num < cfg.value:
                player.sendMsg(MsgDef.ServerCmd.ERROR_MSG, buildErrMsg(MsgDef.ClientCmd.UPDATE_TASK_STATUS, '任务道具没有收集齐'))
                return
            else:
                player.itemCtrl.subItemNumByCfgId(cfg.object, cfg.value)
                from handler import ItemHandler
                ItemHandler.processQueryPkg(player.session)
    except:
        pass
    newTask = taskCtrl.finishTask(taskId)
    sendTaskList(player)
    #if newTask and newTask.__class__ != str:
    #    taskCtrl.whenClickNpc(npcName)
    ffext.dump('finishTaskCallback info', arg[0], arg[1], cfg.finishplay, cfg.finishdialog)
    if cfg.finishdialog:
        player.sendMsg(MsgDef.ServerCmd.SHOW_PLAY, MsgDef.ShowPlayRet(cfg.finishdialog))
    elif cfg.finishplay:
        player.sendMsg(MsgDef.ServerCmd.SHOW_PLAY, MsgDef.ShowPlayRet(cfg.finishplay))


    return
def sendTaskList(player):
    retMsg = MsgDef.TaskListRet([])
    builder= buildTaskMsg
    for taskId, task in player.taskCtrl.allTask.iteritems():
        cfg = task.taskCfg
        ffext.dump('level',task.taskId, player.level , cfg.needLevel)
        if cfg.taskType != TaskType.MAIN_TASK and player.level < cfg.needLevel and cfg.taskType < 1000:
            continue
        info = builder(task)
        retMsg.allTask.append(info)
    player.session.sendMsg(MsgDef.ServerCmd.QUERY_TASK_LIST, retMsg)
    return
class Event(Base.BaseObj):
    def __init__(self, a = 0, o = 0, v = 0):
        self.action = a
        self.object = o
        self.value  = v
class TaskMgr(Base.BaseObj):
    def __init__(self):
        self.allTaskCfg = {}#taskid -> TaskCfg
        self.type2Task  = {}#tasktype -> list<TaskCfg>

    def init(self):#读取任务配置
        db = ffext.allocDbConnection('cfg',ffext.getConfig('-cfg'))
        ret = db.queryResult('select id,name,lastid,task_type,action,jie_npc,jiao_npc,mubiao,show_jie,show_jiao, jie_duibai,jiao_duibai,jie_juqing,complete_juqing,jiao_juqing,jl_exp,jl_coin,mubiao_name,mubiao_num,level,branch_id, jie_gei_daoju from task')
        self.allTaskCfg = {}#taskid -> TaskCfg
        self.type2Task  = {}#tasktype -> list<TaskCfg>

        for i in range(0, len(ret.result)):
            row = ret.result[i]
            taskCfg = TaskCfg()
            taskCfg.taskId = Base.str2Int(row[0])
            taskCfg.name   = row[1]
            taskCfg.desc   = row[7]
            preTaskId = Base.str2Int(row[2])
            taskCfg.needLevel = Base.str2Int(row[19])
            taskCfg.taskType = Base.str2Int(row[20])#TaskType.MAIN_TASK
            action = Base.str2Action(row[4])
            taskCfg.action = action
            taskCfg.object = 0
            taskCfg.value      = 1
            if action == Base.Action.KILL_MONSTER:
                taskCfg.object = 101#TODO
            elif action == Base.Action.COPY_MAP:
                taskCfg.object = 10005#TODO
            if action == Base.Action.NONE_ACTION:
                ffext.error('Task.Init failed taskid = %d not support action = %s'%(taskCfg.taskId, row[4]))
                continue
            elif action == Base.Action.KILL_MONSTER:
                objectStr = row[7]
                monsterName =  row[17]#objectStr.decode('utf-8')[2:].encode('utf-8')
                taskCfg.value = int(row[18])
                #monsterName = row[7][:4]
                monCfg = MonsterModel.getMonsterMgr().getCfgByName(monsterName)
                if None == monCfg:
                    ffext.error('Task.Init failed taskid = %d not support monsterName = %s [%s]'%(taskCfg.taskId, row[7], monsterName))
                    taskCfg.object = 0
                    #return  False
                else:
                    taskCfg.object = monCfg.cfgId
                #ret2 = db.queryResult("update maintask set targetName = '%s', targetNum = 1 where taskid = %d"%(monsterName, taskCfg.taskId))
                #ffext.dump('*************', monsterName, taskCfg.object)
            elif action == Base.Action.COLLECT:
                objectStr = row[7]
                itemName = row[17]#objectStr.decode('utf-8')[2:].encode('utf-8')
                from model import ItemModel
                itemCfg = ItemModel.getItemMgr().getCfgByName(itemName)
                if itemCfg:
                    taskCfg.object = itemCfg.cfgId
                taskCfg.value = int(row[18])
                #ret2 = db.queryResult("update maintask set targetName = '%s', targetNum = 1 where taskid = %d"%(itemName, taskCfg.taskId))
                #ffext.dump('*************', itemName, taskCfg.object)

            taskCfg.nextTaskId = 0

            taskCfg.acceptshow     = row[8]#接任务NPC面板显示
            taskCfg.finishshow     = row[9]#交任务NPC面板显示
            #'select id,name,lastid,task_type,action,jie_npc,jiao_npc,mubiao,show_jie,show_jiao,'
                             #'jie_duibai,jiao_duibai,jie_juqing,complete_juqing,jiao_juqing,jl_exp,jl_coin,mubiao_name,mubiao_num from task')
            if row[10] != '':
                taskCfg.acceptdialog   = int(row[10]) #接任务剧情对白id jie_duibai
            if row[11] != '':
                taskCfg.finishdialog   = int(row[11]) #jiao_duibai
            if row[12] != '':
                taskCfg.acceptplay     = int(row[12]) #接任务插入剧情id jie_juqing

            #if row[11] != '':
            #    taskCfg.completedialog = int(row[11]) #目标完成剧情对白id
            if row[13] != '':
                taskCfg.completeplay   = int(row[13]) #条件达成剧情id complete_juqing
            if row[14] != '':
                taskCfg.finishplay     = int(row[14]) #交任务插入剧情id complete_juqing
            taskCfg.exp            = int(row[15]) #经验奖励
            taskCfg.gold           = int(row[16]) #金币奖励
            if preTaskId == taskCfg.taskId:
                preTaskId = 0
            if i != 0 and preTaskId != 0:
                if self.allTaskCfg.get(preTaskId) == None:
                    ffext.error('tid %d  前置任务 %d 不存在'%(taskCfg.taskId, preTaskId))
                    continue
                self.allTaskCfg[preTaskId].nextTaskId = taskCfg.taskId
            if row[5].isdigit():
                taskCfg.acceptNpc  = int(row[5])
            if row[6].isdigit():
                taskCfg.finishNpc  = int(row[6])
            taskCfg.itemGiveAccept = row[21]

            self.allTaskCfg[taskCfg.taskId] = taskCfg
            cfg = self.type2Task.get(taskCfg.taskType)
            if not cfg:
                self.type2Task [taskCfg.taskType] = [taskCfg]
            else:
                cfg.append(taskCfg)
        ffext.dump('load task num=%d'%(len(ret.result)))
        return True
    def getCfgById(self, tid):
        return self.allTaskCfg.get(tid)
    def getNextTask(self, task):
        taskType = task.getType()
        tid  = task.taskId
        destList = self.type2Task.get(taskType)
        if not destList:
            return None
        for k in range(0, len(destList)):
            if destList[k].taskId == tid:
                if k < len(destList) - 1:
                    return destList[k + 1]
                break
        return None
    def checkNewTask(self, player):
        taskCtrl = player.taskCtrl
        for taskType, destList in self.type2Task.iteritems():
            ffext.dump('checkNewTask', player.name, taskType)
            if taskType not in (TaskType.MAIN_TASK, TaskType.BRANCH_TASK):
                continue
            if None != taskCtrl.getTaskByType(taskType):
                continue
            tid = destList[0].taskId
            if taskType == TaskType.BRANCH_TASK:
                taskCfg = self.getCfgById(tid)
                if not taskCfg:
                    continue
                if taskCfg.needLevel > player.level:
                    continue
            status = TaskStatus.INIT
            task = taskCtrl.addTaskById(tid, True, status)
            if taskType == TaskType.MAIN_TASK:
                taskCtrl.acceptTask(task.taskId)
                #第一个主线任务发对白
                cfg = task.taskCfg
                if cfg.acceptdialog:
                    player.sendMsg(MsgDef.ServerCmd.SHOW_PLAY, MsgDef.ShowPlayRet(cfg.acceptdialog))
                elif cfg.acceptplay:
                    player.sendMsg(MsgDef.ServerCmd.SHOW_PLAY, MsgDef.ShowPlayRet(cfg.acceptplay))
            ffext.info('uid=%d taskCtrl.addTaskById=%d'%(player.uid, tid))
        return True
def buildTaskMsg(task):
    cfg = task.taskCfg
    info= MsgDef.Task(task.getTaskId(), task.getType(), task.status, task.action, task.object, task.value, task.destValue, cfg.name, cfg.desc, str(cfg.acceptNpc), str(cfg.finishNpc), cfg.needLevel, cfg.gold, cfg.exp)
    return info
gTaskMgr = TaskMgr()

def getTaskMgr():
    return gTaskMgr


def onLevelUp(player):
    getTaskMgr().checkNewTask(player)
    sendTaskList(player)