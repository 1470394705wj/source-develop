"""
ModuleName: constants
Description: 常量路径管理模块
date: 2022/5/10 16:06
@author Sylar
@version 1.0
@since Python 3.9
"""
import os

# 获取当前项目目录
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# 基础数据所在路径
BASE_DATA_DIR = os.path.join(BASE_DIR, 'base_data')
LIB_DIR = os.path.join(BASE_DATA_DIR, 'lib')

# 测试用例执行文件所在路径
CASE_DIR = os.path.join(BASE_DIR, 'test_case')

# 测试数据所在路径
DATA_DIR = os.path.join(BASE_DIR, 'data')

# log 所在路径
LOG_DIR = os.path.join(BASE_DIR, 'log')
INFO_FILE = os.path.join(LOG_DIR, 'info.log')
ERROR_FILE = os.path.join(LOG_DIR, 'error.log')

# 配置文件所在路径
CONF_DIR = os.path.join(BASE_DIR, 'config')

# 测试报告所在路径
REPORT_DIR = os.path.join(BASE_DIR, 'report')
