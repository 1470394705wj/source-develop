from common.my_requests import *
from copy import copy
from config.data_test.mds_respond.cfgs import *

class URL_Line_Table():
    Host=SERVERS_Cfg
    Versions=Version_Cfg
    def __init__(self,markertname):
        self.Host = self.__gethost()
        self.markert_options=markertname
        self.urltables=self.__urltable(markertname)
    def __urltable(self, markertnames):#不同市场的url
        urltable=[]
        urltable += self.__get_sh_urltable()
        return urltable

    def __get_sh_urltable(self):#上海市场url
        shlist=[]
        for host in self.Host:#1
            for v in self.__get_version():#2
                for market in self.__get_markert('上海'):#2
                        urls = f'''{host}/{v}/{market}/line'''
                        url_obj = API_LINE(host, v, market,url=urls)
                        shlist.append(url_obj)
        return shlist


    def __gethost(self):#只有host为1，才处理
        hostlist=[]
        for h in self.Host:
            if h['use']==1:
                hostlist.append(h['host'])
        return hostlist
    def __get_version(self):#产生version
        return Version_Cfg
    def __get_markert(self, markertname):#不同的markert字段拼接
        if markertname=='深圳':
            return ['sz1','sz2']
        elif markertname=='上海':
            return ['sh1','sh2']
        elif markertname=='沪深共通':
            return ['sh1','sh2','sz1','sz2']



class API_LINE(API):#对应line接口
    api_type='line'
    def __init__(self,host,version,market,url):
        self.host=host
        self.version=version
        self.market=market
        self.url=url

    def ready_requests_line_v1(self,select_param_line,metheds='get',begin=None,end=None,period=None):
        self.select_param_line=select_param_line
        self.begin=begin
        self.end=end
        self.period=period
        self.line_api_params={'begin':self.begin,'end':self.end,'period':self.period}
        self.url = self.url + '?select=' + select_param_line
        self.req = requests.Request(method=metheds, url=self.url, params=self.line_api_params)
        return self

    def ready_requests_line_v2(self,select_param_list,metheds='get',begin=None,end=None,period=None,days=None):
        self.select_param_list=select_param_list
        self.begin=begin
        self.end=end
        self.period=period
        self.days=days
        self.line_api_params={'begin':self.begin,
          'end':self.end,'period':period,'days':days}
        self.url = self.url + '?select=' + select_param_list
        self.req = requests.Request(method=metheds, url=self.url, params=self.line_api_params)
        return self
    def change_url(self,code):
        print(self.url)

def line_requests_fun(market_options,filter_options,select_param_list):#准备查询参数
    reqlist = []
    url_obj = URL_Line_Table(market_options)
    url_obj_list = list(filter(filter_options, url_obj.urltables))
    param_str = ','.join(select_param_list)
    for url in url_obj_list:#根据urltable表里储存的req对象为他们赋予begin  select  order等属性
            new_url=copy.copy(url)#注意要使用深拷贝，否则会引发问题
            new_url.ready_requests_list(begin=b, end=e, select=param_str, order=o,select_param_list=select_param_list)
            reqlist.append(new_url)
    return reqlist

