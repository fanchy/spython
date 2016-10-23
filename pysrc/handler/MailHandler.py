# -*- coding: utf-8 -*-
import ffext
import json
import weakref
import idtool
import msgtype.ttypes as MsgDef
from base import Base
from model import  MailModel, TeamModel, ItemModel
from db import DbServicePlayer as DbServicePlayer
from db import DbService

#邮件操作
@ffext.onLogic(MsgDef.ClientCmd.MAIL_OPS, MsgDef.MailOpsReq)
def processMarryOPS(session, msg):
    ffext.dump('processMailOPS', msg)
    opstype = msg.opstype
    cmd     = MsgDef.ClientCmd.MAIL_OPS
    player  = session.player

    mailId = msg.mailId
    sendToUid = msg.sendToUid
    sendTgtType = msg.sendTgtType
    title = msg.title
    if not title:
        title = ''
    msg = msg.msg
    if not msg:
        msg = ''
    if opstype == MsgDef.MailOpsCmd.MAIL_OP_ALL:
        # 获取个人所有邮件
        listAllM = []
        for kk, mail in player.mailCtrl.allMail.items():
            mailNode = mail.convertToSendMailData()
            listAllM.append(mailNode)
            pass
        session.sendMsg(MsgDef.ServerCmd.MAIL_OPS_MSG, MailModel.processMailOpsRet(opstype, player, listAllM, mailId))
        pass

    elif opstype == MsgDef.MailOpsCmd.MAIL_OP_SEND:
        # 发送邮件
        if sendTgtType == MsgDef.MailMsgType.MAIL_MSG_FRIEND:
            ## 好友目标...
            tgtFriend = player.friendCtrl.getFriendByUid(sendToUid)
            if not tgtFriend:
                session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, "目标不是好友!"))
                return
            MailModel.doSendMailToPlayer(player, sendToUid, sendTgtType, title, msg)
            session.sendMsg(MsgDef.ServerCmd.MAIL_OPS_MSG, MailModel.processMailOpsRet(opstype, player, [], mailId))
            pass
        elif sendTgtType == MsgDef.MailMsgType.MAIL_MSG_GUILD:
            tgtGuildMember = player.guildCtrl.guildInfo.allGuildMember
            for member in tgtGuildMember.iteritems():
                ffext.dump('member', member[0])
                if member[0] != player.uid:
                    MailModel.doSendMailToPlayer(player, member[0], sendTgtType, title, msg)
                    session.sendMsg(MsgDef.ServerCmd.MAIL_OPS_MSG, MailModel.processMailOpsRet(opstype, player, [], mailId))
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, "邮件已发出！"))
            #session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, "目前只支持发给好友!"))
        #pass

    elif opstype == MsgDef.MailOpsCmd.MAIL_OP_DEL:
        # 删除邮件
        mail = player.mailCtrl.getMail(mailId)
        if not mail:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, "邮件不存在!"))
            return
        player.mailCtrl.delMail(mailId)
        session.sendMsg(MsgDef.ServerCmd.MAIL_OPS_MSG, MailModel.processMailOpsRet(opstype, player, [], mailId))
        pass

    elif opstype == MsgDef.MailOpsCmd.MAIL_OP_BACK:
        # 回复邮件

        mail = player.mailCtrl.getMail(mailId)
        if not mail:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, "邮件不存在!"))
            return
        if mail.status == MsgDef.MailStatusType.MAIL_STATUS_BACKED:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, "邮件已回复!"))
            return
        backUid = mail.sender.uid
        backType = mail.type
        if sendTgtType == MsgDef.MailMsgType.MAIL_MSG_FRIEND:
            ## 好友目标...
            tgtFriend = player.friendCtrl.getFriendByUid(backUid)
            if not tgtFriend:
                session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, "回复目标不是好友!"))
                return
            MailModel.doSendMailToPlayer(player, backUid, backType, title, msg)
            mail.status = MsgDef.MailStatusType.MAIL_STATUS_BACKED
            session.sendMsg(MsgDef.ServerCmd.MAIL_OPS_MSG, MailModel.processMailOpsRet(opstype, player, [], mailId))
            pass
        elif sendTgtType == MsgDef.MailMsgType.MAIL_MSG_GUILD:
            ## 工会发送者目标...
            guildInfo = player.guildCtrl.guildInfo
            if not guildInfo:
                session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, "你不在公会中!"))
                return
            backGuildMem = guildInfo.getGuildMemberByUid(backUid)
            if not backGuildMem:
                session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, "回复目标不在公会中!"))
                return
            MailModel.doSendMailToPlayer(player, backUid, backType, title, msg)
            mail.status = MsgDef.MailStatusType.MAIL_STATUS_BACKED
            session.sendMsg(MsgDef.ServerCmd.MAIL_OPS_MSG, MailModel.processMailOpsRet(opstype, player, [], mailId))
            pass
        else:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, "目前只支持回复好友或工会!"))
            pass
        pass

    elif opstype == MsgDef.MailOpsCmd.MAIL_OP_TAKE_ATTACH:
        # 收取附件
        mail = player.mailCtrl.getMail(mailId)
        if not mail:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, "邮件不存在!"))
            return
        if len(mail.listAttach) <= 0:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, "邮件没有附件!"))
            return
        # 1. 发送附件的内容到“背包”
        for attachNode in mail.listAttach:
            mailAttachToPlayer(player, attachNode, opstype, cmd)
            pass

        # 2. 删除邮件里的附件内容
        mail.removeAttach()

        from handler import ItemHandler
        ItemHandler.processQueryPkg(session)
        # 3. 更新邮件数据
        player.mailCtrl.updateMailData()

        session.sendMsg(MsgDef.ServerCmd.MAIL_OPS_MSG, MailModel.processMailOpsRet(opstype, player, [], mailId))
        pass

    elif opstype == MsgDef.MailOpsCmd.MAIL_OP_MARK_READ:
        # 标记邮件已读
        mail = player.mailCtrl.getMail(mailId)
        if not mail:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, "邮件不存在!"))
            return
        if mail.status != MsgDef.MailStatusType.MAIL_STATUS_UNREAD:
            session.sendMsg(MsgDef.ServerCmd.ERROR_MSG, processErrorMsgRet(opstype, cmd, "邮件已读!"))
            return
        mail.status = MsgDef.MailStatusType.MAIL_STATUS_READ
        player.mailCtrl.updateMailData()
        session.sendMsg(MsgDef.ServerCmd.MAIL_OPS_MSG, MailModel.processMailOpsRet(opstype, player, [], mailId))
        pass

    pass


# 发送邮件附件中的道具、奖励等
def mailAttachToPlayer(player, attachNode, opstype, cmd):
    if not attachNode or not player:
        return
    if attachNode.type == MsgDef.MailAttachType.MAIL_ATTACH_ITEM:
        itemObj = player.itemCtrl.addItemByCfgId(attachNode.arg1, attachNode.arg2)
        if not itemObj:
            player.sendMsg(MsgDef.ServerCmd.ERROR_MSG, MailModel.processErrorMsgRet(opstype, cmd, '系统忙!'))
        pass
    elif attachNode.type == MsgDef.MailAttachType.MAIL_ATTACH_EXP:
        player.addExp(attachNode.arg1)
        pass
    elif attachNode.type == MsgDef.MailAttachType.MAIL_ATTACH_GOLD:
        player.addGold(attachNode.arg1)
        pass
    return

#用于返回错误信息的函数
def processErrorMsgRet(opstype, cmd, msg):
    ret_msg                 = MsgDef.ErrorMsgRet()
    ret_msg.errType         = opstype                           #错误信息所处位置opstype
    ret_msg.cmd             = cmd                               #错误信息所处位置cmd
    ret_msg.errMsg          = msg                               #错误信息
    return ret_msg

