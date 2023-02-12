"""
ModuleName: conftest
Description:
date: 2022/5/11 10:37
@author Sylar
@version 1.0
@since Python 3.9
"""
import os
import pytest

from common.constants import LOG_DIR
from common.log_utils import LogUtils
from common.data_test_base import DataTestBase


# 测试会话夹具
@pytest.fixture(scope='session', autouse=True)
def fixture_session():
    # 初始化 log_utils 对象并赋值给 TestBase 类的 logUtils 属性
    log_utils = LogUtils(name='mds_respond_test',
                         info_file=os.path.join(LOG_DIR, 'data_test/mds_respond/info.log'),
                         error_file=os.path.join(LOG_DIR, 'data_test/mds_respond/error.log'),
                         alarm_file=os.path.join(LOG_DIR, 'data_test/mds_respond/alarm.log'))
    DataTestBase.logUtils = log_utils
    yield
    # 测试执行结束后将环境变量中的 dceHome 改回来并关闭 rm_utils 和 log_utils
    log_utils.close()
