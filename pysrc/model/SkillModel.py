# -*- coding: utf-8 -*-
import random
from base   import Base
from mapmgr import MapMgr
import msgtype.ttypes as MsgDef


from model.skill import SkillCalculatorZhanShi
from model.skill import SkillCalculatorFaShi
from model.skill import SkillCalculatorShuShi
from model.skill import SkillCalculatorYouXia
import  weakref
import ffext
import  json

class SkillCfg(Base.BaseObj):
    def __init__(self):
        self.skillId      = 0#唯一ID
        self.skillType    = 0#同一个技能不同等级，类型相同
        self.name         = ''
        self.intro        = ''
        self.mp           = 0
        self.cd           = 0
        self.attackSpeed  = 0
        self.attackSing   = 0
        self.attackInterval= 0
        self.attackDistance= 0
        self.attackRange  = 0
        self.costAnger    = 0
        self.needlevel    = 0
        self.skillLevel   = 0
        self.lastsec      = 0
        #技能伤害公式
        self.hurtCalcultor  = None
    def getJob(self):
        unlevelUpSkill = [2001, 2011, 3001, 3002, 3003, 3004]
        if self.skillId in unlevelUpSkill:
            return 0
        elif self.skillId >= 1000:
            return int(self.skillId % 5)
        else:
            return int(self.skillId / 100)
class Skill(Base.BaseObj):
    def __init__(self):
        self.skillType    = 0
        self.skillLevel   = 0
        self.lastUsedTmMs = 0#上次使用时间
        self.position     = 0#技能存放位置
        self.skillCfg     = None
        self.ownerref     = None#技能拥有者,玩家或者怪
        self.exp          = 0#技能经验
    @property
    def skillId(self):
        return self.skillCfg.skillId
    def getLastSec(self):#技能持续时间
        return self.skillCfg.lastsec
    #update 接口 0表示技能不能释放，1表示释放成功
    def useSkill(self, tmMs):
        return 0#表示
    def onEvent(self, event):
        return True
def skillId2Level(skillId):
    if skillId >= 1000:
        return 1
    return int(int(skillId) % 10) + 1
def skillId2Type(skillId):
    if skillId >= 1000:
        return skillId
    return int(int(skillId) / 10)*10
