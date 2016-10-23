# -*- coding: utf-8 -*-
from msgtype import ttypes as MsgDef
import  weakref
import ffext
import idtool
from db import DbService
from db import DbServiceLog
from base import Base
import ffext

class LoginOpType:
    LOGIN_ACCOUNT   = 1         # 登录账号
    LOGIN_PLAYER    = 2         # 登录角色
    LOGOUT          = 3         # 登出
    CREATE_PLAYER   = 4         # 创角
    DEL_PLAYER      = 5         # 删角

class LoginReason:
    NEW_LOGIN = 1   # 新玩家
    OLD_LOGIN = 2   # 老玩家
    LOGOUT = 3,     # 正常退出
    KICKOUT = 4,    # 被动退出

def logLoginData(acc_id, player_id, player_name, op, reason, ip = 0, x = 0, y = 0, param = ''):
    svr_id = 0 #get_server_id()
    param = DbServiceLog.UserLogParam(svr_id, acc_id, player_id, player_name, op, reason, ip, x, y, param)
    DbService.getLogService().addUserLog(param)
    return True




