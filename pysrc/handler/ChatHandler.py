# -*- coding: utf-8 -*-
#本文件用于存放好友关系的操作函数
import ffext
#调用msgtype中的ttypes文件，使用系统中的枚举函数
from msgtype import ttypes as MsgDef
#调用、组队信息
from model import TeamModel as TeamModel
from model import GuildModel as GuildModel
#调用地图文件
from mapmgr import MapMgr as MapMgr
from db import DbService
from base   import Base
import random
#当客户端向服务器发送GET_FRIENDLIST指令时，服务器向客户端反馈好友列表
@ffext.onLogic(MsgDef.ClientCmd.CHAT_OPS, MsgDef.ChatMsgReq)
def processChat(session, msg):
    ffext.dump('processChat', msg)
    uid = msg.uid
    #if session.isWebDebug:
    #    msg.chatMsg = msg.chatMsg.encode('utf-8')
    retVal         = MsgDef.ChatMsgRet()
    ret_msg = retVal
    ret_msg.name    = session.player.name
    ret_msg.uid     = session.player.uid
    ret_msg.opstype = msg.opstype
    ret_msg.chatMsg = msg.chatMsg
    if len(msg.chatMsg) > 0 and msg.chatMsg[0] == '@':
        msg.opstype = MsgDef.ChatMsgCmd.MapCHAT
    #用户一对一聊天
    if msg.opstype == MsgDef.ChatMsgCmd.PERSONCHAT:
        friendSession   = ffext.getSessionMgr().findByUid(msg.uid)
        if None != friendSession:
            friendSession.sendMsg(MsgDef.ServerCmd.CHAT_MSG, ret_msg)
            session.sendMsg(MsgDef.ServerCmd.CHAT_MSG, ret_msg)
            return
        ret_msg.chatMsg = '对方不在线!%d'%(msg.uid)
        session.sendMsg(MsgDef.ServerCmd.CHAT_MSG, ret_msg)
        return
    #用户世界聊天
    if msg.opstype == MsgDef.ChatMsgCmd.WORLDCHAT:
        session.broadcast(MsgDef.ServerCmd.CHAT_MSG, ret_msg)
        return
    #用户组队聊天
    if msg.opstype == MsgDef.ChatMsgCmd.TEAMCHAT:
        teamID = session.player.teamCtrl.teamID
        if 0 == teamID:
            ret_msg.chatMsg = '没有参与组队'
            session.sendMsg(MsgDef.ServerCmd.CHAT_MSG, ret_msg)
            return
        for uid, val in TeamModel.getTeamMgr().getTeamById(teamID).getTeamMember().iteritems():
            memberSession = ffext.getSessionMgr().findByUid(uid)
            if None != memberSession:
                memberSession.sendMsg(MsgDef.ServerCmd.CHAT_MSG, ret_msg)
        return
    #用户行会聊天
    if msg.opstype == MsgDef.ChatMsgCmd.GUILDCHAT:
        guildInfo = session.player.guildCtrl.guildInfo
        if None == guildInfo:
            ret_msg.chatMsg = '没有参与组队'
            session.sendMsg(MsgDef.ServerCmd.CHAT_MSG, ret_msg)
            return
        ret_msg.chatMsg = msg.chatMsg
        for uid, val in guildInfo.getGuildMember().iteritems():
            memberSession = ffext.getSessionMgr().findByUid(uid)
            if None != memberSession:
                memberSession.sendMsg(MsgDef.ServerCmd.CHAT_MSG, ret_msg)
        return
    #系统广播
    if msg.opstype == MsgDef.ChatMsgCmd.SYSTEMCHAT:
        ret_msg.uid     = 0
        ret_msg.name    = '系统管理员'
        session.broadcast(MsgDef.ServerCmd.CHAT_MSG , ret_msg)
        return
    #用户地图广播
    if msg.opstype == MsgDef.ChatMsgCmd.MapCHAT or msg.chatMsg[0] == '@':
        data = msg.chatMsg

        print(data)
        if len(data) > 1 and data[0] == '@':#GM
            argsSrc = data.split(' ')

            args = []
            for k in argsSrc:
                if k != '':
                    args.append(k)
            ffext.dump(args)




            func = GM2FUNC.get(args[0], None)
            if func:
                func(session, args)
            ffext.dump("chat", retVal)
            session.player.broadcast(MsgDef.ServerCmd.CHAT_MSG , retVal)
            return

            #下面代码注释掉
        """
            if args[0] == '@setlevel':
               from model import PlayerModel
               session.player.level = int(args[1])
               session.player.updateLevelProp()
               # 发送属性数据
                PlayerModel.sendPropUpdateMsg(session.player)
            elif args[0] == '@addexp':
                #session.player.addExp(int(args[1]), True)
            elif args[0] == '@close':
                session.close()
            elif args[0] == '@addhpmp':
                session.player.addHPMsg(session.player.hpMax, session.player.mpMax)
            elif args[0] == '@addgold':
                session.player.addGold(int(args[1]), True)
            elif args[0] == '@cleartask':
                DbService.getPlayerService().cleerTask(session.player)
            elif args[0] == '@additem':
                num = 1
                if len(args) >= 3:
                    num = int(args[2])
                session.player.itemCtrl.addItemByName(args[1], num)
                from handler import ItemHandler
                ItemHandler.processQueryPkg(session)
            elif args[0] == '@additemid' or args[0] == '@additembyid':
                num = 1
                if len(args) >= 3:
                    num = int(args[2])
                session.player.itemCtrl.addItemByCfgId(int(args[1]), num)
                from handler import ItemHandler
                ItemHandler.processQueryPkg(session)
            elif args[0] == '@addmonster':
                if len(args) < 4:
                    ret_msg.chatMsg = '参数 @addmonster 怪名 x y'
                    session.player.sendMsg(MsgDef.ServerCmd.CHAT_MSG , ret_msg)
                    return
                from model import MonsterModel
                MonsterModel.genMonster(session.player.mapname, args[1], int(args[2]), int(args[3]), 1, 0)
                session.player.sendMsg(MsgDef.ServerCmd.CHAT_MSG , ret_msg)
                return
            elif args[0] == '@killmonster':
                if len(args) < 2:
                    ret_msg.chatMsg = '参数 @killmonster uid'
                    session.player.sendMsg(MsgDef.ServerCmd.CHAT_MSG , ret_msg)
                    return
                uidMon = int(args[1])
                obj = session.player.mapObj.getObjById(uidMon)
                if obj:
                    obj.subHP(obj.hp, session.player)
            elif args[0] == '@mapmonster':
                for monsterUid, monster in session.player.mapObj.allMonter.iteritems():
                    ret_msg.chatMsg = '%s x=%d y=%d uid=%d'%(monster.name, monster.x, monster.y, monster.uid)
                    session.player.sendMsg(MsgDef.ServerCmd.CHAT_MSG , ret_msg)
                return
            elif args[0] == '@mapnpc':
                for monsterUid, npc in session.player.mapObj.allNpc.iteritems():
                    ret_msg.chatMsg = '%s x=%d y=%d uid=%d'%(npc.name, npc.x, npc.y, npc.uid)
                    session.player.sendMsg(MsgDef.ServerCmd.CHAT_MSG , ret_msg)
                return
            elif args[0] == '@jump':
                if len(args) < 2:
                    ret_msg.chatMsg = '参数 @jump mapi x y'
                    session.player.sendMsg(MsgDef.ServerCmd.CHAT_MSG , ret_msg)
                    return
                mapname = args[1]
                x = None
                y = None
                if len(args) >= 4:
                    x = int(args[2])
                    y = int(args[3])
                mapObj = MapMgr.getMapMgr().allocMap(mapname)
                if not mapObj:
                    ret_msg.chatMsg = '地图不存在'
                    session.player.sendMsg(MsgDef.ServerCmd.CHAT_MSG , ret_msg)
                    return
                mapObj.playerEnterMap(session.player, x, y)
            elif args[0] == '@learnskill':
                if len(args) < 2:
                    ret_msg.chatMsg = '参数 @learnskill 技能id'
                    session.player.sendMsg(MsgDef.ServerCmd.CHAT_MSG , ret_msg)
                    return
                skillId = int(args[1])
                skillLv = 1
                if len(args) >= 3:
                    skillLv = int(args[2])
                session.player.skillCtrl.learnSkill(skillId, skillLv, True)
                return
            elif args[0] == '@delskill':
                if len(args) < 2:
                    ret_msg.chatMsg = '参数 @delskill 技能id'
                    session.player.sendMsg(MsgDef.ServerCmd.CHAT_MSG , ret_msg)
                    return
                skillId = int(args[1])
                skill = session.player.skillCtrl.delSkillByType(skillId)
                if skill:
                    ret_msg.chatMsg = '删除成功'
                    session.player.sendMsg(MsgDef.ServerCmd.CHAT_MSG , ret_msg)
                    from handler import SkillHandler
                    SkillHandler.processQuerySkill(session)
                else:
                    ret_msg.chatMsg = '删除失败'
                    session.player.sendMsg(MsgDef.ServerCmd.CHAT_MSG , ret_msg)
                return
            elif args[0] == '@skillpos':
                if len(args) < 2:
                    ret_msg.chatMsg = '参数 @learnskill 技能id position'
                    session.player.sendMsg(MsgDef.ServerCmd.CHAT_MSG , ret_msg)
                    return
                skillId = int(args[1])
                position = int(args[2])
                from handler import SkillHandler
                SkillHandler.processUpdateSkillPosReq(session, MsgDef.UpdateSkillPosReq({skillId:position}))
            elif args[0] == '@addbuff':
                if len(args) < 2:
                    ret_msg.chatMsg = '参数 @addbuff buffId'
                    session.player.sendMsg(MsgDef.ServerCmd.CHAT_MSG , ret_msg)
                    return
                buffId = int(args[1])
                buffSec= 10
                if len(args) >= 3:
                    buffSec = int(args[2])
                session.player.buffCtrl.addBuff(buffId, buffSec)
                session.player.updateBuffMsg()
                return
            elif args[0] == '@reloadcfg':
                from model import  NpcModel, MonsterModel
                NpcModel.getNpcMgr().init()
                return
            elif args[0] == '@alltask':
                for taskid, task in session.player.taskCtrl.allTask.iteritems():
                    ret_msg.chatMsg = 'taskid %d'%(taskid)
                    session.player.sendMsg(MsgDef.ServerCmd.CHAT_MSG , ret_msg)
                    return
                return
            elif args[0] == '@completetask':
                for taskid, task in session.player.taskCtrl.allTask.iteritems():
                    session.player.taskCtrl.trigger(task.action, task.object, task.destValue)
                return
            elif args[0] == '@settask':
                if len(args) < 2:
                    ret_msg.chatMsg = '参数 @settask taskid'
                    session.player.sendMsg(MsgDef.ServerCmd.CHAT_MSG , ret_msg)
                    return
                nextTaskId = int(args[1])
                for taskid, task in session.player.taskCtrl.allTask.iteritems():
                    session.player.taskCtrl.delTaskById(taskid)
                    newTask = session.player.taskCtrl.addTaskById(nextTaskId, False)
                    if newTask:
                        DbService.getPlayerService().replaceTask(session.player, newTask, taskid)
                    break
                from handler import  TaskHandler
                TaskHandler.processQueryTask(session)
                return
            elif args[0] == '@testb':

                msg = MsgDef.BrotherOpsReq(int(args[1]), [])
                msg.invitePlayers.append(long(args[2]))
                msg.invitePlayers.append(long(args[3]))
                msg.invitePlayers.append(long(args[4]))
                from handler import GuildHandler
                GuildHandler.processBrotherOps(session, msg)
                return
            elif args[0] == '@delb':
                if len(args) < 2:
                    ret_msg.chatMsg = '参数 @delb brotherid'
                    session.player.sendMsg(MsgDef.ServerCmd.CHAT_MSG , ret_msg)
                    return

                return
            elif args[0] == '@teste':
                if len(args) < 3:
                    ret_msg.chatMsg = '参数 @teste destuid itemid'
                    session.player.sendMsg(MsgDef.ServerCmd.CHAT_MSG , ret_msg)
                    return
                from handler import  ItemHandler
                ItemHandler.processExchangeOps(session, MsgDef.ExchangeOpsReq(3, 0, 10, {long(args[2]): 1}))
                return
            elif args[0] == '@kickoff':
                if len(args) < 2:
                    ret_msg.chatMsg = '参数 @kickoff playername'
                    session.player.sendMsg(MsgDef.ServerCmd.CHAT_MSG , ret_msg)
                    return
                sess = ffext.getSessionMgr().getSessionByName(args[1])
                if sess:
                    sess.close()
                return
            elif args[0] == '@createrole':
                req = MsgDef.CreateRoleReq()
                req.name = args[1]
                from handler import PlayerHandler
                PlayerHandler.processCreateRoleReq(session, req)
            elif args[0] == '@setpkvalue':
                if len(args) < 2:
                    ret_msg.chatMsg = '参数 @setpkvalue value'
                    session.player.sendMsg(MsgDef.ServerCmd.CHAT_MSG , ret_msg)
                    return
                session.player.pkSinValue = int(args[1])
                #更新pk罪恶值
                session.sendMsg(MsgDef.ServerCmd.PK_SIN_UPDATE_OPS, MsgDef.PkSinUpdateRet(0, session.player.pkSinValue))
            elif args[0] == '@testarena':
                if len(args) < 3:
                    ret_msg.chatMsg = '参数 @testarena uid1 uid2'
                    session.player.sendMsg(MsgDef.ServerCmd.CHAT_MSG , ret_msg)
                    return
                from model import ArenaModel
                sess = ffext.getSessionMgr().findByUid(long(args[1]))
                if not sess:
                    sess = session
                ArenaModel.getArenaMgr().createArena(sess.player, long(args[2]))
            elif args[0] == '@test_map':
                ffext.ff.test_map(session.player, session.player.uid, session.player.mapname, session.player.x, session.player.y)
            elif args[0] == '@force_gen_rank':
                # 强制-每日排行榜刷新
                from model import RankModel
                RankModel.getRankMgr().dailyRefresh()
            elif args[0] == '@sendmail':
                if len(args) < 7:
                    ret_msg.chatMsg = '参数 @sendmail uid sendtype title msg attachtype itemid'
                    session.player.sendMsg(MsgDef.ServerCmd.CHAT_MSG, ret_msg)
                    return
                node = MsgDef.MailAttachData(int(args[5]), int(args[6]))
                if node.arg1 != 0:
                    node.arg2 = 1
                    node = [node]
                else:
                    node = None
                from model import MailModel
                MailModel.doSendMailToPlayer(session.player, long(args[1]), int(args[2]), args[3], args[4], node)
                ret_msg.chatMsg = '发送成功'
                session.player.sendMsg(MsgDef.ServerCmd.CHAT_MSG, ret_msg)
            elif args[0] == '@guildlist':
                from handler import GuildHandler
                GuildHandler.processGuildListInfo(session, MsgDef.GuildMsgReq(MsgDef.GuildInfoClientCmd.GET_GUILD_ALL))
            elif args[0] == '@guildaddgold':
                # 强制-每日排行榜刷新
                from handler import GuildHandler
                GuildHandler.processGuildLevelOps(session, MsgDef.GuildLevelOpsMsgReq(MsgDef.GuildLevelClientCmd.UP_GUILD_EXP, 1))
            elif args[0] == '@createcopy':
                from handler import GuildHandler
                GuildHandler.processGuildOPS(session, MsgDef.GuildMsgReq(MsgDef.GuildOpsClientCmd.OPEN_COPY_MAP))
            elif args[0] == '@entercopy':
                from handler import GuildHandler
                GuildHandler.processGuildOPS(session, MsgDef.GuildMsgReq(MsgDef.GuildOpsClientCmd.ENTER_COPY_MAP))
            elif args[0] == '@randsuit':
                xiongJiaCfgId = 0
                xiongJiaItem = session.player.itemCtrl.allEquiped.get(Base.EQUIP_XIONGJIA_POS, None)
                if not xiongJiaItem:
                    itemCfgId = 30111113
                    sql = 'SELECT cfgid FROM "equipprop" WHERE itemtype = 103 AND job = %d and needlevel <= %d'%(session.player.job, session.player.level)
                    db = ffext.allocDbConnection('cfg', ffext.getConfig('-cfg'))
                    ret = db.queryResult(sql)
                    if ret:
                        result = ret.result
                        ffext.dump('result:', result)
                        randRow = result[random.randint(0, len(result) - 1)]
                        itemCfgId = int(randRow[0])
                    item = session.player.itemCtrl.addItemByCfgId(itemCfgId)
                    from handler import  ItemHandler
                    ItemHandler.processEquipItem(session, MsgDef.EquipOpsReq(item.uid))

        ffext.dump("chat", retVal)
        session.player.broadcast(MsgDef.ServerCmd.CHAT_MSG , retVal)
        return
        """

