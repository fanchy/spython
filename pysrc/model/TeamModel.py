# -*- coding: utf-8 -*-
#本文件用于存放组队字典的增删改查
from db import DbService as DbService
import idtool
import json
import weakref
import ffext
from base import Base
MAX_TEAM_NUM = 5
BROTHER_QUIT_GOLD = 500000





class PersonTeamCtrl:
    def __init__(self, player):
        self.ownerref          = weakref.ref(player)
        self.teamID            = 0
        self.allInviter        = []
    #修改组队信息
    def setTeamID(self, teamID):
        self.teamID = teamID
        return
    #获取组队信息
    def getTeamID(self):
        return self.teamID
    def isLeader(self):#是否是队长
        return  self.teamID == self.ownerref().uid
    def getTeam(self):
        return getTeamMgr().getTeamById(self.teamID)
    #判断ID是否在allInviter中，返回id在allInviter中出现的次数
    def getInviterById(self, teamID):
        return self.allInviter.count(teamID)
    #获取待验证列表中的行会信息
    def getInviter(self):
        return self.allInviter
    #将队伍信息加入至待验证列表
    def addInviter(self, teamID):
        if 0 == self.getInviterById(teamID):
            self.allInviter.append(teamID)
        return
    #将队伍邀请信息删除
    def delInviter(self, teamID):
        if 0 != self.getInviterById(teamID):
            self.allInviter.remove(teamID)
        return
    def __repr__(self):
        L = ['%s=%r' % (key, value)
            for key, value in self.__dict__.iteritems()]
        return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

#初始化队伍类。声明一个函数，用于存储全局对象teamInfoMgr
class TeamMgr:
    def __init__(self):
        self.allTeam       = {}        #行会成员列表
    #将新创建的行会写入行会字典
    def addTeam(self, player):
        teamInfo = teamInfoMgr()
        teamInfo.creatTeam(player)
        self.allTeam[teamInfo.teamID] = teamInfo
        return
    #解散队伍
    def delTeam(self, id):
        if None == self.getTeamById(id):
            return False
        self.allTeam.pop(id)
        return
    #通过ID获取队伍
    def getTeamById(self, id):
        return self.allTeam.get(id)
    #更改队长
    def setTeamLeader(self, uid, otherId):
        self.allTeam[otherId] = self.getTeamById(uid)
        self.getTeamById(uid).setTeamID(otherId)
        self.delTeam(uid)

    def __repr__(self):
        L = ['%s=%r' % (key, value)
            for key, value in self.__dict__.iteritems()]
        return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

gTeamMgr = TeamMgr()
def getTeamMgr():
    return gTeamMgr

class teamInfoMgr:
    def __init__(self):
        self.teamID                = 0         #队伍ID
        self.allTeamMember         = {}        #队伍成员列表
        self.allTeamMemberTemp     = {}        #申请加入队伍成员列表
    #获取队伍成员数量
    def getLenTeamMember(self):
        return int(len(self.allTeamMember))
    #获取申请加入队伍人员数量
    def getLenTeamMemberTemp(self):
        return int(len(self.allTeamMemberTemp))
    #获取队伍成员信息
    def getTeamMember(self):
        return self.allTeamMember
    #通过UID获取队伍成员信息
    def getTeamMemberByUid(self, uid):
        return self.allTeamMember.get(uid)
    #获取申请加入队伍人员信息
    def getTeamMemberTemp(self):
        return self.allTeamMemberTemp
    #通过Uid获取申请加入队伍人员信息
    def getTeamMemberTempByUid(self, uid):
        return self.allTeamMemberTemp.get(uid)
    #获取队伍ID
    def getTeamID(self):
        return self.teamID
    #将成员信息加入至队伍列表
    def addTeamMember(self, player):
        teamMember = PlayerTeamInfo()
        teamMember.setPlayerTeamInfo(player)
        self.allTeamMember[teamMember.uid] = teamMember
        return
    #将成员信息加入至申请加入队伍成员列表
    def addTeamMemberTemp(self, player):
        teamMember = PlayerTeamInfo()
        teamMember.setPlayerTeamInfo(player)
        self.allTeamMemberTemp[teamMember.uid] = teamMember
        return
    #通过待验证队伍成员信息将成员信息加入至申请加入队伍成员列表
    def addTeamMemberByTeamMemberTemp(self, uid):
        teamMember = self.getTeamMemberTempByUid(uid)
        if None == teamMember:
            return False
        self.allTeamMember[teamMember.uid] = teamMember
        self.allTeamMemberTemp.pop(uid)
        return True
    #将成员信息从队伍中删除
    def delTeamMember(self, uid):
        if None == self.getTeamMemberByUid(uid):
            return False
        self.allTeamMember.pop(uid)
        return True
    #将成员信息从待验证队伍成员中删除
    def delTeamMemberTemp(self, uid):
        if None == self.getTeamMemberTempByUid(uid):
            return False
        self.allTeamMemberTemp.pop(uid)
        return True
    #修改队伍ID
    def setTeamID(self, teamID):
        self.teamID = teamID
        return
    #创建队伍
    def creatTeam(self, player):
        self.addTeamMember(player)
        self.allTeamMemberTemp     = {}
        self.teamID                = player.uid

    def __repr__(self):
        L = ['%s=%r' % (key, value)
            for key, value in self.__dict__.iteritems()]
        return '%s(%s)' % (self.__class__.__name__, ', '.join(L))
