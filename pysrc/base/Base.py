# -*- coding: utf-8 -*-
import random

G_FORMATE_DEEP = 0
def formatObj(obj):
    if G_FORMATE_DEEP > 3:
        return obj.__class__.__name__
    return str(obj)

class BaseObj(object):
    def __repr__(self):
        global G_FORMATE_DEEP
        bToRelease = 0
        if G_FORMATE_DEEP == 0:
            bToRelease = 1
        G_FORMATE_DEEP += 1
        ret = ''
        try:
            L = ['%s=%r' % (key, formatObj(value))
              for key, value in self.__dict__.iteritems()]
            ret = '%s(%s)' % (self.__class__.__name__, ', '.join(L))
        except:
            pass
        if bToRelease:
            G_FORMATE_DEEP = 0
        return ret

class Pos(BaseObj):
    def __init__(self, x = 0, y = 0):
        self.x = x
        self.y = y

class Direction:
    UP         = 0
    UP_RIGHT   = 1
    RIGHT      = 2
    RIGHT_DOWN = 3
    DOWN       = 4
    DOWN_LEFT  = 5
    LEFT       = 6
    LEFT_UP    = 7
    NUM        = 8
    DIRECTION4 = [0, 2, 4, 6]
    UP_DIRECTION    = (7, 0, 1)
    RIGHT_DIRECTION = (1, 2, 3)
    DOWN_DIRECTION  = (3, 4, 5)
    LEFT_DIRECTION  = (5, 6, 7)

def randDirection4():
    return Direction.DIRECTION4[random.randint(0, len(Direction.DIRECTION4) -1)]
#寻路用，某个面对某个方向的5个朝向
# MOVE_HELP_DIRECTION = {
#     Direction.UP: (Direction.UP, Direction.UP_RIGHT, Direction.LEFT_UP, Direction.RIGHT, Direction.LEFT),
#     Direction.UP_RIGHT: (Direction.UP_RIGHT, Direction.RIGHT, Direction.UP, Direction.RIGHT_DOWN, Direction.LEFT_UP),
#     Direction.RIGHT: (Direction.RIGHT, Direction.RIGHT_DOWN, Direction.UP_RIGHT, Direction.DOWN, Direction.UP),
#     Direction.RIGHT_DOWN: (Direction.RIGHT_DOWN, Direction.DOWN, Direction.RIGHT, Direction.DOWN_LEFT, Direction.UP_RIGHT),
#     Direction.DOWN: (Direction.DOWN, Direction.DOWN_LEFT, Direction.RIGHT_DOWN, Direction.LEFT, Direction.RIGHT),
#     Direction.DOWN_LEFT: (Direction.DOWN_LEFT, Direction.LEFT, Direction.DOWN,Direction.LEFT_UP, Direction.RIGHT_DOWN),
#     Direction.LEFT: (Direction.LEFT, Direction.LEFT_UP, Direction.DOWN_LEFT, Direction.UP, Direction.DOWN),
#     Direction.LEFT_UP: (Direction.LEFT_UP,Direction.UP, Direction.LEFT, Direction.UP_RIGHT, Direction.DOWN_LEFT),
# }
MOVE_HELP_DIRECTION = {
    Direction.UP: (Direction.UP, Direction.UP_RIGHT, Direction.LEFT_UP, Direction.RIGHT, Direction.LEFT),
    Direction.UP_RIGHT: (Direction.UP_RIGHT, Direction.RIGHT, Direction.UP, Direction.RIGHT_DOWN, Direction.LEFT_UP),
    Direction.RIGHT: (Direction.RIGHT, Direction.RIGHT_DOWN, Direction.UP_RIGHT, Direction.DOWN, Direction.UP),
    Direction.RIGHT_DOWN: (Direction.RIGHT_DOWN, Direction.DOWN, Direction.RIGHT, Direction.DOWN_LEFT, Direction.UP_RIGHT),
    Direction.DOWN: (Direction.DOWN, Direction.DOWN_LEFT, Direction.RIGHT_DOWN, Direction.LEFT, Direction.RIGHT),
    Direction.DOWN_LEFT: (Direction.DOWN_LEFT, Direction.LEFT, Direction.DOWN,Direction.LEFT_UP, Direction.RIGHT_DOWN),
    Direction.LEFT: (Direction.LEFT, Direction.LEFT_UP, Direction.DOWN_LEFT, Direction.UP, Direction.DOWN),
    Direction.LEFT_UP: (Direction.LEFT_UP,Direction.UP, Direction.LEFT, Direction.UP_RIGHT, Direction.DOWN_LEFT),
}
MOVE_HELP_DIRECTION2 = {
    Direction.UP: (Direction.UP,  Direction.RIGHT, Direction.LEFT),
    Direction.UP_RIGHT: (Direction.RIGHT, Direction.UP),
    Direction.RIGHT: (Direction.RIGHT, Direction.DOWN, Direction.UP),
    Direction.RIGHT_DOWN: (Direction.DOWN, Direction.RIGHT),
    Direction.DOWN: (Direction.DOWN, Direction.LEFT, Direction.RIGHT),
    Direction.DOWN_LEFT: (Direction.LEFT, Direction.DOWN),
    Direction.LEFT: (Direction.LEFT, Direction.UP, Direction.DOWN),
    Direction.LEFT_UP: (Direction.UP, Direction.LEFT),
}
#获取两点的朝向
#获取两点的朝向
def getDirection(srcX, srcY, destX, destY):
    if destX == srcX:
        if destY >= srcY:
            return Direction.DOWN
        else:
            return Direction.UP
    elif destX > srcX:
        xRange = destX - srcX
        if destY >= srcY:
            yRange = destY - srcY
            if xRange < (yRange / 2):
                return Direction.DOWN
            elif yRange <= (xRange / 2):
                return Direction.RIGHT
            else:
                return Direction.RIGHT_DOWN
        elif destY < srcY:
            yRange = srcY - destY
            if xRange < (yRange / 2):
                return Direction.UP
            elif yRange <= (xRange / 2):
                return Direction.RIGHT
            else:
                return Direction.UP_RIGHT
    elif destX < srcX:
        xRange = srcX - destX
        if destY < srcY:
            yRange = srcY - destY
            if xRange < (yRange / 2):
                return Direction.UP
            elif yRange <= (xRange / 2):
                return Direction.LEFT
            else:
                return Direction.LEFT_UP
        elif destY >= srcY:
            yRange = destY - srcY
            if xRange < (yRange / 2):
                return Direction.DOWN
            elif yRange <= (xRange / 2):
                return Direction.LEFT
            else:
                return Direction.DOWN_LEFT