global GM2FUNC
GM2FUNC={}
def gm(gmCmd):
    def deco(func):
        def wraps(session, args):
            func(session, args)
        GM2FUNC[gmCmd] = func
        return wraps
    return deco


@gm('@setlevel')
def setlevel(session, args):
    from model import PlayerModel
    session.player.level = int(args[1])
    session.player.onLevelUp()
    session.player.updateLevelProp()
    # 发送属性数据
    PlayerModel.sendPropUpdateMsg(session.player)
@gm('@addanger')
def setlevel(session, args):
    from model import PlayerModel
    n = session.player.angerMax
    if len(args) >= 2:
        n = int(args[1])
    session.player.addAnger(n)
    session.player.updateLevelProp()
    # 发送属性数据
    PlayerModel.sendPropUpdateMsg(session.player)

@gm('@addexp')
def addexp(session, args):
    session.player.addExp(int(args[1]), True)


@gm('@close')
def close(session, args):
    session.close()


@gm('@addhpmp')
def addhpmp(session, args):
    session.player.addHPMsg(session.player.hpMax, session.player.mpMax)


@gm('@addgold')
def addgold(session, args):
    session.player.addGold(int(args[1]), True)


@gm('@cleartask')
def cleartask(session, args):
    DbService.getPlayerService().cleerTask(session.player)


