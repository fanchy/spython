# -*- coding: utf-8 -*-
from msgtype import ttypes as MsgDef
import idtool
from db import DbServicePlayer as DbServicePlayer
from db import DbService
from base import Base
import ffext
import json
import weakref

MARRY_GOLD = 0
MARRY_QUIT_GOLD = 1000000


def getAllMarriage():
    MARRY_CACHE = getMarryMgr().allMarryInfo
    return MARRY_CACHE

class PlayerMarryInfo(Base.BaseObj):
    def __init__(self, player = None):
        self.uid    = 0
        self.name   = ''
        self.job    = 0
        self.gender = 0
        self.level  = 0
        self.status = 0
        self.playerref = None
        if player:
            self.setPlayerMarryInfo(player)
    def getPlayer(self):
        if self.playerref:
            return self.playerref()
        return None
    def setPlayerMarryInfo(self, player):
        self.uid    = player.uid
        self.name   = player.name
        self.job    = player.job
        self.gender = player.gender
        self.level  = player.level

        self.playerref = weakref.ref(player)
        return
    def setPlayerMarry(self, uid, name, job, gender, level):
        self.uid    = uid
        self.name   = name
        self.job    = job
        self.gender = gender
        self.level  = level
        return
    #声明一个函数，用于格式化打印
    def __repr__(self):
        L = ['%s=%r' % (key, value)
            for key, value in self.__dict__.iteritems()]
        return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

class MarryItemInfo:
    def __init__(self):
        self.pos    = 0
        self.itemId = 0
    def setPlayerMarryInfo(self, pos, id):
        self.pos    = pos
        self.itemId = id
        return
    #声明一个函数，用于格式化打印
    def __repr__(self):
        L = ['%s=%r' % (key, value)
            for key, value in self.__dict__.iteritems()]
        return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

class MarryTotalInfo(Base.BaseObj):
    def __init__(self, id = 0):
        self.marryId                = id
        self.totalGold              = 0             #累计总礼金
        self.listAttends            = []            #参加婚礼名单
        self.coupleData             = [PlayerMarryInfo(), PlayerMarryInfo()]            #二人的uid name 等信息
        self.coupleData[0].gender   = Base.Gender.MALE
        self.coupleData[1].gender   = Base.Gender.FEMAIL
        self.flagXiTie              = 0             #是否发送过喜帖
        self.flagWeding             = 0             #婚礼的状态 WeddingFlagCmd
        self.tmWedding              = 0             #结婚时间
        self.tmEndWedding           = 0             #和谐离婚结束时间
        self.listSetItems           = {}
        return
    def assginFromDB(self, marryRow):
        self.coupleData[0].uid = long(marryRow[1])
        self.coupleData[1].uid = long(marryRow[2])
        self.fromJson4Extra(marryRow[4])
        self.fromJson4SetItems(marryRow[3])
        self.tmWedding = ffext.str2timestamp(marryRow[5])
        #ffext.dump('tmwedding', self.tmWedding, marryRow[5])
    def fromJson4Extra(self, data):
        ret = None
        if not data or data == '':
            return ret
        else:
            extraRet = json.loads(data)
            self.coupleData[0].name = extraRet.get('name1', '').encode('utf-8')
            
            self.coupleData[0].status = extraRet.get('status1', 0)
            self.coupleData[0].level = extraRet.get('level1', 0)
            self.coupleData[0].job = extraRet.get('job1', 0)

            self.coupleData[1].name = extraRet.get('name2', '').encode('utf-8')
            self.coupleData[1].status = extraRet.get('status2', 0)
            self.coupleData[1].level = extraRet.get('level2', 0)
            self.coupleData[1].job = extraRet.get('job2', 0)

            self.flagXiTie = extraRet.get('flagXiTie', 0)
            self.flagWeding = extraRet.get('flagWeding', 0)
            self.tmEndWedding = extraRet.get('tmEndWedding', 0)
            allAttends = extraRet.get('listAttends', [])
            for k in allAttends:
                tmpmsg = MsgDef.MarriagePlayerMsg()
                tmpmsg.uid  = k.get('uid', 0)
                tmpmsg.name = k.get('name', '')
                tmpmsg.level= k.get('level', '')
                self.listAttends.append(tmpmsg)
        return ret
    def toJson4Extra(self):
        ret = {
            'status1': self.coupleData[0].status,
            'level1': self.coupleData[0].level,
            'job1': self.coupleData[0].job,
            'status2': self.coupleData[1].status,
            'level2': self.coupleData[1].level,
            'job2': self.coupleData[1].job,
            'flagXiTie': self.flagXiTie,
            'flagWeding': self.flagWeding,
            'tmEndWedding': self.tmEndWedding,
            'name1': self.coupleData[0].name,
            'name2': self.coupleData[1].name,
            'listAttends':[],
        }
        for k in self.listAttends:
            tmp = {
                'uid': k.uid,
                'name':k.name,
                'level':k.level,
            }
            ret['listAttends'].append(tmp)
        return json.dumps(ret, ensure_ascii=False)
    def reset(self):
        self.marryId = 0
        self.totalGold = 0
        self.listAttends = []
        self.coupleData = [PlayerMarryInfo(), PlayerMarryInfo()]
        self.coupleData[0].gender   = Base.Gender.MALE
        self.coupleData[1].gender   = Base.Gender.FEMAIL
        self.flagXiTie = 0
        self.flagWeding = 0
        self.tmWedding = 0
        self.listSetItems = {}
    def getInfoByAnotherGender(self, gender):
        if gender == Base.Gender.MALE:
            return self.coupleData[1]
        return self.coupleData[0]
    def getInfoByGender(self, gender):
        if gender == Base.Gender.MALE:
            return self.coupleData[0]
        return self.coupleData[1]
    def getInfoByNotGender(self, gender):
        if gender == Base.Gender.MALE:
            return self.coupleData[1]
        return self.coupleData[0]
    def toJson4SetItems(self):
        return json.dumps(self.listSetItems)
    def fromJson4SetItems(self, data):
        ret = None
        if not data or data == '':
            ret = {}
        else:
            ret = json.loads(data)
        for k, v in ret.iteritems():
            self.listSetItems[int(k)] = v
        return True
    def addSetItem(self, pos, itemCgId):
        self.listSetItems[pos] = {'itemCfgId':itemCgId}#MsgDef.MarriageItem(pos, itemCgId)
        return True




