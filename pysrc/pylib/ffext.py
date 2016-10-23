# -*- coding: utf-8 -*-
import json
import sys
import datetime
import time
try:
    import ff
    ffsceneObj = ff.ffscene
except:
    class ff:
        pass
import thrift.Thrift                    as Thrift
import thrift.protocol.TBinaryProtocol  as TBinaryProtocol
import thrift.protocol.TCompactProtocol as TCompactProtocol
import thrift.protocol.TJSONProtocol    as TJSONProtocol
import thrift.transport.TTransport      as TTransport

WiNOS = False
try:
    import platform
    print('*'*20, platform.system())
    if platform.system() == 'Windows':
        WiNOS = True
        print('this is windows ', WiNOS)
except:
    pass

gReadTMemoryBuffer    = TTransport.TMemoryBuffer()
#_ReadTBinaryProtocol = TBinaryProtocol.TBinaryProtocol(g_ReadTMemoryBuffer)
gWriteTMemoryBuffer   = TTransport.TMemoryBuffer()
gWriteTBinaryProtocol = TBinaryProtocol.TBinaryProtocol(gWriteTMemoryBuffer)


class Foo:
    pass
def convertMsgTest(msg):
    foo = Foo()
    for k, v in msg.iteritems():
        setattr(foo, k, v)
    return foo

def isJsonStr(val_):
    if len(val_) == 0:
        return False
    return val_[0] == '[' or val_[0] == '{'
def isThrift(obj_):
    return hasattr(obj_, 'thrift_spec')

def tocppBingCmd2MsgName(cmd, msg_name):
    return ffsceneObj.set_py_cmd2msg(cmd, msg_name)

def thriftDecodeMsg(destMsg, msgData):
    global gReadTMemoryBuffer
    if isJsonStr(msgData):
        gReadTMemoryBuffer.cstringio_buf.truncate()
        gReadTMemoryBuffer.cstringio_buf.seek(0)
        gReadTMemoryBuffer.cstringio_buf.write(msgData)
        gReadTMemoryBuffer.cstringio_buf.seek(0)
        proto = TJSONProtocol.TJSONProtocol(gReadTMemoryBuffer)
        proto.readMessageBegin()
        destMsg.read(proto)
        proto.readMessageEnd()
    else:
        gReadTMemoryBuffer.cstringio_buf.truncate()
        gReadTMemoryBuffer.cstringio_buf.seek(0)
        gReadTMemoryBuffer.cstringio_buf.write(msgData)
        gReadTMemoryBuffer.cstringio_buf.seek(0)
        proto = TBinaryProtocol.TBinaryProtocol(gReadTMemoryBuffer)
        proto.readMessageBegin()
        destMsg.read(proto)
        proto.readMessageEnd()
    return True
def protobufDecodeMsg(destMsg, msgData):
    return destMsg.ParseFromString(msgData)


def npc(func):
    def genNewLoginFunc(func_):
        global funcLoginRegister
        print('genNewLoginFunc', msgType)
        if msgType == 'json':
            def warpFunc(cmd, msgData, socketId, ip, gateName):
                msg     = json.loads(msgData)
                session = Session(socketId, ip, '', gateName, True)
                getSessionMgr().addSocket(socketId, session)
                #msg = convertMsgTest(msg)
                func_(session, msg)
                return 0
            funcLoginRegister = warpFunc
#@处理登录
funcLoginRegister = None
def onLogin(cmd_, msgType = 'json'):
    if msgType != 'json':
        tocppBingCmd2MsgName(cmd_, msgType.__name__)
    else:
        tocppBingCmd2MsgName(cmd_, 'CMD=%d'%(cmd_))

    def genNewLoginFunc(func_):
        global funcLoginRegister
        print('genNewLoginFunc', msgType)
        if msgType == 'json':
            def warpFunc(cmd, msgData, socketId, ip, gateName):
                msg     = json.loads(msgData)
                session = Session(socketId, ip, '', gateName, True)
                getSessionMgr().addSocket(socketId, session)
                #msg = convertMsgTest(msg)
                func_(session, msg)
                return 0
            funcLoginRegister = warpFunc
        elif isThrift(msgType):
            def warpFunc(cmd, msgData, socketId, ip, gateName):
                msg = msgType()
                flagDebug = False
                if msgData[0] == '{':
                    jsonData = json.loads(msgData)
                    if jsonData.get('_webdebug_') and jsonData['_webdebug_'] == True:
                        for k in jsonData:
                            setattr(msg, k, jsonData[k])
                        flagDebug = True
                if not flagDebug:
                    thriftDecodeMsg(msg, msgData)
                session = Session(socketId, ip, '', gateName)
                getSessionMgr().addSocket(socketId, session)
                if flagDebug:
                    session.isWebDebug = True
                    session.isJson     = True
                func_(session, msg)
                return 0
            funcLoginRegister = warpFunc
        else: #protobuf
            def warpFunc(cmd, msgData, socketId, ip, gateName):
                msg = msgType()
                protobufDecodeMsg(msg, msgData)
                session = Session(socketId, ip, '', gateName)
                getSessionMgr().addSocket(socketId, session)
                func_(session, msg)
                return 0
            funcLoginRegister = warpFunc
        return func_
    return genNewLoginFunc