@gm('@additem')
def additem(session, args):
    num = 1
    if len(args) >= 3:
        num = int(args[2])
    session.player.itemCtrl.addItemByName(args[1], num)
    from handler import ItemHandler
    ItemHandler.processQueryPkg(session)


@gm('@additemid')
def additemid(session, args):
    num = 1
    if len(args) >= 3:
        num = int(args[2])
    session.player.itemCtrl.addItemByCfgId(int(args[1]), num)
    from handler import ItemHandler
    ItemHandler.processQueryPkg(session)


@gm('@additembyid')
def additembyid(session, args):
    num = 1
    if len(args) >= 3:
        num = int(args[2])
    session.player.itemCtrl.addItemByCfgId(int(args[1]), num)
    from handler import ItemHandler
    ItemHandler.processQueryPkg(session)


@gm('@addmonster')
def addmonster(session, args):
    if len(args) < 4:
        ret_msg.chatMsg = '参数 @addmonster 怪名 x y'
        session.player.sendMsg(MsgDef.ServerCmd.CHAT_MSG, ret_msg)
        return
    from model import MonsterModel
    MonsterModel.genMonster(session.player.mapname, args[1], int(args[2]), int(args[3]), 1, 0)
    session.player.sendMsg(MsgDef.ServerCmd.CHAT_MSG, ret_msg)
    return


