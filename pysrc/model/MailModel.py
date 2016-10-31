# -*- coding: utf-8 -*-
from msgtype import ttypes as MsgDef
import  weakref
import ffext
import idtool
from db import DbServicePlayer as DbServicePlayer
from db import DbService
from base import Base
import ffext
import json

MAIL_DELETE_ELAPSE_TIME_30DAY = 30 * 86400

class Mail(Base.BaseObj):
    def __init__(self):
        self.id         = 0
        self.type       = -1
        self.sender     = MsgDef.MailPlayerMsg()
        self.title      = ''
        self.msg        = ''
        self.listAttach = []
        self.sendTime   = 0
        self.status     = MsgDef.MailStatusType.MAIL_STATUS_UNREAD
    def getAttach(self):
        return self.listAttach
    def addAttach(self, att):
        self.listAttach.append(att)
    def removeAttach(self):
        self.listAttach = []
    def setStatus(self, st):
        self.status = st
    def initFromJson(self, obj):
        # 从DB读取的json字符串反序列化后，设置到内存
        self.id = obj.get('id', 0)
        self.type = obj.get('type', -1)
        self.title = obj.get('title', '').encode('utf-8')
        self.msg = obj.get('msg', '').encode('utf-8')
        self.sendTime = obj.get('send_tm', 0)
        self.status = obj.get('status', MsgDef.MailStatusType.MAIL_STATUS_UNREAD)

        getSender = obj.get('sender', {})
        self.sender.uid = getSender.get('uid', 0)
        self.sender.name = getSender.get('name', '').encode('utf-8')
        self.sender.job = getSender.get('job', 0)
        self.sender.gender = getSender.get('gender', 0)
        self.sender.level = getSender.get('level', 0)

        getListAtt = obj.get('list_att', [])
        for getAtt in getListAtt:
            newAtt = MsgDef.MailAttachData(
                getAtt.get('type', 0),
                getAtt.get('arg1', 0),
                getAtt.get('arg2', 0)
            )
            self.listAttach.append(newAtt)
            pass
        return
    def toJsonObj(self):
        if self.id == 0:
            # 非法邮件，没有初始化
            return None
        if self.sender:
            retSender = {
                'uid':      self.sender.uid,
                'name':     self.sender.name,
                'job':      self.sender.job,
                'gender':   self.sender.gender,
                'level':    self.sender.level,
            }
        else:
            retSender = {}
        retListAttach = []
        for attachNode in self.listAttach:
            singleAttach = {
                'type':     attachNode.type,
                'arg1':     attachNode.arg1,
                'arg2':     attachNode.arg2,
            }
            retListAttach.append(singleAttach)
            pass
        ret = {
            'id':       self.id,
            'type':     self.type,
            'sender':   retSender,
            'title':    self.title,
            'msg':      self.msg,
            'list_att': retListAttach,
            'send_tm':  self.sendTime,
            'status':   self.status,
        }
        return ret
    def toJsonStr(self):
        obj = self.toJsonObj()
        if not obj:
            return ''
        return json.dumps(obj, ensure_ascii=False)
    def convertToSendMailData(self):
        retData = MsgDef.MailDataNode()
        retData.mailId = self.id
        retData.msgType = self.type
        retData.sender = self.sender
        retData.title = self.title
        retData.msg = self.msg
        retData.listAttach = self.listAttach
        retData.sendTime = self.sendTime
        retData.status = self.status
        return retData
    # 声明一个函数，用于格式化打印
    def __repr__(self):
        L = ['%s=%r' % (key, value)
             for key, value in self.__dict__.iteritems()]
        return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

