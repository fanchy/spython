# -*- coding: utf-8 -*-
#本页面存放一个PlayerService类，用于存放本游戏中用户登录、创建等操作的SQL操作。使用该类时，请调用DbService文件中的getPlayerService()函数

#引用数据库初始化页面，用于调用getDB()函数

#创建一个类，用于存放本游戏中用户登录、创建等的数据库操作呢
class PlayerService:
    def loadUser(self, userName, callback, arg = None):
        sql = "select accountid, uid, name, job, gender, level, exp from player where username = '%s' and delflag <> 1 order by updatetime desc" %(userName)
        DbServiceBase.getDB().query(sql, callback, arg)
    def createUser(self, userName, callback, arg=None):
        def cb(ret):
            if len(ret.result) > 0:
                callback(ret)
                return
            now = ffext.datetime_to_str(ffext.datetime_from_time(ffext.getTime()))
            sql = "insert into user(username, password, create_time) values ('%s', '', '%s')" % (userName, now)
            ffext.dump('createUser', sql)
            DbServiceBase.getDB().query(sql)
            sql = "select id from user where username = '%s'" % (userName)
            DbServiceBase.getDB().query(sql, callback)
        sql = "select id from user where username = '%s'" % (userName)
        DbServiceBase.getDB().query(sql, cb)

    def createRole(self, user, role, mapname, x, y, callback):
        level = 1
        now = ffext.datetime_to_str(ffext.datetime_from_time(ffext.getTime()))
        #sql = "insert into player(accountid, uid, username, name, job, gender) values (%d, %d, '%s', '%s', %d, %d)" % (user.accountid, role.uid, user.username, role.name, role.job, role.gender)
        sql = "insert into player(accountid, uid, username, name, job, gender, mapname, x, y,skill,level,updatetime) \
            values (%d, %d, '%s', '%s', %d, %d, '%s', %d, %d, '',%d,'%s')" % \
              (user.accountid, role.uid, user.username, role.name, role.job, role.gender, str(mapname), x, y, level, now)
        ffext.dump(sql)
        DbServiceBase.getDB().query(sql, callback)
    def delRole(self, uid, callback = None):
        #sql = "insert into player(accountid, uid, username, name, job, gender) values (%d, %d, '%s', '%s', %d, %d)" % (user.accountid, role.uid, user.username, role.name, role.job, role.gender)
        sql = "update player set delflag = 1 where uid = %d" %(uid)
        ffext.dump(sql)
        DbServiceBase.getDB().query(sql, callback)
    def loadPlayer(self, uid, accountid, callback, argAreaFlag = None):
        selSet = {}
        #selSet['player'] = "select uid, name, job, gender, mapname, x, y, direction, level, exp, hp, mp, skill,gold,pksinvalue,pet,\
        #                pkgmaxsize,repomaxsize,extra,brotherid \
        #      from player where uid = %d" %(uid)
        ## 索引index注释:
        ## select player.uid->0,player.name->1,player.job->2,player.gender->3,player.mapname->4,player.x->5,player.y->6,player.direction->7,
        ## player.level->8, player.exp->9, player.hp->10, player.mp->11, player.skill->12,player.gold->13,player.pksinvalue->14,player.pet->15,
        ## player.pkgmaxsize->16,player.repomaxsize->17,player.extra->18,player.brotherid->19,
        ##player.moneybank->20,player.marryid->21,marryinviter->22 arenascore->23
        # selSet['player'] = "select player.uid,player.name,player.job,player.gender,player.mapname,player.x,player.y,player.direction,\
        #                 player.level, player.exp, player.hp, player.mp, player.skill,player.gold,player.pksinvalue,player.pet,\
        #                 player.pkgmaxsize,player.repomaxsize,player.extra,player.brotherid,\
        #                 player.uidmarry,marry.name,marry.job, marry.gender,marry.level,player.moneybank,player.marryid,player.marryinviter \
        #                 from player LEFT JOIN player marry on player.uidmarry = marry.uid where player.uid = %d" %(uid)
        selSet['player'] = "select uid,name,job,gender,mapname,x,y,direction,\
                        level, exp, hp, mp, skill,gold,pksinvalue,pet,\
                        pkgmaxsize,repomaxsize,extra,brotherid,\
                        moneybank,marryid,arenascore,last_logout,gametime, safePasswd \
                        from player where uid = %d" %(uid)

        selSet['item'] = "select itemid,cfgid,createtime,position,strengthen_level,lefttimes,propext from item where uid = %d"%(uid)
        selSet['pet'] = "select uid, cfgid,level,exp, createtime from pet where ownerid = %d"%(uid)
        if not argAreaFlag:
            selSet['task'] = "select taskid,status,value,createtime from task where uid = %d"%(uid)
            selSet['friend'] = "select player.uid as uid, name, level from player,friend where player.uid = friend.fid and friend.uid = %d" % (uid)
            selSet['enemy'] = "select player.uid as uid, name, level from player,enemy where player.uid = enemy.eid and enemy.uid = %d" % (uid)
            selSet['guild'] = "select guildid, daycontribute, lastdate from guildmemberinfo where uid = %d limit 1" % (uid)
            selSet['mail'] = "select uid, mail_data from mail where uid = %d" % (uid)
            if accountid and accountid > 0:
                selSet['login_activity'] = "select accountid,seven_login_days,seven_login_mask,\
                                            online_reward_mask,invite_reward from daily_login_activity where accountid = %d limit 1" % (accountid)
        DbServiceBase.getUserDB(uid).multiQuery(selSet, callback)
    