@gm('@killmonster')
def killmonster(session, args):
    if len(args) < 2:
        ret_msg.chatMsg = '参数 @killmonster uid'
        session.player.sendMsg(MsgDef.ServerCmd.CHAT_MSG, ret_msg)
        return
    uidMon = int(args[1])
    obj = session.player.mapObj.getObjById(uidMon)
    if obj:
        obj.subHP(obj.hp, session.player)


@gm('@mapmonster')
def mapmonster(session, args):
    for monsterUid, monster in session.player.mapObj.allMonter.iteritems():
        ret_msg.chatMsg = '%s x=%d y=%d uid=%d' % (monster.name, monster.x, monster.y, monster.uid)
        session.player.sendMsg(MsgDef.ServerCmd.CHAT_MSG, ret_msg)
    return


@gm('@mapnpc')
def mapnpc(session, args):
    for monsterUid, npc in session.player.mapObj.allNpc.iteritems():
        ret_msg.chatMsg = '%s x=%d y=%d uid=%d' % (npc.name, npc.x, npc.y, npc.uid)
        session.player.sendMsg(MsgDef.ServerCmd.CHAT_MSG, ret_msg)
    return


@gm('@jump')
def jump(session, args):
    if len(args) < 2:
        ret_msg.chatMsg = '参数 @jump mapi x y'
        session.player.sendMsg(MsgDef.ServerCmd.CHAT_MSG, ret_msg)
        return
    mapname = args[1]
    x = None
    y = None
    if len(args) >= 4:
        x = int(args[2])
        y = int(args[3])
    mapObj = MapMgr.getMapMgr().allocMap(mapname)
    if not mapObj:
        ret_msg.chatMsg = '地图不存在'
        session.player.sendMsg(MsgDef.ServerCmd.CHAT_MSG, ret_msg)
        return
    mapObj.playerEnterMap(session.player, x, y)


