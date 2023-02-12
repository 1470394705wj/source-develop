"""
ModuleName: test_dce_ppm
Description:
date: 2022/8/2 9:59
@author Sylar
@version 1.0
@since Python 3.9
"""
import os
import pytest
import allure

from datetime import datetime
from common.constants import DATA_DIR
from common.yaml_utils import YamlUtils
from common.dce_module import DCEModule
from common.dce_test_base import DCETestBase


@allure.epic('DCE项目')
@allure.feature('ppm模块')
class TestDCEPpm(DCETestBase):
    # 测试类夹具
    @pytest.fixture(scope='class')
    def fixture_class(self, fixture_session):
        # 根据测试会话夹具返回的字典拿到 ppm 模块的 DCEModule() 并执行该模块的 setup()
        dce_modules = fixture_session
        ppm = dce_modules.get('ppm')
        ppm.setup()
        yield ppm
        # 本类的测试结束后执行 ppm 模块的 teardown()
        ppm.teardown()

    @allure.severity('critical')
    @allure.story('功能测试')
    @pytest.mark.parametrize('run_type', DCETestBase.testRunTypes)
    @pytest.mark.parametrize(
        'case', YamlUtils(os.path.join(DATA_DIR, 'app_test/dce/ppm/test_dce_ppm_func.yml')).get_data())
    def test_dce_ppm_func(self, run_type, case, fixture_class):
        # 获取测试类夹具返回的 ppm 对象并赋值给 self.module
        self.module = fixture_class

        # 添加 allure 报告信息
        allure.dynamic.title(case.get('caseTitle'))
        allure.dynamic.description(
            f'DCE系统ppm模块功能测试，软件部署地址[{self.module.hostIp}]，软件部署目录[{self.module.dceHome}]，模块启动方式[{run_type}]，'
            f'用例编号[{case.get("caseId")}]，用例标题[{case.get("caseTitle")}]')

        # 如果当前 run_type 是 test_run_types 的第一个且本条 case 存在 setupCmd 则执行该命令
        if (run_type == self.testRunTypes[0]) and case.get('setupCmd'):
            self.module.rmUtils.exec_cmd(eval(case.get('setupCmd')))

        # 如果本条 case 设置了 caseRunTypes 且当前 run_type 不在本条 case 的 caseRunTypes 则跳过本条用例
        if case.get('caseRunTypes') and (run_type not in case.get('caseRunTypes')):
            # 如果当前 run_type 是 test_run_types 的最后一个且本条 case 存在 tearCmd 则在跳过之前执行该命令
            if (run_type == self.testRunTypes[-1]) and case.get('teardownCmd'):
                self.module.rmUtils.exec_cmd(eval(case.get('teardownCmd')))
            pytest.skip('run_type is not valid for current case!')

        # 记录模块的启动时间
        self.moduleStartTime = datetime.now()
        # 如果本条 case 设置了等待模块启动的时间则将其赋值给 self.waitStartSecs
        if case.get('waitStartSecs'):
            self.waitStartSecs = case.get('waitStartSecs')
        # 通过 self.module 执行模块的启动，并将控制台输出的信息赋值给 self.consoleInfo
        self.consoleInfo = self.module.start(run_type, self.waitStartSecs)
        # 获取当前的 shmdump_info 并赋值给 self.shmdumpInfo
        self.shmdumpInfo = self.module.get_shmdump_info()

        # 获取本条用例的 expect 字典，并获取其中的 moduleStartResult 的值
        expect = case.get('expect')
        expect_module_start_result = expect.get('moduleStartResult')

        # 如果本条用例的预期模块启动结果是成功，则赋值 self.waitShutdownSecs 用以在关闭模块的时候执行休眠以等待模块关闭
        if expect_module_start_result == 'successful':
            self.waitShutdownSecs = 5

        try:
            # 如果用例预期模块启动结果是失败，则验证该模块未能成功启动，反之则验证其成功启动
            if expect_module_start_result == 'failed':
                assert self.verify_process_started(False, 'module')
            else:
                assert self.verify_process_started(True, 'module')
                # 如果用例的模块启动类型是 load 模式，则还要验证 load 进程启动成功
                if run_type == 'load':
                    assert self.verify_process_started(True, 'load')

            # 如果当前用例在模块启动后有额外的 shell 命令需要执行则执行该命令
            if case.get('extraCmd'):
                self.consoleInfo = self.module.rmUtils.exec_cmd(eval(case.get('extraCmd')))

            # 如果当前用例在模块启动后有额外的 python 表达式需要执行则执行该 python 代码
            if case.get('extraPythonExpr'):
                exec(case.get('extraPythonExpr'))

            # 从预期字典中获取当前用例属于 common 和专属于当前 run_type 的额外验证点的字典并添加到列表
            extra_verify_points = []
            extra_common_verify_points = expect.get('extraVerifyPoints').get('common')
            if extra_common_verify_points:
                extra_verify_points.extend(extra_common_verify_points)
            extra_run_type_verify_points = expect.get('extraVerifyPoints').get(run_type)
            if extra_run_type_verify_points:
                extra_verify_points.extend(extra_run_type_verify_points)

            # 遍历额外验证点列表，获得每个额外验证点的验证类型和验证的参数，并根据其验证类型选择验证方法执行验证
            for extra_verify_point in extra_verify_points:
                verify_type = extra_verify_point.get('verifyType')
                verify_params = extra_verify_point.get('verifyParams')
                if verify_type == 1:
                    assert self.verify_process_started(verify_params.get('expectFlag'),
                                                       verify_params.get('expectInfo'))
                elif verify_type == 2:
                    assert self.verify_process_closed(verify_params.get('expectFlag'),
                                                      verify_params.get('expectInfo'))
                elif verify_type == 3:
                    assert self.verify_console_info(verify_params.get('expectFlag'),
                                                    verify_params.get('expectType'),
                                                    verify_params.get('expectInfo'))
                elif verify_type == 4:
                    assert self.verify_shmdump_info(verify_params.get('expectFlag'),
                                                    verify_params.get('expectType'),
                                                    verify_params.get('expectInfo'))
                elif verify_type == 5:
                    assert self.verify_log_info(verify_params.get('expectFlag'),
                                                verify_params.get('expectType'),
                                                verify_params.get('expectInfo'),
                                                [DCEModule.LogLocator(i.get('logType'), i.get('logHandlers'))
                                                 for i in verify_params.get('logLocatorsInfo')])
        # 根据是否捕获断言异常判断用例是否执行成功并分别记录日志
        except AssertionError as e:
            self.logUtils.logger.error(
                f'用例编号[{case.get("caseId")}]，用例标题[{case.get("caseTitle")}]，模块启动方式[{run_type}]，执行失败！')
            self.logUtils.logger.exception(e)
            raise e
        else:
            self.logUtils.logger.info(
                f'用例编号[{case.get("caseId")}]，用例标题[{case.get("caseTitle")}]，模块启动方式[{run_type}]，执行成功！')
        finally:
            # 执行测试后关闭模块程序
            self.module.shutdown(run_type, self.waitShutdownSecs)
            # 如果当前 run_type 是 test_run_types 的最后一个且本条 case 存在 tearCmd 则执行该命令
            if (run_type == self.testRunTypes[-1]) and case.get('teardownCmd'):
                self.module.rmUtils.exec_cmd(eval(case.get('teardownCmd')))


if __name__ == '__main__':
    pytest.main()
