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

from common.constants import BASE_DATA_DIR, LOG_DIR
from common.log_utils import LogUtils
from common.yaml_utils import YamlUtils
from common.dce_module import DCEModule
from common.dce_test_base import DCETestBase
from common.remote_manage_utils import RemoteManageUtils


# 测试会话夹具
@pytest.fixture(scope='session')
def fixture_session():
    # 初始化 log_utils 对象并赋值给 TestBase 类的 logUtils 属性
    log_utils = LogUtils(name='dce_test',
                         info_file=os.path.join(LOG_DIR, 'app_test/dce/info.log'),
                         error_file=os.path.join(LOG_DIR, 'app_test/dce/error.log'))
    DCETestBase.logUtils = log_utils
    # 初始化 rm_utils 对象并赋值给 DCEModule 类的 rmUtils 属性
    rm_utils = RemoteManageUtils(host=DCEModule.hostIp)
    DCEModule.rmUtils = rm_utils
    # 根据从 dce_modules_params.yml 中读取的 module_params 生成 key=moduleName: value=DCEModule() 的字典 dce_modules
    dce_modules = {module_params.get('moduleName'): DCEModule(module_params)
                   for module_params in
                   YamlUtils(os.path.join(BASE_DATA_DIR, 'app_test/dce/dce_modules_params.yml')).get_data()}
    # 执行 shell 命令修改服务器的 bash 环境变量中的 dceHome 为待测试程序所在目录
    rm_utils.exec_cmd(f"sed -i 's#/level2/dce#{DCEModule.dceHome}#' ~/.bash_profile")
    yield dce_modules
    # 测试执行结束后将环境变量中的 dceHome 改回来并关闭 rm_utils 和 log_utils
    rm_utils.exec_cmd(f"sed -i 's#{DCEModule.dceHome}#/level2/dce#' ~/.bash_profile")
    rm_utils.close()
    log_utils.close()
