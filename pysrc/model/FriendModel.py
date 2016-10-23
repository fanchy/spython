# -*- coding: utf-8 -*-
#本文件用于存放好友列表字典的增删改查

#声明一个类，用于存放好友列表字典的增删改查
class FriendCtrl:
    #该类初始化两个字典属性，分别为allFriend，用于存储好友列表，allFriendTemp用于存放待验证的好友列表
    def __init__(self):
        self.allFriend          = {}
        self.allFriendTemp      = {}
        self.allEnemy           = {}
        self.allShieldPerson    = {}
    #声明一个函数，用于返回好友列表中的数目
    def getLenFriend(self):
        return len(self.allFriend)
    #声明一个函数，用于返回好友待验证列表中的数目
    def getLenFriendTemp(self):
        return len(self.allFriendTemp)
    def getLenaEnemy(self):
        return len(self.allEnemy)
    def getLenShieldPerson(self):
        return len(self.allShieldPerson)
    #声明一个函数，用于返回好友列表
    def getFriend(self):
        return self.allFriend
    #声明一个函数，用于返回待验证的好友列表
    def getFriendTemp(self):
        return self.allFriendTemp
    def getEnemy(self):
        return self.allEnemy
    def getShieldPerson(self):
        return self.allShieldPerson
    #通过好友ID查找好友列表中的好友属性
    def getFriendByUid(self, uid):
        return self.allFriend.get(uid)
    #通过好友ID查找待验证好友列表中的好友属性
    def getFriendTempByUid(self, uid):
        return self.allFriendTemp.get(uid)
    def getEnemyByUid(self, uid):
        return self.allEnemy.get(uid)
    def getShieldPersonByUid(self, uid):
        return self.allShieldPerson.get(uid)
    #将好友信息加入好友列表中
    def addFriend(self, player):
        friend = PlayerFriendInfo()
        #调用PlayerSocialInfo类中的函数，将player属性付给friend对象
        friend.setByPlayer(player)
        #将friend写入字典uid为Key
        self.allFriend[friend.uid] = friend
        return
    #通过待验证好友信息，将好友添加至好友列表中
    def addFriendByFriendTemp(self, uid):
        friend = self.getFriendTempByUid(uid)
        if  None == friend:
            return False
        self.allFriend[friend.uid] = friend
        self.allFriendTemp.pop(uid)
        return True
    #将好友信息添加至待验证好友列表中
    def addFriendTemp(self, player):
        friend = PlayerFriendInfo()
        friend.setByPlayer(player)
        self.allFriendTemp[friend.uid] = friend
        return
    def addEnemy(self, player):
        playerInfo = PlayerFriendInfo()
        playerInfo.setByPlayer(player)
        self.allEnemy[playerInfo.uid] = playerInfo
        return
    def addShieldPerson(self, player):
        playerInfo = PlayerFriendInfo()
        playerInfo.setByPlayer(player)
        self.allShieldPerson[playerInfo.uid] = playerInfo
        return
    #将好友从好友列表中删除
    def delFriend(self, uid):
        if self.getFriendByUid(uid) == None:
            return False
        self.allFriend.pop(uid)
        return True
    #将好友从待验证好友列表中删除
    def delFriendTempByUid(self, uid):
        if self.getFriendTempByUid(uid) == None:
            return False
        self.allFriendTemp.pop(uid)
        return True
    def delEnemyByUid(self, uid):
        if self.getEnemyByUid(uid) == None:
            return False
        self.allEnemy.pop(uid)
        return True
    def deShieldPersonByUid(self, uid):
        if self.getShieldPersonByUid(uid) == None:
            return False
        self.allShieldPerson.pop(uid)
        return True

    def fromDataFriend(self, result):
        for i in range(0, len(result)):
            playerInfo = PlayerFriendInfo()
            playerInfo.uid  = long(result[i][0])
            playerInfo.name = str(result[i][1])
            playerInfo.level= int(result[i][2])
            self.allFriend[playerInfo.uid] = playerInfo
        return
    def fromDataEnemy(self, result):
        for i in range(0, len(result)):
            playerInfo = PlayerFriendInfo()
            playerInfo.uid  = long(result[i][0])
            playerInfo.name = str(result[i][1])
            playerInfo.level= int(result[i][2])
            typeId = 0#int(result[i][2])
            if 0 == typeId:
                self.allEnemy[playerInfo.uid] = playerInfo
            else:
                self.allShieldPerson[playerInfo.uid] = playerInfo
        return






class PlayerFriendInfo:
    def __init__(self):
        self.uid        = 0
        self.name       = ''
        self.job        = 0             #职业
        self.gender     = 0             #性别
        self.level      = 0             #等级
        self.online     = False         #是否在线
    def setByPlayer(self,player):
        self.uid        = player.uid
        self.name       = player.name
        self.job        = player.job             #职业
        self.gender     = player.gender             #性别
        self.level      = player.level             #等级
    #声明一个函数，用于格式化打印
    def __repr__(self):
        L = ['%s=%r' % (key, value)
            for key, value in self.__dict__.iteritems()]
        return '%s(%s)' % (self.__class__.__name__, ', '.join(L))