@gm('@learnskill')
def learnskill(session, args):
    if len(args) < 2:
        ret_msg.chatMsg = '参数 @learnskill 技能id'
        session.player.sendMsg(MsgDef.ServerCmd.CHAT_MSG, ret_msg)
        return
    skillId = int(args[1])
    skillLv = 1
    if len(args) >= 3:
        skillLv = int(args[2])
    session.player.skillCtrl.learnSkill(skillId, skillLv, True)
    return


@gm('@delskill')
def delskill(session, args):
    if len(args) < 2:
        ret_msg.chatMsg = '参数 @delskill 技能id'
        session.player.sendMsg(MsgDef.ServerCmd.CHAT_MSG, ret_msg)
        return
    skillId = int(args[1])
    skill = session.player.skillCtrl.delSkillByType(skillId)
    if skill:
        ret_msg.chatMsg = '删除成功'
        session.player.sendMsg(MsgDef.ServerCmd.CHAT_MSG, ret_msg)
        from handler import SkillHandler
        SkillHandler.processQuerySkill(session)
    else:
        ret_msg.chatMsg = '删除失败'
        session.player.sendMsg(MsgDef.ServerCmd.CHAT_MSG, ret_msg)
    return


@gm('@skillpos')
def skillops(session, args):
    if len(args) < 2:
        ret_msg.chatMsg = '参数 @learnskill 技能id position'
        session.player.sendMsg(MsgDef.ServerCmd.CHAT_MSG, ret_msg)
        return
    skillId = int(args[1])
    position = int(args[2])
    from handler import SkillHandler
    SkillHandler.processUpdateSkillPosReq(session, MsgDef.UpdateSkillPosReq({skillId: position}))


