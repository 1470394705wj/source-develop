"""
ModuleName: data_test_base
Description:
date: 2022/9/15 9:29
@author Sylar
@version 1.0
@since Python 3.9
"""
import os
import socket
import datacompy
import pandas as pd
import plotly.io as pio
import plotly.graph_objs as go

from typing import Union
from common.public_api import resetDir


class DataTestBase:
    defaultFileEncoding = ''
    defaultChunkSize = 0
    logUtils = None
    logTemplate = {
        '_dataTime': None,
        '_hostName': 'data_test_host',
        '_hostIp': socket.gethostbyname(socket.gethostname()),
        '_metric': None
    }

    def get_filtered_df_from_single_entity(self, file_path: Union[str, os.PathLike[str]],
                                           usecols: list = None, dtype: dict = None,
                                           stop_iteration_expr: str = '', drop_redundant_expr: str = '',
                                           drop_dp_kwargs: dict = None
                                           ) -> pd.DataFrame or None:
        if drop_dp_kwargs is None:
            drop_dp_kwargs = {}

        temp = []
        for chunk in pd.read_csv(file_path, usecols=usecols, dtype=dtype, encoding=self.defaultFileEncoding,
                                 low_memory=False, chunksize=self.defaultChunkSize):
            if stop_iteration_expr and exec(stop_iteration_expr):
                break
            if drop_redundant_expr:
                chunk.drop(eval(drop_redundant_expr), inplace=True)
            if drop_dp_kwargs:
                chunk.drop_duplicates(**drop_dp_kwargs, inplace=True)
            temp.append(chunk)

        if temp:
            df = pd.concat(temp, ignore_index=True)
            if drop_dp_kwargs:
                df.drop_duplicates(**drop_dp_kwargs, inplace=True)
            return df
        else:
            return None

    def verify_2df_equal(self, df_standard: pd.DataFrame, df_compare: pd.DataFrame,
                         compare_report_path: Union[str, os.PathLike[str]],
                         ignore_uniq_rows: bool = False, **kwargs) -> bool:
        resetDir(compare_report_path)

        compare = datacompy.Compare(df_standard, df_compare, **kwargs)

        # 输出比对结果报告到文件
        with open(file=os.path.join(compare_report_path, 'compare_summary.txt'), mode='w') as f:
            f.write(compare.report())
        # 如果比对结果存在不匹配的数据则输出到 csv
        if not compare.all_mismatch().empty:
            compare.all_mismatch().to_csv(os.path.join(compare_report_path, 'all_mismatch.csv'),
                                          index=False, encoding=self.defaultFileEncoding)
        # 如果比对结果两路数据存在各自独有的数据则输出到 csv
        if not compare.df1_unq_rows.empty:
            compare.df1_unq_rows.to_csv(os.path.join(compare_report_path, 'df_standard_unique_rows.csv'),
                                        index=False, encoding=self.defaultFileEncoding)
        if not compare.df2_unq_rows.empty:
            compare.df2_unq_rows.to_csv(os.path.join(compare_report_path, 'df_compared_unique_rows.csv'),
                                        index=False, encoding=self.defaultFileEncoding)
        if ignore_uniq_rows:
            return compare.intersect_rows_match()
        else:
            return compare.matches()

    @staticmethod
    def draw_line_chart_according_to_traces(traces: list[go.Scatter], output_file_path: Union[str, os.PathLike[str]],
                                            **update_layout_kwargs) -> bool:
        # noinspection PyBroadException
        try:
            # 执行绘图
            fig = go.Figure(traces)
            # 更新布局(标题，横纵坐标轴标签等)
            if update_layout_kwargs:
                fig.update_layout(**update_layout_kwargs)
            # 创建输出路径的父目录
            os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
            # 输出 html 文件
            pio.write_html(fig, output_file_path)
        except Exception:
            return False
        else:
            return True
