"""
ModuleName: test_mds_respond_data
Description:
date: 2022/9/21 13:59
@author Sylar
@version 1.0
@since Python 3.9
"""
import pytest

from common.options import *
from common.data_test_base import DataTestBase
from common.second_diff_csv import Compare_csv_diff

from gevent import monkey, wait, pool

monkey.patch_all()


class TestMDSRespondData(DataTestBase):

    def test_mds_api_request(self):
        op = options('all')
        resdics = {}

        # print(op)
        def sends(i):
            async_io_result = i.requests_send()
            resdics[i] = async_io_result

        for i in op:
            pool.Pool(1000).spawn(sends, i)
        wait()
        out = Output(resdics)

    def test_mds_respond_compare(self):
        Compare_csv_diff().act_diff_case()


if __name__ == '__main__':
    pytest.main(['-k test_mds_api_request'])
    # pytest.main(['-k test_mds_respond_compare'])
    # pytest.main()
