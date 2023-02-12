"""
ModuleName: dce_modules
Description:
date: 2022/8/2 10:28
@author Sylar
@version 1.0
@since Python 3.9
"""
import os
import re

from time import sleep
from typing import Literal
from datetime import date, datetime, timedelta
from common.constants import BASE_DATA_DIR
from common.dce_test_base import test_config


class DCEModule:
    _validRunTypes = Literal['plain', 'load', 'script']
    _validProcessTypes = Literal['module', 'load']

    dateStr = date.today().strftime('%Y%m%d')
    hostIp = test_config.get('hostIp')
    dceHome = test_config.get('dceHome')
    startScript = f'{dceHome}/script/dce_start.sh'
    stopScript = f'{dceHome}/script/dce_stop.sh'
    patternIsoDatetime = re.compile(
        r'([1-9]\d{3})-(0[1-9]|1[0-2])-(0[1-9]|[1-2]\d|3[0-1])\s([0-1]\d|20|21|22|23):([0-5]\d):([0-5]\d\.\d{3})')
    patternPid = re.compile(r'^\d+$')
    rmUtils = None

    def __init__(self, module_params: dict):
        """
        根据传入的 module_params 字典实例化 DCEModule 对象
        :param module_params: 存储模块各参数的字典
        """
        self.moduleName = module_params.get('moduleName')
        self.moduleParams = module_params
        self.localDataDir = os.path.join(BASE_DATA_DIR, f'app_test/dce/{self.moduleName}')
        self.remoteConfDir = f'{self.dceHome}/conf/{self.moduleName}'
        self.appLog = f'{self.dceHome}/log/applog/{self.moduleName}_{self.dateStr}.log'
        self.loadLog = f'{self.dceHome}/log/applog/{self.moduleName}Load_{self.dateStr}.log'
        self.alarmLog = f'{self.dceHome}/log/alarm/{self.moduleName}_{self.dateStr}.log'

    class LogLocator:
        _validLogTypes = Literal['appLog', 'loadLog', 'alarmLog']

        def __init__(self, log_type: _validLogTypes, loc_handlers: list[str], loc_range: int = 50):
            """
            辅助定位日志的数据类
            :param log_type: 日志的类型 appLog
            :param loc_handlers: 定位某条具体日志需要的处理命令列表 e.g. ['grep ERROR', 'tail -1']
            :param loc_range: 从文件末尾开始定位日志的大概范围
            """
            self.logType = log_type
            self.locHandlers = loc_handlers
            self.locRange = loc_range

    def setup(self):
        """
        模块的初始化方法，包括上传/下载文件，执行初始化命令
        """
        # 从模块参数中获取文件上传/下载的命令列表和初始化命令
        setup_fuad = self.moduleParams.get('setupFUAD')
        setup_cmd = self.moduleParams.get('setupCmd')
        # 如果该列表不为空则遍历文件上传/下载列表执行
        if setup_fuad:
            for sf in setup_fuad:
                method = sf.get('method')
                if not isinstance(method, str) or method not in ('upload', 'download'):
                    raise ValueError('文件上传下载方式传值错误！')
                if method == 'upload':
                    self.rmUtils.upload_file(eval(sf.get('localPath')), eval(sf.get('remotePath')))
                else:
                    self.rmUtils.download_file(eval(sf.get('remotePath')), eval(sf.get('localPath')))
        # 如果模块初始化命令不为空则执行该命令
        if setup_cmd:
            self.rmUtils.exec_cmd(eval(setup_cmd))

    def teardown(self):
        """
        模块的反初始化方法，包括上传/下载文件，执行反初始化命令
        """
        # 从模块参数中获取文件上传/下载的命令列表和反初始化命令
        teardown_fuad = self.moduleParams.get('teardownFUAD')
        teardown_cmd = self.moduleParams.get('teardownCmd')
        # 如果该列表不为空则遍历文件上传/下载列表执行
        if teardown_fuad:
            for tf in teardown_fuad:
                method = tf.get('method')
                if not isinstance(method, str) or method not in ('upload', 'download'):
                    raise ValueError('文件上传下载方式传值错误！')
                if method == 'upload':
                    self.rmUtils.upload_file(eval(tf.get('localPath')), eval(tf.get('remotePath')))
                else:
                    self.rmUtils.download_file(eval(tf.get('remotePath')), eval(tf.get('localPath')))
        # 如果模块反初始化命令不为空则执行该命令
        if teardown_cmd:
            self.rmUtils.exec_cmd(eval(teardown_cmd))

    def start(self, run_type: _validRunTypes, wait_secs: int or float = 0):
        """
        模块的启动方法
        :param run_type: 模块启动的模式，plain 直接启动模块进程，load 启动模块的load 进程再利用其启动模块进程
        :param wait_secs: 等待模块启动的时间
        :return: 执行启动命令后的控制台输出
        """
        if run_type == 'plain':
            start_cmd = f'{self.dceHome}/bin/dce {self.moduleName} start &'
        elif run_type == 'load':
            start_cmd = f'{self.dceHome}/bin/dce {self.moduleName}Load load &'
        else:
            start_cmd = f'sh {self.startScript} {self.moduleName} &'

        console_info = self.rmUtils.send_cmd(start_cmd)

        if wait_secs > 0:
            sleep(wait_secs)

        return console_info

    def shutdown(self, run_type: _validRunTypes, wait_secs: int or float = 0):
        """
        模块的关闭方法
        :param run_type: 模块关闭的模式，plain 直接关闭模块，load 关闭模块的load 进程并利用其关闭模块进程
        :param wait_secs: 等待模块关闭的时间
        :return: 执行关闭命令后的控制台输出
        """
        if run_type == 'plain':
            shutdown_cmd = f'{self.dceHome}/bin/dce {self.moduleName} shutdown'
            process = 'module'
        elif run_type == 'load':
            shutdown_cmd = f'{self.dceHome}/bin/dce {self.moduleName}Load unload'
            process = 'load'
        else:
            shutdown_cmd = f'sh {self.stopScript} {self.moduleName}'
            process = 'load'

        # 获取需要关闭的进程pid，只有该进程pid 存在才执行关闭操作
        process_id = self.get_pid(process)
        if self.patternPid.match(process_id):
            console_info = self.rmUtils.send_cmd(shutdown_cmd)

            if wait_secs > 0:
                sleep(wait_secs)

            return console_info

    def get_pid(self, process_type: _validProcessTypes):
        """
        获取进程的 pid
        :param process_type: 需要获取 pid 的进程，module/load
        :return: 读取对应 pid 文件后的控制台输出(如果进程存在则为 pid)
        """
        if process_type == 'module':
            get_pid_cmd = f'cat {self.dceHome}/env/{self.moduleName}_pid.txt'
        else:
            get_pid_cmd = f'cat {self.dceHome}/env/{self.moduleName}Load_pid.txt'

        console_info = self.rmUtils.exec_cmd(get_pid_cmd)
        return console_info

    def get_shmdump_info(self):
        """
        获取共享内存的信息
        :return: 执行 shmdump 命令后的控制台输出
        """
        console_info = self.rmUtils.send_cmd(f'{self.dceHome}/bin/shmdump')
        return console_info

    def locate_target_log(self, log_locator: LogLocator):
        """
        定位模块某条/某几条目标日志的方法
        :param log_locator: 用于日志定位的 LogLocator 类的实例
        :return: 定位到的某条/某几条日志的内容
        """
        if log_locator.logType == 'appLog':
            log_file = self.appLog
        elif log_locator.logType == 'loadLog':
            log_file = self.loadLog
        else:
            log_file = self.alarmLog

        # 生成获取日志的命令
        get_log_cmd = f'tail -{log_locator.locRange} {log_file}'
        if log_locator.locHandlers:
            temp = [get_log_cmd]
            temp.extend(log_locator.locHandlers)
            get_log_cmd = ' | '.join(temp)

        console_info = self.rmUtils.exec_cmd(get_log_cmd)
        return console_info

    def is_expect_log_exist(self, expect_log_info: str or re.Pattern, log_locator: LogLocator, exec_cmd_time: datetime,
                            max_diff_secs: int or float, min_diff_secs: int or float = -60):
        """
        判断预期日志是否存在的方法
        :param expect_log_info: 预期日志的包含信息
        :param log_locator: 用于日志定位的 LogLocator 类的实例
        :param exec_cmd_time: 产生目标日志的命令的执行时间
        :param max_diff_secs: 预期日志的记录时间和产生日志的命令执行时间的最大差异
        :param min_diff_secs: 预期日志的记录时间和产生日志的命令执行时间的最小差异
        :return: bool 该预期日志存在则为 True，反之则为 False
        """
        # 根据 log_locator 定位目标日志
        target_log = self.locate_target_log(log_locator)

        # 多数时候传入的最大差异值是等待启动或关闭命令执行完成的休眠时间，大多失败的用例是 0，为保证校验的合理性，在该值基础上 +5
        max_diff_secs += 5

        # 如果没有定位到目标日志则直接返回 False
        if not target_log:
            return False

        # 如果传入的预期日志的包含信息是编译过的正则表达式则使用该表达式到目标日志中进行匹配，如果匹配结果为空则直接返回 False
        if isinstance(expect_log_info, re.Pattern):
            if not expect_log_info.search(target_log):
                return False
        # 如果传入的预期日志的包含信息是字符串则该字符串内容应该是目标日志内容的子串，如果不是则直接返回 False
        else:
            if expect_log_info not in target_log:
                return False

        # 目标日志中应包含 datetime 信息，如无法通过正则匹配到则也属于异常日志，直接返回 False
        pattern_match = self.patternIsoDatetime.search(target_log)
        if not pattern_match:
            return False

        # 将从目标日志中匹配到的 datetime 字符串转换为 datetime 类型对象，和产生日志的命令执行时间进行比较
        # 如果两者的差值不在预期范围内，则该目标日志很可能非本次执行命令产生的日志，直接返回 False
        log_time = datetime.fromisoformat(pattern_match.group())
        if not timedelta(seconds=min_diff_secs) < log_time - exec_cmd_time < timedelta(seconds=max_diff_secs):
            return False

        # 如果以上校验均通过，则可以确定本次执行的命令产生了预期的日志，返回 True
        return True

    def is_process_started_right(self, process_type: _validProcessTypes, exec_start_time: datetime,
                                 wait_start_secs: int or float):
        """
        判断进程是否成功启动的方法
        :param process_type: 需要判断的进程类型
        :param exec_start_time: 执行进程启动的时间
        :param wait_start_secs: 进程成功启动需要等待的时间
        :return: bool 该进程成功启动则为 True，反之则为 False
        """
        # 尝试获取进程 pid，如果未获取到则直接返回 False
        process_id = self.get_pid(process_type)
        if not self.patternPid.match(process_id):
            return False

        # 根据进程类型执行相应的预期日志是否存在的判断，存在多个判断的话则返回与运算的结果
        if process_type == 'module':
            expect_log_info1 = f'component quotCOM@{self.moduleName} is started'
            expect_log_info2 = f'{self.moduleName} is running now.'

            check_result1 = self.is_expect_log_exist(expect_log_info1,
                                                     self.LogLocator('appLog', ['grep WARN', 'tail -1']),
                                                     exec_start_time, wait_start_secs)
            check_result2 = self.is_expect_log_exist(expect_log_info1,
                                                     self.LogLocator('alarmLog', ['tail -1']),
                                                     exec_start_time, wait_start_secs)
            check_result3 = self.is_expect_log_exist(expect_log_info2,
                                                     self.LogLocator('appLog', ['grep INFO', 'tail -1']),
                                                     exec_start_time, wait_start_secs)
            return check_result1 and check_result2 and check_result3
        else:
            expect_log_info = f'{self.moduleName}Load run'
            return self.is_expect_log_exist(expect_log_info, self.LogLocator('loadLog', ['tail -1']),
                                            exec_start_time, wait_start_secs)

    def is_process_closed_right(self, process_type: _validProcessTypes, exec_shutdown_time: datetime,
                                wait_shutdown_secs: int or float):
        """
        判断进程是否成功关闭的方法
        :param process_type: 需要判断的进程类型
        :param exec_shutdown_time: 执行进程关闭的时间
        :param wait_shutdown_secs: 进程成功关闭需要等待的时间
        :return: bool 该进程成功关闭则为 True，反之则为 False
        """
        process_id = self.get_pid(process_type)
        if self.patternPid.match(process_id):
            return False

        if process_type == 'module':
            expect_log_info1 = f'component quotCOM@{self.moduleName} is closed'
            expect_log_info2 = f'Process {self.moduleName} is shutdown!'

            check_result1 = self.is_expect_log_exist(expect_log_info1,
                                                     self.LogLocator('appLog', ['grep WARN', 'tail -1']),
                                                     exec_shutdown_time, wait_shutdown_secs)
            check_result2 = self.is_expect_log_exist(expect_log_info1,
                                                     self.LogLocator('alarmLog', ['tail -1']),
                                                     exec_shutdown_time, wait_shutdown_secs)
            check_result3 = self.is_expect_log_exist(expect_log_info2,
                                                     self.LogLocator('appLog', ['grep INFO', 'tail -1']),
                                                     exec_shutdown_time, wait_shutdown_secs)

            return check_result1 and check_result2 and check_result3
        else:
            expect_log_info = f'Process {self.moduleName}Load is shutdown!'
            return self.is_expect_log_exist(expect_log_info, self.LogLocator('loadLog', ['tail -1']),
                                            exec_shutdown_time, wait_shutdown_secs)
