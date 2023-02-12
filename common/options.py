from  gevent import monkey,spawn,wait
import copy
from base_data.data_test.mds_respond.api_lib.list_api  import *
from common.output import Output
monkey.patch_all()

def sh1(x):#筛选器
    return x.market=='sh1'
def sh2(x):
    return x.market=='sh2'
def sz1(x):
    return x.market=='sz1'
def sz2(x):
    return x.market=='sz2'

def f_exchange_self_v2(x):#对url进行筛选-筛选器
    return (x.version=='v2' and x.type=='exchange') or (x.type=='self' and x.version=='v2')

def f_block_options(x):#对url进行筛选-筛选器
    return x.type=='block'

def f_exchange_self_v1(x):#对url进行筛选-筛选器
    return (x.version=='v1' and x.type=='exchange') or (x.type=='self' and x.version=='v1')


def options(mk):
    res=[]
    if mk=='sh1':
        res_sh1=ready_requests('上海市场', f_exchange_self_v1, exchange_self_v1.values())
        res_sh2=ready_requests('沪深共通', f_exchange_self_v1, exchange_self_v1.values())
        res_sh3 = ready_requests('上海市场', f_exchange_self_v2, exchange_self_v2.values())
        res_sh4 = ready_requests('沪深共通', f_block_options, block_v1_v2.values())
        res_sh5 = ready_requests('沪深共通', f_exchange_self_v2, exchange_self_v2.values())
        res=list(filter(sh1,(res_sh1+res_sh2+res_sh3+res_sh4+res_sh5)))
    elif mk=='sh2':
        if mk == 'sh2':
            res_sh1 = ready_requests('上海市场', f_exchange_self_v1, exchange_self_v1.values())
            res_sh2 = ready_requests('沪深共通', f_exchange_self_v1, exchange_self_v1.values())
            res_sh3 = ready_requests('上海市场', f_exchange_self_v2, exchange_self_v2.values())
            res_sh4 = ready_requests('沪深共通', f_block_options, block_v1_v2.values())
            res_sh5 = ready_requests('沪深共通', f_exchange_self_v2, exchange_self_v2.values())
            res = list(filter(sh2, (res_sh1 + res_sh2 + res_sh3 + res_sh4 + res_sh5)))
    elif mk=='sz1':
        res_sh1 = ready_requests('深圳市场', f_exchange_self_v1, exchange_self_v1.values())
        res_sh2 = ready_requests('沪深共通', f_exchange_self_v1, exchange_self_v1.values())
        res_sh3 = ready_requests('深圳市场', f_exchange_self_v2, exchange_self_v2.values())
        res_sh4 = ready_requests('沪深共通', f_block_options, block_v1_v2.values())
        res_sh5 = ready_requests('沪深共通', f_exchange_self_v2, exchange_self_v2.values())
        res = list(filter(sz1, (res_sh1 + res_sh2 + res_sh3 + res_sh4 + res_sh5)))
    elif mk=='sz2':
        res_sh1 = ready_requests('深圳市场', f_exchange_self_v1, exchange_self_v1.values())
        res_sh2 = ready_requests('沪深共通', f_exchange_self_v1, exchange_self_v1.values())
        res_sh3 = ready_requests('深圳市场', f_exchange_self_v2, exchange_self_v2.values())
        res_sh4 = ready_requests('沪深共通', f_block_options, block_v1_v2.values())
        res_sh5 = ready_requests('沪深共通', f_exchange_self_v2, exchange_self_v2.values())
        res = list(filter(sz2, (res_sh1 + res_sh2 + res_sh3 + res_sh4 + res_sh5)))
    elif mk=='all':
        #sz
        res_sh1 = ready_requests('深圳市场', f_exchange_self_v1, exchange_self_v1.values())
        res_sh2 = ready_requests('深圳市场', f_exchange_self_v2, exchange_self_v2.values())
        #-------------------------------------------
        #sz&sh
        res_sh3 = ready_requests('沪深共通', f_exchange_self_v1, exchange_self_v1.values())
        res_sh4 = ready_requests('沪深共通', f_block_options, block_v1_v2.values())
        res_sh5 = ready_requests('沪深共通', f_exchange_self_v2, exchange_self_v2.values())
        #-----------------------
        #sh
        res_sh6=ready_requests('上海市场', f_exchange_self_v1, exchange_self_v1.values())
        res_sh7 = ready_requests('上海市场', f_exchange_self_v2, exchange_self_v2.values())
        #-------------------
        res = (res_sh1 + res_sh2 + res_sh3 + res_sh4 + res_sh5+res_sh6+res_sh7)
    return res

if __name__ == "__main__":
    op = options('all')
    resdics = {}
    #print(op)
    def sends(i):
        async_io_result=i.requests_send()
        resdics[i] = async_io_result
    for i in op:
        spawn(sends,i)
    wait()
    out = Output(resdics)

