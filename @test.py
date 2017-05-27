# coding=utf-8
import os
import sys
import re
import unittest
from config import *
from zmirror.zmirror import *
import custom_func

#from zmirror.zmirror import *

class string(str):
    def try_match_and_add_domain_to_http2https_white_list(domain, force_add=False):
        """
        若域名与`domains_whitelist_auto_add_glob_list`中的通配符匹配, 则加入 external_domains 列表
        被加入 external_domains 列表的域名, 会被应用重写机制
        用于在程序运行过程中动态添加域名到external_domains中
        也可在外部函数(custom_func.py)中使用
        关于 external_domains 更详细的说明, 请看 default_config.py 中对应的文档
        :type domain: str
        :type force_add: bool
        :rtype: bool
        """
        global external_domains, external_domains_set, allowed_domains_set, prefix_buff
        global regex_basic_mirrorlization

        if domain is None or not domain:
            return False
        if domain in allowed_domains_set:
            return True
        if not force_add and not is_domain_match_glob_whitelist(domain,domains_whitelist_http2https_glob_list):
            return False

        infoprint('A domain:', domain, 'was added to http2https list')

        _buff = list(external_domains)  # external_domains是tuple类型, 添加前需要先转换
        _buff.append(domain)
        external_domains = tuple(_buff)  # 转换回tuple, tuple有一些性能优势
        external_domains_set.add(domain)
        allowed_domains_set.add(domain)

        prefix_buff[domain] = calc_domain_replace_prefix(domain)

        # 重新生成匹配正则
        regex_basic_mirrorlization = _regex_generate__basic_mirrorlization()

        # write log
        try:
            with open(zmirror_root('automatic_http2https_whitelist.log'), 'a', encoding='utf-8') as fp:
                fp.write(domain + '\n')
        except:  # coverage: exclude
            traceback.print_exc()

        return True

    def regex_url_http2https(self,match_obj):
        prefix = get_group('prefix', match_obj)
        quote_left = get_group('quote_left', match_obj)
        quote_right = get_group('quote_right', match_obj)
        path = get_group('path', match_obj)
        match_domain = get_group('domain', match_obj)
        scheme = get_group('scheme', match_obj)

        whole_match_string = match_obj.group()

        if r"\/" in path or r"\/" in scheme:
            require_slash_escape = True
            path = path.replace(r"\/", "/")
            # domain_and_scheme = domain_and_scheme.replace(r"\/", "/")
        else:
            require_slash_escape = False

        # path must be not blank
        if (not path  # path is blank

            # only url(something) and @import are allowed to be unquoted
            or ('url' not in prefix and 'import' not in prefix) and (not quote_left or quote_right == ')')

            # for "key":"value" type replace, we must have at least one '/' in url path (for the value to be regard as url)
            or (':' in prefix and '/' not in path)

            # if we have quote_left, it must equals to the right
            or (quote_left and quote_left != quote_right)

            # in javascript, those 'path' contains one or only two slash, should not be rewrited (for potential error)
            # or (parse.mime == 'application/javascript' and path.count('/') < 2)
            # in javascript, we only rewrite those with explicit scheme ones.
            # v0.21.10+ in "key":"value" format, we should ignore those path without scheme
            or (not scheme and ('javascript' in parse.mime or '"' in prefix))
            ):
            dbgprint('returned_un_touch', whole_match_string, v=5)
            return whole_match_string

        # v0.19.0+ Automatic Domains Whitelist (Experimental)
        if enable_automatic_domains_whitelist:
            self.try_match_and_add_domain_to_http2https_white_list(match_domain)

        # dbgprint(match_obj.groups(), v=5)

        domain = match_domain or parse.remote_domain
        # dbgprint('rewrite match_obj:', match_obj, 'domain:', domain, v=5)

        # skip if the domain are not in our proxy list
        if domain not in allowed_domains_set:
            # dbgprint('return untouched because domain not match', domain, whole_match_string, v=5)
            return match_obj.group()  # return raw, do not change

        # this resource's absolute url path to the domain root.
        # dbgprint('match path', path, "remote path", parse.remote_path, v=5)
        path = urljoin(parse.remote_path, path)  # type: str

        # 在 Python3.5 以前, urljoin无法正确处理如 urljoin("/","../233") 的情况, 需要手动处理一下
        if sys.version_info < (3, 5) and "/../" in path:
            path = path.replace("/../", "/")

        if not path.startswith("/"):
            # 当整合后的path不以 / 开头时, 如果当前是主域名, 则不处理, 如果是外部域名则加上 / 前缀
            path = "/" + path

        # dbgprint('middle path', path, v=5)
        if ':' not in parse.remote_domain:  # the python's builtin urljoin has a bug, cannot join domain with port correctly
            url_no_scheme = urljoin(domain + '/', path.lstrip('/'))
        else:
            url_no_scheme = domain + '/' + path.lstrip('/')

        # dbgprint('url_no_scheme', url_no_scheme, v=5)
        # add extdomains prefix in path if need
        if domain in external_domains_set:
            path = '/extdomains/' + url_no_scheme

        # dbgprint('final_path', path, v=5)
        if enable_static_resource_CDN and url_no_scheme in url_to_use_cdn:
            # dbgprint('We Know:', url_no_scheme, v=5)
            _this_url_mime_cdn = url_to_use_cdn[url_no_scheme][0]
        else:
            # dbgprint('We Don\'t know:', url_no_scheme,v=5)
            _this_url_mime_cdn = False

        # Apply CDN domain
        if _this_url_mime_cdn:
            # pick an cdn domain due to the length of url path
            # an advantage of choose like this (not randomly), is this can make higher CDN cache hit rate.

            # CDN rewrite, rewrite static resources to cdn domains.
            # A lot of cases included, the followings are just the most typical examples.
            # http(s)://target.com/img/love_lucia.jpg --> http(s)://your.cdn.domains.com/img/love_lucia.jpg
            # http://external.com/css/main.css --> http(s)://your.cdn.domains.com/extdomains/external.com/css/main.css
            # http://external.pw/css/main.css --> http(s)://your.cdn.domains.com/extdomains/external.pw/css/main.css
            replace_to_scheme_domain = my_host_scheme + CDN_domains[zlib.adler32(path.encode()) % cdn_domains_number]

        # else:  # parse.mime == 'application/javascript':
        #     replace_to_scheme_domain = ''  # Do not use explicit url prefix in js, to prevent potential error
        elif not scheme:
            replace_to_scheme_domain = ''
        elif 'http' not in scheme:
            replace_to_scheme_domain = '//' + my_host_name
        else:
            replace_to_scheme_domain = myurl_prefix

        reassembled_url = urljoin(replace_to_scheme_domain, path)
        if _this_url_mime_cdn and cdn_redirect_encode_query_str_into_url:
            reassembled_url = embed_real_url_to_embedded_url(
                reassembled_url,
                url_mime=url_to_use_cdn[url_no_scheme][1],
                escape_slash=require_slash_escape
            )

        if require_slash_escape:
            reassembled_url = s_esc(reassembled_url)

        # reassemble!
        # prefix: src=  quote_left: "
        # path: /extdomains/target.com/foo/bar.js?love=luciaZ
        reassembled = prefix + quote_left + reassembled_url + quote_right + get_group('right_suffix', match_obj)

        # dbgprint('---------------------', v=5)
        return reassembled

    def http2https(self):
        self = regex_adv_url_rewriter.sub(self.regex_url_http2https, self)
        return self

    def name(self, name):  
        self.name = name  
        return self  
    def age(self, age):  
        self.age = age  
        return self  
    def show(self):  
        print("My name is", self.name, "and I am", self.age, "years old.")  
  
p = string("abs")  
p.name("Li Lei").age(15).show()  

import urllib
#根据URL获取域名
def getdomain(url):
    proto, rest = urllib.request.splittype(url)
    host, rest = urllib.request.splithost(rest)
    return host

domain = getdomain("http://www.cnblogs.com/goodhacker/admin/EditPosts.aspx?opt=1")
print(domain)
append_list_to_file('automatic_force_https_domains_whitelist.txt',domain)


if __name__ == '__main__':
    os.environ['ZMIRROR_UNITTEST'] = "True"
    parse.remote_domain="www.google.com"
    parse.mime="text/html; charset=UTF-8"

    file = '@html'
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
        
    from winreg import *
    key=OpenKey(HKEY_CURRENT_USER,"Software\Microsoft\Windows\CurrentVersion\Internet Settings\Connections",0,KEY_ALL_ACCESS)
    (value, regtype) = QueryValueEx(key, "DefaultConnectionSettings")
    print(key)
    print(value)
    print()
    print(value[:16])
    #if regtype == REG_BINARY:
    #     value = value[:8].decode() + chr(0x03) + value[9:].decode()
    SetValueEx(key, "DefaultConnectionSettings", None, regtype, value)
