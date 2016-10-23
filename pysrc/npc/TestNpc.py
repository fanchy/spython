# -*- coding: utf-8 -*-
import ffext
from mapmgr import MapMgr

def main(player, npc):
    if npc.name == '强化':
        player.sendShowUIMsg(4)#UI_QIANGHUA
        return None
    if npc.name == '结义':
        player.sendShowUIMsg(1)#UI_QIANGHUA
        return None
    if npc.name == '结婚':
        player.sendShowUIMsg(2)#UI_QIANGHUA
        return None
    if npc.name == '行会和皇城攻占申请':
        player.sendShowUIMsg(5)
        return None
    if npc.name == '拍卖行':
        player.sendShowUIMsg(6)
        return None
    if npc.name == '仓库保管':
        player.sendShowUIMsg(7)
        return None
    if npc.name == '钱庄':
        player.sendShowUIMsg(8)
        return None
    if npc.name == '贩卖装备':
        player.sendShowUIMsg(9)
        return None
    if npc.name == '消耗道具':
        player.sendShowUIMsg(10)
        return None
    if npc.name == '传送':
        player.sendShowUIMsg(11)
        return None
    #mapObj = MapMgr.getMapMgr().createCopyMap('10001')
    #mapObj.playerEnterMap(player)
    #return npc.getDefaultDuiBai(), [('结义', 'showUI&1'), ('结婚', 'showUI&2'),('测试动画', 'test')]
    return npc.getDefaultDuiBai(), []

def showUI(player, npc, a):
    player.sendShowUIMsg(int(a))
    return

def test(player, npc):
   npc.showPlay(player, 10013)
def foo(player, npc, a, b):
    print('foo', a, b)
    return '收到参数:%s,%s '%(a, b)
