#!/usr/bin/env python3
# coding=utf-8

import io
import sys
#sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='utf8') #改变标准输出的默认编码  
sys.stdout = io.TextIOWrapper(sys.stdout.buffer,encoding='gb18030') #改变标准输出的默认编码  cmd

import datetime
from pyquery import PyQuery
import PyRSS2Gen

class PlusOne2Rss():
    def __init__(self):
        self.url = 'http://dig.chouti.com/all/hot/recent/1'
        self.pq = PyQuery(url=self.url).make_links_absolute()
        self.user_name = self.pq('a.a-n[href="%s"]').text()

    def _title(self, table):
        return self.pq('a.show-content', table).text().strip()

    def _link(self, table):
        return self.pq('a.time-a', table).attr('href')

    def _description(self, table):
        #print(dir(self.pq('.news-pic', table)))
        href=self.pq('.show-content', table).attr("href")
        description=''
        description+='<p><img src="'+self.pq('.news-pic>img', table).attr("original")+'" /></p>'
        description+='<p><a href="'+href+'" target="_blank">'+href+'</a></p>'
        description+='<iframe style="width:100%;height:100%;border:0;width:1px;min-width:100%;*width:100%;" src="'+href+'"></iframe>'
        description+=self.pq('.summary', table).text().strip()
        return description
        
    def write_feed(self, filename='rss/chouti.xml'):
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
        rss.write_xml(open(filename, "w", encoding='utf-8'), encoding='utf-8')

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
    PlusOne2Rss().write_feed()

from config_default import *
cron_tasks_list.append(dict(name='RssTask', priority=42, interval=60 * 10, target='RssTask'))

RssTask()