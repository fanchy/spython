# -*- coding: utf-8 -*-
#本页面存放一个DbServiceFriend类，用于存放本游戏中好友关系的增删查的SQL操作。使用该类时，请调用DbService文件中的getFriendService()函数

#引用数据库初始化页面，用于调用getDB()函数
from db import DbServiceBase as DbServiceBase
from model import FriendModel as FriendModel

#创建一个类，用于保存用户添加、查询、删除好友列表时的数据库操作呢
class DbServiceFriend:

    #添加好友
    def addFriend(self, uid, fid):
        sql  = "insert into friend (uid, fid) values ('%d', '%d') " % (uid, fid)
        sql2 = "insert into friend (uid, fid) values ('%d', '%d') " % (fid, uid)
        DbServiceBase.getDB().query(sql)
        DbServiceBase.getDB().query(sql2)
        return True
    #删除好友
    def delFriend(self, uid, fid):
        sql  = "delete from friend where uid = %d and fid = %d" % (uid, fid)
        sql2 = "delete from friend where uid = %d and fid = %d" % (fid, uid)
        DbServiceBase.getDB().query(sql)
        DbServiceBase.getDB().query(sql2)
        return True
    #添加仇人
    def addEnemy(self, uid, eid, typeId):
        sql  = "insert into enemy (uid, eid, typeId) values ('%d', '%d', '%d') " % (uid, eid, typeId)
        DbServiceBase.getDB().query(sql)
        return True
    #删除仇人
    def delEnemy(self, uid, eid, typeId):
        sql  = "delete from enemy where uid = %d and eid = %d and typeId = %d" % (uid, eid, typeId)
        DbServiceBase.getDB().query(sql)
        return True
