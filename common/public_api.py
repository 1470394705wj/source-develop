"""
ModuleName: public_api
Description: 提供读取配置文件中保存的信息和修改字符串字典中的数据的API
date: 2022/5/10 15:27
@author Sylar
@version 1.0
@since Python 3.9
"""
import os
import shutil
import hashlib

from functools import reduce
from decimal import Decimal

# from common.my_requests import *
# from options import *
# from copy import copy
# from config.data_test.mds_respond.cfgs import SelfSubtype_code_Cfg


def getHashCode(content: str) -> int:
    """
    根据传入的字符串计算其哈希值(int)
    :param content: 需要计算哈希值的字符串
    :return: 哈希值(int)
    """
    count = 0
    length = len(content)
    for idx, char in enumerate(content):
        count += ord(char) * 31 ** (length - 1 - idx)
    return (count + 2 ** 31) % 2 ** 32 - 2 ** 31


def resetDir(dir_path):
    """
    重置目录，如果文件夹不存在就创建，如果文件存在就清空
    :param dir_path: 需要重置的文件夹路径
    """
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    else:
        shutil.rmtree(dir_path)
        os.makedirs(dir_path)


def nestedDictGet(nested_dict: dict, keys_by_level: list, default_value=None):
    """
    从嵌套字典中获取值
    :param nested_dict: 嵌套字典
    :param keys_by_level: 嵌套字典逐级 key 组成的列表
    :param default_value: 获取失败时的默认值
    """
    try:
        result = reduce(dict.get, keys_by_level, nested_dict)
    except TypeError:
        return default_value
    else:
        if result:
            return result
        else:
            return default_value


def convert2Decimal(num, exp: str = '0.00', rounding: str = 'ROUND_DOWN') -> Decimal:
    """
    转 Decimal，默认截取
    :param num: int, str, float, Decimal
    :param exp: 精度
    :param rounding: 圆整模式，默认趋近于零取整(截取)
    :return: Decimal
    """
    if not num:
        return Decimal('0').quantize(exp=Decimal(exp), rounding=rounding)
    if not isinstance(num, str):
        num = str(num)
    return Decimal(num).quantize(exp=Decimal(exp), rounding=rounding)


# def get_listcode_snap(SelfSubtype_code_Cfg):
#     listcode = []
#     for k, v in SelfSubtype_code_Cfg.items():
#         listcode.append(v)
#     return listcode
#
#
# def get_code(op):
#     args_dic = []
#     for i in op:
#         res = {}
#         res['host'] = i.host
#         res['markert'] = i.market
#         args_dic.append(res)
#     lists = []
#     for i in args_dic:
#         if i not in lists:
#             lists.append(i)
#     dicts = {}
#     for i in lists:
#         ##print(i)
#         for h, m in i.items():
#             activecode_url = i['host'] + "/v1/" + i["markert"] + "/list/exchange/all?select=code&order=volume,DESC"
#             activecode = requests.get(url=activecode_url)
#             try:
#                 res = activecode.json()['list']
#                 codelist = [i[0] for i in res]
#                 # print(codelist)
#                 dicts[i['markert']] = codelist
#             except:
#                 dicts[i['markert']] = None
#     return dicts


if __name__ == '__main__':
    with open(file='../base_data/original_static_file/base/TradeInformationIndex002.txt', mode='rb') as tfr:
        md5_obj = hashlib.md5(tfr.read())
        md5_code = md5_obj.hexdigest()
    print(md5_code)
    print(getHashCode(md5_code.upper()))
