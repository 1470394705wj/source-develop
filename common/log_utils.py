"""
ModuleName: logUtils
Description: 日志工具类
date: 2022/5/10 14:26
@author Sylar
@version 1.0
@since Python 3.9
"""
import os
import logging.handlers
from common.constants import INFO_FILE, ERROR_FILE

_LOGGERS = {}  # 用于存放由 LogUtils 对象生成的 Logger 对象，在 LogUtils 类不为单例设计下保证同名 Logger 对象的单例特性


class LogUtils:
    def __init__(self, name: str = None, level='INFO', info_file=INFO_FILE, error_file=ERROR_FILE, alarm_file=None):
        """
        初始化 LogUtils 实例对象，并设置 self.logger 关联的 Logger 对象
        如果传入 name 对应的 logger 已存在，则当前初始化的 LogUtils 对象引用该已存在的 logger
        :param name: 默认为 None，如不传则使用 RootLogger
        :param level: logger 的记录级别，默认为 INFO
        :param info_file: info.log 文件对象，默认为 constants.INFO_FILE
        :param error_file: error.log 文件对象，默认为 constants.ERROR_FILE
        :param alarm_file: alarm.log 文件对象，默认为 None，如不传入则不生成告警日志
        """
        if _LOGGERS.get(name) is None:  # 如果 _LOGGERS 中没有 name 对应的 logger，则生成该 logger 并关联至 self.logger
            # 根据 name 生成 logger 对象，如果 name 为 None 则返回 RootLogger
            self.logger = logging.getLogger(name)
            # 设置 self.logger 的日志记录级别
            self.logger.setLevel(level)

            # 获取 StreamHandler 对象，入参为空则该对象默认关联 sys.stderr
            sh_stderr = logging.StreamHandler()
            # 设置关联系统标准错误输出流的 sh_stderr 日志输出级别为 WARNING
            sh_stderr.setLevel('WARNING')

            # 创建日志文件父目录
            os.makedirs(os.path.split(info_file)[0], exist_ok=True)
            os.makedirs(os.path.split(error_file)[0], exist_ok=True)

            # 获取关联 info_file 文件的 TimedRotatingFileHandler 按时间分割的日志文件处理器对象
            # 设置日志分割时间单位，分割日志的单位标准，日志的最大保存数量，字符集
            fh_info = logging.handlers.TimedRotatingFileHandler(filename=info_file, when='midnight', interval=1,
                                                                backupCount=30, encoding='utf8')
            # 设置 fh_info 的日志输出级别为 INFO
            fh_info.setLevel('INFO')

            fh_error = logging.handlers.TimedRotatingFileHandler(filename=error_file, when='midnight', interval=1,
                                                                 backupCount=30, encoding='utf8')
            # 设置 fh_error 的日志输出级别为 ERROR
            fh_error.setLevel('ERROR')

            # 通过传入的格式化字符串获取日志格式器对象
            my_fmt = logging.Formatter('%(asctime)s - [%(filename)s - %(lineno)d] - %(levelname)s : %(message)s')

            # 为每个处理器设置格式器
            sh_stderr.setFormatter(my_fmt)
            fh_info.setFormatter(my_fmt)
            fh_error.setFormatter(my_fmt)

            # 添加每个处理器到 self.logger 的 handlers 列表
            self.logger.addHandler(sh_stderr)
            self.logger.addHandler(fh_info)
            self.logger.addHandler(fh_error)

            # 如果存在告警日志路径则生成对应的 handler 并添加到列表
            if alarm_file:
                os.makedirs(os.path.split(alarm_file)[0], exist_ok=True)
                fh_alarm = logging.handlers.TimedRotatingFileHandler(filename=alarm_file, when='midnight', interval=1,
                                                                     backupCount=30, encoding='utf8')
                fh_alarm.setLevel('INFO')
                self.logger.addHandler(fh_alarm)

            # 添加键值对 name, self.logger 至 _LOGGERS
            _LOGGERS[name] = self.logger
        else:  # 如果 _LOGGERS 中存在 name 对应的 logger，则直接关联该 logger 至 self.logger
            self.logger = _LOGGERS[name]

    def close(self):
        """
        手动关闭 self.logger 的 handlers 中所有 FileHandler，FileHandler.close() 会执行关闭其关联的文件流
        """
        for handler in self.logger.handlers:
            if isinstance(handler, logging.FileHandler):
                handler.close()