def getDirectionOld(srcX, srcY, destX, destY):
    if destX == srcX:
        if destY >= srcY:
            return Direction.UP
        else:
            return Direction.DOWN
    elif destX > srcX:
        xRange = destX - srcX
        if destY >= srcY:
            yRange = destY - srcY
            if xRange < (yRange / 2):
                return Direction.UP
            elif yRange <= (xRange / 2):
                return Direction.RIGHT
            else:
                return Direction.UP_RIGHT
        elif destY < srcY:
            yRange = srcY - destY
            if xRange < (yRange / 2):
                return Direction.DOWN
            elif yRange <= (xRange / 2):
                return Direction.RIGHT
            else:
                return Direction.RIGHT_DOWN
    elif destX < srcX:
        xRange = srcX - destX
        if destY < srcY:
            yRange = srcY - destY
            if xRange < (yRange / 2):
                return Direction.DOWN
            elif yRange <= (xRange / 2):
                return Direction.LEFT
            else:
                return Direction.DOWN_LEFT
        elif destY >= srcY:
            yRange = destY - srcY
            if xRange < (yRange / 2):
                return Direction.UP
            elif yRange <= (xRange / 2):
                return Direction.LEFT
            else:
                return Direction.LEFT_UP

#获取反向方向
def getReverseDirection(direction):
    if direction == Direction.UP:
        return Direction.DOWN
    elif direction == Direction.DOWN:
        return Direction.UP
    elif direction == Direction.RIGHT:
        return Direction.LEFT
    elif direction == Direction.LEFT:
        return Direction.RIGHT
    elif direction == Direction.UP_RIGHT:
        return Direction.DOWN_LEFT
    elif direction == Direction.DOWN_LEFT:
        return Direction.UP_RIGHT
    elif direction == Direction.RIGHT_DOWN:
        return Direction.LEFT_UP
    elif direction == Direction.LEFT_UP:
        return Direction.RIGHT_DOWN
    return -1

def distance(x, y, x2, y2):
    return max(abs(x - x2), abs(y - y2))
def getPosByDirectionOld(x, y, direction, len = 1):
    if direction == Direction.UP:
        return x, y + len
    elif direction == Direction.UP_RIGHT:
        return x + len, y + len
    elif direction == Direction.RIGHT:
        return x + len, y
    elif direction == Direction.RIGHT_DOWN:
        return x + len, y - len
    elif direction == Direction.DOWN:
        return x, y - len
    elif direction == Direction.DOWN_LEFT:
        return x - len, y - len
    elif direction == Direction.LEFT:
        return x - len, y
    elif direction == Direction.LEFT_UP:
        return x - len, y + len
    else:
        return x, y