def processLogin(cmd, msgData, socketId, ip, gateName):
    '''
    session_key 为client发过来的验证key，可能包括账号密码
    online_time 为上线时间
    gate_name 为从哪个gate登陆的
    '''
    if funcLoginRegister:
        return funcLoginRegister(cmd, msgData, socketId, ip, gateName)
    return -1

#@处理退出
funcLogoutRegister = None
def onLogout(func_):
    global funcLogoutRegister
    def warpFunc(socketId):
        session = getSessionMgr().getBySocketId(socketId)
        if 1 == getSessionMgr().delBySocketId(socketId):
            logLogout(session.getUid())
            try:
                func_(session)
            except:
                pass
            session.setPlayer(None)
    funcLogoutRegister = warpFunc
    return func_

def processLogout(socketId):
    '''
    session_key 为client发过来的验证key，可能包括账号密码
    online_time 为上线时间
    gate_name 为从哪个gate登陆的
    '''
    if funcLogoutRegister:
        return funcLogoutRegister(socketId)
    return -1

#@处理进入场景,玩家跳转场景时，调用此接口
funcEnterRegister = None
def onEnter(msgType = 'json'):
    def genNewEnterFunc(func_):
        global funcEnterRegister
        if msgType == 'json':
            def warpFunc(nameGroup, nameGate, socketId, nameSceneFrom, dataExtra):
                session = Session(socketId, '', nameGroup, nameGate, isJsonStr(dataExtra))
                getSessionMgr().addSocket(socketId, session)
                msgDest = json.loads(dataExtra)
                return func_(session, msgDest)
            funcEnterRegister = warpFunc
        elif isThrift(msgType):
            def warpFunc(nameGroup, nameGate, socketId, nameSceneFrom, dataExtra):
                session = Session(socketId, '', nameGroup, nameGate, isJsonStr(dataExtra))
                getSessionMgr().addSocket(socketId, session)
                msgDest = msgType()
                thriftDecodeMsg(msgDest, dataExtra)
                return func_(session, msgDest)
            funcEnterRegister = warpFunc
        else: #protobuf
            def warpFunc(nameGroup, nameGate, socketId, nameSceneFrom, dataExtra):
                session = Session(socketId, '', nameGroup, nameGate, isJsonStr(dataExtra))
                getSessionMgr().addSocket(socketId, session)
                msgDest = msgType()
                protobufDecodeMsg(msgDest, dataExtra)
                return func_(session, msgDest)
            funcEnterRegister = warpFunc
        return func_
    return genNewEnterFunc

def processEnter(nameGroup, nameGate, socketId, nameSceneFrom, dataExtra):
    '''
    session_id 为client id
    from_scene 为从哪个scene过来的，若为空，则表示第一次进入
    extra_data 从from_scene附带过来的数据
    '''
    print('processEnter', dataExtra)
    if funcEnterRegister != None:
       return funcEnterRegister(nameGroup, nameGate, socketId, nameSceneFrom, dataExtra)
    return -1