class PersonMarryCtrl:
    def __init__(self, player, id = 0):
        self.ownerref               = weakref.ref(player)
        self._marryId                = id
        self.marryTotalInfo         = None
    def getStatus(self):
        gender = self.ownerref().gender
        if self.marryTotalInfo == None:
            return MsgDef.MarryStatusCmd.MARRY_STATUS_NOT
        return self.marryTotalInfo.getInfoByGender(gender).status
    def setStatus(self, value):
        gender = self.ownerref().gender
        if self.marryTotalInfo != None:
            self.marryTotalInfo.getInfoByGender(gender).status = value
    def getMarryInfo(self):
        gender = self.ownerref().gender
        if self.marryTotalInfo != None:
            return self.marryTotalInfo.getInfoByGender(gender)
        return None
    @property
    def marryId(self):
        if self.marryTotalInfo:
            return self.marryTotalInfo.marryId
        return 0
    @marryId.setter
    def marryId(self, value):
        self._marryId = value
    @property
    def marryFlag(self):
        return self.getStatus()
    @marryFlag.setter
    def marryFlag(self, value):
        self.setStatus(value)
    #载入DB数据初始化结婚信息，玩家login的时候触发
    #@param player:玩家对象
    #@param dbPlayerRow:玩家db记录
    def initFromDb(self, player, dbPlayerRow):
        if None == player or None == dbPlayerRow:
            return
        if self._marryId > 0:
            #self.marryFlag = MsgDef.MarryStatusCmd.MARRY_STATUS_MARRIED
            self.marryTotalInfo = getMarryMgr().getMarryTotalInfo(self._marryId)
            if self.marryTotalInfo:
                info = self.getMarryInfo()
                info.level = player.level
                info.job   = player.job
                info.playerref = weakref.ref(player)
            else:
                self._marryId = 0
        return

    #强制离婚
    def divorceForce(self):
        oldMarryId = self.marryId
        self.marryId                = 0
        self.marryTotalInfo         = None
        return

    def __repr__(self):
        L = ['%s=%r' % (key, value)
            for key, value in self.__dict__.iteritems()]
        return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

def handleTimerWedding(marryId):

    marryTotalInfo = getMarryMgr().getMarryTotalInfo(marryId)
    if not marryTotalInfo:
        return
    #ffext.dump('handleTimerWedding', marryTotalInfo)
    #举行婚礼
    playerSess = ffext.getSessionMgr().findByUid(marryTotalInfo.coupleData[0].uid)
    marryPlayerSess = ffext.getSessionMgr().findByUid(marryTotalInfo.coupleData[1].uid)
    if not playerSess or not marryPlayerSess:
        marryTotalInfo.flagWeding = MsgDef.WeddingFlagCmd.WEDDING_FAIL
        DbService.getPlayerService().updateMarry(marryTotalInfo)
        return
    player = playerSess.player
    from handler import  MarryHandler
    ret_msg2 = MarryHandler.processMarryOpsMsgRet(MsgDef.MarriageClientCmd.MARRY_WEDDING_START, player)
    #ffext.dump('marryTotalInfo.listAttends', marryTotalInfo.listAttends)
    for k in marryTotalInfo.listAttends:
        ret_msg2.argPlayer = k
        prizePlayer = player.mapObj.getPlayerById(k.uid)
        if prizePlayer:
            ret_msg2.argPlayer = k
            ret_msg2.gold = marryTotalInfo.totalGold
            prizePlayer.addGold(marryTotalInfo.totalGold)
            #清楚婚礼进行数据
            marryTotalInfo.totalGold = 0
            marryTotalInfo.listAttends = []
            break
    marryTotalInfo.flagWeding = MsgDef.WeddingFlagCmd.WEDDING_FINISH
    player.broadcast(MsgDef.ServerCmd.MARRIAGE_OPS_MSG, ret_msg2)

    #状态变化，更新数据库
    DbService.getPlayerService().updateMarry(marryTotalInfo)
