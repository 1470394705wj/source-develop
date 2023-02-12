"""
ModuleName: test_base
Description:
date: 2022/8/19 9:23
@author Sylar
@version 1.0
@since Python 3.9
"""
import os
import re

from typing import Literal
from common.constants import CONF_DIR
from common.yaml_utils import YamlUtils

test_config = YamlUtils(os.path.join(CONF_DIR, 'app_test/dce/dce_test_config.yml')).get_data()


class DCETestBase:
    _validExpectTypes = Literal['str', 'regex']

    testRunTypes = test_config.get('testRunTypes')
    logUtils = None
    module = None
    moduleStartTime = None
    moduleShutdownTime = None
    waitStartSecs = 0
    waitShutdownSecs = 0
    consoleInfo = ''
    shmdumpInfo = ''

    def verify_process_started(self, expect_flag: bool, expect_info: str):
        """
        进程启动后执行验证的方法，对应 verifyType 1
        :param expect_flag: 预期的状态，是否成功启动
        :param expect_info: 用于执行验证的信息，当前方法代表需要验证的进程的类型
        :return: bool 验证通过则为 True，反之则为 False
        """
        return self.module.is_process_started_right(expect_info, self.moduleStartTime,
                                                    self.waitStartSecs) == expect_flag

    def verify_process_closed(self, expect_flag: bool, expect_info: str):
        """
        进程关闭后执行验证的方法，对应 verifyType 2
        :param expect_flag: 预期的状态，是否成功关闭
        :param expect_info: 用于执行验证的信息，当前方法代表需要验证的进程的类型
        :return: bool 验证通过则为 True，反之则为 False
        """
        return self.module.is_process_closed_right(expect_info, self.moduleShutdownTime,
                                                   self.waitShutdownSecs) == expect_flag

    def verify_console_info(self, expect_flag: bool, expect_type: _validExpectTypes, expect_info: str):
        """
        验证控制台信息的方法，对应 verifyType 3
        :param expect_flag: 预期的结果，控制台信息中是否应包含预期的信息
        :param expect_type: 预期信息类型，字符串/正则表达式
        :param expect_info: 预期的信息
        :return: bool 验证通过则为 True，反之则为 False
        """
        # 预期信息中可能存在动态内容需要填充，执行验证之前尝试 eval() 识别
        try:
            eval_str = eval(expect_info)
            expect_info = eval_str
        except SyntaxError or NameError:
            pass

        if expect_type == 'regex':
            pattern_expect_type = re.compile(expect_info)
            search_res = pattern_expect_type.search(self.consoleInfo)
            if (search_res is not None) != expect_flag:
                return False
        else:
            if (expect_info in self.consoleInfo) != expect_flag:
                return False

        return True

    def verify_shmdump_info(self, expect_flag: bool, expect_type: _validExpectTypes, expect_info: str):
        """
        验证共享内存信息的方法，对应 verifyType 4
        :param expect_flag: 预期的结果，共享内存信息中是否应包含预期的信息
        :param expect_type: 预期信息类型，字符串/正则表达式
        :param expect_info: 预期的信息
        :return: bool 验证通过则为 True，反之则为 False
        """
        try:
            eval_str = eval(expect_info)
            expect_info = eval_str
        except SyntaxError or NameError:
            pass

        if expect_type == 'regex':
            pattern_expect_type = re.compile(expect_info)
            search_res = pattern_expect_type.search(self.shmdumpInfo)
            if (search_res is not None) != expect_flag:
                return False
        else:
            if (expect_info in self.shmdumpInfo) != expect_flag:
                return False

        return True

    def verify_log_info(self, expect_flag: bool, expect_type: _validExpectTypes, expect_info: str, log_locators: list):
        """
        验证日志信息的方法，对应 verifyType 5
        :param expect_flag: 预期的结果，包含预期信息的日志是否应该存在
        :param expect_type: 预期信息类型，字符串/正则表达式
        :param expect_info: 预期的信息
        :param log_locators: 用于日志定位的 DCEModule.LogLocator 类的实例列表
        :return: bool 验证通过则为 True，反之则为 False
        """
        try:
            eval_str = eval(expect_info)
            expect_info = eval_str
        except SyntaxError or NameError:
            pass

        if expect_type == 'regex':
            expect_log_info = re.compile(expect_info)
        else:
            expect_log_info = expect_info

        for log_locator in log_locators:
            if self.module.is_expect_log_exist(expect_log_info, log_locator,
                                               self.moduleStartTime, self.waitStartSecs) != expect_flag:
                return False

        return True
