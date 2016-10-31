# -*- coding: utf-8 -*-
#本页面用于存放全局对象（函数用于判断该类是否创建对象，如创建，则返回该对象，如没有创建，则创建后返回该对象。）
#本页面存放一个PlayerService类，用于存放本游戏中用户登录、创建等操作的SQL操作。使用该类时，请调用DbService文件中的getPlayerService()函数
#本页面存放一个DbServiceFriend类，用于存放本游戏中好友关系创建，删除等操作的SQL语句，使用该类时，请调用DbService文件中的getFriendService()函数

#引用本游戏中好友关系增删查的SQL操作类所在的文件，提供给getFriendService()函数，来声明一个对象
from db import DbServiceFriend as DbServiceFriend
#引用存放本游戏中用户登录、创建等操作的SQL操作类所在的文件，提供给getPlayerService()函数，来声明一个对象
from db import DbServicePlayer as DbServicePlayer
from db import DbServiceGuild as DbServiceGuild
from db import DbServiceLog as DbServiceLog

#声明一个函数，用于声明一个DbServiceFriend类的对象
gDbServiceFriend = DbServiceFriend.DbServiceFriend()
def getFriendService():
    return gDbServiceFriend
#声明一个函数，用于声明一个PlayerService类的对象s
gPlayerService = DbServicePlayer.PlayerService()
def getPlayerService():
    return gPlayerService
#声明一个函数，用于声明一个GuildService类的对象s
gGuildService = DbServiceGuild.DbServiceGuild()
def getGuildService():
    return gGuildService

gLogService = DbServiceLog.DbServiceLog()
def getLogService():
    return gLogService
