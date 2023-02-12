import pandas as pd
import requests
from config.data_test.mds_respond.cfgs import *
import json
from time import sleep

class API():#封装requests
    def _printResponse(self,response):
        print('\n\n-------- HTTP response * begin -------')
        for k,v in response.headers.items():
            print(f'{k}: {v}')

        print('')

        body = response.content.decode('utf8')
        print(body)
        try:
            jsonBody = response.json()
            print(f'\n\n---- 消息体json ----\n'  )
            print(jsonBody)
        except:
            print('消息体不是json格式！！')

        print('-------- HTTP response * end -------\n\n')
    def _pretty_print_request(self,req):#打印响应
        if req.body == None:
            msgBody = ''
        else:
            msgBody = req.body
        print(
            '{}\n{}\n{}\n\n{}'.format(
                '\n\n----------- 发送请求 -----------',
                req.method + ' ' + req.url,
                '\n'.join('{}: {}'.format(k, v) for k, v in req.headers.items()),
                msgBody,
            ))
    def requests_send(self):#发送方法
        self.session = requests.Session()
        self.prepared = self.session.prepare_request(self.req)
        self.res = self.session.send(self.prepared)
        return self.res



