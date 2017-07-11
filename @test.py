# coding=utf-8
import os
import sys
import re
import unittest
import urllib
from config import *
from zmirror.zmirror import *
import custom_func
import os

#from zmirror.zmirror import *

class string(str):
    def name(self, name):  
        self.name = name  
        return self  
    def age(self, age):  
        self.age = age  
        return self  
    def show(self):  
        print("My name is", self.name, "and I am", self.age, "years old.")  
    def getDomain(self):#根据URL获取域名
        proto, rest = urllib.request.splittype(self)
        host, rest = urllib.request.splithost(rest)
        self.domain = host  
        return self
    def showDomain(self):
        self.getDomain()
        print(self.domain)
        return self
    def getSysProxy(self):
        if os.name == 'nt':
            try:
                #from winreg import *
                key=OpenKey(HKEY_CURRENT_USER,"Software\Microsoft\Windows\CurrentVersion\Internet Settings\Connections",0,KEY_ALL_ACCESS)
                (value, regtype) = QueryValueEx(key, "DefaultConnectionSettings")
                print(key)
                print(value)
                print()
                print(value[:16])
                #if regtype == REG_BINARY:
                #     value = value[:8].decode() + chr(0x03) + value[9:].decode()
                SetValueEx(key, "DefaultConnectionSettings", None, regtype, value)
            except:
                return ''
  
url = 'https://219.76.4.10'
url = 'http://www.cnblogs.com/goodhacker/admin/EditPosts.aspx?opt=1'
headers = {'Host': 'tumblr.com'}
r = requests.get(url, headers=headers)
print(r.text)

p = string(url)  
p.name("Li Lei").age(15).showDomain().show()  

import urllib.request
req = urllib.request.Request(p, method="HEAD")
resp = urllib.request.urlopen(req)
print("resp "+str(resp))
print("resp.url "+str(resp.url))
print("resp.status "+str(resp.status))
print("resp.headers\n"+str(resp.headers))
a = resp.read()
print("a.length "+str(len(a)))

if __name__ == '__main__':
    os.environ['ZMIRROR_UNITTEST'] = "True"
    parse.remote_domain="www.google.com"
    parse.mime="text/html; charset=UTF-8"

    file = '@html'
    if os.path.exists(zmirror_root(file+'.html')): 
        resp_text = string(open(file+'.html','r',encoding='utf-8').read())#.http2https()

        resp_text = response_text_rewrite(resp_text)
        p = re.compile('http:\\/\\/' + my_host_name + '\\/')
        print(p.findall(resp_text))
        #resp_text = resp_text.replace('http:\\/\\/' + my_host_name + '\\/', '\/\/'+ my_host_name + '\/')
        with open(file+'1.html', mode='w',encoding='utf-8') as pubilc_file:
            pubilc_file.write(resp_text)
        
        resp_text = custom_func.custom_response_text_rewriter(resp_text, '', '')
        with open(file+'2.html', mode='w',encoding='utf-8') as pubilc_file:
            pubilc_file.write(resp_text)
        
        resp_text = resp_text.replace('http%3A%2F%2F' + my_host_name, '%2F%2F' + my_host_name)
        resp_text = resp_text.replace('http:\\/\\/' + my_host_name + '\\/', '\/\/'+ my_host_name + '\/')
        #resp_text = resp_text.replace('http://static.tumblr.com','//static.tumblr.com')
        #resp_text = resp_text.replace('http://assets.tumblr.com','//assets.tumblr.com')
        #resp_text = resp_text.replace('http://media.tumblr.com','//media.tumblr.com')
        resp_text = resp_text.replace(r'http://\\w+.tumblr.com','//static.tumblr.com')
        with open(file+'3.html', mode='w',encoding='utf-8') as pubilc_file:
            pubilc_file.write(resp_text)
        
