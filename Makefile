#交叉编译器路径
CROSS=
CP=/bin/cp
RM=-/bin/rm -rf
LN=/bin/ln -s 
CFLAGS= -g -Wall 
LDFLAGS= -O2 
#-lcurl
#-llua 
#链接库名
LIB_NAME=
#链接库版本
LIB_VER=1.0.0
#平台
ARCH=
# 二进制目标
BIN=spython

#源文件目录
SrcDir= . src src/objhandler
#头文件目录
IncDir=  ./ include
#连接库目录
LibDir= /usr/local/lib 
SRCS=$(foreach dir,$(SrcDir),$(wildcard $(dir)/*.cpp))
#INCS=$(foreach dir,$(IncDir),$(wildcard $(dir)/*.h))
INCS=$(foreach dir,$(IncDir),$(addprefix -I,$(dir)))
LINKS=$(foreach dir,$(LibDir),$(addprefix -L,$(dir)))
CFLAGS := $(CFLAGS) $(INCS)
LDFLAGS:= $(LINKS) $(LDFLAGS) -lpthread
CC=gcc
ARCH=PC
OBJS = $(SRCS:%.cpp=%.o)
.PHONY:all clean

all:$(BIN)
$(BIN):$(OBJS)
	g++ -o $(BIN) $(OBJS) $(LDFLAGS)  
	@echo  " OK! Build $@ "
# @$(LN) $(shell pwd)/$(LIB_NAME).$(LIB_VER) /lib/$(LIB_NAME)

%.o:%.cpp
	@echo  "Build $@..."
	@$(CC) $(CFLAGS)  -c $< -o $@

.PHONY: clean
clean:
	@echo  "[$(ARCH)] Cleaning files..."
	@$(RM) $(OBJS) $(BIN) 
	@$(RM) sqlite3.o