@gm('@addbuff')
def addbuff(session, args):
    if len(args) < 2:
        ret_msg.chatMsg = '参数 @addbuff buffId'
        session.player.sendMsg(MsgDef.ServerCmd.CHAT_MSG, ret_msg)
        return
    buffId = int(args[1])
    buffSec = 10
    if len(args) >= 3:
        buffSec = int(args[2])
    session.player.buffCtrl.addBuff(buffId, buffSec)
    session.player.updateBuffMsg()
    return


@gm('@reloadcfg')
def reloadcfg(session, args):
    from model import NpcModel, MonsterModel
    NpcModel.getNpcMgr().init()
    return


@gm('@alltask')
def alltask(session, args):
    for taskid, task in session.player.taskCtrl.allTask.iteritems():
        ret_msg.chatMsg = 'taskid %d' % (taskid)
        session.player.sendMsg(MsgDef.ServerCmd.CHAT_MSG, ret_msg)
        return
    return


@gm('@completetask')
def completetask(session, args):
    for taskid, task in session.player.taskCtrl.allTask.iteritems():
        session.player.taskCtrl.trigger(task.action, task.object, task.destValue)
    return


@gm('@settask')
def settask(session, args):
    if len(args) < 2:
        ret_msg.chatMsg = '参数 @settask taskid'
        session.player.sendMsg(MsgDef.ServerCmd.CHAT_MSG, ret_msg)
        return
    nextTaskId = int(args[1])
    for taskid, task in session.player.taskCtrl.allTask.iteritems():
        session.player.taskCtrl.delTaskById(taskid)
        newTask = session.player.taskCtrl.addTaskById(nextTaskId, False)
        if newTask:
            DbService.getPlayerService().replaceTask(session.player, newTask, taskid)
        break
    from handler import TaskHandler
    TaskHandler.processQueryTask(session)
    return