class SkillCtrl(Base.BaseObj):
    def __init__(self, owner):
        self.ownerref      = weakref.ref(owner)
        self.allSkill   = {}   #skillType -> skill
        self.skillUsing = None #正在使用的技能
        return
    #返回技能拥有者
    def owner(self):
        return self.ownerref()
    def getSkillByType(self, skillType):
        return self.allSkill.get(skillType)
    def getSkillById(self, skillId):
        return self.allSkill.get(skillId2Type(skillId))
    def addSkillBySkill(self, skill):
        self.allSkill[skill.skillId] = skill
        return True
    def delSkillByType(self, skillType):
        dest = self.allSkill.pop(skillType, None)
        if dest:
            return True
        else:
            return  False
    def delSkillById(self, skillId):
        dest = self.allSkill.pop(skillId2Type(skillId), None)
        if dest:
            return True
        else:
            return  False
    def toData(self):
        nType = 0
        player = self.ownerref()
        if player:
            nType = player.modeAttack
        ret = {
            0:{
                 'lv' : nType,
            },
        }
        for skillType, skill in self.allSkill.iteritems():
            tmpData = {
                'lv' : skill.skillLevel,
                'utm': skill.lastUsedTmMs,
                'pos': skill.position,
                'exp': skill.exp
            }
            ret[skillType] = tmpData
        #ffext.dump('ALLSKILL!!!!!!!!!!!!!!',self.allSkill)
        return ret
    def fromData(self, data):
        #ffext.dump('data=', data)
        ret = None
        if not data or data == '':
            ret = {}
        else:
            ret = json.loads(data)
        for skillType, tmpData in ret.iteritems():
            nType = int(skillType)
            if nType == 0:#攻击模式
                player = self.ownerref()
                if player:
                    player.modeAttack = int(tmpData.get('lv', 0))
            skill = Skill()
            skill.skillType = nType
            skill.skillLevel = int(tmpData['lv'])
            if skill.skillLevel <=  0:
                skill.skillLevel = 1
            skill.position = tmpData.get('pos', 0)
            skill.skillCfg= getSkillMgr().getCfgByTypeLevel(skill.skillType, skill.skillLevel)
            if not skill.skillCfg and skill.skillType != Base.MAKE_ITEM_ID:
                ffext.dump('SKILLCFG!!!!!!!!!!!!!!!!!', skill.skillType)
                continue
            skill.lastUsedTmMs = int(tmpData['utm'])
            skill.owner        = self.ownerref
            skill.exp = tmpData.get('exp',0 )
            self.allSkill[skill.skillType] = skill
            #ffext.dump('ALLSKILL!!!!!!!!!!!!!!!!!!!!!!!!', self.allSkill)
        if len(self.allSkill) <= 1:
            cfg = getSkillMgr().getDefaultSkillList(self.ownerref().job)
            ffext.dump(cfg)
            for skillCfg in cfg:
                ffext.dump('add default skillcfg', skillCfg)
                try:
                    self.learnSkill(skillCfg.skillType, skillCfg.skillLevel)
                except:
                    pass
        return ret
    def onEvent(self, event):
        if self.skillUsing:
            self.skillUsing.onEvent(event)
            return True
        return False
    #怪物的自动使用技能
    def autoUseSkill(self, objTarget, tmMs):
        if self.skillUsing and tmMs - self.skillUsing.lastUsedTmMs < self.skillUsing.getLastSec():
            return 0
        for sillId, skill in self.allSkill.iteritems():
            ret = self.useSkill(skill, objTarget, None)
            owner = self.ownerref()
            owner.direction = Base.getDirection(owner.x, owner.y, objTarget.x, objTarget.y)
            retMsg = MsgDef.UseSkillRet(owner.uid, sillId, objTarget.uid, 0, owner.hp, owner.mp)
            owner.broadcast(MsgDef.ServerCmd.USE_SKILL, retMsg)
            if 1 == ret: #skill.useSkill(tmMs):#使用成功
                self.skillUsing = skill
                return 1
            elif self.ownerref and self.ownerref() and self.ownerref().getType() == Base.PLAYER:
                self.skillUsing = skill
                return 1
        return 0
    #角色学习技能
    def learnSkill(self, skillTypeSrc, skillLevel, msgFlag = False):
        skillType = skillId2Type(skillTypeSrc)
        if skillType != skillTypeSrc:
            skillLevel= skillId2Level(skillTypeSrc)
        player = self.ownerref()
        playerLevel = player.level
        skillCfg    = getSkillMgr().getCfgByTypeLevel(skillType, skillLevel)
        if not skillCfg:
            ffext.dump( 'not exist this skill type', skillType, skillLevel)
            return '不存在此技能'
        skill = self.getSkillByType(skillType)
        if skill == None:
            pass
            #if skillLevel != 1:
            #    return '需要先学习1级'
        elif skill.skillLevel >= skillLevel:
            ffext.dump( 'has learned higer skill', skillType)
            return '已经学习了更高级别的技能'
        skill = Skill()
        skill.skillType  = skillType
        skill.skillLevel = skillLevel
        skill.exp        = 0
        skill.ownerref      = self.ownerref
        skill.skillCfg   = skillCfg
        self.allSkill[skillType] = skill
        ffext.dump( 'learn ok', skillType, skillLevel)
        if msgFlag:
            player.sendMsg(MsgDef.ServerCmd.LEARN_SKILL, MsgDef.LearnSkillRet(skillType, skillLevel))
        return None

    #删除技能
    def deleteSkill(self, skillTypeSrc, msgFlag = False):
        skillType = skillId2Type(skillTypeSrc)
        self.allSkill.pop(skillType, None)
        return None



    def onLevelUp(self, level):
        player = self.ownerref()
        skillCfgAll = getSkillMgr().getAllCanLearn(level, player.job)
        for skillType, skillLevel in skillCfgAll.iteritems():
            ffext.dump("Skilllllllllllllll", skillType)
            if skillType == Base.MAKE_ITEM_ID and player.level >= 10:
                self.learnSkill(Base.MAKE_ITEM_ID, 1,True )
                ffext.dump('MAKESKILLLLLLL', 1)
            if skillType == Base.BRO_SKILL_ID:
                pass
            if self.getSkillByType(skillType) == None:
                self.learnSkill(skillType, 1, True)#只学习1级的

    #怪物学习技能
    def learnMonsterSkill(self, skillType):
        skillCfg    = getSkillMgr().getMonsterSkillCfg(skillType)
        if not skillCfg:
            ffext.dump( 'not exist this monster skill type', skillType)
            return '不存在此技能'
        skill = Skill()
        skill.skillType  = skillType
        skill.skillLevel = 0
        skill.ownerref      = self.ownerref
        skill.skillCfg   = skillCfg
        self.allSkill[skillType] = skill
        #ffext.dump( 'learn ok', skillType)
        return None
    #角色使用技能
    def useSkill(self, skill, objDest, param):
        hurtCalcultor = skill.skillCfg.hurtCalcultor
        ffext.dump('UUUUUUUUUUUUU*********************', skill.skillCfg.skillId, type(hurtCalcultor))
        if hurtCalcultor != None:
            #伤血计算
            return hurtCalcultor.exe(self.ownerref(), skill, objDest, param)
        return '该技能禁止使用'
