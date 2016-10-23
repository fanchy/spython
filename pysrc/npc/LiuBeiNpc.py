# -*- coding: utf-8 -*-
import ffext
from mapmgr import MapMgr

def main(player, npc):
    #mapObj = MapMgr.getMapMgr().createCopyMap('10001')
    #mapObj.playerEnterMap(player)
    return npc.getDefaultDuiBai()


def test(player, npc):
    npc.showNpcPlay(player, 101, 'foo&1&2')
    return
def foo(player, npc, a, b):
    print('foo', a, b)
    return '收到参数:%s,%s!'%(a, b)