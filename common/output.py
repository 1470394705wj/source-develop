import os
import time
import pandas as pd
import re
from common.constants import DATA_DIR


class Output():
    def __init__(self,reqdic):#初始化方法

        self.outtime=time.strftime('%Y-%m-%d-%H-%M-%S',time.localtime())#获得当前时间
        # self.cwd = os.getcwd()#当前工作目录
        # self.root_path = os.path.join(self.cwd, 'output')#输出目录
        self.root_path = os.path.join(DATA_DIR, 'data_test/mds_respond')#输出目录
        os.makedirs(self.root_path, exist_ok=True)#创建输出目录
        self.reqdic=reqdic
        self.market_type_list = list(set([i.market for i in self.reqdic.keys()]))#获得市场集合
        self.api_type_list=list(set([i.api_type for i in self.reqdic.keys()]))#api_type_list集合
        self.hostlist=list(set([re.sub(r'(http:\/\/)', '' , i.host).replace(':','_')  for i in self.reqdic.keys()]))#host集合
        self.creat_folder()#调用递归创建方法
        self.creat_excle()#创建excle方法

    def write_cfg_log(self,path,filenames,text):#写日志
        with open(os.path.join(path,f'{filenames}.txt'),'a+',encoding='utf8') as f:
            text+='\n'
            f.writelines(text)

    def creat_folder(self):#创建目录树方法，递归的创建目录
        for (dirpath, dirnames, filenames) in os.walk(self.root_path):#多层次递归写入创建并目录
            for m in self.market_type_list:
                marketpath = os.path.join(self.root_path,m)
                time_path=os.path.join(marketpath,self.outtime)
                os.makedirs(time_path, exist_ok=True)
                for host_s in self.hostlist:
                    h_path = os.path.join(time_path, host_s)
                    for i in self.api_type_list:
                        os.makedirs(os.path.join(h_path, i), exist_ok=True)

    def data_processing(self,res,col):#给文件加上列头，进行数据处理
        json_text = res.json()['list']
        df = pd.DataFrame(json_text)
        try:
         df.columns = col

         return df
        except:
            self.error_log(self.time_path, res.status_code, res.url)
            #print(res.url)

    def creat_excle(self):#写入excle方法
        self.output_catalogue = set({})#存储写入目录
        for req_obj,res_obj in self.reqdic.items():
            host=re.sub(r'(http:\/\/)', '', req_obj.host).replace(':', '_')
            begin = req_obj.begin
            end = req_obj.end
            order = req_obj.order
            sub_type = req_obj.sub_type
            mk_path = os.path.join(self.root_path, req_obj.market)
            self.time_path = os.path.join(mk_path, self.outtime)
            host_path = os.path.join(self.time_path, host)
            type_path = os.path.join(host_path, req_obj.api_type)
            #-------------------------------
            if res_obj.status_code==200:#请求正常
                for (dirpath, dirnames, filenames) in os.walk(self.root_path):#多层次递归文件

                    if type_path==dirpath:
                        df=self.data_processing(res_obj,req_obj.select_param_list)#创建文件
                        df.to_csv(
                            fr'{dirpath}/{req_obj.version}_{req_obj.market}_{req_obj.api_type}_{req_obj.belong_to_types}_{sub_type}_begin={begin}_end={end}_order={order}.csv',index=False)

                        self.output_catalogue.add(host_path)
                    if (dirpath==mk_path) and (host_path not in self.output_catalogue):#写配置
                        filenames=req_obj.market+'_'+self.outtime[0:10]
                        self.write_cfg_log(dirpath,filenames,host_path)
            else:#异常写入异常log
                self.error_log(self.time_path,res_obj.status_code,res_obj.url)

                #
    def error_log(self,path,code,errlog):#日志写入方法
        with open(os.path.join(path,'error.txt'),'a+',encoding='utf8') as f:
            f.writelines(f'错误code:{code}\n'
                         f'错误url:{errlog}\n'
                         f'****************************\n')
