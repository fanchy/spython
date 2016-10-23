# -*- coding: utf-8 -*-
import random
from base   import Base
from mapmgr import MapMgr
import msgtype.ttypes as MsgDef
from db import DbService
import weakref
import ffext
import json
import idtool

class PetCfg(Base.BaseObj):
    def __init__(self):
        self.quality            = ''
        self.petType            = 0
        self.level              = 0
        self.expMax             = 0
        self.needlevel          = 0
        self.hp                 = 0
        self.mp                 = 0
        self.physicAttackMin  = 0
        self.physicAttackMax  = 0
        self.magicAttackMin   = 0
        self.magicAttackMax   = 0
        self.physicDefendMin  = 0
        self.physicDefendMax  = 0
        self.magicDefendMin   = 0
        self.magicDefendMax   = 0
        self.crit               = 0
        self.hit                = 0
        self.avoid              = 0
        self.attackspeed        = 0
        self.attacksing         = 0
        self.attackinterval     = 0
        self.attackdistance     = 0
        self.movespeed          = 0
        self.hurtabsorb         = 0
        self.hpabsorb           = 0
        #临时数据
        self.propData           = None
        self.cfgid              = 0
    def toPropData(self):
        if None != self.propData:
            return self.propData
        self.propData = {}
        self.propData[Base.PropType.HP_MAX] = self.hp
        self.propData[Base.PropType.MP_MAX] = self.mp
        self.propData[Base.PropType.PHYSIC_ATTACK_MIN] = self.physicAttackMin
        self.propData[Base.PropType.PHYSIC_ATTACK_MAX] = self.physicAttackMax
        self.propData[Base.PropType.MAGIC_ATTACK_MIN]  = self.magicAttackMin
        self.propData[Base.PropType.MAGIC_ATTACK_MAX]  = self.magicAttackMax
        self.propData[Base.PropType.PHYSIC_DEFEND_MIN] = self.physicDefendMin
        self.propData[Base.PropType.PHYSIC_DEFEND_MAX] = self.physicDefendMax
        self.propData[Base.PropType.MAGIC_DEFEND_MIN]  = self.magicDefendMin
        self.propData[Base.PropType.MAGIC_DEFEND_MAX]  = self.magicDefendMax

        self.propData[Base.PropType.CRIT]              = self.crit
        self.propData[Base.PropType.HIT]               = self.hit
        self.propData[Base.PropType.AVOID]             = self.avoid
        self.propData[Base.PropType.ATTACK_SPEED]      = self.attackspeed
        self.propData[Base.PropType.ATTACK_SING]       = self.attacksing
        self.propData[Base.PropType.ATTACK_INTERVAL]   = self.attackinterval
        self.propData[Base.PropType.ATTACK_DISTANCE]   = self.attackdistance
        self.propData[Base.PropType.MOVE_SPEED]        = self.movespeed
        self.propData[Base.PropType.HURT_ABSORB]       = self.hurtabsorb
        self.propData[Base.PropType.HP_ABSORB]         = self.hpabsorb
        toDel = []
        for k,v in self.propData.iteritems():
            if v == 0:
                toDel.append(k)
        for k in toDel:
            self.propData.pop(k, None)
        return self.propData

class Pet(Base.BaseObj):
    def __init__(self, owner):
        self.ownerref = weakref.ref(owner)
        self.uid      = 0
        self.level    = 1
        self.exp      = 0
        self.createTime = ffext.getTime()
        self.cfg      = None
    def addExp(self, exp, msgFlag = False):
        self.exp += exp
        oldLevel    = self.level
        curMaxExp   = self.cfg.expMax
        owner = self.ownerref()
        while (self.exp >= curMaxExp and curMaxExp > 0):
            newLevel  = self.level + 1
            cfg       = getPetMgr().getCfg(self.cfg.petType, newLevel)
            if None == cfg:#升到顶级了
                self.exp = curMaxExp
                break
            self.cfg  = cfg
            self.exp -= curMaxExp
            curMaxExp = self.cfg.expMax
            self.level= newLevel
            owner.addModuleProp(Base.PropModule.PET, cfg.toPropData())#增加属性
        player = self.ownerref()
        if msgFlag:#发送消息给客户端
            player.session.sendMsg(MsgDef.ServerCmd.UPDATE_PET_EXP, MsgDef.UpdatePetExpRet(self.exp, self.level, self.cfg.expMax, self.uid))
        DbService.getPlayerService().updatePet(player, self)
        return self.level - oldLevel
    def fromData(self, row):
        self.uid      = long(row[0])
        cfgid  = int(row[1])
        self.level    = int(row[2])
        if self.level <= 0:
            self.level = 1
        self.exp      = int(row[3])
        self.createtime=ffext.str2timestamp(row[4])
        self.cfg      = getPetMgr().getCfgById(cfgid)
        if self.cfg == None:
            ffext.dump('pet fromdata cfgid', cfgid)
            return False
        return True
class PetEgg:
    def __init__(self):
        self.eggItemCfgId = 0
        self.starttm = 0
        self.needsec = 0
