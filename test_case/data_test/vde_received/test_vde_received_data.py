"""
ModuleName: test_vde_received_data
Description:
date: 2022/9/13 11:18
@author Sylar
@version 1.0
@since Python 3.9
"""
import os
import json
import re
import shutil
import time

import dask as dd
import pytest
import pandas as pd
import plotly.graph_objs as go

from datetime import datetime
from copy import copy, deepcopy
from ordered_set import OrderedSet
from common.yaml_utils import YamlUtils
from common.data_test_base import DataTestBase
from common.public_api import resetDir, convert2Decimal
from common.constants import BASE_DATA_DIR, CONF_DIR, DATA_DIR, REPORT_DIR

_vdeReceivedTestConfig = YamlUtils(
    os.path.join(CONF_DIR, 'data_test/vde_received/vde_received_test_config.yml')).get_data()


class TestVDEReceivedData(DataTestBase):
    _vdeReceivedTestBasic = YamlUtils(
        os.path.join(BASE_DATA_DIR, 'data_test/vde_received/vde_received_test_basic.yml')).get_data()
    _dfFilters = _vdeReceivedTestBasic.get('dfFilters')
    _snapDataFieldsInfo = _vdeReceivedTestBasic.get('snapDataFieldsInfo')
    _txDataFieldsInfo = _vdeReceivedTestBasic.get('txDataFieldsInfo')
    defaultFileEncoding = _vdeReceivedTestBasic.get('defaultFileEncoding')
    defaultChunkSize = _vdeReceivedTestBasic.get('defaultChunkSize')

    def _update_filtered_df_to_data_infos(self, filtered_df_type: _dfFilters.keys()):
        df_filter = self._dfFilters.get(filtered_df_type)
        df_entity_key_words = df_filter.get('dfEntityKeyWords')

        for data_info in self._data_infos:
            if filtered_df_type in data_info.keys():
                continue
            df_entity_path = os.path.join(DATA_DIR, 'data_test/vde_received', df_entity_key_words,
                                          f'{df_entity_key_words}_of_{data_info.get("dataName")}.csv')
            data_fields_info = data_info.get('dataFieldsInfo')
            comm_fields_info = data_fields_info.get('commFieldsInfo', {})
            fields_name_mapping = {k: v.get('fieldName') for k, v in comm_fields_info.items()}
            fields_dtype_mapping = {i.get('fieldName'): i.get('fieldType')
                                    for i in comm_fields_info.values() if i.get('fieldType')}

            if os.path.exists(df_entity_path):
                df = pd.read_csv(df_entity_path, usecols=data_fields_info.get('useCols'), dtype=fields_dtype_mapping,
                                 encoding=self.defaultFileEncoding, low_memory=False)
            else:
                stop_iteration_expr = ''
                drop_redundant_expr = ''
                drop_dp_kwargs = None
                if df_filter.get('stopIterationExpr'):
                    stop_iteration_expr += eval(df_filter.get('stopIterationExpr'))
                if df_filter.get('dropRedundantExpr'):
                    drop_redundant_expr += eval(df_filter.get('dropRedundantExpr'))
                if df_filter.get('dropDpKwargs'):
                    drop_dp_kwargs = deepcopy(df_filter.get('dropDpKwargs'))
                    subset = drop_dp_kwargs.get('subset')
                    if subset:
                        subset = [fields_name_mapping.get(i) for i in subset if fields_name_mapping.get(i)]
                    else:
                        subset = [fields_name_mapping.get(i)
                                  for i in self._testParams.get('primaryKeyFields') if fields_name_mapping.get(i)]
                    drop_dp_kwargs.update({'subset': subset})

                df = self.get_filtered_df_from_single_entity(data_info.get('dataPath'),
                                                             usecols=data_fields_info.get('useCols'),
                                                             dtype=fields_dtype_mapping,
                                                             stop_iteration_expr=stop_iteration_expr,
                                                             drop_redundant_expr=drop_redundant_expr,
                                                             drop_dp_kwargs=drop_dp_kwargs)
                if df is None:
                    raise RuntimeError(f'get {filtered_df_type} from raw data failed!')
                if df_entity_key_words:
                    os.makedirs(os.path.dirname(df_entity_path), exist_ok=True)
                    df.to_csv(df_entity_path, index=False, encoding=self.defaultFileEncoding)

            df.rename(columns={v: k for k, v in fields_name_mapping.items()}, inplace=True)  # 字段重命名
            # 非空数值缩放后按指定精度(圆整模式)转 Decimal
            fields_value_precision_mapping = {k: v.get('valuePrecisionExp')
                                              for k, v in comm_fields_info.items() if v.get('valuePrecisionExp')}
            for k, v in fields_value_precision_mapping.items():
                if k not in df.columns:
                    continue
                value_scaling_factor = comm_fields_info.get(k).get('valueScalingFactor', 1)
                value_rounding_mode = comm_fields_info.get(k).get('valueRoundingMode', 'ROUND_DOWN')
                df[k] = [i if pd.isna(i) else convert2Decimal(i * value_scaling_factor, v, value_rounding_mode)
                         for i in df[k]]

            data_info.update({filtered_df_type: df})

    def _compare_last_snap_from_2data(self, standard_data_info, compared_data_info) -> bool:
        standard_df_last_snap = standard_data_info.get('dfLastSnap')
        compared_df_last_snap = compared_data_info.get('dfLastSnap')
        intersection_of_columns = OrderedSet(standard_df_last_snap.columns) & OrderedSet(compared_df_last_snap.columns)
        standard_df_last_snap = standard_df_last_snap.loc[:, intersection_of_columns]
        compared_df_last_snap = compared_df_last_snap.loc[:, intersection_of_columns]

        compare_report_path = os.path.join(
            REPORT_DIR, 'data_test/vde_received/last_snap_comparison',
            f'{standard_data_info.get("dataName")}_vs_{compared_data_info.get("dataName")}')
        is_ignore_uniq_rows = self._testParams.get('ignoreUniqRows')
        log_json = copy(self.logTemplate)
        log_json['_dataTime'] = datetime.now().isoformat(sep=' ')

        try:
            assert self.verify_2df_equal(standard_df_last_snap, compared_df_last_snap, compare_report_path,
                                         ignore_uniq_rows=is_ignore_uniq_rows,
                                         join_columns=self._testParams.get('primaryKeyFields'),
                                         df1_name='standard', df2_name='compared')
        except AssertionError:
            if is_ignore_uniq_rows:
                log_json['_metric'] = ('Data verification failed! The last snap of the common security IDs in the '
                                       f'{standard_data_info.get("dataName")} and {compared_data_info.get("dataName")} '
                                       'are not identical!')
            else:
                log_json['_metric'] = ('Data verification failed! The last snap of all security IDs in the '
                                       f'{standard_data_info.get("dataName")} and {compared_data_info.get("dataName")} '
                                       'are not identical!')
            self.logUtils.logger.error(json.dumps(log_json, ensure_ascii=False))
            return False
        else:
            if is_ignore_uniq_rows:
                log_json['_metric'] = ('Data verification succeeded! The last snap of the common security IDs in the '
                                       f'{standard_data_info.get("dataName")} and {compared_data_info.get("dataName")} '
                                       'are identical!')
            else:
                log_json['_metric'] = ('Data verification failed! The last snap of all security IDs in the '
                                       f'{standard_data_info.get("dataName")} and {compared_data_info.get("dataName")} '
                                       'are identical!')
            self.logUtils.logger.info(json.dumps(log_json, ensure_ascii=False))
            return True
        finally:
            self._data_infos.clear()

    @pytest.mark.parametrize('case', [
        {
            'standardDataInfos': _vdeReceivedTestConfig.get('snapComparison').get('standardDataInfos'),
            'comparedDataInfos': i.get('comparedDataInfos'),
            'testParams': i.get('testItems').get('lastSnap')
        }
        for i in _vdeReceivedTestConfig.get('snapComparison', {}).get('testTasks', [])
        if i.get('testItems').get('lastSnap')
    ])
    def test_vde_received_last_snap_comparison(self, case):
        # 转换两个列表为 key=dataMsgType: value=dataInfo 的字典，并生成包含所有 dataMsgType 的集合
        data_msg_types = set()
        standard_data_infos = dict()
        compared_data_infos = dict()
        for data_infos_dict, data_infos_list in zip((standard_data_infos, compared_data_infos),
                                                    (case.get('standardDataInfos'), case.get('comparedDataInfos'),)):
            for data_info in data_infos_list:
                data_msg_type = data_info.get('dataMsgType')
                data_msg_types.add(data_msg_type)
                data_infos_dict.update({data_msg_type: data_info})

        # 遍历 dataMsgTypes 集合，根据 dataMsgType 从两个字典中获取 dataInfo 并为其添加 dataFieldsInfo，再添其到 self._data_infos
        self._is_case_passed = True
        self._testParams = case.get('testParams')
        self._data_infos = []
        comparison_done_msg_types = set()
        for data_msg_type in data_msg_types:
            data_fields_info = deepcopy(self._snapDataFieldsInfo.get(data_msg_type))
            comparable_fields = (OrderedSet(data_fields_info.get('readFields'))
                                 -
                                 OrderedSet(data_fields_info.get('snapComparisonIgnoreFields')))
            data_fields_info.update({'useCols': comparable_fields})
            for data_infos in (standard_data_infos, compared_data_infos):
                data_info = data_infos.get(data_msg_type)
                if not data_info:
                    continue
                if 'dataFieldsInfo' not in data_info.keys():
                    data_info.update({'dataFieldsInfo': data_fields_info})
                self._data_infos.append(data_info)

            # 如果当前 dataMsgType 只在某一个字典中出现则清空 self._data_infos 并跳过当前循环
            if len(self._data_infos) < 2:
                self._data_infos.clear()
                continue
            # 如果当前 dataMsgType 在两个字典中都出现则通过 self._data_infos 为两个 dataInfo 添加 dfLastSnap 并执行对比
            self._update_filtered_df_to_data_infos('dfLastSnap')
            if (not self._compare_last_snap_from_2data(standard_data_infos.get(data_msg_type),
                                                       compared_data_infos.get(data_msg_type))
                    and self._is_case_passed):
                self._is_case_passed = False
            # 对比完成记录当前 dataMsgType 并清空 self._data_infos 且从两个字典中分别移除当前 dataMsgType 的键值对
            comparison_done_msg_types.add(data_msg_type)
            self._data_infos.clear()
            standard_data_infos.pop(data_msg_type)
            compared_data_infos.pop(data_msg_type)

        # 从 dataMsgTypes 中移除已完成对比的 dataMsgType，并清空已完成对比的 comparisonDoneMsgTypes 集合
        data_msg_types -= comparison_done_msg_types
        comparison_done_msg_types.clear()

        # 如果配对对比完成后 dataMsgTypes 不为空，且 UA5302 存在，UA3113/3202 至少存在一个，则尝试执行L1 L2 的比对
        if data_msg_types and ('UA5302' in data_msg_types) and (data_msg_types & {'UA3113', 'UA3202'}):
            # 取出 UA5302 的 dataInfo
            is_ua5302_as_standard = 'UA5302' in standard_data_infos.keys()
            if is_ua5302_as_standard:
                ua5302_data_info = standard_data_infos.get('UA5302')
            else:
                ua5302_data_info = compared_data_infos.get('UA5302')

            for data_msg_type in ('UA3113', 'UA3202'):
                # 添加 UA5302 的 dataInfo 到 self._data_infos，再取出 UA3113/UA3202 的 dataInfo 添加到 self._data_infos
                resource_data_infos = compared_data_infos if is_ua5302_as_standard else standard_data_infos
                if data_msg_type not in resource_data_infos.keys():
                    continue
                self._data_infos.append(ua5302_data_info)
                ua3113_or_ua3202_data_info = resource_data_infos.get(data_msg_type)
                self._data_infos.append(ua3113_or_ua3202_data_info)
                self._update_filtered_df_to_data_infos('dfLastSnap')
                # 根据当前的 L2 的数据类型取部分 UA5302 的数据组成 dataInfo 进行比对
                ua5302_df_last_snap = ua5302_data_info.get('dfLastSnap')
                if data_msg_type == 'UA3113':
                    df_last_snap = ua5302_df_last_snap.drop(
                        ua5302_df_last_snap.index[[not i.startswith('0') for i in ua5302_df_last_snap['securityID']]]
                    )
                    data_name = f'{ua5302_data_info.get("dataName")}_3113_part'
                else:
                    df_last_snap = ua5302_df_last_snap.drop(
                        ua5302_df_last_snap.index[[i.startswith('0') for i in ua5302_df_last_snap['securityID']]]
                    )
                    data_name = f'{ua5302_data_info.get("dataName")}_3202_part'
                ua5302_comparable_part_data_info = {'dataName': data_name, 'dfLastSnap': df_last_snap}
                # 根据 UA5302 是否来自于 standardDataInfos 调整比对传值的顺序
                comparable_data_infos = ((ua5302_comparable_part_data_info, ua3113_or_ua3202_data_info)
                                         if is_ua5302_as_standard else
                                         (ua3113_or_ua3202_data_info, ua5302_comparable_part_data_info))
                if not self._compare_last_snap_from_2data(*comparable_data_infos) and self._is_case_passed:
                    self._is_case_passed = False
                comparison_done_msg_types.add(data_msg_type)
                self._data_infos.clear()
                resource_data_infos.pop(data_msg_type)

            # 从 dataMsgTypes 中移除已完成对比的 dataMsgType，并清空已完成对比的 comparisonDoneMsgTypes 集合
            comparison_done_msg_types.add('UA5302')
            data_msg_types -= comparison_done_msg_types
            comparison_done_msg_types.clear()

        # 如果仍有剩下 dataMsgTypes 无法对比，则直接记录日志并抛出异常终止本条用例的执行
        if data_msg_types:
            log_json = copy(self.logTemplate)
            log_json['_dataTime'] = datetime.now().isoformat(sep=' ')
            log_json['_metric'] = ('An error occurred while data verification! The remaining data {} may '
                                   'came from same data group or have different message types, '
                                   'and the last snap in these data cannot be directly compared! '
                                   'Please check the configuration of the test!').format(
                [i.get("dataName") for i in list(standard_data_infos.values()) + list(compared_data_infos.values())]
            )
            self.logUtils.logger.error(json.dumps(log_json, ensure_ascii=False))
            raise RuntimeError

        assert self._is_case_passed

    @pytest.mark.parametrize('case', [
        {
            'standardDataInfos': _vdeReceivedTestConfig.get('snapComparison').get('standardDataInfos'),
            'comparedDataInfos': i.get('comparedDataInfos'),
            'testParams': i.get('testItems').get('securityID')
        }
        for i in _vdeReceivedTestConfig.get('snapComparison', {}).get('testTasks', [])
        if i.get('testItems').get('securityID')
    ])
    def test_vde_received_security_id_comparison(self, case):
        self._data_infos = []
        standard_data_infos = case.get('standardDataInfos')
        compared_data_infos = case.get('comparedDataInfos')
        for data_infos in (standard_data_infos, compared_data_infos):
            for data_info in data_infos:
                if 'dataFieldsInfo' not in data_info.keys():
                    data_fields_info = deepcopy(self._snapDataFieldsInfo.get(data_info.get('dataMsgType')))
                    comparable_fields = (OrderedSet(data_fields_info.get('readFields'))
                                         -
                                         OrderedSet(data_fields_info.get('snapComparisonIgnoreFields')))
                    data_fields_info.update({'useCols': comparable_fields})
                    data_info.update({'dataFieldsInfo': data_fields_info})
                self._data_infos.append(data_info)

        self._testParams = case.get('testParams')
        self._update_filtered_df_to_data_infos('dfLastSnap')

        standard_data_security_ids = OrderedSet()
        compared_data_security_ids = OrderedSet()
        for security_ids, data_infos in zip((standard_data_security_ids, compared_data_security_ids),
                                            (standard_data_infos, compared_data_infos)):
            temp = set()
            for data_info in data_infos:
                temp.update(data_info.get('dfLastSnap')['securityID'].values)

            security_ids.update(sorted(temp))

        intersection_of_security_ids = standard_data_security_ids & compared_data_security_ids
        all_unique_security_id_output_dir = os.path.join(
            REPORT_DIR, 'data_test/vde_received/security_id_comparison',
            f'{standard_data_infos[0].get("dataName")}_etc_vs_{compared_data_infos[0].get("dataName")}_etc')
        log_json = copy(self.logTemplate)
        log_json['_dataTime'] = datetime.now().isoformat(sep=' ')

        try:
            assert standard_data_security_ids == compared_data_security_ids
        except AssertionError as e:
            resetDir(all_unique_security_id_output_dir)
            standard_data_uniq_security_ids = standard_data_security_ids - intersection_of_security_ids
            compared_data_uniq_security_ids = compared_data_security_ids - intersection_of_security_ids
            all_uniq_security_id = pd.DataFrame(
                {'standardDataUniqSecurityID': pd.Series(standard_data_uniq_security_ids, dtype='string'),
                 'comparedDataUniqSecurityID': pd.Series(compared_data_uniq_security_ids, dtype='string')}
            )
            all_uniq_security_id.to_csv(os.path.join(all_unique_security_id_output_dir, 'all_unique_security_id.csv'),
                                        index=False, encoding=self.defaultFileEncoding)
            log_json['_metric'] = ('Data verification failed! The security IDs in the '
                                   f'{[i.get("dataName") for i in standard_data_infos]} and '
                                   f'{[i.get("dataName") for i in compared_data_infos]} are not identical! '
                                   f'The count of security IDs in the first data group is '
                                   f'{len(standard_data_security_ids)}. But in the second data group, '
                                   f'this number is {len(compared_data_security_ids)}. Check the '
                                   'all_uniq_security_id.csv if u want to know the details of the difference.')
            self.logUtils.logger.error(json.dumps(log_json, ensure_ascii=False))
            raise e
        else:
            shutil.rmtree(all_unique_security_id_output_dir, ignore_errors=True)
            log_json['_metric'] = ('Data verification succeeded! The security IDs in The '
                                   f'{[i.get("dataName") for i in standard_data_infos]} and '
                                   f'{[i.get("dataName") for i in compared_data_infos]} are identical! '
                                   'The count of security IDs in both data group is '
                                   f'{len(intersection_of_security_ids)}.')
            self.logUtils.logger.info(json.dumps(log_json, ensure_ascii=False))

    def _update_df_comparable_iopv_to_data_infos(self):
        self._update_filtered_df_to_data_infos('dfFundIOPVUniqSnap')

        for data_info in self._data_infos:
            if 'dfComparableIOPV' in data_info.keys():
                continue
            df_fund_iopv_uniq_snap = data_info.get('dfFundIOPVUniqSnap')
            if 'lowPrecisionIOPV' not in df_fund_iopv_uniq_snap.columns:
                # 低精度 iopv 由高精度 iopv (非空)四舍五入为 3 位 Decimal
                df_fund_iopv_uniq_snap['lowPrecisionIOPV'] = [i if pd.isna(i)
                                                              else convert2Decimal(i, '0.000', 'ROUND_HALF_UP')
                                                              for i in df_fund_iopv_uniq_snap['highPrecisionIOPV']]
            df_comparable_iopv = df_fund_iopv_uniq_snap.loc[:, ['securityID', 'highPrecisionIOPV', 'lowPrecisionIOPV']]
            data_info.update({'dfComparableIOPV': df_comparable_iopv})

    @pytest.mark.parametrize('case', [
        {
            'standardDataInfos': _vdeReceivedTestConfig.get('snapComparison').get('standardDataInfos'),
            'comparedDataInfos': i.get('comparedDataInfos'),
            'testParams': i.get('testItems').get('fundIOPVPrecision')
        }
        for i in _vdeReceivedTestConfig.get('snapComparison', {}).get('testTasks', [])
        if i.get('testItems').get('fundIOPVPrecision')
    ])
    def test_vde_received_fund_iopv_precision_comparison(self, case):
        self._data_infos = []
        standard_data_infos = case.get('standardDataInfos')
        compared_data_infos = case.get('comparedDataInfos')
        for data_infos in (standard_data_infos, compared_data_infos):
            for data_info in data_infos:
                data_msg_type = data_info.get('dataMsgType')
                if data_msg_type not in ('UA5302', 'UA3202'):
                    continue
                if 'dataFieldsInfo' not in data_info.keys():
                    data_fields_info = deepcopy(self._snapDataFieldsInfo.get(data_info.get('dataMsgType')))
                    comparable_fields = (OrderedSet(data_fields_info.get('readFields'))
                                         -
                                         OrderedSet(data_fields_info.get('snapComparisonIgnoreFields')))
                    data_fields_info.update({'useCols': comparable_fields})
                    data_info.update({'dataFieldsInfo': data_fields_info})
                self._data_infos.append(data_info)

        log_json = copy(self.logTemplate)
        if len(self._data_infos) > 2:
            log_json['_dataTime'] = datetime.now().isoformat(sep=' ')
            log_json['_metric'] = ('An error occurred while data verification! '
                                   'A group of data cannot have both UA5302 and UA3202 message types! '
                                   'Please check the configuration of the test!')
            self.logUtils.logger.error(json.dumps(log_json, ensure_ascii=False))
            raise RuntimeError

        self._testParams = case.get('testParams')
        self._update_df_comparable_iopv_to_data_infos()

        standard_data_info = tuple(
            filter(lambda x: x.get('dataMsgType') in ('UA5302', 'UA3202'), standard_data_infos)
        )[0]
        compared_data_info = tuple(
            filter(lambda x: x.get('dataMsgType') in ('UA5302', 'UA3202'), compared_data_infos)
        )[0]
        compare_report_path = os.path.join(
            REPORT_DIR, 'data_test/vde_received/fund_iopv_precision_comparison',
            f'{standard_data_info.get("dataName")}_vs_{compared_data_info.get("dataName")}')
        is_ignore_uniq_rows = self._testParams.get('ignoreUniqRows')
        log_json['_dataTime'] = datetime.now().isoformat(sep=' ')

        try:
            assert self.verify_2df_equal(standard_data_info.get('dfComparableIOPV'),
                                         compared_data_info.get('dfComparableIOPV'),
                                         compare_report_path, ignore_uniq_rows=is_ignore_uniq_rows,
                                         join_columns=self._testParams.get('primaryKeyFields'),
                                         df1_name='standard', df2_name='compared')
        except AssertionError as e:
            if is_ignore_uniq_rows:
                log_json['_metric'] = ('Data verification failed! '
                                       'The common fund IOPV values of 2 kinds of precision in the '
                                       f'{standard_data_info.get("dataName")} and {compared_data_info.get("dataName")} '
                                       'are not identical!')
            else:
                log_json['_metric'] = ('Data verification failed! '
                                       'The all fund IOPV values of 2 kinds of precision in the '
                                       f'{standard_data_info.get("dataName")} and {compared_data_info.get("dataName")} '
                                       'are not identical!')
            self.logUtils.logger.error(json.dumps(log_json, ensure_ascii=False))
            raise e
        else:
            if is_ignore_uniq_rows:
                log_json['_metric'] = ('Data verification succeeded! '
                                       'The common fund IOPV values of 2 kinds of precision in the '
                                       f'{standard_data_info.get("dataName")} and {compared_data_info.get("dataName")} '
                                       'are identical!')
            else:
                log_json['_metric'] = ('Data verification succeeded! '
                                       'The all fund IOPV values of 2 kinds of precision in the '
                                       f'{standard_data_info.get("dataName")} and {compared_data_info.get("dataName")} '
                                       'are identical!')
            self.logUtils.logger.info(json.dumps(log_json, ensure_ascii=False))

    def _update_df_sampled_iopv_trends_to_data_infos(self):
        self._update_filtered_df_to_data_infos('dfSampledAllSnap')

        for data_info in self._data_infos:
            if 'dfSampledIOPVTrends' in data_info.keys():
                continue
            df_sampled_all_snap = deepcopy(data_info.get('dfSampledAllSnap'))
            data_fields_info = data_info.get('dataFieldsInfo')
            comm_fields_info = data_fields_info.get('commFieldsInfo')
            data_datetime_format = '%Y%m%d' + comm_fields_info.get('dataTime').get('timeFormat')
            # 丢弃非基金代码的所有快照
            df_sampled_all_snap.drop(
                df_sampled_all_snap.index[[not i.startswith('5') for i in df_sampled_all_snap['securityID']]],
                inplace=True
            )
            # 解析行情数据时间为 datetime 对象并作为新列 dataDatetime 添加到 df
            df_sampled_all_snap['dataDatetime'] = [
                datetime.strptime(self._trade_date + i.rjust(8, '0').removeprefix('00').ljust(8, '0'),
                                  data_datetime_format)
                for i in df_sampled_all_snap['dataTime']
            ]
            # 丢弃非统计时间段内的数据
            df_sampled_all_snap.drop(df_sampled_all_snap.index[
                                         (df_sampled_all_snap['dataDatetime'] < self._statistical_start_datetime)
                                         |
                                         (df_sampled_all_snap['dataDatetime'] > self._statistical_end_datetime)
                                         ], inplace=True)
            df_sampled_iopv_fields = OrderedSet(['securityID', 'dataDatetime', 'highPrecisionIOPV', 'lowPrecisionIOPV'])
            df_sampled_iopv_fields &= OrderedSet(df_sampled_all_snap.columns)
            df_sampled_iopv = df_sampled_all_snap.loc[:, df_sampled_iopv_fields]

            df_sampled_iopv_trends = {}
            for security_id, df_iopv in df_sampled_iopv.groupby(['securityID']):
                df_iopv_trend = df_iopv.set_index('dataDatetime')
                df_sampled_iopv_trends.update({security_id: df_iopv_trend})

            data_info.update({'dfSampledIOPVTrends': df_sampled_iopv_trends})

    @pytest.mark.parametrize('case', [
        {
            'dataInfos': _vdeReceivedTestConfig.get('snapStatistic').get('dataInfos'),
            'tradeDate': _vdeReceivedTestConfig.get('snapStatistic').get('tradeDate'),
            'sampleSecurityIDs': _vdeReceivedTestConfig.get('snapStatistic').get('sampleSecurityIDs'),
            'testParams': v
        }
        for k, v in _vdeReceivedTestConfig.get('snapStatistic', {}).get('testItems', {}).items()
        if k == 'sampledIOPV'
    ])
    def test_vde_received_sampled_iopv_statistic(self, case):
        self._data_infos = list(filter(lambda x: x.get('dataMsgType') in ('UA5302', 'UA3202'), case.get('dataInfos')))
        for data_info in self._data_infos:
            if 'dataFieldsInfo' in data_info.keys():
                continue
            data_fields_info = deepcopy(self._snapDataFieldsInfo.get(data_info.get('dataMsgType')))
            statistic_fields = (OrderedSet(data_fields_info.get('readFields'))
                                -
                                OrderedSet(data_fields_info.get('snapStatisticIgnoreFields')))
            data_fields_info.update({'useCols': statistic_fields})
            data_info.update({'dataFieldsInfo': data_fields_info})

        self._trade_date = case.get('tradeDate')
        self._sample_security_ids = case.get('sampleSecurityIDs')
        self._testParams = case.get('testParams')
        self._statistical_start_time = self._testParams.get('statisticalTimeInterval').get('startTime') + '00'
        self._statistical_end_time = self._testParams.get('statisticalTimeInterval').get('endTime') + '00'
        self._statistical_start_datetime = datetime.strptime(self._trade_date + self._statistical_start_time,
                                                             '%Y%m%d%H%M%S%f')
        self._statistical_end_datetime = datetime.strptime(self._trade_date + self._statistical_end_time,
                                                           '%Y%m%d%H%M%S%f')

        self._update_df_sampled_iopv_trends_to_data_infos()

        self._is_case_passed = True
        valid_security_ids = list(filter(lambda x: x.startswith('5'), self._sample_security_ids))
        drawing_failed_security_ids = []
        for security_id in valid_security_ids:
            traces = []
            for data_info in self._data_infos:
                df_iopv_trend = data_info.get('dfSampledIOPVTrends', {}).get(security_id)
                if df_iopv_trend is None:
                    continue
                trace_high_precision = go.Scatter(
                    x=df_iopv_trend.index,
                    y=df_iopv_trend.highPrecisionIOPV,
                    name=f'{data_info.get("dataName")}_high_precision',
                    mode='lines+markers'
                )
                traces.append(trace_high_precision)
                if 'lowPrecisionIOPV' not in df_iopv_trend.columns:
                    continue
                trace_low_precision = go.Scatter(
                    x=df_iopv_trend.index,
                    y=df_iopv_trend.lowPrecisionIOPV,
                    name=f'{data_info.get("dataName")}_low_precision',
                    mode='lines+markers'
                )
                traces.append(trace_low_precision)

            output_file_path = os.path.join(REPORT_DIR,
                                            'data_test/vde_received/sampled_iopv_statistic', self._trade_date,
                                            f'{security_id}_iopv_statistic_of_{self._trade_date}_'
                                            f'{self._statistical_start_time[:4]}_{self._statistical_end_time[:4]}.html')
            if not self.draw_line_chart_according_to_traces(traces, output_file_path,
                                                            title=f'{security_id} IOPV走势图',
                                                            xaxis_title='行情时间',
                                                            yaxis_title='IOPV'):
                if self._is_case_passed:
                    self._is_case_passed = False
                drawing_failed_security_ids.append(security_id)

        log_json = copy(self.logTemplate)
        log_json['_dataTime'] = datetime.now().isoformat(sep=' ')

        try:
            assert self._is_case_passed
        except AssertionError as e:
            log_json['_metric'] = ('Data statistic failed! Failed to draw the line chart of IOPV trend '
                                   f'for the security IDs as {drawing_failed_security_ids}! '
                                   'Please check the configuration or the data of the test!')
            self.logUtils.logger.error(json.dumps(log_json, ensure_ascii=False))
            raise e
        else:
            log_json['_metric'] = ('Data statistic succeeded! Succeeded in drawing the line chart of IOPV trend '
                                   f'for the security IDs as {valid_security_ids}')
            self.logUtils.logger.info(json.dumps(log_json, ensure_ascii=False))

    def _update_df_sampled_last_price_trends_to_data_infos(self):
        self._update_filtered_df_to_data_infos('dfSampledAllSnap')

        for data_info in self._data_infos:
            if 'dfSampledLastPriceTrends' in data_info.keys():
                continue
            df_sampled_all_snap = deepcopy(data_info.get('dfSampledAllSnap'))
            data_fields_info = data_info.get('dataFieldsInfo')
            comm_fields_info = data_fields_info.get('commFieldsInfo')
            data_datetime_format = '%Y%m%d' + comm_fields_info.get('dataTime').get('timeFormat')
            # 解析行情数据时间为 datetime 对象并作为新列 dataDatetime 添加到 df
            df_sampled_all_snap['dataDatetime'] = [
                datetime.strptime(self._trade_date + i.rjust(8, '0').removeprefix('00').ljust(8, '0'),
                                  data_datetime_format)
                for i in df_sampled_all_snap['dataTime']
            ]
            # 丢弃非统计时间段内的数据
            df_sampled_all_snap.drop(df_sampled_all_snap.index[
                                         (df_sampled_all_snap['dataDatetime'] < self._statistical_start_datetime)
                                         |
                                         (df_sampled_all_snap['dataDatetime'] > self._statistical_end_datetime)
                                         ],
                                     inplace=True)
            # 截取统计最新价需要的字段生成 dfSampledLastPrice
            df_sampled_last_price_fields = OrderedSet(['securityID', 'dataDatetime', 'lastPrice', 'bid1Price'])
            df_sampled_last_price_fields &= OrderedSet(df_sampled_all_snap.columns)
            df_sampled_last_price = df_sampled_all_snap.loc[:, df_sampled_last_price_fields]
            # 替换开盘前股票和基金的现价为买1价格
            if 'bid1Price' in df_sampled_all_snap.columns:
                df_sampled_last_price['lastPrice'] = [
                    i.lastPrice
                    if i.dataDatetime >= self._trade_start_datetime or i.securityID.startswith('0') else i.bid1Price
                    for i in df_sampled_last_price.itertuples()
                ]
            if self._testParams.get('ignore0Values'):  # 丢弃最新价为零的快照
                df_sampled_last_price.drop(df_sampled_last_price.index[df_sampled_last_price['lastPrice'] == 0],
                                           inplace=True)

            df_sampled_last_price_trends = {}
            for security_id, df_last_price in df_sampled_last_price.groupby(['securityID']):
                df_last_price_trend = df_last_price.set_index('dataDatetime')
                df_sampled_last_price_trends.update({security_id: df_last_price_trend})

            data_info.update({'dfSampledLastPriceTrends': df_sampled_last_price_trends})

    @pytest.mark.parametrize('case', [
        {
            'dataInfos': _vdeReceivedTestConfig.get('snapStatistic').get('dataInfos'),
            'tradeDate': _vdeReceivedTestConfig.get('snapStatistic').get('tradeDate'),
            'sampleSecurityIDs': _vdeReceivedTestConfig.get('snapStatistic').get('sampleSecurityIDs'),
            'testParams': v
        }
        for k, v in _vdeReceivedTestConfig.get('snapStatistic', {}).get('testItems', {}).items()
        if k == 'sampledLastPrice'
    ])
    def test_vde_received_sampled_last_price_statistic(self, case):
        self._data_infos = list(
            filter(lambda x: x.get('dataMsgType') in ('UA5302', 'UA3202', 'UA3113'), case.get('dataInfos'))
        )
        for data_info in self._data_infos:
            if 'dataFieldsInfo' in data_info.keys():
                continue
            data_fields_info = deepcopy(self._snapDataFieldsInfo.get(data_info.get('dataMsgType')))
            statistic_fields = (OrderedSet(data_fields_info.get('readFields'))
                                -
                                OrderedSet(data_fields_info.get('snapStatisticIgnoreFields')))
            data_fields_info.update({'useCols': statistic_fields})
            data_info.update({'dataFieldsInfo': data_fields_info})

        self._trade_date = case.get('tradeDate')
        self._sample_security_ids = case.get('sampleSecurityIDs')
        self._testParams = case.get('testParams')
        self._trade_start_datetime = datetime.strptime(self._trade_date + '092500', '%Y%m%d%H%M%S')
        self._statistical_start_time = self._testParams.get('statisticalTimeInterval').get('startTime') + '00'
        self._statistical_end_time = self._testParams.get('statisticalTimeInterval').get('endTime') + '00'
        self._statistical_start_datetime = datetime.strptime(self._trade_date + self._statistical_start_time,
                                                             '%Y%m%d%H%M%S%f')
        self._statistical_end_datetime = datetime.strptime(self._trade_date + self._statistical_end_time,
                                                           '%Y%m%d%H%M%S%f')

        self._update_df_sampled_last_price_trends_to_data_infos()

        self._is_case_passed = True
        valid_security_ids = OrderedSet(self._sample_security_ids)
        valid_security_ids.discard('000000')
        valid_security_ids = list(valid_security_ids)
        drawing_failed_security_ids = []
        for security_id in valid_security_ids:
            traces = []
            for data_info in self._data_infos:
                df_last_price_trend = data_info.get('dfSampledLastPriceTrends', {}).get(security_id)
                if df_last_price_trend is None:
                    continue
                trace = go.Scatter(x=df_last_price_trend.index,
                                   y=df_last_price_trend.lastPrice,
                                   name=data_info.get('dataName'), mode='lines+markers')
                traces.append(trace)

            output_file_path = os.path.join(REPORT_DIR,
                                            'data_test/vde_received/sampled_last_price_statistic', self._trade_date,
                                            f'{security_id}_last_price_statistic_of_{self._trade_date}_'
                                            f'{self._statistical_start_time[:4]}_{self._statistical_end_time[:4]}.html')
            if not self.draw_line_chart_according_to_traces(traces, output_file_path,
                                                            title=f'{security_id} 最新价走势图',
                                                            xaxis_title='行情时间',
                                                            yaxis_title='最新价(元)'):
                if self._is_case_passed:
                    self._is_case_passed = False
                drawing_failed_security_ids.append(security_id)

        log_json = copy(self.logTemplate)
        log_json['_dataTime'] = datetime.now().isoformat(sep=' ')

        try:
            assert self._is_case_passed
        except AssertionError as e:
            log_json['_metric'] = ('Data statistic failed! Failed to draw the line chart of last price trend '
                                   f'for the security IDs as {drawing_failed_security_ids}! '
                                   'Please check the configuration or the data of the test!')
            self.logUtils.logger.error(json.dumps(log_json, ensure_ascii=False))
            raise e
        else:
            log_json['_metric'] = ('Data statistic succeeded! Succeeded in drawing the line chart of last price trend '
                                   f'for the security IDs as {valid_security_ids}!')
            self.logUtils.logger.info(json.dumps(log_json, ensure_ascii=False))

    def _update_df_sampled_snap_update_freq_trends_to_data_infos(self):
        self._update_filtered_df_to_data_infos('dfSampledAllSnap')

        for data_info in self._data_infos:
            if 'dfSampledSnapUpdateFreqTrends' in data_info.keys():
                continue
            df_sampled_all_snap = deepcopy(data_info.get('dfSampledAllSnap'))
            data_fields_info = data_info.get('dataFieldsInfo')
            comm_fields_info = data_fields_info.get('commFieldsInfo')
            data_datetime_format = '%Y%m%d' + comm_fields_info.get('dataTime').get('timeFormat')
            idx_trade_datetime_format = '%Y%m%d' + comm_fields_info.get('idxTradeTime', {}).get('timeFormat', '')
            df_sampled_all_snap['dataDatetime'] = [
                datetime.strptime(self._trade_date + i.rjust(8, '0').removeprefix('00').ljust(8, '0'),
                                  data_datetime_format)
                for i in df_sampled_all_snap['dataTime']
            ]
            df_sampled_all_snap.drop(df_sampled_all_snap.index[
                                         (df_sampled_all_snap['dataDatetime'] < self._statistical_start_datetime)
                                         |
                                         (df_sampled_all_snap['dataDatetime'] > self._statistical_end_datetime)
                                         ],
                                     inplace=True)
            df_sampled_snap_time_fields = OrderedSet(['securityID', 'dataDatetime', 'idxTradeTime'])
            df_sampled_snap_time_fields &= OrderedSet(df_sampled_all_snap.columns)
            df_sampled_snap_time = df_sampled_all_snap.loc[:, df_sampled_snap_time_fields]

            df_sampled_snap_update_freq_trends = {}
            for security_id, df_snap_time in df_sampled_snap_time.groupby(['securityID']):
                df_snap_time['snapUpdateFreq'] = df_snap_time['dataDatetime'].diff()
                df_snap_time['snapUpdateFreq'] = [0 if pd.isna(i) else int(i.total_seconds())
                                                  for i in df_snap_time['snapUpdateFreq']]
                if 'idxTradeTime' in df_snap_time.columns and security_id.startswith('0'):
                    df_snap_time['idxTradeDatetime'] = [
                        self._statistical_start_datetime if pd.isna(i)
                        else datetime.strptime(self._trade_date + i.rjust(8, '0').removeprefix('00').ljust(8, '0'),
                                               idx_trade_datetime_format)
                        for i in df_snap_time['idxTradeTime']
                    ]
                    df_snap_time['tradeUpdateFreq'] = df_snap_time['idxTradeDatetime'].diff()
                    df_snap_time['tradeUpdateFreq'] = [0 if pd.isna(i) else int(i.total_seconds())
                                                       for i in df_snap_time['tradeUpdateFreq']]
                    df_snap_time.drop(columns='idxTradeTime', inplace=True)

                df_snap_update_freq_trend = df_snap_time.set_index('dataDatetime')
                df_sampled_snap_update_freq_trends.update({security_id: df_snap_update_freq_trend})

            data_info.update({'dfSampledSnapUpdateFreqTrends': df_sampled_snap_update_freq_trends})

    @pytest.mark.parametrize('case', [
        {
            'dataInfos': _vdeReceivedTestConfig.get('snapStatistic').get('dataInfos'),
            'tradeDate': _vdeReceivedTestConfig.get('snapStatistic').get('tradeDate'),
            'sampleSecurityIDs': _vdeReceivedTestConfig.get('snapStatistic').get('sampleSecurityIDs'),
            'testParams': v
        }
        for k, v in _vdeReceivedTestConfig.get('snapStatistic', {}).get('testItems', {}).items()
        if k == 'sampledSnapUpdateFreq'
    ])
    def test_vde_received_sampled_snap_update_freq_statistic(self, case):
        self._testParams = case.get('testParams')#开始结束时间，onlyldx
        self._sample_security_ids = case.get('sampleSecurityIDs')#证券代码列表
        valid_security_ids = []
        if self._testParams.get('onlyIdx'):
            self._data_infos = list(
                filter(lambda x: x.get('dataMsgType') in ('UA3113', 'UA3115'), case.get('dataInfos'))
            )#筛选出UA3113和UA3115
            valid_security_ids.extend(filter(lambda x: x.startswith('0'), self._sample_security_ids))#筛选出以’0‘开头的证券代码

        else:
            self._data_infos = case.get('dataInfos')#数据源信息
            valid_security_ids.extend(self._sample_security_ids)
        for data_info in self._data_infos:
            if 'dataFieldsInfo' in data_info.keys():
                continue
            data_fields_info = deepcopy(self._snapDataFieldsInfo.get(data_info.get('dataMsgType')))
            statistic_fields = (OrderedSet(data_fields_info.get('readFields'))
                                -
                                OrderedSet(data_fields_info.get('snapStatisticIgnoreFields')))
            data_fields_info.update({'useCols': statistic_fields})
            data_info.update({'dataFieldsInfo': data_fields_info})

        self._trade_date = case.get('tradeDate')
        self._trade_start_datetime = datetime.strptime(self._trade_date + '092500', '%Y%m%d%H%M%S')
        self._statistical_start_time = self._testParams.get('statisticalTimeInterval').get('startTime') + '00'
        self._statistical_end_time = self._testParams.get('statisticalTimeInterval').get('endTime') + '00'
        self._statistical_start_datetime = datetime.strptime(self._trade_date + self._statistical_start_time,
                                                             '%Y%m%d%H%M%S%f')
        self._statistical_end_datetime = datetime.strptime(self._trade_date + self._statistical_end_time,
                                                           '%Y%m%d%H%M%S%f')

        self._update_df_sampled_snap_update_freq_trends_to_data_infos()

        self._is_case_passed = True
        drawing_failed_security_ids = []
        all_traces = []
        for security_id in valid_security_ids:
            traces = []
            for data_info in self._data_infos:

                df_snap_update_freq_trend = data_info.get('dfSampledSnapUpdateFreqTrends', {}).get(security_id)
                if df_snap_update_freq_trend is None:
                    continue
                trace_snap_update_freq = go.Scatter(x=df_snap_update_freq_trend.index,
                                                    y=df_snap_update_freq_trend.snapUpdateFreq,
                                                    name=(f'{security_id}_snap_update_freq_'
                                                          f'in_{data_info.get("dataName")}'),
                                                    mode='lines+markers')
                traces.append(trace_snap_update_freq)
                all_traces.append(trace_snap_update_freq)
                if 'idxTradeDatetime' not in df_snap_update_freq_trend.columns:
                    continue
                df_trade_update_freq_trend = df_snap_update_freq_trend.set_index('idxTradeDatetime')
                trace_trade_update_freq = go.Scatter(x=df_trade_update_freq_trend.index,
                                                     y=df_trade_update_freq_trend.tradeUpdateFreq,
                                                     name=(f'{security_id}_trade_update_freq_'
                                                           f'in_{data_info.get("dataName")}'),
                                                     mode='lines+markers')
                traces.append(trace_trade_update_freq)
                all_traces.append(trace_trade_update_freq)

            if self._testParams.get('onlyIdx'):
                continue

            output_file_path = os.path.join(REPORT_DIR,
                                            'data_test/vde_received/sampled_snap_update_freq_statistic',
                                            self._trade_date,
                                            f'{security_id}_snap_update_freq_statistic_of_{self._trade_date}_'
                                            f'{self._statistical_start_time[:4]}_{self._statistical_end_time[:4]}.html')
            if not self.draw_line_chart_according_to_traces(traces, output_file_path,
                                                            title=f'{security_id} 快照更新频率走势图',
                                                            xaxis_title='行情/指数成交时间',
                                                            yaxis_title='快照/指数成交更新频率'):
                if self._is_case_passed:
                    self._is_case_passed = False
                drawing_failed_security_ids.append(security_id)

        if self._testParams.get('onlyIdx'):
            output_file_path = os.path.join(REPORT_DIR,
                                            'data_test/vde_received/sampled_snap_update_freq_statistic',
                                            self._trade_date,
                                            f'idx_snap_update_freq_statistic_of_{self._trade_date}_'
                                            f'{self._statistical_start_time[:4]}_{self._statistical_end_time[:4]}.html')
            if not self.draw_line_chart_according_to_traces(all_traces, output_file_path,
                                                            title=f'指数快照频率走势图',
                                                            xaxis_title='行情/指数成交时间',
                                                            yaxis_title='快照/指数成交更新频率'):
                if self._is_case_passed:
                    self._is_case_passed = False
                drawing_failed_security_ids.extend(valid_security_ids)

        log_json = copy(self.logTemplate)
        log_json['_dataTime'] = datetime.now().isoformat(sep=' ')

        try:
            assert self._is_case_passed
        except AssertionError as e:
            log_json['_metric'] = ('Data statistic failed! Failed to draw the line chart of snap update frequency '
                                   f'trend for the security IDs as {drawing_failed_security_ids}! '
                                   'Please check the configuration or the data of the test!')
            self.logUtils.logger.error(json.dumps(log_json, ensure_ascii=False))
            raise e
        else:
            log_json['_metric'] = ('Data statistic succeeded! Succeeded in drawing the line chart of update frequency '
                                   f'trend for the security IDs as {valid_security_ids}!')
            self.logUtils.logger.info(json.dumps(log_json, ensure_ascii=False))

    def _update_df_idx_snap_update_freq_to_data_infos(self):
        self._update_filtered_df_to_data_infos('dfUnfilteredSnap')

        for data_info in self._data_infos:
            if 'dfIdxSnapUpdateFreq' in data_info.keys():
                continue
            df_unfiltered_snap = deepcopy(data_info.get('dfUnfilteredSnap'))
            data_fields_info = data_info.get('dataFieldsInfo')
            comm_fields_info = data_fields_info.get('commFieldsInfo')
            data_datetime_format = '%Y%m%d' + comm_fields_info.get('dataTime').get('timeFormat')
            df_unfiltered_snap['dataDatetime'] = [
                datetime.strptime(self._trade_date + i.rjust(8, '0').removeprefix('00').ljust(8, '0'),
                                  data_datetime_format)
                for i in df_unfiltered_snap['dataTime']
            ]
            df_unfiltered_snap['prevDataDatetime'] = df_unfiltered_snap['dataDatetime'].shift(1)
            df_unfiltered_snap['snapUpdateFreq'] = (df_unfiltered_snap['dataDatetime']
                                                    -
                                                    df_unfiltered_snap['prevDataDatetime'])
            df_unfiltered_snap['snapUpdateFreq'] = [0 if pd.isna(i) else int(i.total_seconds())
                                                    for i in df_unfiltered_snap['snapUpdateFreq']]
            df_idx_snap_update_freq_fields = ['dataTime', 'dataDatetime', 'prevDataDatetime', 'snapUpdateFreq']
            df_idx_snap_update_freq = df_unfiltered_snap.loc[:, df_idx_snap_update_freq_fields]

            data_info.update({'dfIdxSnapUpdateFreq': df_idx_snap_update_freq})

    @pytest.mark.parametrize('case', [
        {
            'dataInfos': _vdeReceivedTestConfig.get('snapStatistic').get('dataInfos'),
            'tradeDate': _vdeReceivedTestConfig.get('snapStatistic').get('tradeDate'),
            'testParams': v
        }
        for k, v in _vdeReceivedTestConfig.get('snapStatistic', {}).get('testItems', {}).items()
        if k == 'idxSnapUpdateFreq'
    ])
    def test_vde_received_idx_snap_update_freq_statistic(self, case):
        self._data_infos = list(
            filter(lambda x: x.get('dataMsgType') in ('UA3113', 'UA3115'), case.get('dataInfos'))
        )
        for data_info in self._data_infos:
            if 'dataFieldsInfo' in data_info.keys():
                continue
            data_fields_info = deepcopy(self._snapDataFieldsInfo.get(data_info.get('dataMsgType')))
            statistic_fields = (OrderedSet(data_fields_info.get('readFields'))
                                -
                                OrderedSet(data_fields_info.get('snapStatisticIgnoreFields')))
            data_fields_info.update({'useCols': statistic_fields})
            data_info.update({'dataFieldsInfo': data_fields_info})

        self._trade_date = case.get('tradeDate')
        self._testParams = case.get('testParams')
        self._expected_min_value = self._testParams.get('expectedValueRange').get('min')
        self._expected_max_value = self._testParams.get('expectedValueRange').get('max')

        self._update_df_idx_snap_update_freq_to_data_infos()

        self._is_case_passed = True
        output_file_dir = os.path.join(REPORT_DIR, 'data_test/vde_received/idx_snap_update_freq_statistic',
                                       self._trade_date)
        os.makedirs(output_file_dir, exist_ok=True)
        log_json = copy(self.logTemplate)
        for data_info in self._data_infos:
            df_idx_snap_update_freq = data_info.get('dfIdxSnapUpdateFreq')
            update_freq_value_counts = df_idx_snap_update_freq['snapUpdateFreq'].value_counts().sort_index()
            unexpected_update_freq_values = (set(update_freq_value_counts.index)
                                             -
                                             set(range(self._expected_min_value, self._expected_max_value + 1)))

            log_json['_dataTime'] = datetime.now().isoformat(sep=' ')
            if unexpected_update_freq_values:
                if self._is_case_passed:
                    self._is_case_passed = False
                df_unexpected_update_freq_idx_snap = df_idx_snap_update_freq[
                    df_idx_snap_update_freq['snapUpdateFreq'].isin(unexpected_update_freq_values)
                ]
                df_unexpected_update_freq_idx_snap.to_csv(
                    os.path.join(output_file_dir,
                                 f'unexpected_update_freq_idx_snap_of_{data_info.get("dataName")}.csv'),
                    index=False, encoding=self.defaultFileEncoding
                )
                log_json['_metric'] = ('Data statistic succeeded! But there are some unexpected '
                                       f'update frequency values of index snap in the {data_info.get("dataName")}! '
                                       f'The value counts of update frequency is {update_freq_value_counts.to_dict()}! '
                                       'And also u can view the file name format as '
                                       'unexpected_update_freq_idx_snap.csv for more information!')
                self.logUtils.logger.error(json.dumps(log_json, ensure_ascii=False))
            else:
                log_json['_metric'] = ('Data statistic succeeded! All update frequency values of index snap '
                                       f'in the {data_info.get("dataName")} are as expected! And the value counts of '
                                       f'update frequency is {update_freq_value_counts.to_dict()}')
                self.logUtils.logger.info(json.dumps(log_json, ensure_ascii=False))

        assert self._is_case_passed

    def _update_df_tx_max_forwarding_delay_trend_to_data_infos(self):
        self._update_filtered_df_to_data_infos('dfForwardingTimeUniqTx')

        for data_info in self._data_infos:
            if 'dfTxMaxForwardingDelayTrend' in data_info.keys():
                continue
            df_forwarding_time_uniq_tx = deepcopy(data_info.get('dfForwardingTimeUniqTx'))
            data_fields_info = data_info.get('dataFieldsInfo')
            comm_fields_info = data_fields_info.get('commFieldsInfo')
            trd_or_ord_datetime_format = '%Y%m%d' + comm_fields_info.get('trdOrOrdTime').get('timeFormat')
            vde_datetime_format = comm_fields_info.get('vdeDatetime').get('datetimeFormat')
            # 解析成交/委托时asse间为 datetime 对象并作为新列 trdOrOrdDatetime 添加到 df
            df_forwarding_time_uniq_tx['trdOrOrdDatetime'] = [
                self._statistical_start_datetime
                if i.rjust(8, '0').removeprefix('00').ljust(8, '0') < self._statistical_start_time
                else datetime.strptime(self._trade_date + i.rjust(8, '0').removeprefix('00').ljust(8, '0'),
                                       trd_or_ord_datetime_format)
                for i in df_forwarding_time_uniq_tx['trdOrOrdTime']
            ]
            # 解析 df 第一行的 VDE 时间为 datetime 对象
            try:
                first_vde_datetime = datetime.strptime(df_forwarding_time_uniq_tx['vdeDatetime'].iloc[0],
                                                       vde_datetime_format)
            except ValueError:
                vde_datetime_format += '.%f'
                first_vde_datetime = datetime.strptime(df_forwarding_time_uniq_tx['vdeDatetime'].iloc[0],
                                                       vde_datetime_format)
            # 获得第一条消息的 VDE 时间相对于统计开始时间(第一条消息的成交/委托时间)的偏移量
            vde_datetime_offset = first_vde_datetime - self._statistical_start_datetime
            # 解析每条消息的 VDE 时间为 datetime 对象并同时修正其相对于统计开始时间的偏移量
            df_forwarding_time_uniq_tx['vdeDatetime'] = [
                datetime.strptime(i, vde_datetime_format) - vde_datetime_offset
                for i in df_forwarding_time_uniq_tx['vdeDatetime']
            ]
            # 计算转发时延
            df_forwarding_time_uniq_tx['forwardingDelay'] = [
                0 if (i.vdeDatetime - i.trdOrOrdDatetime).total_seconds() < 0
                else round((i.vdeDatetime - i.trdOrOrdDatetime).total_seconds(), 3)
                for i in df_forwarding_time_uniq_tx.loc[:, ['vdeDatetime', 'trdOrOrdDatetime']].itertuples()
            ]
            df_tx_forwarding_delay = df_forwarding_time_uniq_tx.loc[:, ['vdeDatetime', 'forwardingDelay']]
            df_tx_max_forwarding_delay_trend = df_tx_forwarding_delay.groupby(['vdeDatetime']).max()
            df_tx_max_forwarding_delay_trend.rename(columns={'forwardingDelay': 'maxForwardingDelay'}, inplace=True)
            data_info.update({'dfTxMaxForwardingDelayTrend': df_tx_max_forwarding_delay_trend})

    @pytest.mark.parametrize('case', [
        {
            'dataInfos': _vdeReceivedTestConfig.get('txStatistic').get('dataInfos'),
            'tradeDate': _vdeReceivedTestConfig.get('txStatistic').get('tradeDate'),
            'testParams': v
        }
        for k, v in _vdeReceivedTestConfig.get('txStatistic', {}).get('testItems', {}).items()
        if k == 'maxForwardingDelay'
    ])
    def test_vde_received_tx_max_forwarding_delay_statistic(self, case):
        self._data_infos = case.get('dataInfos')
        for data_info in self._data_infos:
            if 'dataFieldsInfo' in data_info.keys():
                continue
            data_fields_info = deepcopy(self._txDataFieldsInfo.get(data_info.get('dataMsgType')))
            data_fields_info.update({'useCols': data_fields_info.get('readFields')})
            data_info.update({'dataFieldsInfo': data_fields_info})

        self._trade_date = case.get('tradeDate')
        self._testParams = case.get('testParams')
        self._statistical_start_time = self._testParams.get('statisticalTimeInterval').get('startTime') + '00'
        self._statistical_end_time = self._testParams.get('statisticalTimeInterval').get('endTime') + '00'
        self._statistical_start_datetime = datetime.strptime(self._trade_date + self._statistical_start_time,
                                                             '%Y%m%d%H%M%S%f')

        self._update_df_tx_max_forwarding_delay_trend_to_data_infos()

        traces = []
        for data_info in self._data_infos:
            df_tx_max_forwarding_delay_trend = data_info.get('dfTxMaxForwardingDelayTrend')
            df_tx_max_forwarding_delay_trend = df_tx_max_forwarding_delay_trend.resample('s').max()  # 按秒重新采样取最大值
            df_tx_max_forwarding_delay_trend.fillna(value=0, inplace=True)  # 无逐笔转发时延的时间空值补零
            trace = go.Scatter(x=df_tx_max_forwarding_delay_trend.index,
                               y=df_tx_max_forwarding_delay_trend.maxForwardingDelay,
                               name=data_info.get('dataName'), mode='lines+markers')
            traces.append(trace)

        output_file_path = os.path.join(REPORT_DIR,
                                        'data_test/vde_received/tx_max_forwarding_delay_statistic', self._trade_date,
                                        f'tx_max_forwarding_delay_statistic_of_{self._trade_date}_'
                                        f'{self._statistical_start_time[:4]}_{self._statistical_end_time[:4]}.html')
        log_json = copy(self.logTemplate)
        log_json['_dataTime'] = datetime.now().isoformat(sep=' ')

        try:
            assert self.draw_line_chart_according_to_traces(traces, output_file_path,
                                                            title='开盘高峰时段主题数据最大转发时延统计',
                                                            xaxis_title='VDE落地时间',
                                                            yaxis_title='最大转发时延(s)')
        except AssertionError as e:
            log_json['_metric'] = ('Data statistic failed! Failed to draw the line chart of '
                                   'transaction max forwarding delay trend at rush-hour data traffic '
                                   f'from data names as {[i.get("dataName") for i in self._data_infos]}! '
                                   'Please check the configuration or the data of the test!')
            self.logUtils.logger.error(json.dumps(log_json, ensure_ascii=False))
            raise e
        else:
            log_json['_metric'] = ('Data statistic succeeded! Succeeded in drawing the line chart of '
                                   'transaction max forwarding delay trend at rush-hour data traffic '
                                   f'from data names as {[i.get("dataName") for i in self._data_infos]}!')
            self.logUtils.logger.info(json.dumps(log_json, ensure_ascii=False))

    @pytest.mark.parametrize('case', [
        {
            'dataInfos': _vdeReceivedTestConfig.get('statisticsLosePacket').get('dataInfos'),
            'tradeDate': _vdeReceivedTestConfig.get('statisticsLosePacket').get('tradeDate'),
            'environment_list': _vdeReceivedTestConfig.get('statisticsLosePacket').get('environment_list'),
            'time_list': _vdeReceivedTestConfig.get('statisticsLosePacket').get('statisticalTimeInterval'),
            'testParams': v
        }
        for k, v in _vdeReceivedTestConfig.get('statisticsLosePacket', {}).items()
        if k == 'categoryList'
    ])
    def test_statistical_lose_packet(self, case):
        print(case)
        environment_dataInfos = case.get('dataInfos')
        log_json = copy(self.logTemplate)
        log_json['_dataTime'] = datetime.now().isoformat(sep=' ')
        category_dict = case.get('testParams')
        for environment, dataInfos in environment_dataInfos.items():
            package_jhjj_statistic = {
                "指数行情数据早市包数": 0,  # UA3113
                "市场总览数据早市包数": 0,  # UA3115
                "竞价行情快照数据早市包数": 0,  # UA3202
                "竞价逐笔成交数据早市包数": 0,  # UA3201
                "竞价逐笔委托数据早市包数": 0,  # UA5801
            }
            package_noon_statistic = {

                "指数行情数据午市包数": 0,  # UA3113
                "市场总览数据午市包数": 0,  # UA3115
                "竞价行情快照数据午市包数": 0,  # UA3202
                "竞价逐笔成交数据午市包数": 0,  # UA3201
                "竞价逐笔委托数据午市包数": 0,  # UA5801
            }
            package_all_statistic = {
                "指数行情数据全天包数": 0,  # UA3113
                "市场总览数据全天包数": 0,  # UA3115
                "竞价行情快照数据全天包数": 0,  # UA3202
                "竞价逐笔成交数据全天包数": 0,  # UA3201
                "竞价逐笔委托数据全天包数": 0,  # UA5801
            }
            category_datainfo_dict = {}
            for category in category_dict.keys():
                category_datainfo_list = []
                for dataInfo in dataInfos:
                    msg_type = dataInfo.get('dataMsgType')
                    if msg_type in category_dict[category]:
                        category_datainfo_list.append(dataInfo)
                category_datainfo_dict.update({category: category_datainfo_list})

            for category, dataInfos in category_datainfo_dict.items():
                df_concat_list = []
                if len(dataInfos) != 0:
                    for dataInfo in dataInfos:
                        msg_type = dataInfo.get('dataMsgType')
                        usecols = ['消息类型', 'TAG_10072', '数据落地时间', 'TAG_95', 'TAG_10142', '行情时间']
                        if msg_type == 'UA5803':
                            usecols = ['消息类型', 'TAG_10072', '数据落地时间', 'TAG_95', 'TAG_10142']
                        if msg_type == 'UA3115':
                            usecols = ['消息类型', 'TAG_10072', '数据落地时间', 'TAG_10142', 'TAG_95', '行情时间（秒）']
                        elif msg_type == 'UA5801':
                            usecols = ['消息类型', 'TAG_10072', '数据落地时间', 'TAG_10142', 'TAG_95', '委托时间']
                        elif msg_type == 'UA3201':
                            usecols = ['消息类型', 'TAG_10072', '数据落地时间', 'TAG_10142', 'TAG_95', '成交时间']

                        df = pd.read_csv(dataInfo['dataPath'], encoding='gbk', usecols=usecols)

                        fields_name_mappings = [{"行情时间": "fieldName"}, {"行情时间（秒）": "fieldName"},
                                                {"委托时间": "fieldName"}, {"成交时间": "fieldName"}]
                        for fields_name_mapping in fields_name_mappings:
                            df.rename(columns={k: v for k, v in fields_name_mapping.items()}, inplace=True)  # 字段重命名
                        df_concat_list.append(df)

                        df.drop_duplicates(subset=['TAG_10072'], keep='first', inplace=True,
                                           ignore_index=True)  # 根据消息号去重
                        print(df)

                        if msg_type in ['UA3113', 'UA3115', 'UA5801', 'UA3201', 'UA3202']:
                            df['fieldName'] = [
                                '20230201' + str(i).rjust(8, '0').removeprefix('00').ljust(8, '0')[0:-2]
                                for i in df['fieldName']]
                            df['fieldName'] = pd.to_datetime(df['fieldName'])
                            time_file_list = [
                                datetime.strptime('20230201' + str(i).rjust(8, '0').removeprefix('00').ljust(8, '0'),
                                                  '%Y%m%d%H%M%S%f')
                                for i in case.get('time_list')]

                            hjj_package_number = len(
                                df[df['fieldName'].between(time_file_list[0], time_file_list[1])])  # 早市
                            noon_package_number = len(
                                df[df['fieldName'].between(time_file_list[0], time_file_list[2])])  # 午市
                            all_package_number = len(
                                df[df['fieldName'].between(time_file_list[0], time_file_list[3])])  # 全天
                            if msg_type == 'UA3113':
                                package_jhjj_statistic['指数行情数据早市包数'] = hjj_package_number
                                package_noon_statistic['指数行情数据午市包数'] = noon_package_number
                                package_all_statistic['指数行情数据全天包数'] = all_package_number
                            if msg_type == 'UA3115':
                                package_jhjj_statistic['市场总览数据早市包数'] = hjj_package_number
                                package_noon_statistic['市场总览数据午市包数'] = noon_package_number
                                package_all_statistic['市场总览数据全天包数'] = all_package_number
                            if msg_type == 'UA3202':
                                package_jhjj_statistic['竞价行情快照数据早市包数'] = hjj_package_number
                                package_noon_statistic['竞价行情快照数据午市包数'] = noon_package_number
                                package_all_statistic['竞价行情快照数据全天包数'] = all_package_number
                            if msg_type == 'UA3201':
                                package_jhjj_statistic['竞价逐笔成交数据早市包数'] = hjj_package_number
                                package_noon_statistic['竞价逐笔成交数据午市包数'] = noon_package_number
                                package_all_statistic['竞价逐笔成交数据全天包数'] = all_package_number
                            if msg_type == 'UA5801':
                                package_jhjj_statistic['竞价逐笔委托数据早市包数'] = hjj_package_number
                                package_noon_statistic['竞价逐笔委托数据午市包数'] = noon_package_number
                                package_all_statistic['竞价逐笔委托数据全天包数'] = all_package_number
                else:
                    continue
                df_concat = pd.concat(df_concat_list)
                df_concat.sort_values(by=['TAG_10072'], ignore_index=True, inplace=True)
                print(df_concat)
                total_package_number = df_concat.shape[0]
                total_length = 0
                lost_package = 0
                pre_msg_seq_id = 0
                for row in df_concat.itertuples():
                    cur_length = row[5] if (row[1] == 'UA5803') else row[6]
                    total_length = int(total_length) + int(cur_length)
                    cur_msg_seq_id = row[3] if (row[1] == 'UA5803') else row[4]

                    if cur_msg_seq_id == 0:
                        continue
                    else:
                        # 计算序列号差值
                        diff = int(cur_msg_seq_id) - int(pre_msg_seq_id)
                        if diff == 1:
                            pre_msg_seq_id = cur_msg_seq_id
                        elif diff != 1 and pre_msg_seq_id == 0:
                            pre_msg_seq_id = cur_msg_seq_id
                        else:
                            pass
                            # print(
                            #     "环境为{},有丢包,丢包数据序号为{} 到 {}".format(environment, int(pre_msg_seq_id) + 1,
                            #                                       int(cur_msg_seq_id) - 1),
                            #     '最新数据的category、step长度、序号分别为{},{},{}'.format(category, cur_length, cur_msg_seq_id))
                            lost_package = lost_package + diff - 1
                            pre_msg_seq_id = cur_msg_seq_id

                try:
                    avg_package = round(int(total_length) / int(total_package_number))
                except:
                    avg_package = 0

                statistics_dicts = {
                    'environment': environment,
                    "category_id": category,
                    "total_length": total_length,
                    "lost_package": lost_package,
                    "total_package_number": total_package_number,
                    "avg_package": avg_package
                }
                print({environment: statistics_dicts})
                self.logUtils.logger.info(json.dumps({environment: statistics_dicts}, ensure_ascii=False))

            print({environment: package_jhjj_statistic})
            print({environment: package_noon_statistic})
            print({environment: package_all_statistic})
            self.logUtils.logger.info(json.dumps({environment: package_jhjj_statistic}, ensure_ascii=False))
            self.logUtils.logger.info(json.dumps({environment: package_noon_statistic}, ensure_ascii=False))
            self.logUtils.logger.info(json.dumps({environment: package_all_statistic}, ensure_ascii=False))


if __name__ == '__main__':
    # pytest.main(['-k not fund_iopv_precision_comparison', 'test_vde_received_data.py'])
    # pytest.main(['-k fund_iopv_precision_comparison', 'test_vde_received_data.py'])
    # pytest.main(['-k last_snap_comparison', 'test_vde_received_data.py'])
    # pytest.main(['-k security_id_comparison', 'test_vde_received_data.py'])
    # pytest.main(['-k sampled_iopv_statistic', 'test_vde_received_data.py'])
    # pytest.main(['-k sampled_last_price_statistic', 'test_vde_received_data.py
    # pytest.main(['-k sampled_snap_update_freq_statistic', 'test_vde_received_data.py'])
    # pytest.main(['-k idx_snap_update_freq_statistic', 'test_vde_received_data.py'])
    pytest.main(['-k test_statistical_lose_packet', 'test_vde_received_data.py'])
    # pytest.main(['-k test_vde_received_security_id_comparison', 'test_vde_received_data.py'])

    # test_statistical_packet_numbers

