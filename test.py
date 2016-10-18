
'test doc'

cc = -1
a = 10
b = a + 1
c = b - 2
d = c * 2
e = c / 3

g = 3.5
x, y = 113, 224
if a*0:
    h = 10
elif b:
    h = 15
else:
    h = 20
i = 0
j = a
while j:
    j = j - 1
    i = i + 1
    pass
    if not j > 10:
        break
else:
    i = 1
    

def f1(a, b, c):
    return a + b

s= f1(**{'a':1, 'b':2, 'c':5})
class F:
    'OhThisIsDoc'
    def hi(self):
        self.d = 99
        print('hi')
        a = b
        return 1023

class Foo(F):
    a = 10
    def __init__(self):
        self.b = 1022
    def __str__(self):
        return 'Foo instance:'
    def __len__(self):
        return 10
    def __eq__(self, v):
        print('eeeeeeeee')
        return v.c == 12
    def go(self):
        self.c = 20
        print('go')
        return self
    def say(a):
        return a
    @property
    def A(self):
        print('property self:', self)
        return self.b
    @A.setter
    def A(self, v):
        print('property set:', v)
        self.b = v
f = Foo()
print('lenf', len(f))
f.A = 9966
property1 = f.A

f2 = Foo()
f2.c = 10
if f == f2:
    print('equal2')

foo = Foo()
print(foo)
ee = foo.hi()
foo.c = 201
foo.a = 20
Fa = Foo.a
fa = foo.a
print('fa', Fa, fa)
foo.go()

foo.c = 202
fc = foo.c
print 1, 2, 3
print('fc', fc)


fhi = foo.hi()
fd  = foo.d
a, b, c = (1, 2, 3)
#from mod import *
#from mod import mb


import ma

try:
    ta = 109
    raise 1002
except int, i:
    teai = 2399
except Foo, f:
    teafoo = 199
except F, f:
    teaf = 299
except:
    tea = 99
else:
    tel = 89
finally:
    tef = 78

ecpp = Exception

def wf2():
    return 6633
def wrap(f):
    print('wrap....')
    return f
def wrap2(f):
    print('wrap2....')
    return wf2
@wrap2
@wrap
def wf():
    return 1122334

testD = wf()
testN = None
testtuple = (1, 2, 3, 4, 2)
testtupcount = testtuple.index(4)

testlen = len('1222')
tests1 = 'abcdefg'
tests2 = tests1.upper()
tests3 = tests2.lower()
tests3 = tests2.lower()


xx = tests3[3:100]
print(xx)
fooname = Foo.__name__

lista = [1, 2, 3, 4]
listb = [5, 6, 5]
listb.append(7)
listb.extend(lista)
listc = lista + listb
listalen = len(lista)
listb.insert(0, 100)
listb.insert(2, 102)
listb.insert(10, 110)
listb.insert(120, 120)
listb.pop(1)
listb.remove(110)
lista.reverse()
def cmpf(a, b):
    return b - a
def keyf(a):
    return a

listb.sort(None, keyf)
print(listb)
listindex= listb.index(6)
listcount= listb.count(5)

listtuple = (1, 2, 3, 4)
listtuple = (1, 2, 3, 4)
testdict2= {k:k for k in listtuple}
testdict2['a'] = 'aaa'
testdict3 = testdict2[3]
testdict4 = testdict2['a']

#listtuple[1] = 2

lambda1 = lambda x : x + 1
lambda2 = lambda1(120)
testdict5 = testdict2.items()
testdict2.pop(3)
testdict6 = testdict2.items()
for k, v in testdict2.items():
    print(k, v)

for k  in testdict2:
    print('xxxx', k, testdict2[k])
testdict7 = testdict2.copy()
testdict7.clear()
testdict7 = dict.fromkeys(listtuple, 122)
testdict8 = testdict7.get(12, 13)
testdict9 = testdict7.has_key(12)
testdict10= testdict7.keys()
testdict7.popitem()
testdict7.update({3:333, 1:1111})
testdict11 = testdict7.values()

for m, n in testdict7.iteritems():
    print('iter', m, n)

def closure1():
    'closure doc'
    def closure2():
        print('closure2', mm)
        def closure3():
            print('closure3', mm)
            return mm
        return closure3
    
    mm = 101
    return closure2
print('f.b1', f.b)
del testdict11
del f.b
del testdict2[1]

del listb[1]
foodoc = f.__doc__
closuredoc = closure1.__doc__
testdoc = __doc__

def fglobal():
    global gX
    print('gX', gX)
    gX = 1010

gX = 1009
fglobal()

e1 = BaseException(1, 2, 'a')
print('e1', e1)
iAdd1 = 100
iAdd1 += 10
iAdd1 *= 2
iAdd1 %= 3
n1 = 0X12
n2 = -n1
n3 = 1 << 4
list21 = '''ss'
gg'''
print(list21)

#import weakref
weakref = __import__('weakref')
ref1 = weakref.ref(foo)
del foo
ref2 = ref1()
#ref3 = foo.c
import time
time1 = time.time() - 3600
time2 = time.localtime(time1 )
print(time2)
time3 = time.mktime(time2)
print(time1, time3)

from time import time as time4


import datetime

dt1 = datetime.datetime(2016, 9, 12, 7, 8, 12)
dt2 = dt1.strftime("%Y-%m-%d %H:%M:%S")

dt3 = datetime.datetime.now()
print(dt1)
print(dt2)
print(dt3.strftime("%Y-%m-%d %H:%M:%S"))

dt4 = dt1.date()
print(dt4)
dt5 = datetime.date.today()
print(dt5)
dt6 = datetime.datetime.strptime("2016-10-17 18:20:10", "%Y-%m-%d %H:%M:%S")
print(dt6)
dt7 = datetime.timedelta(3)
print(dt7)
dt8 = dt6 - dt7
dt9 = dt8 - dt6
print(dt9)
dt10 = dt8.timetuple()
print(dt10)
dt11 = datetime.datetime.fromtimestamp(1421077403.0)
print(dt11)
dt12 = dt6.weekday()
print(dt12)
dt13 = dt6.isoweekday()
print(dt13)
dt14 = dt3.isoformat()
print(dt14)
dt15 = dt5 - dt4
print(dt15)
dt16 = dt4 + dt15
print(dt16)
dt17 = dt16.weekday()
print(dt17)
dt18 = dt16.isoweekday()
print(dt18)
dt19 = dt16.isoformat()
print(dt19)

import json

import StringIO
output = StringIO.StringIO()
output.write('First line.')
contents = output.getvalue()
print(contents)
testrange = range(0, 10)

import math
ceil1 = math.ceil(3.4)
print(ceil1)
floor1 = math.floor(5.6)
print(floor1)

acos1 = math.acos(0.3)
print(acos1)

strmod1 = 'abc%d'%10