#@处理逻辑消息接口
funcLogicRegisterAll = {}
def onLogic(cmd_, msgType = 'json'):
    if msgType != 'json':
        tocppBingCmd2MsgName(cmd_, msgType.__name__)
    else:
        tocppBingCmd2MsgName(cmd_, 'CMD=%d'%(cmd_))

    def genNewLoginFunc(func_):
        global funcLogicRegister
        if msgType == 'json':
            def warpFunc(socketId, cmd, msgData):
                msg     = json.loads(msgData)
                session = getSessionMgr().getBySocketId(socketId)
                #msg = convertMsgTest(msg)
                func_(session, msg)
                return 0
            funcLogicRegisterAll[cmd_] = warpFunc
        elif isThrift(msgType):
            def warpFunc(socketId, cmd, msgData):
                msg = msgType()
                session = getSessionMgr().getBySocketId(socketId)
                if session.isWebDebug and (msgData[0] == '{' or msgData[0] == '['):
                    tmpData = json.loads(msgData)
                    for k, v in tmpData.iteritems():
                        setattr(msg, k, v)
                    session.sendMsg(0, '发送:'+str(msg))
                else:
                    thriftDecodeMsg(msg, msgData)
                func_(session, msg)
                return 0
            funcLogicRegisterAll[cmd_] = warpFunc
        else: #protobuf
            def warpFunc(socketId, cmd, msgData):
                msg = msgType()
                protobufDecodeMsg(msg, msgData)
                session = getSessionMgr().getBySocketId(socketId)
                func_(session, msg)
                return 0
            funcLogicRegisterAll[cmd_] = warpFunc
        return func_
    return genNewLoginFunc

def processLogic(socketId, cmd, msgData):
    #print('processLogic', socketId, cmd, len(msgData))
    info = funcLogicRegisterAll.get(cmd)
    if info:
        return info(socketId, cmd, msgData)
    else:
        print('processLogic cmd not found', socketId, cmd, msgData, funcLogicRegisterAll)
    return -1

#**********************************************分隔线*********************************
#$封装的定时器接口
GID = 0
def allocId():
    global GID
    GID += 1
    return GID

#记录需要回调的函数对象
gTimerFunRegister = {}

GID = 0
def timer(timeout_, func_):# 毫秒
    global gTimerFunRegister
    timerId = allocId()
    gTimerFunRegister[timerId] = func_
    ffsceneObj.once_timer(timeout_, timerId)

def processTimer(timerId):
    #print('processTimer', timerId)
    func = gTimerFunRegister.get(timerId)
    if func:
        del gTimerFunRegister[timerId]
        func()
    else:
        print('processTimer timerId not found', timerId)
    return 0

#$封装的消息编码
def encodeMsg(msg, isJson = False, isWebDebug = False):
    if isThrift(msg):
        if isWebDebug:
            tmp = {}
            for k, v in msg.__dict__.iteritems():
                if v.__class__ != str and v.__class__ != int and v.__class__ != float and v.__class__ != long:
                    if v.__class__ == dict:
                        tmp[k] = {}
                        for m, n in v.iteritems():
                            if isThrift(n):
                                tmpM = {}
                                for p, q in n.__dict__.iteritems():
                                    if q.__class__ != str and q.__class__ != int and q.__class__ != float and q.__class__ != long:
                                        tmpM[p] = str(q)
                                    else:
                                        tmpM[p] = q
                                tmp[k][m] = tmpM
                            else:
                                tmp[k][m] = n
                    elif v.__class__ == list:
                        tmp[k] = []
                        for n in v:
                            if isThrift(n):
                                tmpM = {}
                                for p, q in n.__dict__.iteritems():
                                    if q.__class__ != str and q.__class__ != int and q.__class__ != float and q.__class__ != long:
                                        tmpM[p] = str(q)
                                    else:
                                        tmpM[p] = q
                                tmp[k].append(tmpM)
                            else:
                                tmp[k].append(n)
                    else:
                        tmp[k] = str(v)
                    #print(v)
                else:
                    tmp[k] = v
            if not isJson:
                 ret = json.dumps(tmp, ensure_ascii=False, indent=4)
            else:
                ret = json.dumps(tmp, ensure_ascii=False)
            return ret
        global gWriteTMemoryBuffer, gWriteTBinaryProtocol
        gWriteTMemoryBuffer.cstringio_buf.truncate()
        gWriteTMemoryBuffer.cstringio_buf.seek(0)
        ret = None
        if isJson:
            tmpWriteTMemoryBuffer = TTransport.TMemoryBuffer()
            proto = TJSONProtocol.TJSONProtocol(tmpWriteTMemoryBuffer)
            proto.writeMessageBegin(msg.__class__.__name__, 0, 0);
            msg.write(proto)
            proto.writeMessageEnd();
            ret = tmpWriteTMemoryBuffer.getvalue()
        else:
            gWriteTBinaryProtocol.writeMessageBegin(msg.__class__.__name__, 0, 0);
            
            msg.write(gWriteTBinaryProtocol)
            gWriteTBinaryProtocol.writeMessageEnd();
            ret = gWriteTMemoryBuffer.getvalue()
        return ret
    elif hasattr(msg, 'SerializeToString'):
        return msg.SerializeToString()
    elif isinstance(msg, unicode):
        return msg.encode('utf-8')
    elif isinstance(msg, str):
        return msg
    elif msg.__class__ == int or msg.__class__ == long or msg.__class__ == float:
        return str(msg)
    else:
        return json.dumps(msg, ensure_ascii=False)

