#!/usr/bin/env python3
# coding=utf-8

import os

import io
import sys
#sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf8') #改变标准输出的默认编码  
sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='gb18030') #改变标准输出的默认编码  cmd

import datetime
from pyquery import PyQuery
import PyRSS2Gen

useragent="Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1"

class PlusOne2Rss():
    def __init__(self,_url,filename):
        self.url = _url
        self.filename = filename
        self.pq = PyQuery(url=self.url, headers={'user-agent': useragent}).make_links_absolute()
        self.user_name = self.pq('a.a-n[href="%s"]').text()

    def _title(self, table):
        return self.pq('a.show-content', table).text().strip()

    def _link(self, table):
        return self.pq('a.time-a', table).attr('href')

    def _description(self, table):
        href=self.pq('.show-content', table).attr("href")
        host=href.split('/')[2]
        description=''
        if self.pq('.news-pic>img', table).size() > 0:
            imgsrc=self.pq('.news-pic>img', table).attr("original").replace("=C60x60","")
            if imgsrc.find("//")==0:
                imgsrc='http:'+imgsrc
            description+='<p><img style="max-width:100%;" src="'+imgsrc+'" /></p>'
        if host=="dig.chouti.com" and href.split('/')[4].startswith("show?"):
            pq=PyQuery(href, headers={'user-agent': useragent}).make_links_absolute()
            imgs=pq(".no-page")
            if imgs.size() > 0:
                imgs.find("img").css("max-width","100%")
                description+=imgs.outerHtml()
            imgs=pq("#container")
            if imgs.size() > 0:
                imgs.find("img").css("max-width","100%")
                description+=imgs.outerHtml()
        elif href.find(".sinaimg.cn/")>0:
            description+='<p><img style="max-width:100%;" src="'+href+'" /></p>'
        elif href.find("www.miaopai.com")>0:
            pq=PyQuery(href, headers={'user-agent': useragent}).make_links_absolute()
            videoImg=pq(".video_img").attr("data-url")
            imgs=pq(".video_player")
            imgs.find("video").attr(poster=videoImg)
            description+=imgs.outerHtml()
        description+='<p><a href="'+href+'" target="_blank">'+href.split('/')[2]+'</a></p>\n'
        
        #description+='\n<iframe style="width:100%;height:100%;border:0;width:1px;min-width:100%;*width:100%;" src="'+href+'"></iframe>'
        description+=self.pq('.summary', table).text().strip()
        return description
        
    def write_feed(self):
        rss_items = []
        tables = self.pq('#content-list .item')
        for table in tables:
            #item = PyRSS2Gen.RSSItem(
            item = self.IPhoneRSS2(
                    title = self._title(table),
                    link = self._link(table),
                    description = self._description(table),
                    guid = PyRSS2Gen.Guid(self._link(table)),
                    pubDate = datetime.datetime.now()
                )
            rss_items.append(item)
        rss = PyRSS2Gen.RSS2(
                title = self.pq("title").text(),
                link = self.url,
                generator= u'PlusOne2Rss',
                description = self.pq("meta[name='description']").attr("content").strip(),
                lastBuildDate = datetime.datetime.utcnow(),
                items = rss_items
            )

        if not os.path.exists(os.path.dirname(self.filename)):
            try:
                os.makedirs(os.path.dirname(self.filename))
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
        rss.write_xml(open(self.filename, "w", encoding='utf-8'), encoding='utf-8')

    class IPhoneRSS2(PyRSS2Gen.RSSItem):
        def __init__(self, **kwargs):
            PyRSS2Gen.RSSItem.__init__(self, **kwargs)

        def publish(self, handler):
            self.do_not_autooutput_description = self.description
            self.description = self.NoOutput() # This disables the Py2GenRSS "Automatic" output of the description, which would be escaped.
            PyRSS2Gen.RSSItem.publish(self, handler)

        def publish_extensions(self, handler):
            handler._write('<%s><![CDATA[%s]]></%s>' % ("description", self.do_not_autooutput_description, "description"))

        class NoOutput:
            def __init__(self):
                pass
            def publish(self, handler):
                pass

def RssTask():
    PlusOne2Rss('http://dig.chouti.com/all/hot/recent/1','rss/chouti.xml').write_feed()
    PlusOne2Rss('http://dig.chouti.com/r/news/hot/1','rss/chouti_news.xml').write_feed()
    PlusOne2Rss('http://dig.chouti.com/r/scoff/hot/1','rss/chouti_scoff.xml').write_feed()
    PlusOne2Rss('http://dig.chouti.com/r/pic/hot/1','rss/chouti_pic.xml').write_feed()
    PlusOne2Rss('http://dig.chouti.com/r/tec/hot/1','rss/chouti_tec.xml').write_feed()
    PlusOne2Rss('http://dig.chouti.com/r/ask/hot/1','rss/chouti_ask.xml').write_feed()

try:
    from config_default import *
    cron_tasks_list.append(dict(name='RssTask', priority=42, interval=60 * 10, target='RssTask'))
except:
    pass

RssTask()