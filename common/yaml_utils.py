"""
ModuleName: yaml_utils
Description: Yaml 工具类，提供对 Yaml 文件的读取功能
date: 2022/5/10 14:22
@author Sylar
@version 1.0
@since Python 3.9
"""
import yaml


class YamlUtils:
    def __init__(self, file_path: str, encoding='utf8'):
        """
        根据传入的文件路径初始化 YamlUtils 实例，读取文件内容至 self._datas
        :param file_path: yaml 文件路径
        """
        self._filePath = file_path
        with open(file_path, mode='r', encoding=encoding) as fr:
            self._datas = yaml.safe_load(fr)

    def save(self, file_path: str = None):
        """
        通过传入的 file_path 或 self._filePath 创建文件流，并将 self._datas 写入该流
        :param file_path: 文件的保存路径，如果不传入则默认保存至 self._filePath
        """
        with open((file_path or self._filePath), mode='w', encoding='utf8') as fw:
            yaml.safe_dump(self._datas, fw, allow_unicode=True)

    def get_data(self, begin_id: int = None, end_id: int = None, step: int = 1):
        """
        返回 self._datas 中的数据，为了方便 yaml 中列表数据的取用，提供按 id 执行的切片或选取
        :param begin_id: 仅当数据为列表时有效，本参数为需要获取的第一条数据的 data_id，不传入则默认从列表第一条数据开始获取
        :param end_id: 仅当数据为列表时有效，本参数为需要获取的最后一条数据的 data_id，不传入则默认获取到列表的最后一条数据
        :param step: 仅当数据为列表时有效，本参数为获取数据时在 begin_id 到 end_id 之间采样的步长
        :return: 返回的 dict 数据或者 list 数据
        """
        if isinstance(self._datas, list):
            # 根据用户传入的 begin_id 和 end_id 预处理 index
            # 默认为 None，如果用户传入了 begin_id 且大于 1，则使用用户传入的 begin_id - 1 作为 begin_index
            begin_index = begin_id - 1 if (begin_id and begin_id > 1) else None
            # 如果用户没有传入则直接截取至末尾，如果用户有传入，由于 slice[b, e)，所以直接按 end_id 截取即可得到想要的切片
            end_index = end_id

            return self._datas[begin_index: end_index: step]
        else:
            return self._datas