@gm('@testb')
def testb(session, args):
    msg = MsgDef.BrotherOpsReq(int(args[1]), [])
    msg.invitePlayers.append(long(args[2]))
    msg.invitePlayers.append(long(args[3]))
    msg.invitePlayers.append(long(args[4]))
    from handler import GuildHandler
    GuildHandler.processBrotherOps(session, msg)
    return


@gm('@delb')
def delb(session, args):
    if len(args) < 2:
        ret_msg.chatMsg = '参数 @delb brotherid'
        session.player.sendMsg(MsgDef.ServerCmd.CHAT_MSG, ret_msg)
        return

    return


@gm('@teste')
def teste(session, args):
    if len(args) < 3:
        ret_msg.chatMsg = '参数 @teste destuid itemid'
        session.player.sendMsg(MsgDef.ServerCmd.CHAT_MSG, ret_msg)
        return
    from handler import ItemHandler
    ItemHandler.processExchangeOps(session, MsgDef.ExchangeOpsReq(3, 0, 10, {long(args[2]): 1}))
    return


@gm('@kickoff')
def kickoff(session, args):
    if len(args) < 2:
        ret_msg.chatMsg = '参数 @kickoff playername'
        session.player.sendMsg(MsgDef.ServerCmd.CHAT_MSG, ret_msg)
        return
    sess = ffext.getSessionMgr().getSessionByName(args[1])
    if sess:
        sess.close()
    return


@gm('@createrole')
def createrole(session, msg):
    req = MsgDef.CreateRoleReq()
    req.name = args[1]
    from handler import PlayerHandler
    PlayerHandler.processCreateRoleReq(session, req)


@gm('@setpkvalue')
def setpkvalue(session, args):
    if len(args) < 2:
        ret_msg.chatMsg = '参数 @setpkvalue value'
        session.player.sendMsg(MsgDef.ServerCmd.CHAT_MSG, ret_msg)
        return
    session.player.pkSinValue = int(args[1])
    # 更新pk罪恶值
    session.sendMsg(MsgDef.ServerCmd.PK_SIN_UPDATE_OPS, MsgDef.PkSinUpdateRet(0, session.player.pkSinValue))


@gm('@testarena')
def testarena(session, args):
    if len(args) < 3:
        ret_msg.chatMsg = '参数 @testarena uid1 uid2'
        session.player.sendMsg(MsgDef.ServerCmd.CHAT_MSG, ret_msg)
        return
    from model import ArenaModel
    sess = ffext.getSessionMgr().findByUid(long(args[1]))
    if not sess:
        sess = session
    ArenaModel.getArenaMgr().createArena(sess.player, long(args[2]))
@gm('@resetarena')
def testarena(session, args):
    session.player.arenaCtrl.usedTimes = 0


@gm('@test_map')
def test_map(session, args):
    ffext.ff.test_map(session.player, session.player.uid, session.player.mapname, session.player.x, session.player.y)


@gm('@force_gen_rank')
def force_gen_rank(session, args):
    # 强制-每日排行榜刷新
    from model import RankModel
    RankModel.getRankMgr().dailyRefresh()


@gm('@sendmail')
def sendmail(session, args):
    if len(args) < 7:
        ret_msg.chatMsg = '参数 @sendmail uid sendtype title msg attachtype itemid'
        session.player.sendMsg(MsgDef.ServerCmd.CHAT_MSG, ret_msg)
        return
    node = MsgDef.MailAttachData(int(args[5]), int(args[6]))
    if node.arg1 != 0:
        node.arg2 = 1
        node = [node]
    else:
        node = None
    from model import MailModel
    MailModel.doSendMailToPlayer(session.player, long(args[1]), int(args[2]), args[3], args[4], node)
    ret_msg.chatMsg = '发送成功'
    session.player.sendMsg(MsgDef.ServerCmd.CHAT_MSG, ret_msg)


