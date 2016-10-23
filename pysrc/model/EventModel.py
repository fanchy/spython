# -*- coding: utf-8 -*-
import random
from base   import Base
import  weakref
import ffext

class Event(Base.BaseObj):
    EVENT_ID      = ffext.allocId()
    def __init__(self):
        return
    def getEventId(self):
        return Event.EVENT_ID