def handleTimerDivorce(marryId):
    #ffext.dump('marry divorcing handleTimerDivorce', marryId)
    marryTotalInfo = getMarryMgr().getMarryTotalInfo(marryId)
    if not marryTotalInfo:
        return
    myMarryInfo = marryTotalInfo.getInfoByGender(Base.Gender.MALE)
    if myMarryInfo.status != MsgDef.MarryStatusCmd.MARRY_STATUS_DIVORCING:#取消了
        ffext.dump('marry divorcing handleTimerDivorce cancel', marryId)
        return
    getMarryMgr().delMarryById(marryTotalInfo.marryId)

    husbend = marryTotalInfo.coupleData[0].getPlayer()
    wife    = marryTotalInfo.coupleData[1].getPlayer()

    from handler import  MarryHandler
    opstype = MsgDef.MarriageClientCmd.MARRY_DIVORCE_NORMAL
    if husbend:
        husbend.marriageCtrl.divorceForce()
        ret_msg = MarryHandler.processMarryOpsMsgRet(opstype, husbend)
        husbend.sendMsg(MsgDef.ServerCmd.MARRIAGE_OPS_MSG, ret_msg)

    if wife:
        wife.marriageCtrl.divorceForce()
        ret_msg = MarryHandler.processMarryOpsMsgRet(opstype, wife)
        wife.sendMsg(MsgDef.ServerCmd.MARRIAGE_OPS_MSG, ret_msg)

    # 更新数据库
    DbService.getPlayerService().updateMarryDivorce(marryTotalInfo.marryId)
    DbService.getPlayerService().updateMarryDivorcePlayer(marryTotalInfo.coupleData[0].uid)
    DbService.getPlayerService().updateMarryDivorcePlayer(marryTotalInfo.coupleData[1].uid)
class MarryMgr:
    def __init__(self):
        self.allMarryInfo = {} #marryid -> marryTotalInfo
        return
    def getMarryTotalInfo(self, marryId):
        return self.allMarryInfo.get(marryId)
    def allocMarryTotalInfo(self, player1, player2):
        if player1.gender == Base.Gender.FEMAIL:
            tmp = player1
            player1 = player2
            player2 = tmp
        marryId = idtool.allocId()
        marryTotalInfo = MarryTotalInfo(marryId)
        marryTotalInfo.coupleData[0].setPlayerMarryInfo(player1)
        marryTotalInfo.coupleData[1].setPlayerMarryInfo(player2)

        player1.marriageCtrl.marryId = marryId
        player1.marriageCtrl.marryTotalInfo = marryTotalInfo

        player2.marriageCtrl.marryId = marryId
        player2.marriageCtrl.marryTotalInfo = marryTotalInfo
        self.allMarryInfo[marryId] = marryTotalInfo
        return marryTotalInfo
    def delMarryById(self, id):
        self.allMarryInfo.pop(id, None)
    def init(self):
        def cb(ret):
            for marryRow in ret.result:
                marryId = long(marryRow[0])
                marryTotalInfo = MarryTotalInfo(marryId)
                marryTotalInfo.assginFromDB(marryRow)
                #定时举行婚礼
                if marryTotalInfo.flagWeding == MsgDef.WeddingFlagCmd.WEDDING_APPLYED:
                    leftSec = ffext.getTime() - marryTotalInfo.tmWedding

                    if leftSec <= 0 or marryTotalInfo.tmWedding == 0:
                        leftSec = 30
                    #ffext.dump('timer wedding', leftSec, marryTotalInfo)
                    def cb():
                        handleTimerWedding(marryId)
                    ffext.timer(leftSec*1000, cb)
                #如果和谐离婚，定时离婚
                if marryTotalInfo.tmEndWedding != 0 and marryTotalInfo.getInfoByGender(Base.Gender.MALE).status == MsgDef.MarryStatusCmd.MARRY_STATUS_DIVORCING and \
                    marryTotalInfo.getInfoByGender(Base.Gender.FEMAIL).status == MsgDef.MarryStatusCmd.MARRY_STATUS_DIVORCING:
                    leftSec = marryTotalInfo.tmEndWedding - ffext.getTime()
                    if leftSec <= 0:
                        leftSec = 10
                    def cbDiv():
                        handleTimerDivorce(marryId)
                    #ffext.timer(leftSec*1000, cbDiv)
                    #ffext.dump('marry divorcing left sec', leftSec, marryId)
                #如果婚礼未举行
                self.allMarryInfo[marryTotalInfo.marryId] = marryTotalInfo
                #ffext.dump('load marryTotalInfo', marryTotalInfo)
            #ffext.dump('load self.allMarryInfo', len(self.allMarryInfo))
            return
        DbService.getPlayerService().loadAllMarry(cb)
        return True

gMgr = MarryMgr()
def getMarryMgr():
    return gMgr
