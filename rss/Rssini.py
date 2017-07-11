#!/usr/bin/env python3
# coding=utf-8

import io
import sys
#sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf8') #改变标准输出的默认编码  
sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='gb18030') #改变标准输出的默认编码  cmd

#from Rss import *

#-read(filename)            直接读取文件内容
#-sections()                得到所有的section，并以列表的形式返回
#-options(section)          得到该section的所有option
#-items(section)            得到该section的所有键值对
#-get(section,option)       得到section中option的值，返回为string类型
#-getint(section,option)    得到section中option的值，返回为int类型，还有相应的getboolean()和getfloat() 函数

import configparser
config = configparser.ConfigParser()
config.read('Rss.ini')
sections=config.sections()
print(sections)
for section in sections:
    for key in config[section]: print(key)

mycode = 'print (sections)'
exec(mycode)