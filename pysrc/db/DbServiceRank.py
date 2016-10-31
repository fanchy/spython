# -*- coding: utf-8 -*-
#本页面存放一个DbServiceRank类，用于存放本游戏中排行榜操作的增删查的SQL操作。使用该类时，请调用DbService文件中的getRankService()函数
#引用数据库初始化页面，用于调用getDB()函数
from db import DbServiceBase as DbServiceBase


class DbServiceRank:
    #获取数据库中综合战力排行榜前20名人员信息。
    def getRankInfoList(self, callback):
        sql = "select guildid, name, createrName,empiric from guildinfo"
        DbServiceBase.getDB().query(sql, callback)
        return
    #获取数据库中职业战力排行榜前20名人员信息。
    def getRankInfoList(self, callback, job):
        sql = "select uid, name, job, level from player where job = %d order by level desc limit 20" % (job)
        DbServiceBase.getDB().query(sql, callback)
        return
    #获取数据库中等级排行榜前20名人员信息。
    def getLevelInfoList(self, callback):
        sql = "select uid, name, job, level from player order by level desc limit 20"
        DbServiceBase.getDB().query(sql, callback)
        return
    #获取数据库中金币排行榜前20名人员信息。
    def getGoldInfoList(self, callback):
        sql = "select uid, name, job, gold from player order by gold desc limit 20"
        DbServiceBase.getDB().query(sql, callback)
        return