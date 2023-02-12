"""
ModuleName: remote_manage_utils
Description: 远程管理工具
date: 2022/5/10 18:38
@author Sylar
@version 1.0
@since Python 3.9
"""

import paramiko

from time import sleep


class RemoteManageUtils:
    def __init__(self, host: str, port: int = 22, username: str = 'level2op', password: str = 'level2op'):
        """
        根据传入的参数初始化 RemoteManageUtils 实例，保存数据到实例的相应私有属性
        :param host: 远程主机地址
        :param port: ssh 服务端口
        :param username: 主机用户名
        :param password: 主机密码
        """
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._ssh = None
        self._sftp = None

    def _get_ssh_connect(self):
        """
        根据实例的私有属性数据创建 ssh 连接
        """
        try:
            if self._ssh is None:
                self._ssh = paramiko.SSHClient()
                self._ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                self._ssh.connect(hostname=self._host, port=self._port,
                                  username=self._username, password=self._password)
        except Exception as e:
            print('尝试与远端服务器建立SSH通信失败，请检查网络通信或服务器信息！', e)

    def close(self):
        """
        关闭通过实例打开的 sftp 和 ssh 连接
        """
        try:
            if self._sftp:
                self._sftp.close()
            if self._ssh:
                self._ssh.close()
        except Exception as e:
            print('关闭SFTP/SSH连接异常，请检查网络通信是否正常！', e)

    def exec_cmd(self, cmd: str):
        """
        通过 ssh 连接，执行传入的 bash 命令
        :param cmd: 需要执行的 bash 命令
        :return: 执行 bash 命令后，远程主机控制台(标准输出流)输出的字符内容
        """
        try:
            self._get_ssh_connect()
            std_ios = self._ssh.exec_command(cmd)
            sleep(0.5)
            return std_ios[1].read().decode()
        except Exception as e:
            print('执行bash命令失败，请检查网络通信或命令文本！', e)

    def send_cmd(self, cmd: str):
        """
        根据 SSHClient() 创建 shell 会话，执行传入的 shell 命令
        :param cmd: 需要执行的 shell 命令
        :return: 执行 shell 命令后，远程主机控制台(标准输出流)输出的字符内容
        """
        try:
            self._get_ssh_connect()
            chan = self._ssh.invoke_shell()
            chan.send(cmd + '\r')
            sleep(2)
            return chan.recv(65535).decode()
        except Exception as e:
            print('执行shell命令失败，请检查网络通信或命令文本！', e)

    def _get_sftp_connect(self):
        """
        根据实例的私有属性创建 sftp 连接
        :return:
        """
        try:
            if self._sftp is None:
                t = paramiko.Transport(sock=(self._host, self._port))
                t.connect(username=self._username, password=self._password)
                self._sftp = paramiko.SFTPClient.from_transport(t)
        except Exception as e:
            print('尝试与远端服务器建立SFTP通信失败，请检查网络通信或用户信息！', e)

    def upload_file(self, local_path: str, remote_path: str):
        """
        通过 sftp 连接上传本地文件到远程主机
        :param local_path: 待上传的本地文件路径
        :param remote_path: 上传到远程主机后的文件路径
        :return:
        """
        try:
            self._get_sftp_connect()
            self._sftp.put(local_path, remote_path)
        except Exception as e:
            print('上传文件异常，请检查网络通信或文件路径信息！', e)

    def download_file(self, remote_path: str, local_path: str):
        """
        通过 sftp 连接下载远程主机文件到本地
        :param remote_path: 待下载的远程主机文件连接
        :param local_path: 下载到本地后的文件路径
        :return:
        """
        try:
            self._get_sftp_connect()
            self._sftp.get(remote_path, local_path)
        except Exception as e:
            print('下载文件异常，请检查网络通信或文件路径信息！', e)
