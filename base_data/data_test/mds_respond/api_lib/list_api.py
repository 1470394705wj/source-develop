from common.my_requests import *
import copy as copy
from config.data_test.mds_respond.cfgs import *
class URL_Table():

    Host=SERVERS_Cfg
    Versions=Version_Cfg
    Sh1AndSh2_Subtype_Cfg=Sh1AndSh2Exchange_Cfg
    Sz1AndSz2_Subtype_Cfg=Sz1AndSz2Exchange_Cfg
    ShAndSz_Subtype_Cfg_block=SubTypeBlock_Cfg
    ShAndSz_Subtype_Cfg_exchange=SubTypeExchange_Cfg

    ShAndSz_Subtype_Cfg_self_exchange=ListSelfCode
    def __init__(self,markertname):
        self.Host = self.__gethost()
        self.markert_options=markertname
        self.urltables=self.__urltable(markertname)
    def __urltable(self, markertnames):#不同市场的url
        urltable=[]
        if markertnames=='上海市场':
            #self.options='exchange'
            urltable+=self.__get_sh_urltable()
        elif markertnames=='深圳市场':
            #self.options = 'exchange'
            urltable+=self.__get_sz_urltable()
        elif markertnames=='沪深共通':
            #self.options=['self','block','exchange']
            urltable+=self.get_options_subtype('self')
            #print(self.get_options_subtype('block'))
            urltable+=self.get_options_subtype('block')
            urltable+=self.get_options_subtype('exchange')
        return urltable
    def get_options_subtype(self,options):

        if self.markert_options!='沪深共通':
            raise TypeError('错误,只有沪深共通可以选择subtype类型')

        elif options not in ['self','block','exchange']:
                raise ValueError('你选择的子类型有问题，重新选择')
        elif options in   ['self','block','exchange']:
           return  self.__get_shAndsz_urltable(options)
    def __get_sh_urltable(self):#上海市场url
        shlist=[]
        for host in self.Host:#1
            for v in self.__get_version():#2
                for market in self.__get_markert('上海'):#2
                    for s_type_t,s_type, in self.__get_sub_type('上海','exchange').items():#44
                        urls = f'''{host}/{v}/{market}/list/{self.__get_type('exchange')}/{s_type}'''
                        url_obj = API_LIST(host, v, market, self.__get_type('exchange'), s_type,
                                           belong_to_market='上海', belong_to_type='exchange',sub_type_type=s_type_t,url=urls)

                        shlist.append(url_obj)
        return shlist
    def __get_sz_urltable(self):#深圳url
        szlist = []
        for host in self.Host:#1
            for v in self.__get_version():#2
                for market in self.__get_markert('深圳'):#2
                    for s_type_t,s_type in self.__get_sub_type('深圳','exchange').items():#33
                        urls = f'''{host}/{v}/{market}/list/{self.__get_type('exchange')}/{s_type}'''
                        url_obj = API_LIST(host, v, market, self.__get_type('exchange'), s_type,
                                           belong_to_market='深圳', belong_to_type='exchange',sub_type_type=s_type_t,url=urls)
                        szlist.append(url_obj)
        return szlist
    def __get_shAndsz_urltable(self, typess):#共通url
        shAndsz_list = []
        if typess=='exchange':
            for host in self.Host:  # 1
                for v in self.__get_version():  # 2
                    for market in self.__get_markert('沪深共通'):  # 4
                        for s_type_t,s_type in self.__get_sub_type('沪深共通','exchange').items():  # block-8  #exchange-17
                            urls = f'''{host}/{v}/{market}/list/{self.__get_type(typess)}/{s_type}'''
                            url_obj = API_LIST(host, v, market, self.__get_type(typess), s_type,
                                               belong_to_market='沪深共通', belong_to_type='exchange', sub_type_type=s_type_t,url=urls)
                            shAndsz_list.append(url_obj)
        elif typess=='block':
            for host in self.Host:  # 1
                for v in self.__get_version():  # 2
                    for market in self.__get_markert('沪深共通'):  # 4
                        for s_type_t,s_type in self.__get_sub_type('沪深共通','block').items():  # block-8  #exchange-17
                            urls = f'''{host}/{v}/{market}/list/{self.__get_type(typess)}/{s_type}'''
                            url_obj = API_LIST(host, v, market, self.__get_type(typess), s_type,
                                               belong_to_market='沪深共通', belong_to_type='block',sub_type_type=s_type_t, url=urls)
                            shAndsz_list.append(url_obj)

        elif typess == 'self':
            for host in self.Host:  # 1
                for v in self.__get_version():  # 2
                    for market in self.__get_markert('沪深共通'):  # 4
                        for s_type_t,s_type in self.__get_sub_type('沪深共通','self').items():  # block-8  #exchange-17

                            urls = f'''{host}/{v}/{market}/list/{self.__get_type(typess)}/{s_type}'''

                            url_obj = API_LIST(host, v, market, self.__get_type(typess), s_type,
                                               belong_to_market='沪深共通', belong_to_type='self',sub_type_type=s_type_t, url=urls)
                            shAndsz_list.append(url_obj)

        return shAndsz_list
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
    def __get_type(self, typename):
        if typename=='block':
            return 'block'
        elif typename=='exchange':
            return 'exchange'
        elif typename=='self':
            return 'self'

    def __get_sub_type(self, marketname,suboptions):
        if marketname=='上海':
            return self.Sh1AndSh2_Subtype_Cfg
        elif marketname=='深圳':
            return self.Sz1AndSz2_Subtype_Cfg
        elif marketname=='沪深共通' and suboptions=='self':
            return self.ShAndSz_Subtype_Cfg_self_exchange
        elif marketname=='沪深共通' and suboptions=='block':
            return self.ShAndSz_Subtype_Cfg_block
        elif marketname=='沪深共通' and suboptions=='exchange':
            return self.ShAndSz_Subtype_Cfg_exchange
