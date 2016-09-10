# a = 10
# b = a + 1
# c = b - 2
# d = c * 2
# e = c / 3

# g = 3.5

# if a*0:
    # h = 10
# elif b:
    # h = 15
# else:
    # h = 20
# i = 0
# j = a
# while j:
    # j = j - 1
    # i = i + 1
    # pass
    # if not j > 10:
        # break
# else:
    # i = 1
    

#def f1(a, b, c):
    #return a + b

#s= f1(**{'a':1, 'b':2, 'c':5})


class Foo:
    a = 10
    def go(self):
        self.c = 20
        return self
    def say(a):
        return a

foo = Foo()
Fa = Foo.a
fa = foo.a

foo.go()

foo.c = 202
fc = foo.c
print 1, 2, 3
print('fc', fc)
#print(f)
