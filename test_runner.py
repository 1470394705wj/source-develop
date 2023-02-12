"""
ModuleName: test_runner
Description: DCE自动化测试用例执行模块
date: 2022/5/10 15:06
@author Sylar
@version 1.0
@since Python 3.9
"""
import os
import pytest

from common.yaml_utils import YamlUtils
from common.constants import BASE_DATA_DIR, CONF_DIR, CASE_DIR, REPORT_DIR
from gevent import monkey

monkey.patch_all()


class TestView:
    _appTestBasic = YamlUtils(os.path.join(BASE_DATA_DIR, 'app_test/app_test_basic.yml')).get_data()
    _dataTestBasic = YamlUtils(os.path.join(BASE_DATA_DIR, 'data_test/data_test_basic.yml')).get_data()

    def __init__(self):
        self.loop = True

    def main_view(self):
        while self.loop:
            print()
            print('=' * 20, '欢迎使用SSE自动化测试工具', '=' * 20)
            print(' ' * 24, '1 项目功能测试')
            print(' ' * 24, '2 数据跟账测试')
            print(' ' * 24, '3 RawData数据解码')
            print(' ' * 24, '0 退出程序')
            user_input = input('请输入序号选择对应功能：').lower()
            print('=' * 65)

            if user_input == '1':
                self._app_test_view()
            elif user_input == '2':
                self._data_test_view()
            elif user_input == '3':
                if self._decoder_executor():
                    self.loop = False
            elif user_input in ('0', 'exit'):
                self.loop = False
                print('用户退出...')
            else:
                print('用户输入有误，请查阅菜单后重新输入！')

    def _app_test_view(self):
        while True:
            print()
            print('=' * 23, '项目功能测试子菜单', '=' * 23)
            print(' ' * 24, '1 DCE项目测试')
            print(' ' * 24, '2 LDDS项目测试')
            print(' ' * 24, '3 MDS项目测试')
            print(' ' * 24, '9 返回上级菜单')
            print(' ' * 24, '0 退出程序')
            user_input = input('请输入序号选择对应功能：').lower()
            print('=' * 65)

            if user_input == '1':
                if self._app_test_executor('dce'):
                    self.loop = False
                    break
            elif user_input == '2':
                if self._app_test_executor('ldds'):
                    self.loop = False
                    break
            elif user_input == '3':
                if self._app_test_executor('mds'):
                    self.loop = False
                    break
            elif user_input == '9':
                print('用户返回上一级菜单...')
                break
            elif user_input in ('0', 'exit'):
                self.loop = False
                print('用户退出...')
                break
            else:
                print('用户输入有误，请查阅菜单后重新输入！')

    def _data_test_view(self):
        while True:
            print()
            print('=' * 23, '数据跟账测试子菜单', '=' * 23)
            print(' ' * 24, '1 MDS响应数据对比测试')
            print(' ' * 24, '2 VDE落地数据对比测试')
            print(' ' * 24, '9 返回上级菜单')
            print(' ' * 24, '0 退出程序')
            user_input = input('请输入序号选择对应功能：').lower()
            print('=' * 65)

            if user_input == '1':
                if self._data_test_executor('mdsRespond'):
                    self.loop = False
                    break
            elif user_input == '2':
                if self._data_test_executor('vdeReceived'):
                    self.loop = False
                    break
            elif user_input == '9':
                print('用户返回上一级菜单...')
                break
            elif user_input in ('0', 'exit'):
                self.loop = False
                print('用户退出...')
                break
            else:
                print('用户输入有误，请查阅菜单后重新输入！')

    @staticmethod
    def _get_user_confirm(prompt: str):
        while True:
            user_confirm = input(prompt).lower()

            if user_confirm not in ('y', 'n', 'yes', 'no'):
                continue

            if user_confirm in ('y', 'yes'):
                return True
            else:
                return False

    @classmethod
    def _app_test_executor(cls, project: str):
        project_info = cls._appTestBasic.get(project)
        project_modules = {str(idx): module for idx, module in enumerate(project_info.get('projectModules'))}
        while True:
            prompt = f'请输入需要测试的{project.upper()}子模块名称或其序号：\n' \
                     f'{", ".join([f"{idx}: {module}" for idx, module in project_modules.items()])}\n' \
                     f'直接回车默认执行该项目所有子模块的测试，选择多个子模块输入内容以","号拼接，输入exit退出本功能：'

            user_inputs = list(map(lambda x: x.strip(), input(prompt).lower().split(',')))
            continue_flag = False
            test_modules = set()

            for user_input in user_inputs:
                if user_input not in ['', 'exit'] + list(project_modules.keys()) + \
                        [module.lower() for module in project_modules.values()]:
                    print('子模块选择输入有误，请根据提示重新输入！')
                    continue_flag = True
                    break

                if user_input == 'exit':
                    print(f'用户退出{project.upper()}项目测试...')
                    return False

                test_modules.add(project_modules[user_input] if user_input.isnumeric() else user_input)

            if continue_flag:
                continue

            if not cls._get_user_confirm('请确认已完成测试准备(部署被测项目/修改测试配置)，输入Y/N：'):
                print(f'测试准备未就绪，用户退出{project.upper()}项目测试...')
                return False

            pytest_args = [os.path.join(CASE_DIR, f'app_test/{project}')]

            test_modules.discard('')
            if test_modules:
                pytest_args.insert(0, f'-k {" or ".join(test_modules)}')

            if cls._get_user_confirm('请确认是否为本次测试生成allure报告，输入Y/N：'):
                print()
                pytest_args.insert(1, os.path.join(REPORT_DIR, f'app_test/{project}/allure_json'))
                pytest_args.insert(1, '--alluredir')
                pytest.main(pytest_args)
                os.system(f'allure generate {os.path.join(REPORT_DIR, f"app_test/{project}/allure_json")} -c -o '
                          f'{os.path.join(REPORT_DIR, f"app_test/{project}/allure_html")}')
            else:
                print()
                pytest.main(pytest_args)

            print()
            print('测试完成，程序即将自动退出，如已生成测试报告，请及时保存！')

            return True

    @classmethod
    def _data_test_executor(cls, project: str):
        project_info = cls._dataTestBasic.get(project)
        project_test_items = project_info.get('testItems')
        project_test_item_names = {str(idx): test_item.get('testName')
                                   for idx, test_item in enumerate(project_test_items)}
        while True:
            prompt = f'请输入需要执行的{project_info.get("viewName")}的子项目名称或其序号：\n' \
                     f'{", ".join([f"{k}: {v}" for k, v in project_test_item_names.items()])}\n' \
                     f'直接回车默认执行该项目所有子项目的测试，选择多个子项目输入内容以","号拼接，输入exit退出本功能：'

            user_inputs = list(map(lambda x: x.strip(), input(prompt).lower().split(',')))
            continue_flag = False
            test_item_names = set()

            for user_input in user_inputs:
                if user_input not in ['', 'exit'] + list(project_test_item_names.keys()) + \
                        [test_item_name.lower() for test_item_name in project_test_item_names.values()]:
                    print('子项目选择输入有误，请根据提示重新输入！')
                    continue_flag = True
                    break

                if user_input == 'exit':
                    print(f'用户退出{project_info.get("viewName")}...')
                    return False

                test_item_names.add(project_test_item_names[user_input] if user_input.isnumeric() else user_input)

            if continue_flag:
                continue

            if not cls._get_user_confirm('请确认已完成测试准备(部署测试数据/修改测试配置)，输入Y/N：'):
                print(f'测试准备未就绪，用户退出{project_info.get("viewName")}...')
                return False

            pytest_args = [os.path.join(CASE_DIR, f'data_test/{project_info.get("dirName")}')]

            test_item_names.discard('')
            if test_item_names:
                test_item_methods = []
                for test_item_name in test_item_names:
                    test_item_methods.append(
                        tuple(
                            filter(lambda x: x.get("testName") == test_item_name, project_test_items)
                        )[0].get("testMethod"))

                pytest_args.insert(0, f'-k {" or ".join(test_item_methods)}')

            print()
            pytest.main(pytest_args)

            print()
            print('测试完成，程序即将自动退出！')

            return True

    @classmethod
    def _decoder_executor(cls):
        if not cls._get_user_confirm('请确认已完成解码准备(修改解码配置)，输入Y/N：'):
            print(f'解码准备未就绪，用户退出RawData数据解码功能...')
            return False

        if not cls._get_user_confirm('请确认解码后的目标输出文件不存在，否则数据将在该文件中追加写入！输入Y/N：'):
            print(f'解码后的目标输出文件已存在，用户退出RawData数据解码功能...')
            return False

        print()
        decode_jar_path = os.path.join(BASE_DATA_DIR, 'lib', 'decode.jar')
        codec_conf_path = os.path.join(CONF_DIR, 'decoder', 'codecConfig.json')
        log4j_conf_path = os.path.join(BASE_DATA_DIR, 'decoder', 'log4j2-spring.xml')
        fast_templates_dir = os.path.join(BASE_DATA_DIR, 'decoder', 'fast_templates')
        os.system(f'java -Xms2G -Xmx4G -cp {decode_jar_path} -Dloader.main=com.sseinfo.bfcodec.Main '
                  f'org.springframework.boot.loader.PropertiesLauncher '
                  f'{codec_conf_path} {log4j_conf_path} {fast_templates_dir}')

        print()
        print('解码完成，程序即将自动退出，请于输出目录查看解码后的文件！')

        return True


if __name__ == '__main__':
    test_view = TestView()
    test_view.main_view()
    # TODO 统一 app_test_basic.yml 和 data_test_basic.yml 格式，甚至合并为 test_basic.yml
    # TODO 合并 _app_test_view() 和 _data_test_view() 为 _secondary_view()
    # TODO 合并 _app_test_executor() 和 _data_test_executor() 为 _test_executor()