class MailCtrl(Base.BaseObj):
    def __init__(self, owner):
        self._owner      = weakref.ref(owner)   # {Player}
        self.allMail     = {}                   # mailId -> Mail
        return
    @property
    def owner(self):
        return self._owner()
    def getMail(self, mailId):
        return self.allMail.get(mailId)
    def addMail(self, mail, saveFlag = True, msgFlag = True):
        if not mail:
            return
        self.allMail[mail.id] = mail
        # 新增邮件，肯定别人发的，需要主动推送给玩家
        if msgFlag:
            updateNewMailMsg(self.owner, mail)
        if saveFlag:
            self.updateMailData()
        return
    def delMail(self, mailId, saveFlag = True):
        if mailId <= 0:
            return False
        dest = self.allMail.pop(mailId, None)
        if not dest:
            return False
        if saveFlag:
            self.updateMailData()
        return
    def updateMailData(self):
        DbService.getPlayerService().updateMail(self.owner.uid, self.allMailToJson())
        pass
    def allMailToJson(self):
        if len(self.allMail) == 0:
            # 特殊的空json字符串，为了方便离线玩家直接更新mailDB的字段
            return '[{}]'
        retAll = []
        for kk, aMail in self.allMail.items():
            aObj = aMail.toJsonObj()
            if aObj:
                retAll.append(aObj)
            pass
        if len(retAll) == 0:
            return '[{}]'
        retStr = json.dumps(retAll, ensure_ascii=False)
        return retStr
    def fromData(self, result):
        # 从DB获取的数据初始化邮件
        if not result or len(result) <= 0:
            createMailRecrodAtFirstTime(self.owner.uid)
            return
        row = result[0]
        mailDataStr = row[1]
        if not mailDataStr or mailDataStr == '':
            return
        # [{}]
        # [{}, {"d":1}]
        mailDataObj = json.loads(mailDataStr)
        for mailNodeObj in mailDataObj:
            if len(mailNodeObj) <= 0:
                continue
            newM = Mail()
            newM.initFromJson(mailNodeObj)
            mLastTm = ffext.getTime() - newM.sendTime
            # load时发现邮件超过30天，删除
            if mLastTm >= MAIL_DELETE_ELAPSE_TIME_30DAY:
                continue
            self.addMail(newM, False, False)
            pass
        return

    # 发邮件给一个目标
    def sendMail(self, toUid, sendType, title, msg):
        doSendMailToPlayer(self.owner, toUid, sendType, title, msg)
        pass

def doSendMailToPlayer(player, toUid, sendType, title, msg, listAtt = None):
    if not listAtt:
        listAtt = []
    tgtPlayer = ffext.getSessionMgr().findByUid(toUid)
    newMail = createNewMail(player, sendType, title, msg, listAtt)
    if not tgtPlayer:
        # 目标玩家-离线
        ffext.dump('tgtplayer', tgtPlayer)
        saveMailOffline(toUid, newMail)
    else:
        # 玩家在线
        tgtPlayer.player.mailCtrl.addMail(newMail)
    return

def playerToMailPlayer(player):
    mp = MsgDef.MailPlayerMsg()
    mp.uid = player.uid
    mp.name = player.name
    mp.job = player.job
    mp.gender = player.gender
    mp.level = player.level
    return mp

def createNewMail(player, type, title, msg, listAtt = None):
    mail = Mail()
    mail.id = idtool.allocId()
    mail.type = type
    if player:
        mail.sender = playerToMailPlayer(player)
    else:
        mail.sender = None
    mail.title = title
    mail.msg = msg
    mail.sendTime = ffext.getTime()
    if listAtt == None:
        listAtt = []
    mail.listAttach = listAtt
    return mail

def saveMailOffline(uid, mail):
    mailStr = mail.toJsonStr()
    if not mailStr or mailStr == '':
        return
    ffext.dump('mailStr', mailStr)
    DbService.getPlayerService().updateMail4Extend(uid, mailStr)
    return

def callbackCreateMailRecrodAtFirstTime(db):
    if not db.isOk():
        print("create mail record failed")
        pass

def createMailRecrodAtFirstTime(uid):
    DbService.getPlayerService().addMail(uid, '[{}]', callbackCreateMailRecrodAtFirstTime)
    pass

# 增加新邮件时，主动更新给在线玩家
def updateNewMailMsg(player, mail):
    newM = []
    newM.append(mail.convertToSendMailData())
    ret_msg = processMailOpsRet(MsgDef.MailOpsCmd.MAIL_OP_GET_NEW, player, [], mail.id, newM)
    player.sendMsg(MsgDef.ServerCmd.MAIL_OPS_MSG, ret_msg)
    pass

#邮件操作时，服务器给客户端广播的信息格式
def processMailOpsRet(opstype, player, listAllM = [], opMailId = 0, listNewM = []):
    ret_msg = MsgDef.MailOpsRet()
    ret_msg.opstype = opstype
    ret_msg.listAllMaill = listAllM
    ret_msg.opMailId = opMailId
    ret_msg.listNewMail = listNewM
    return  ret_msg