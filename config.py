# coding=utf-8
# 这是为Google和中文维基(无缝整合)镜像配置的示例配置文件
#
# 使用方法:
#   1. 复制本文件到 zmirror 根目录(wsgi.py所在目录), 并重命名为 config.py
#   2. 修改 my_host_name 为你自己的域名
#
# 各项设置选项的详细介绍请看 config_default.py 中对应的部分
# 本配置文件假定你的服务器本身在墙外
# 如果服务器本身在墙内(或者在本地环境下测试, 请修改`Proxy Settings`中的设置
#
# 由于google搜索结果经常会出现中文维基, 所以顺便把它也加入了.
# google跟中文维基之间使用了本程序的镜像隔离功能, 可以保证中文维基站的正常使用
#
# 本配置文件试图还原出一个功能完整的google.
#   但是由于程序本身所限, 还是不能[完整]镜像过来整个[google站群]
#   在后续版本会不断增加可用的网站
#
# 以下google服务完全可用:
#   google网页搜索/学术/图片/新闻/图书/视频(搜索)/财经/APP搜索/翻译/网页快照/...
#   google搜索与中文维基百科无缝结合
# 以下服务部分可用:
#     gg地图(地图可看, 左边栏显示不正常)/G+(不能登录)
# 以下服务暂不可用(因为目前无法解决登录的问题):
#     所有需要登录的东西, docs之类的
#

# Github: https://github.com/aploium/zmirror

# ############## Local Domain Settings ##############
my_host_name = 'zm.guge.cf'
my_host_scheme = 'http://'
my_host_port = None  # None表示使用默认端口, 可以设置成非标准端口, 比如 81

developer_temporary_disable_ssrf_prevention = True
custom_text_rewriter_enable = True
verbose_level = 3
local_cache_enable = True

# ############## Target Domain Settings ##############
target_domain = 'www.google.com.hk'
target_scheme = 'https://'

# 这里面大部分域名都是通过 `enable_automatic_domains_whitelist` 自动采集的, 我只是把它们复制黏贴到了这里
# 实际镜像一个新的站时, 手动只需要添加很少的几个域名就可以了.
# 自动采集(如果开启的话)会不断告诉你新域名
external_domains = ('google.com','zh.wikipedia.org','zh.m.wikipedia.org',)

# 强制所有Google站点使用HTTPS
force_https_domains = 'ALL'

# 自动动态添加域名
enable_automatic_domains_whitelist = True
domains_whitelist_auto_add_glob_list = (
    '*.google.com','*.google*.com','*.google.com.*',
    '*.gstatic.com','*.ggpht.com','*.gmail.com',
    '*.youtube.com','*.youtube*.com','*.ytimg.com',
    '*.android.com','*.wikipedia.org',
    '*.tumblr.com','*.t66y.com',
)
domains_whitelist_ignore_glob_list = (
    'tumblr.co','tumblr.com','www.tumblr.com',
    'assets.tumblr.com','*.assets.tumblr.com',
    'media.tumblr.com','*.media.tumblr.com',
    'static.tumblr.com','*.static.tumblr.com',
    'api.tumblr.com','mx.tumblr.com','px.srvcs.tumblr.com',
    'ls.srvcs.tumblr.com','vt.tumblr.com','cynicallys.tumblr.com',
)
domains_whitelist_http2https_glob_list = (
    '*.tumblr.com',
)
# ############## Proxy Settings ##############
# 如果你在墙内使用本配置文件, 请指定一个墙外的http代理
is_use_proxy = False
# 代理的格式及SOCKS代理, 请看 http://docs.python-requests.org/en/latest/user/advanced/#proxies
requests_proxies = dict(
    http='http://127.0.0.1:1080',
    https='https://127.0.0.1:1080',
)

allowed_remote_response_headers = {'location'}

# ############## Sites Isolation ##############
enable_individual_sites_isolation = True

# 镜像隔离, 用于支持Google和维基共存
isolated_domains = {'zh.wikipedia.org', 'zh.m.wikipedia.org'}

# ############## URL Custom Redirect ##############
url_custom_redirect_enable = True
url_custom_redirect_list = {
    # 这是一个方便的设置, 如果你访问 /wiki ,程序会自动重定向到后面这个长长的wiki首页
    '/wiki': '/extdomains/https-zh.wikipedia.org/',
    '/ytb': '/extdomains/https-www.youtube.com/',
    '/t': '/extdomains/https-www.twitter.com/',
    # 这是gmail
    '/gmail': '/extdomains/mail.google.com/mail/u/0/h/girbaeneuj90/',
}

# ############## m.youtube.com ##############
custom_text_rewriter_enable = True
url_custom_redirect_enable = True
url_custom_redirect_regex = (
    (r'^/api/stats/(?P<ext>.*)', r'/extdomains/https-s.youtube.com/api/stats/\g<ext>'),
    (r'^/user/api/stats(?P<ext>.*)', r'/extdomains/https-s.youtube.com/user/api/stats\g<ext>'),
)
shadow_url_redirect_regex = (
    (r'^/videoplayback(?P<ext>.*)', r'/extdomains/https-r8---sn-q4f7snss.googlevideo.com/videoplayback\g<ext>'),
    (r'^/videoplayback\?ewmytbserver=(?P<prefix>r\d+---sn-[a-z0-9]{8})&(?P<ext>.*?)',
     r'/extdomains/https-\g<prefix>.googlevideo.com/videoplayback?\g<ext>'),
)
text_like_mime_keywords = ('text', 'json', 'javascript', 'xml', 'x-www-form-urlencoded')

# ############# Additional Functions #############
# 移除google搜索结果页面的url跳转
#   原理是往页面中插入一下面这段js
# js来自: http://userscripts-mirror.org/scripts/review/117942
custom_inject_content = {
    "head_first": [
        {
            "content": r"""<script>
function checksearch(){
   var list = document.getElementById('ires');
   if(list){
       document.removeEventListener('DOMNodeInserted',checksearch,false);
       document.addEventListener('DOMNodeInserted',clear,false)
   }
};

function clear(){
   var i; var items = document.querySelectorAll('a[onmousedown]');
   for(i =0;i<items.length;i++){
       items[i].removeAttribute('onmousedown');
   }
};
document.addEventListener('DOMNodeInserted',checksearch,false)
</script>""",
            "url_regex": r"^www\.google(?:\.[a-z]{2,3}){1,2}",
        },
        {
            "content": r"""<script>
window.history.replaceState=function(a,b,c){
    c=location.href.replace("/"+location.search,"")+c;
}
</script>""",
            "url_regex": r"^m\.youtube(?:\.[a-z]{2,3}){1,2}",
        },
    ]
}