class PetCtrl(Base.BaseObj):
    def __init__(self, owner):
        self.ownerref = weakref.ref(owner)
        self.allPet   = {} # uid -> Pet
        self.outPetUid= 0#当前跟随的宠物
        self.petEgg   = PetEgg()
    def petOut(self, uid):
        if self.outPetUid != 0:
            self.petIn(self.outPetUid)
        pet = self.getPet(uid)
        if None == pet:
            return None
        self.outPetUid = uid
        player = self.ownerref()
        player.addModuleProp(Base.PropModule.PET, pet.cfg.toPropData())#增加属性
        return pet
    def petIn(self, uid = 0):
        if self.outPetUid == 0:
            return None
        pet = self.getPet(self.outPetUid)
        if None == Pet:
            return None
        self.outPetUid = 0
        player = self.ownerref()
        player.subModuleProp(Base.PropModule.PET)
        return pet
    def getPet(self, uid):
        return self.allPet.get(uid)
    def completeEgg(self):#完成孵化
        nowtm = ffext.getTime()
        if self.petEgg.eggItemCfgId == 0:
            return False
        if nowtm < self.petEgg.starttm + self.petEgg.needsec:
            return False
        player = self.ownerref()
        pet = Pet(player)
        pet.uid = idtool.allocUid()
        cfgid = 1
        pet.cfg   = getPetMgr().getCfgById(cfgid)
        self.allPet[pet.uid] = pet
        DbService.getPlayerService().addPet(player, pet)

        self.petEgg.eggItemCfgId = 0
        self.petEgg.starttm      = 0
        self.petEgg.needsec      = 0
        return pet
    def fromData(self, result):
        ffext.dump('petctrl fromdata', result)
        player = self.ownerref()
        for row in result:
            pet = Pet(player)
            if True == pet.fromData(row):
                self.allPet[pet.uid] = pet
        return True
    def toJson(self):
        ret = {
             'eggItemCfgId': self.petEgg.eggItemCfgId,
             'starttm' : self.petEgg.starttm,
             'needsec' : self.petEgg.needsec,
            'outPetUid': self.outPetUid,
        }
        return ret
    def fromJson(self, data):
        ret = None
        if not data or data == '':
            ret = {}
        else:
            ret = json.loads(data)
        self.petEgg.eggItemCfgId = ret.get('eggItemCfgId', 0)
        self.petEgg.starttm = ret.get('starttm', 0)
        self.petEgg.needsec = ret.get('needsec', 0)
        self.outPetUid = ret.get('outPetUid', 0)
        return True
class PetMgr(Base.BaseObj):
    def __init__(self):
        self.str2Type = {'低': 1, '中':2, '高':3}
        self.allCfg   = {} #type -> level -> config
        self.id2cfg   = {}
    def getCfgById(self, id):
        return self.id2cfg.get(id)
    def init(self):#读取配置
        db = ffext.allocDbConnection('cfg',ffext.getConfig('-cfg'))
        ret = db.queryResult('select quality,level,expMax,needlevel,hp,mp,physic_attack_min,physic_attack_max,magic_attack_min,magic_attack_max,physic_defend_min,physic_defend_max,\
magic_defend_min,magic_defend_max,crit,hit,avoid,attackspeed,attacksing,attackinterval,attackdistance,movespeed,hurtabsorb,hpabsorb, cfgid from pet')
        self.allCfg = {}
        def toNum(s, d = 0):
            if s != '':
                return int(s)
            return d
        def toFloat(s, d = 0.0):
            if s != '':
                m = s.replace('%','')
                return float(m)
            return d
        for row in ret.result:
            cfg   = PetCfg()
            cfg.quality            = row[0]
            cfg.level              = int(row[1])
            cfg.expMax             = toNum(row[2])
            cfg.needlevel          = toNum(row[3])
            cfg.hp                 = toNum(row[4])
            cfg.mp                 = toNum(row[5])
            cfg.physicAttackMin    = toNum(row[6])
            cfg.physicAttackMax    = toNum(row[7])
            cfg.magicAttackMin     = toNum(row[8])
            cfg.magicAttackMax     = toNum(row[9])
            cfg.physicDefendMin    = toNum(row[10])
            cfg.physicDefendMax    = toNum(row[11])
            cfg.magicDefendMin     = toNum(row[12])
            cfg.magicDefendMax     = toNum(row[13])
            cfg.crit               = int(toFloat(row[14]) * Base.CRIT_RATE_BASE / 100)
            cfg.hit                = int(toFloat(row[15]) * Base.HIT_RATE_BASE / 100)
            cfg.avoid              = int(toFloat(row[16]) * Base.AVOID_RATE_BASE / 100)
            cfg.attackspeed        = toNum(row[17])
            cfg.attacksing         = toNum(row[18])
            cfg.attackinterval     = toNum(row[19])
            cfg.attackdistance     = toNum(row[20])
            cfg.movespeed          = toNum(row[21])
            cfg.hurtabsorb         = toNum(row[22])
            cfg.hpabsorb           = toNum(row[23])
            cfg.petType            = self.str2Type[cfg.quality]
            destDict               = self.allCfg.get(cfg.petType)
            cfg.cfgid                  = toNum(row[24])
            if None == destDict:
                destDict = {}
                self.allCfg[cfg.petType] = destDict
            destDict[cfg.level] = cfg
            self.id2cfg[cfg.cfgid]  = cfg
        ffext.dump('load pet num=%d'%(len(ret.result)))
        return True
    def getCfg(self, petType, level):
        destDict = self.allCfg.get(petType)
        if destDict:
            return destDict.get(level)
        return None
gPetMgr = PetMgr()
def getPetMgr():
    return gPetMgr