def getPosByDirection(x, y, direction, len = 1):
    if direction == Direction.UP:
        return x, y - len
    elif direction == Direction.UP_RIGHT:
        return x + len, y - len
    elif direction == Direction.RIGHT:
        return x + len, y
    elif direction == Direction.RIGHT_DOWN:
        return x + len, y + len
    elif direction == Direction.DOWN:
        return x, y + len
    elif direction == Direction.DOWN_LEFT:
        return x - len, y + len
    elif direction == Direction.LEFT:
        return x - len, y
    elif direction == Direction.LEFT_UP:
        return x - len, y - len
    else:
        return x, y
#对象类型
PLAYER = 0
MONSTER= 1
ITEM   = 2
NPC    = 3

PLAYER_RECOVER_HPMP_MS = 5000    #角色滴答定时恢复血量
MONSTER_TIMER_MS       = 500     #怪物AI 定时器的滴答毫秒数
COPY_MAP_TIMER_MS      = 1000    #副本定时器
REPO_POS_START         = 1000    #仓库包裹位置索引起始值
AUCTION_TIMER_MS       = 30000  #寄售、拍卖行物品刷新时间

#装备配置类型
EQUIP_WUQI_TYPE      = 101
EQUIP_TOUKUI_TYPE    = 102
EQUIP_XIONGJIA_TYPE  = 103
EQUIP_HUJIAN_TYPE    = 104
EQUIP_HUSHOU_TYPE    = 105
EQUIP_XIANGLIAN_TYPE = 106
EQUIP_JIEZHI_TYPE    = 107
EQUIP_ZHANXUE_TYPE   = 108
#装备相关
EQUIP_WUQI_POS      = 1
EQUIP_TOUKUI_POS    = 2
EQUIP_XIONGJIA_POS  = 3
EQUIP_HUJIAN_POS    = 4
EQUIP_HUSHOU_POS    = 5
EQUIP_XIANGLIAN_POS = 6
EQUIP_JIEZHI_POS    = 7
EQUIP_ZHANXUE_POS   = 8
#准备类型 to 装备位置
EQUIP_TYPE_TO_POS = {
    EQUIP_WUQI_TYPE      : EQUIP_WUQI_POS,
    EQUIP_TOUKUI_TYPE    : EQUIP_TOUKUI_POS,
    EQUIP_XIONGJIA_TYPE  : EQUIP_XIONGJIA_POS,
    EQUIP_HUJIAN_TYPE    : EQUIP_HUJIAN_POS,
    EQUIP_HUSHOU_TYPE    : EQUIP_HUSHOU_POS,
    EQUIP_XIANGLIAN_TYPE : EQUIP_XIANGLIAN_POS,
    EQUIP_JIEZHI_TYPE    : EQUIP_JIEZHI_POS,
    EQUIP_ZHANXUE_TYPE   : EQUIP_ZHANXUE_POS,
}
EQUIP_POS_TO_TYPE = {
    EQUIP_WUQI_POS      : EQUIP_WUQI_TYPE,
    EQUIP_TOUKUI_POS    : EQUIP_TOUKUI_TYPE,
    EQUIP_XIONGJIA_POS  : EQUIP_XIONGJIA_TYPE,
    EQUIP_HUJIAN_POS    : EQUIP_HUJIAN_TYPE,
    EQUIP_HUSHOU_POS    : EQUIP_HUSHOU_TYPE,
    EQUIP_XIANGLIAN_POS : EQUIP_XIANGLIAN_TYPE,
    EQUIP_JIEZHI_POS    : EQUIP_JIEZHI_TYPE,
    EQUIP_ZHANXUE_POS   : EQUIP_ZHANXUE_TYPE,
}


def str2Int(s, d = 0):
    if s != '' and s != None:
        return  int(s)
    return d



class Action:#任务类型为对话、打怪、探索、采集四类
    NONE_ACTION  = 0
    CHAT_NPC     = 1
    KILL_MONSTER = 2
    EXPLORE      = 3
    COLLECT      = 4
    COPY_MAP     = 5

    ACTION_CFG = {#任务类型为对话、打怪、探索、采集四类
        'NONE' : 0,
        '对话' : 1,
        '杀怪' : 2,
        '打怪' : 2,
        '探索' : 3,
        '采集' : 4,
        '副本' : 5,
    }
def str2Action(s):
    return Action.ACTION_CFG.get(s, 0)
def lang(str):
    return str