class PlayerTeamInfo:
    def __init__(self):
        self.uid    = 0
        self.name   = ''
        self.job    = 0
        self.gender = 0
        self.level  = 0
        self.hp    = 0
        self.hpMax = 0
        self.mp  = 0
        self.mpMax    = 0
        self.anger = 0
        self.angerMax  = 0
    def setPlayerTeamInfo(self,player):
        self.uid    = player.uid
        self.name   = player.name
        self.job    = player.job
        self.gender = player.gender
        self.level  = player.level
        self.hp     = player.hp
        self.hpMax  = player.hpMax
        self.mp     = player.mp
        self.mpMax  = player.mpMax
        self.anger  = player.anger
        self.angerMax  = player.angerMax
        return
    #声明一个函数，用于格式化打印
    def __repr__(self):
        L = ['%s=%r' % (key, value)
            for key, value in self.__dict__.iteritems()]
        return '%s(%s)' % (self.__class__.__name__, ', '.join(L))
#以上为组队的相关信息


#以下为结义的相关信息

#枚举用户的结义状态
class BrotherFlag:
    flag1 = 1   #未又结义操作状态
    flag2 = 2   #已被邀请状态
    flag3 = 3   #已同意邀请状态
    flag4 = 4   #已结义状态
    flag5 = 5   #待取消结义状态


class PersonBrotherCtrl:
    def __init__(self):
        self.brotherInfo            = None
        self.inviter                = []            #待结义的其它成员信息
        self.brotherFlag            = BrotherFlag.flag1
        self.tmpBrotherInfo         = None #临时结义数据，结义操作过程中，临时存在这里
    # #将数据库中查询出的数据，传递至用户对象中
    def fromData(self, brotherid, player = None):
        for key, val in getBrotherMgr().getBrotherList().iteritems():
            if val.bid == brotherid:
                self.brotherInfo    = getBrotherMgr().getBrotherById(brotherid)
                self.inviter        = []
                if (self.brotherInfo.flag):
                    self.brotherFlag    = BrotherFlag.flag4
                else:
                    self.brotherFlag    = BrotherFlag.flag5
                return
        self.brotherInfo            = None
        self.inviter                = []            #待结义的其它成员信息
        self.brotherFlag            = BrotherFlag.flag1
        self.delBrother(player)
        return
    #解除结义
    def delBrother(self, player = None):
        self.brotherInfo = None
        self.brotherFlag = BrotherFlag.flag1
        if player:
            if player.skillCtrl.delSkillByType(Base.BRO_SKILL_ID):
                from handler import SkillHandler
                SkillHandler.processQuerySkill(player.session)
        return
    #加入结义
    def AddBrother(self, id):
        self.brotherInfo = getBrotherMgr().getBrotherById(id)
        self.inviter     = []
        return
    #加入邀请
    def AddBrotherInviter(self, uid1,  uid2):
        self.inviter.append(uid1)
        self.inviter.append(uid2)
        self.brotherFlag = BrotherFlag.flag2
        return
    #拒绝邀请
    def refuseBrotherInviter(self):
        self.inviter     = []
        self.brotherFlag = BrotherFlag.flag1
        return
    #再次确认邀请
    def confirmBrotherInviter(self):
        self.brotherFlag = BrotherFlag.flag4
        return
    #同意邀请
    def verifyBrotherInviter(self):
        self.brotherFlag = BrotherFlag.flag3
        return
    #协商退出
    def consultBrotherQuit(self):
        self.brotherFlag = BrotherFlag.flag5
        return
    def __repr__(self):
        L = ['%s=%r' % (key, value)
            for key, value in self.__dict__.iteritems()]
        return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