def decodeMsg(dest, val_):
    if isThrift(dest):
        return thriftDecodeMsg(dest, val_)
    else:
        dest.ParseFromString(val_)
    return dest

class SessionMgr(object):
    def __init__(self):
        self.nameGroup      = '' #区组名
        self.allSession     = {} # uid       -> session]
        self.socket2session = {} # socket id -> session
        self.name2SocketId  = {} # name -> socketid
    def getGroupName(self):
        return self.nameGroup
    def add(self, id, socketId, session):
        self.allSession[id]           = session
        self.socket2session[socketId] = session
    def addName2Socket(self, name, socketId):
        self.name2SocketId[name]      = socketId
    def delName2Socket(self, name):
        return self.name2SocketId.pop(name, None)
    def getSessionByName(self, name):
        id = self.name2SocketId.get(name)
        if id != None:
            return self.getBySocketId(id)
        return None
    def addSocket(self, socketId, session):
        self.socket2session[socketId] = session
    def findByUid(self, uid):
        return self.allSession.get(uid)
    def isPlayerOnline(self, uid):
        return self.findByUid(uid) != None
    def getBySocketId(self, id):
        return self.socket2session.get(id)
    def delByUid(self, uid):
        session = self.allSession.get(uid)
        if None != session:
            del self.allSession[uid]
            del self.socket2session[session.getSocketId()]
    def delBySocketId(self, socketId):
        session = self.socket2session.get(socketId)
        if None != session:
            del self.socket2session[socketId]
            if None != self.allSession.get(session.getUid()):
                del self.allSession[session.getUid()]
            return 1
        return 0
    def foreach(self, func):
        for k, v in self.allSession.iteritems():
            func(v)
    def foreach_until(self, func):
        for k, v in self.allSession.iteritems():
            if True == func(v):
                return
gSessionMgr = None
def getSessionMgr():
    global gSessionMgr
    if gSessionMgr:
        return gSessionMgr
    gSessionMgr = SessionMgr()
    return gSessionMgr

def processSetGroupName(group_name):
    getSessionMgr().nameGroup = group_name
    return 0
class SessionNone(object):
    def __init__(self, socket_id_ =0, ip='', group_name='', gate_name='', is_json = False):
        self.socketId    = socket_id_
        self.ip          = ip
        self.nameGroup  = group_name
        self.nameGate   = gate_name
        self.uid         = 0
        self.name        = ''
        self.flagKuafu   = False
        self.isJson     = is_json
        self.isWebDebug = False
        if self.nameGroup != '' and getSessionMgr().getGroupName() != self.nameGroup and getSessionMgr().getGroupName() != '':
            self.flagKuafu = True
        #方便用
        self.player    = None

    def setPlayer(self, player):
        print('setPlayer', player)
        if player != None:
            self.player = player
            player.session = self
    #判断是否仍然有效
    def isValid(self):
        return True
    def verify_id(self, uid_):
        return True
    def getUid(self):
        return self.uid
    def getSocketId(self):
        return self.socketId
    def getName(self):
        return self.name
    def set_name(self, name):
        self.name = name
    def encodeMsg(self, retMsg):
        body = None
        if str != retMsg.__class__:
            body = encodeMsg(retMsg, self.isJson, self.isWebDebug)
        else:
            body = retMsg
        return body
    def sendMsg(self, cmd, retMsg):
        return
    def broadcast(self, cmd, ret_msg):
        return
    def enterScene(self, toSceneName, retMsg):
        return
    def enterSceneByGroup(self, group_name, toSceneName, retMsg):
        return
    def close(self):
        return