class API_LIST(API):#对应list接口
    api_type='list'

    def __init__(self,host,version,market,type,sub_type,belong_to_market,belong_to_type,sub_type_type,
                 url):
        self.belong_to_market=belong_to_market
        self.belong_to_types=belong_to_type
        #--------------------------
        self.host=host
        self.version=version
        self.market=market
        self.type=type
        self.sub_type=sub_type
        self.sub_type_type=sub_type_type
        #self.url=rf'{self.host}/{self.version}/{self.market}/{self.api_type}/{self.apitype}/{self.sub_type}'
        self.url=url
    def ready_requests_list(self,select_param_list,metheds='get',begin=None,end=None,select='',order='',):
        self.select_param_list=select_param_list
        self.begin=begin
        self.end=end
        self.select=select
        self.order=order
        self.list_api_params={'begin':self.begin,
          'end':self.end}
        #self.req = self.ready_requests(metheds,urls=self.url,params=self.list_api_params)
        self.url = self.url + '?select=' + select+'&'+'order'+'='+order
        self.req = requests.Request(method=metheds, url=self.url, params=self.list_api_params)
        return self
    def change_url(self,code):
        print(self.url)

def ready_requests(market_options,filter_options,select_param_list,order_parm=order_params):#准备查询参数

    reqlist=[]
    url_obj=URL_Table(market_options)
    url_obj_list=list(filter(filter_options, url_obj.urltables))
    param_str = ','.join(select_param_list)
    for url in url_obj_list:#根据urltable表里储存的req对象为他们赋予begin  select  order等属性
        for b,e,o in order_parm:
            new_url=copy.copy(url)#注意要使用深拷贝，否则会引发问题
            new_url.ready_requests_list(begin=b, end=e, select=param_str, order=o,select_param_list=select_param_list)
            reqlist.append(new_url)
    return reqlist