#初始化队伍类。声明一个函数，用于存储全局对象teamInfoMgr
class BrotherMgr:
    def __init__(self):
        self.allBrotherList       = {}        #行会成员列表
    def init(self):
        def brotherInfo(ret):
            ffext.dump('brother init', ret.result)
            if ret.flag == False or len(ret.result) == 0:
                self.allBrotherList       = {}
                return
            for i in range(0, len(ret.result)):
                brotherID = long(ret.result[i][0])
                if None == self.getBrotherById(brotherID):
                    brotherCtrl = BrotherCtrl()
                    brotherCtrl.bid         = brotherID
                    brotherCtrl.allBrothers = {}
                    brotherCtrl.flag        = True
                    extra       = str(ret.result[i][1])
                    if extra != '':
                        extra = json.loads(extra)
                        if extra:
                            brotherCtrl.extra  = extra
                    brotherCtrl.ranking     = 0
                    self.allBrotherList[brotherCtrl.bid]        = brotherCtrl
                brotherCtrl = self.getBrotherById(brotherID)
                playerBrotherInfo = PlayerBrotherInfo()
                playerBrotherInfo.setPlayerBrother(long(ret.result[i][2]), str(ret.result[i][3]), long(ret.result[i][4]), long(ret.result[i][5]), long(ret.result[i][6]))
                brotherCtrl.allBrothers[playerBrotherInfo.uid]        = playerBrotherInfo
            return
        DbService.getGuildService().syncGetBrotherMemberInfoList(brotherInfo)
        return True
    #将新的结义列表存入字典
    def addBrotherList(self, player1, player2, player3):
        brotherid = idtool.allocId()
        brother = BrotherCtrl()
        brother.bid = brotherid
        brother.addBrotherMember(player1, player2, player3)
        #brother.extra = ''
        self.allBrotherList[brother.bid] = brother
        DbService.getGuildService().addBrother(brotherid, player1.uid, player2.uid, player3.uid)
        return brotherid
    def addBrotherInfo(self, brotherInfo):
        brotherid = idtool.allocId()
        brotherInfo.bid = brotherid
        self.allBrotherList[brotherInfo.bid] = brotherInfo
        playerInfo = brotherInfo.getPlayerInfo()
        DbService.getGuildService().addBrother(brotherid, playerInfo[0].uid, playerInfo[1].uid, playerInfo[2].uid)
    #通过ID获取结义
    def getBrotherById(self, id):
        return self.allBrotherList.get(id)
    def getBrotherList(self):
        return self.allBrotherList
    #解除结义
    def delBrother(self, bid):
        brotherCtrl = self.allBrotherList.pop(bid)
        if None == brotherCtrl:
            return False
        DbService.getGuildService().delBrother(brotherCtrl)
        return True


    def __repr__(self):
        L = ['%s=%r' % (key, value)
            for key, value in self.__dict__.iteritems()]
        return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

gBrotherMgr = BrotherMgr()
def getBrotherMgr():
    return gBrotherMgr



class BrotherCtrl:
    def __init__(self):
        self.bid               = 0  #结义ID
        self.allBrothers       = {} #uid -> PlayerBrotherInfo
        self.extra             = {}
        self.flag              = False #用于标识结义是否正常
        self.ranking           = 0 #结义排名（暂时未提供）
    #将成员信息加入至队伍列表
    def addBrotherMember(self, player1, player2, player3):
        brotherMember = PlayerBrotherInfo()
        brotherMember.setPlayerBrotherInfo(player1)
        self.allBrothers[brotherMember.uid] = brotherMember
        brotherMember = PlayerBrotherInfo()
        brotherMember.setPlayerBrotherInfo(player2)
        self.allBrothers[brotherMember.uid] = brotherMember
        brotherMember = PlayerBrotherInfo()
        brotherMember.setPlayerBrotherInfo(player3)
        self.allBrothers[brotherMember.uid] = brotherMember
        return
    def getMemberInfo(self, uid):
        return self.allBrothers.get(uid)
    def getPlayers(self):
        ret = []
        for k, v in self.allBrothers.iteritems():
            p = None
            if v.ownerref:
                p = v.ownerref()
            ret.append(p)
        return ret

    def getPlayerInfo(self):
        ret = []
        for k, v in self.allBrothers.iteritems():
            ret.append(v)
        return ret
    def getBrotherMember(self):
        return self.allBrothers
    def getBrotherExtra(self):
        return self.extra
    def delTime(self):
        self.flag = True
        if None == self.getBrotherExtra().pop('delTime', None):
            return False
        DbService.getGuildService().updateBrotherExtra(self.bid, json.dumps(self.extra))
        return
    def addTime(self, time):
        self.flag = False
        self.extra['delTime'] = time
        DbService.getGuildService().updateBrotherExtra(self.bid, json.dumps(self.extra))
        return
    def getBrotherExtraByKey(self, key):
        return self.extra.get(key , None)
    def __repr__(self):
        L = ['%s=%r' % (key, value)
            for key, value in self.__dict__.iteritems()]
        return '%s(%s)' % (self.__class__.__name__, ', '.join(L))



class BrotherStatus:
    BRO_NONE = 0 #未结义
    BRO_VERIFY_INVIT = 1  # 同意邀请
    BRO_CONFIRM = 2 #确认
    BRO_OK      = 3 #结义完成
    BRO_QUIT      = 4 #结义请求解除

class PlayerBrotherInfo:
    def __init__(self):
        self.uid    = 0
        self.name   = ''
        self.job    = 0
        self.gender = 0
        self.level  = 0
        self.ownerref = None
        self.status = 0#
    def setPlayerBrotherInfo(self, player):
        self.uid    = player.uid
        self.name   = player.name
        self.job    = player.job
        self.gender = player.gender
        self.level  = player.level
        self.ownerref = weakref.ref(player)
        return
    def setPlayerBrother(self, uid, name, job, gender, level):
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