class PropType:
    HP                = 1
    MP                = 2
    HP_MAX            = 3
    MP_MAX            = 4
    PHYSIC_ATTACK_MIN = 5
    PHYSIC_ATTACK_MAX = 6
    MAGIC_ATTACK_MIN  = 7
    MAGIC_ATTACK_MAX  = 8
    PHYSIC_DEFEND_MIN = 9
    PHYSIC_DEFEND_MAX = 10
    MAGIC_DEFEND_MIN  = 11
    MAGIC_DEFEND_MAX  = 12
    #暴击
    CRIT              = 13#暴击 影响暴击的概率	浮点数
    HIT               = 14#命中 影响攻击时的命中率	浮点数
    AVOID             = 15#躲避 被攻击时，影响降低被命中的概率	浮点数
    ATTACK_SPEED      = 16#攻击速度
    ATTACK_SING       = 17#攻击吟唱时间 影响释放攻击动作前的吟唱时间 吟唱时间内被攻击，有50%概率被打断，打断后需要重新吟唱，单位：秒  精确到毫秒
    ATTACK_INTERVAL   = 18#两次攻击之间间隔时间，单位：秒  精确到毫秒
    ATTACK_DISTANCE   = 19#攻击距离	以单位为中心的圆内可以攻击，近战标准值：100，远程值：600
    MOVE_SPEED        = 20#移动速度 影响地图上移动速度，标准值：100 精确到毫秒
    HURT_ABSORB       = 21#伤害吸收 受到伤害时，一定比例转换为生命值 百分比
    HP_ABSORB         = 22#吸血 当对敌人造成伤害时，吸取血量恢复自身生命值 百分比
class PropModule:
    LEVEL = 1
    PET   = 2
    #装备配置类型
    EQUIP_WUQI_TYPE      = 101
    EQUIP_TOUKUI_TYPE    = 102
    EQUIP_XIONGJIA_TYPE  = 103
    EQUIP_HUJIAN_TYPE    = 104
    EQUIP_HUSHOU_TYPE    = 105
    EQUIP_XIANGLIAN_TYPE = 106
    EQUIP_JIEZHI_TYPE    = 107
    EQUIP_ZHANXUE_TYPE   = 108
#角色属性的一些枚举定义
PROP_STR2TYPE ={
     'hpMax'             : PropType.HP_MAX,
     'physicAttackMin' : PropType.PHYSIC_ATTACK_MIN,
     'physicAttackMax' : PropType.PHYSIC_ATTACK_MAX,
     'magicAttackMin'  : PropType.MAGIC_ATTACK_MIN,
     'magicAttackMax'  : PropType.MAGIC_ATTACK_MAX,
     'physicDefendMin' : PropType.PHYSIC_DEFEND_MIN,
     'physicDefendMax' : PropType.PHYSIC_DEFEND_MAX,
     'magicDefendMin'  : PropType.MAGIC_DEFEND_MIN,
     'magicDefendMax'  : PropType.MAGIC_DEFEND_MAX,
}
PROP_TYPE2STR = {}
for k, v in PROP_STR2TYPE.iteritems():
    PROP_TYPE2STR[v] = k
PROP_TYPE2STR ={}
for k, v in PROP_STR2TYPE.iteritems():
    PROP_TYPE2STR[v] =k

class Job:
    ZHANSHI = 1
    FASHI   = 2
    SHUSHI  = 3
    YOUXIA  = 4
ALL_JOB = [Job.ZHANSHI, Job.FASHI, Job.SHUSHI, Job.YOUXIA]
class Gender:
    MALE   = 1
    FEMAIL = 2
#暴击率的比率，千分比还是百分比
CRIT_RATE_BASE = 1000
HIT_RATE_BASE  = 1000
AVOID_RATE_BASE= 1000
#最大叠加次数
MAX_DIEJIA_NUM = 99

#地图上分成九宫格
MAP_BLOCK_SIZE = 20
ZHUJI_LEN = 40
##血回复10% 死亡后2s后
REBORN_TIMEOUT = 2000
#最大怒气值
MAX_ANGER = 100
#每次使用技能增加怒气值
ANGER_USE_SKILL = 0.5
#切磋最大距离
QIECUO_MAX_RANGE = 43
#结义技能id
BRO_SKILL_ID = 2001
WUSHUANG_SKILL_ID = 1001
FA_WUSHUANG_SKILL_ID = 1002
#锻造技能id
MAKE_ITEM_ID = 4001
#默认背包大小
DEFAULT_PKG_SIZE = 16
MAX_PKG_SIZE = 125
#默认仓库大小
DEFAULT_REPO_SIZE = 20
MAX_REPO_SIZE = 124
#每个格子收费
OPEN_PKG_SLOT_PRICE = 1000

def parseStrBetween(s, a, b):
    args = s.split(a)
    if len(args) >= 2:
        return  args[1].split(b)[0]
    return ''

class HurtCalculator(BaseObj):
    def __init__(self, a = 100):
        self.paramHurt = a

class BossType:
    MON_NORMAL   = 0
    MON_JINGYING = 1
    MON_BOSS     = 2
