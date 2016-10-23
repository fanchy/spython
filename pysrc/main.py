#-*- coding: utf-8 -*-

import os
TOPDIR = os.path.dirname(__file__)
TOPDIR = TOPDIR[0:-4]

if __name__ == '__main__':
    print('***************main just for check syntax error*************')
    import sys
    sys.path.append('./pysrc/justfortest')
    sys.path.append('./pysrc/pylib')
    sys.path.append('./pysrc')
    sys.path.append('pysrc/pylib/thrift')
    sys.path.append('pysrc/pylib/thrift/protocol')
    sys.path.append('pysrc/pylib/thrift/transport')
    TOPDIR = './'
    
import ffext

from db import DbServiceBase
from mapmgr import MapMgr
from db import DbService as DbService
import idtool

from model import MonsterModel , PlayerModel , ItemModel, SkillModel, TaskModel, NpcModel, GuildModel
from model import PetModel, TeamModel, MarryModel, RankModel, GlobalRecordModel, LoginRewardModel, ArenaModel

def init():
    #pdb.set_trace()
    print('scene init......')
    #if ffext.is_enable_option('-d'):
        #ffext.ENABLE_DUMP = False
    if not idtool.init(ffext.getConfig('-db')):
        ffext.error ('idtool init failed:'+ffext.getConfig('-db'))
        return -1
    if not DbServiceBase.init():
        ffext.error('scene init failed when DbService.init......')
        return -1

    if not GlobalRecordModel.getGlobalRecordMgr().init():
        ffext.error('scene init failed when GlobalRecordModel.getGlobalRecordMgr().init......')
        return -1
    if not MapMgr.getMapMgr().init(TOPDIR):
        ffext.error('scene init failed when MapMgr.getMapMgr().init......')
        return -1
    if not PlayerModel.getPlayerMgr().init():
        ffext.error('scene init failed when PlayerModel.getPlayerMgr().init......')
        return -1
    if not SkillModel.getSkillMgr().init():
        ffext.error('scene init failed when SkillModel.getSkillMgr().init()......')
        return -1
    if not SkillModel.getSkillMgr().initMonster():
        ffext.error('scene init failed when SkillModel.getSkillMgr().initMonster()......')
        return -1
    if not ItemModel.getItemMgr().init():
        ffext.error('scene init failed when ItemModel.getItemMgr().init().....')
        return -1

    #ffext.dump("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
    #pdb.set_trace()

    if not MonsterModel.getMonsterMgr().loadCfg():
        ffext.error('scene init failed when MonsterModel.loadCfg()......')
        return -1

    #pdb.set_trace()
    #ffext.dump("bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb")
    #pdb.set_trace()
    if not TaskModel.getTaskMgr().init():
        ffext.error('scene init failed when TaskModel.geTaskMgr().init()......')
        return -1

    #print "xxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    #pdb.set_trace()

    #读取NPC 配置
    if not NpcModel.getNpcMgr().init():
        ffext.error('scene init failed when NpcModel.getMgr().init()......')
        return -1
    if not PetModel.getPetMgr().init():
        ffext.error('scene init failed when PetModel.getMgr().init()......')
        return -1

    #读取行会配置
    if not GuildModel.getGuildMgr().init():
        ffext.error('scene init failed when GuildModel.getMgr().init()......')
        return -1
    if not TeamModel.getBrotherMgr().init():
        ffext.error('scene init failed when BrotherModel.getBrotherMgr().init()......')
        return -1
    if not MarryModel.getMarryMgr().init():
        ffext.error('scene init failed when MarryModel.getMarryMgr().init......')
        return -1
    if not RankModel.getRankMgr().init():
        ffext.error('scene init failed when RankModel.getRankMgr().init......')
        return -1

    # 读取每日登录配置
    if not LoginRewardModel.getLoginRewardMgr().init():
        ffext.error('scene init failed when LoginRewardModel.getLoginRewardMgr().init......')
        return -1
    if not ArenaModel.getArenaMgr().init():
        ffext.error('scene init failed when ArenaModel.init......')
        return -1

    #print "xxxxxxxx"
    #pdb.set_trace()
    ffext.timer(1000, MonsterModel.onTimer)
    MapMgr.getMapMgr().initTimer()
    #db.set_trace()
    ffext.timer(5000, PlayerModel.autoRecoverHpMp)
    GuildModel.getGuildMgr().initTimer()
    #print "autcitonTimer"
    #pdb.set_trace()
    ffext.timer(30000 , ItemModel.auctionOnTimer)
    #pdb.set_trace()
    return 0
    

def cleanup():
    print('scene cleanup.....')
    if not idtool.cleanup():
        print ('idtool cleanup failed')
        return -1
    return 0
import msgtype.ttypes as MsgDef
msg = MsgDef.UpdatePetExpRet(1, -2000000000, 3, 10000000000)
testmsg = ffext.encodeMsg(msg)
print('testmsg len', len(testmsg))
msg2 = MsgDef.UpdatePetExpRet(0, 0, 0, 0)
ffext.thriftDecodeMsg(msg2, testmsg)
print(msg.exp, msg.level, msg.expMax, msg.uid)
print(msg2.exp, msg2.level, msg2.expMax, msg.uid)
print('i64', 10000000000, 0x123, 0.123)