def buildSkillCalcilator(typeSrc, param):
    return
class SkillMgr(Base.BaseObj):
    def __init__(self):
        self.allSkillCfg = {}#skillId -> dict level -> skillTCfg
        self.allMonsterSkillCfg = {}#skillId -> skillTCfg
    def data2cfg(self, row):
        skillCfg = SkillCfg()
        skillCfg.skillId     = int(row[0])
        skillCfg.name        = row[1].strip()
        skillCfg.intro       = row[2]
        skillCfg.mp          = int(row[3])
        skillCfg.cd          = int(float(row[4]) * 1000)
        skillCfg.attackSpeed         = int(row[5])
        skillCfg.attackSing         = int(row[6])
        skillCfg.attackInterval         = (float(row[7]) * 1000)
        skillCfg.attackDistance         = int(row[8])
        skillCfg.attackRange         = int(row[9])
        skillCfg.costAnger         = int(row[10])
        if len(row) >= 12:
            skillCfg.needlevel         = int(row[11])
            skillCfg.skillType = int(row[12])#skillId2Level(skillCfg.skillId)
            skillCfg.skillLevel  = int(row[13])#skillId2Type(skillCfg.skillId)
            #ffext.dump('skilltype skilllevel', skillCfg.skillType, skillCfg.skillLevel)
        else:
            skillCfg.skillLevel = 0
            skillCfg.skillType  = skillCfg.skillId
        return skillCfg
    def init(self):#读取任务配置
        db = ffext.allocDbConnection('cfg',ffext.getConfig('-cfg'))

        #id	name	des	mofa	lengque	speed	yinchang	jiange	juli	zuoyong	nuqi	icon
        ret = db.queryResult('select id,name,des,mofa,lengque,speed,yinchang,jiange,juli,zuoyong,nuqi,needlevel,skilltype,skilllevel from skill')
        self.allSkillCfg = {}
        from handler import MarryHandler
        for row in ret.result:
            skillCfg = self.data2cfg(row)
            cfgDict = self.allSkillCfg.get(skillCfg.skillType)
            #ffext.dump('load skill cfg', skillCfg.skillType, skillCfg.skillLevel)
            #读取战士相关的技能配置
            if skillCfg.skillId == 110:
                param = int(Base.parseStrBetween(skillCfg.intro, '攻击', '%'))
                #ffext.dump('skill param', skillCfg.skillId, param)
                skillCfg.hurtCalcultor = SkillCalculatorZhanShi.PuGong(param)

            elif skillCfg.skillId>= 120 and skillCfg.skillId <= 129:
                param = int(Base.parseStrBetween(skillCfg.intro, '攻击', '%'))
                #ffext.dump('skill param', skillCfg.skillId, param)
                skillCfg.hurtCalcultor = SkillCalculatorZhanShi.ChuanQiangCiShu(param)
            elif skillCfg.skillId >= 130 and skillCfg.skillId <= 139:
                param = int(Base.parseStrBetween(skillCfg.intro, '目标造成', '%'))
                param2 = int(Base.parseStrBetween(skillCfg.intro, '溅射造成', '%'))
                #ffext.dump('skill param', skillCfg.skillId, param, param2)
                skillCfg.hurtCalcultor = SkillCalculatorZhanShi.HengSaoQianJun(param, param2)
            elif skillCfg.skillId >= 140 and skillCfg.skillId <= 149:
                param = int(Base.parseStrBetween(skillCfg.intro, '造成', '%'))
                param2 = float(Base.parseStrBetween(skillCfg.intro, '眩晕', '秒'))
                #ffext.dump('skill param', skillCfg.skillId, param, param2)
                skillCfg.hurtCalcultor = SkillCalculatorZhanShi.ChongFengXianZhen(param, 2, param2)
            elif skillCfg.skillId >= 150 and skillCfg.skillId <= 159:#151	暴怒一击-2	对目标造成200%物理伤害
                param = int(Base.parseStrBetween(skillCfg.intro, '造成', '%'))
                #ffext.dump('skill param', skillCfg.skillId, param)
                skillCfg.hurtCalcultor = SkillCalculatorZhanShi.PuGong(param)
            elif skillCfg.skillId >= 160 and skillCfg.skillId <= 169:#TODO
                strArg = Base.parseStrBetween(skillCfg.intro, '造成', '%的物理伤害')
                args   = strArg.split('%，')
                ##ffext.dump('skill param', skillCfg.skillId, strArg, args)
                intArgs = []
                for k in args:
                    intArgs.append(int(k))
                #ffext.dump('skill param', skillCfg.skillId, intArgs)
                skillCfg.hurtCalcultor = SkillCalculatorZhanShi.YinLongHuXiao(intArgs[0], intArgs[1], intArgs[2])
            elif skillCfg.skillId == Base.WUSHUANG_SKILL_ID:#    1001 战士无双 - 无人能挡 对自身周围敌人造成物理攻击250 % 的物理伤害，同时敌人眩晕1秒
                param = int(Base.parseStrBetween(skillCfg.intro, '物理攻击', '%'))
                param2 = float(Base.parseStrBetween(skillCfg.intro, '眩晕', '秒'))
                #ffext.dump('skill param', skillCfg.skillId, param, param2)
                skillCfg.hurtCalcultor = SkillCalculatorZhanShi.WuShuangWuRenNengDang(param, param2)
            elif skillCfg.skillId == 210:#210	普通攻击	对目标造成魔法攻击105%的魔法伤害
                param = int(Base.parseStrBetween(skillCfg.intro, '魔法攻击', '%'))
                #ffext.dump('skill param', skillCfg.skillId, param)
                skillCfg.hurtCalcultor = SkillCalculatorFaShi.PuGong(param)
            elif skillCfg.skillId >= 220 and skillCfg.skillId <= 229:#220	引动天雷-1	对目标敌人造成125%的魔法伤害，有30%几率对目标周围造成15%魔法伤害
                param = int(Base.parseStrBetween(skillCfg.intro, '敌人造成', '%'))
                param2 = int(Base.parseStrBetween(skillCfg.intro, '，有', '%'))
                param3 = int(Base.parseStrBetween(skillCfg.intro, '周围造成', '%'))
                #ffext.dump('skill param', skillCfg.skillId, param, param2, param3)
                skillCfg.hurtCalcultor = SkillCalculatorFaShi.YinDongTianLei(param, param2, param3)
            elif skillCfg.skillId >= 230 and skillCfg.skillId <= 239:  # 230	冰封之术-1	对目标造成魔法攻击100%的魔法伤害，同时5秒内减速目标15%移动速度
                param = int(Base.parseStrBetween(skillCfg.intro, '魔法攻击', '%'))
                param2 = int(Base.parseStrBetween(skillCfg.intro, '减速目标', '%'))
                #ffext.dump('skill param', skillCfg.skillId, param, param2)
                skillCfg.hurtCalcultor = SkillCalculatorFaShi.BingFengZhiShu(param, param2)
            elif skillCfg.skillId >= 240 and skillCfg.skillId <= 249:  # 240	神明护体-1	魔法的能量环绕身体，120秒内降低对法师的造成伤害25%
                param = int(Base.parseStrBetween(skillCfg.intro, '身体，', '秒'))
                param2 = int(Base.parseStrBetween(skillCfg.intro, '伤害', '%'))
                #ffext.dump('skill param', skillCfg.skillId, param, param2)
                skillCfg.hurtCalcultor = SkillCalculatorFaShi.ShenMingFuTi(param, param2)
            #250	陨石暴落-1	一颗陨石从天而降，对单个目标造成250%的魔法伤害，5秒内造成2次附带灼烧25%魔法伤害
            elif skillCfg.skillId >= 250 and skillCfg.skillId <= 259:
                param = int(Base.parseStrBetween(skillCfg.intro, '目标造成', '%'))
                param2 = int(Base.parseStrBetween(skillCfg.intro, '伤害，', '秒'))
                param3 = int(Base.parseStrBetween(skillCfg.intro, '内造成', '次附带'))
                param4 = int(Base.parseStrBetween(skillCfg.intro, '灼烧', '%魔法伤害'))
                #ffext.dump('skill param', skillCfg.skillId, param, param2)
                skillCfg.hurtCalcultor = SkillCalculatorFaShi.YunShiBaoLuo(param, param2, param3, param4)
            elif skillCfg.skillId >= 260 and skillCfg.skillId <= 269:  # 260	天火燎原-1	对目标造成120%的魔法伤害，同时对目标周围范围的目标造成35%溅射伤害。
                param = int(Base.parseStrBetween(skillCfg.intro, '对目标造成', '%'))
                param2 = int(Base.parseStrBetween(skillCfg.intro, '的目标造成', '%'))
                #ffext.dump('skill param', skillCfg.skillId, param, param2)
                skillCfg.hurtCalcultor = SkillCalculatorFaShi.TianHuoLiaoYuan(param, param2)
            elif skillCfg.skillId == Base.FA_WUSHUANG_SKILL_ID:  # 1002 法师 无双
                param = int(Base.parseStrBetween(skillCfg.intro, '魔法攻击', '%'))
                # ffext.dump('skill param', skillCfg.skillId, param, param2)
                skillCfg.hurtCalcultor = SkillCalculatorFaShi.FaShiWuShuang_LongXiaoJiuTian(param)
            # 术士-技能读取 --------
            elif skillCfg.skillId == 310:
                param = int(Base.parseStrBetween(skillCfg.intro, '攻击', '%'))
                #ffext.dump('skill param', skillCfg.skillId, param)
                skillCfg.hurtCalcultor = SkillCalculatorShuShi.PuGong(param)
            elif skillCfg.skillId >= 320 and skillCfg.skillId <= 329:
                param = int(Base.parseStrBetween(skillCfg.intro, '目标', '秒内'))
                param2 = int(Base.parseStrBetween(skillCfg.intro, '内每', '秒回'))
                param3 = int(Base.parseStrBetween(skillCfg.intro, '回复', '点'))
                #ffext.dump('skill param', skillCfg.skillId, param, param2, param3)
                skillCfg.hurtCalcultor = SkillCalculatorShuShi.ZhiYuShu(param3)
            elif skillCfg.skillId >= 330 and skillCfg.skillId <= 339:
                param = int(Base.parseStrBetween(skillCfg.intro, '召唤', '个'))
                param2 = int(Base.parseStrBetween(skillCfg.intro, '自身属性', '%'))
                #ffext.dump('skill param', skillCfg.skillId, param, param2)
                skillCfg.hurtCalcultor = SkillCalculatorShuShi.ZhaoHuanYinXiang(param, param2)
            elif skillCfg.skillId >= 340 and skillCfg.skillId <= 349:
                param = int(Base.parseStrBetween(skillCfg.intro, '中毒，', '秒内'))
                param2 = int(Base.parseStrBetween(skillCfg.intro, '每', '秒受'))
                param3 = int(Base.parseStrBetween(skillCfg.intro, '受到', '%'))
                #ffext.dump('skill param', skillCfg.skillId, param, param2)
                skillCfg.hurtCalcultor = SkillCalculatorShuShi.ShiDuShu(param, param2, param3)
            elif skillCfg.skillId >= 350 and skillCfg.skillId <= 359:
                param = int(Base.parseStrBetween(skillCfg.intro, '目标', '%'))
                #ffext.dump('skill param', skillCfg.skillId, param)
                skillCfg.hurtCalcultor = SkillCalculatorShuShi.GuWuShiQi(60, param)
            elif skillCfg.skillId >= 360 and skillCfg.skillId <= 369:
                param = int(Base.parseStrBetween(skillCfg.intro, '最大生命值', '%'))
                #ffext.dump('skill param', skillCfg.skillId, param)
                skillCfg.hurtCalcultor = SkillCalculatorShuShi.FuHuoZhiShu(param)
            # 术士-技能读取 --------
            #游侠/弓箭手-技能读取 --------
            elif skillCfg.skillId == 410:
                param = int(Base.parseStrBetween(skillCfg.intro, '攻击', '%'))
                #ffext.dump('skill param', skillCfg.skillId, param)
                skillCfg.hurtCalcultor = SkillCalculatorYouXia.PuGong(param)
            elif skillCfg.skillId >= 420 and skillCfg.skillId <= 429:
                param = int(Base.parseStrBetween(skillCfg.intro, '造成', '%的物理'))
                param2 = int(Base.parseStrBetween(skillCfg.intro, '四个目标造成', '%溅射'))
                #ffext.dump('skill param', skillCfg.skillId, param, param2)
                skillCfg.hurtCalcultor = SkillCalculatorYouXia.WuJianLianShe(param, 4, param2)
            elif skillCfg.skillId >= 430 and skillCfg.skillId <= 439:
                param = int(Base.parseStrBetween(skillCfg.intro, '攻击', '%'))
                param2 = float(Base.parseStrBetween(skillCfg.intro, '同时', '秒内'))
                param3 = int(Base.parseStrBetween(skillCfg.intro, '减速目标', '%'))
                #ffext.dump('skill param XuRuoZhiJian', skillCfg.skillId, param, param2, param3)
                skillCfg.hurtCalcultor = SkillCalculatorYouXia.XuRuoZhiJian(param, param2, param3)
            elif skillCfg.skillId >= 440 and skillCfg.skillId <= 449:
                param = int(Base.parseStrBetween(skillCfg.intro, '攻击', '%'))
                #ffext.dump('skill param', skillCfg.skillId, param)
                skillCfg.hurtCalcultor = SkillCalculatorYouXia.PoJiaZhiJian(param)
            elif skillCfg.skillId >= 450 and skillCfg.skillId <= 459:
                param = int(Base.parseStrBetween(skillCfg.intro, '2次', '%'))
                #ffext.dump('skill param', skillCfg.skillId, param)
                skillCfg.hurtCalcultor = SkillCalculatorYouXia.SanLianJiShe(3, param)
            elif skillCfg.skillId >= 460 and skillCfg.skillId <= 469:
                #ffext.dump('skill param', skillCfg.skillId)
                skillCfg.hurtCalcultor = SkillCalculatorYouXia.JiSuHouChe()
            # 游侠/弓箭手-技能读取 --------
            # elif int(skillCfg.skillId / 100) == 2:
            #     param = 125
            #     skillCfg.hurtCalcultor = SkillCalculatorFaShi.PuGong(param)
            # elif int(skillCfg.skillId / 100) == 3:
            #     param = 110
            #     skillCfg.hurtCalcultor = SkillCalculatorShuShi.PuGong(param)
            # elif int(skillCfg.skillId / 100) == 4:
            #     param = 110
            #     skillCfg.hurtCalcultor = SkillCalculatorShuShi.PuGong(param)
            elif skillCfg.skillId == Base.BRO_SKILL_ID:#结义技能
                #2001	结义技能	当结义队友在场时，释放技能后，60秒内结义队友全部增加10%物理和魔法攻击力
                param1 = 60
                param2 = 0.1
                skillCfg.hurtCalcultor = SkillCalculatorZhanShi.JieYi(param1, param2)
            elif skillCfg.skillId == MarryHandler.WEDDING_SKILL_ID:
                param1 = 60
                param2 = 10
                skillCfg.hurtCalcultor = SkillCalculatorZhanShi.Wedding(param1, param2)
            else:
                param = 110
                skillCfg.hurtCalcultor = SkillCalculatorZhanShi.PuGong(param)
            if not cfgDict:
                self.allSkillCfg[skillCfg.skillType] = {skillCfg.skillLevel: skillCfg}
            else:
                self.allSkillCfg[skillCfg.skillType][skillCfg.skillLevel] = skillCfg
            #ffext.dump('load skill type=%d,level=%d, %s'%(skillCfg.skillType, skillCfg.skillLevel, type(skillCfg.skillLevel)))
            #sql = 'update skill set skilltype=%d,skilllevel=%d where skillid=%d'%(skillCfg.skillType, skillCfg.skillLevel, int(row[0]))
            #ffext.dump('sql', sql)
            #ret = db.queryResult(sql)
        ffext.dump('load skill num=%d'%(len(self.allSkillCfg)))
        #print(self.allSkillCfg[120][2])
        return True
    def getAllCanLearn(self, levelPlayer, job):
        ret = {}
        for skillType, dest in self.allSkillCfg.iteritems():
            #ffext.dump("SKILLLLLLTYPE", skillType)
            for level, cfg in dest.iteritems():
                if cfg.getJob() != job and skillType != Base.MAKE_ITEM_ID:
                    continue
                if cfg.needlevel <= levelPlayer:
                    if level >= ret.get(skillType, -1):
                        ret[skillType] = level
        return ret

    def initMonster(self):#读取任务配置
        db = ffext.allocDbConnection('cfg',ffext.getConfig('-cfg'))
        ret = db.queryResult('select skillid,name,intro,mp,cd,attackspeed,attacksing,attackinterval,attackdistance,attackrange,costanger from monsterskill')
        self.allMonsterSkillCfg = {}
        for row in ret.result:
            skillCfg = self.data2cfg(row)
            cfgDict = self.allMonsterSkillCfg.get(skillCfg.skillType)
            #ffext.dump('load monsterskill cfg', skillCfg)
            if skillCfg.skillId == 4151:
                skillCfg.hurtCalcultor = SkillCalculatorZhanShi.PuGong()
            self.allMonsterSkillCfg[skillCfg.skillType] = skillCfg

        ffext.dump('load monsterskill num=%d'%(len(self.allMonsterSkillCfg)))
        return True

    def getCfgByTypeLevel(self, skillType, level):
        cfgDict = self.allSkillCfg.get(skillType)
        if cfgDict:
            return cfgDict.get(level)
        return None
    def getDefaultSkillList(self, job):
        skillType = skillId2Type((job)*100+10)
        ffext.dump('get default skill type', skillType)
        ret = [self.getCfgByTypeLevel(skillType, 1)]#默认给一个1级的技能
        skillType2= skillType + 10
        cfg2 = self.getCfgByTypeLevel(skillType2, 0)
        if None != cfg2:
            ret.append(cfg2)
        return ret
    #获取怪物的技能配置
    def getMonsterSkillCfg(self, skillType):

        return self.allMonsterSkillCfg.get(skillType)
gSkillMgr = SkillMgr()
def getSkillMgr():
    return gSkillMgr