@gm('@guildlist')
def guildlist(session, args):
    from handler import GuildHandler
    GuildHandler.processGuildListInfo(session, MsgDef.GuildMsgReq(MsgDef.GuildInfoClientCmd.GET_GUILD_ALL))


@gm('@guildaddgold')
def guildaddgold(session, args):
    # 强制-每日排行榜刷新
    from handler import GuildHandler
    GuildHandler.processGuildLevelOps(session, MsgDef.GuildLevelOpsMsgReq(MsgDef.GuildLevelClientCmd.UP_GUILD_EXP, 1))


@gm('@createcopy')
def createcopy(session, args):
    from handler import GuildHandler
    GuildHandler.processGuildOPS(session, MsgDef.GuildMsgReq(MsgDef.GuildOpsClientCmd.OPEN_COPY_MAP))


@gm('@entercopy')
def entercopy(session, args):
    from handler import GuildHandler
    GuildHandler.processGuildOPS(session, MsgDef.GuildMsgReq(MsgDef.GuildOpsClientCmd.ENTER_COPY_MAP))


@gm('@randsuit')
def randsuit(session, args):
    xiongJiaCfgId = 0
    xiongJiaItem = session.player.itemCtrl.allEquiped.get(Base.EQUIP_XIONGJIA_POS, None)
    from handler import ItemHandler
    if xiongJiaItem:
        ffext.dump('randsuit...', xiongJiaItem.uid)
        ItemHandler.processUnEquipItem(session, MsgDef.EquipOpsReq(xiongJiaItem.uid))
        session.player.itemCtrl.delItem(xiongJiaItem.uid)
    itemCfgId = 30111113
    canUseCfgId = []
    needlv = 10#session.player.level
    randomLv = [1, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50]
    lv = randomLv[random.randint(0, len(randomLv) - 1)]
    sql = "SELECT cfgid FROM  equipprop  WHERE itemtype = 103 AND job = "+str(session.player.job)+" and name like '%" + str(lv) + "级-品质1-1套'"
    db = ffext.allocDbConnection('cfg', ffext.getConfig('-cfg'))
    ret = db.queryResult(sql)
    if ret:
        result = ret.result
        ffext.dump('result:', result)
        randRow = result[random.randint(0, len(result) - 1)]
        itemCfgId = int(randRow[0])
    item = session.player.itemCtrl.addItemByCfgId(itemCfgId)

    ItemHandler.processEquipItem(session, MsgDef.EquipOpsReq(item.uid))

@gm('@start_citywar')
def startcitywar(session, args):
    GuildModel.onCityWarStart()

@gm('@gm_citywar')
def gm_citywar(session, args):
    GuildModel.g_debugCityWar = 1
@gm('@go_citywar')
def go_citywar(session, args):
    from model import GlobalRecordModel
    citywar_info = GlobalRecordModel.getGlobalRecordMgr().citywar_info
    if citywar_info.copyMap:
        citywar_info.copyMap.playerEnterMap(session.player, 13, 50)
@gm('@setloginday')
def go_citywar(session, args):
    session.player.loginActCtrl.seven_login_days = int(args[1])
    session.player.loginActCtrl.updateData()
@gm('@setonlinetime')
def go_citywar(session, args):
    session.player.gametime = int(args[1])

@gm('@addguildexp')
def addGuildExp(session, args):
    from handler import GuildHandler
    gold = int(args[1])
    ffext.dump("gold")
    guildInfo = session.player.guildCtrl.guildInfo
    guildMemberList = GuildHandler.getMemberList(session)
    ret_msg = GuildHandler.processGuildLevelOpsMsgRet(1, 1, session.player.uid, session.player.name, gold, guildInfo.levelRanking, guildMemberList)
    ffext.dump('ret_msg', ret_msg)
    guildInfo.guildExp += gold
    GuildHandler.processGuildAllMemberRet(guildInfo, ret_msg, MsgDef.ServerCmd.GUILD_LEVEL_MSG)