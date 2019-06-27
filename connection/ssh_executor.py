#
# Copyright(c) 2019 Intel Corporation
# SPDX-License-Identifier: BSD-3-Clause-Clear
#

import paramiko
from utils.output import Output
from connection.base_executor import BaseExecutor
from datetime import timedelta


class SshExecutor(BaseExecutor):
    def __init__(self, ip, username, password, port=22):
        self.ssh = paramiko.SSHClient()
        self.connect(ip, username, password, port)
        self.channel = self.ssh.invoke_shell()
        self.stdin = self.channel.makefile('wb')
        self.stdout = self.channel.makefile('r')
        self.execute("")  # empty command is sent to initialize and check connection

    def __del__(self):
        self.ssh.close()

    def connect(self, ip, user, passwd, port, timeout: timedelta = timedelta(seconds=30)):
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            self.ssh.connect(ip, username=user, password=passwd,
                             port=port, timeout=timeout.total_seconds())
        except paramiko.SSHException:
            raise Exception(f"An exception occurred while trying to connect to {self.ip}")

    def disconnect(self):
        try:
            self.ssh.close()
        except Exception:
            raise Exception(f"An exception occurred while trying to disconnect from {self.ip}")

    def execute(self, command, timeout: timedelta = timedelta(hours=1)):
        self.stdin.write(command + '\n')
        echo_cmd = f'echo __exit_code: $?'
        self.stdin.write(echo_cmd + '\n')
        self.stdin.flush()
        result = Output([], "", 0)

        for line in self.stdout:
            if line.startswith(f'__exit_code:'):
                result.exit_code = int(str(line).split()[-1])
                break
            elif str(line).startswith(command) or str(line).startswith(echo_cmd):
                result.stdout = []
            elif '__exit_code' not in line and \
                    not line.replace(' \r', '').strip().endswith(command):
                result.stdout.append(line.replace('\b', '')
                                     .replace('\r', '')
                                     .replace('\x9B', '')
                                     .replace('\x1B', '')
                                     .replace('\n', ''))

        if result.stdout:
            result.stdout = '\n'.join(result.stdout)
        else:
            result.stdout = ""
        if result.exit_code:
            result.stderr = result.stdout
            result.stdout = ""

        return result
