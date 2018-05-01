#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
__version__ = '1.0.0'
__date__ = '2018-04-22'
__author__ = 'Ding Yi, <dingyi@dingyix.com>'
"""

import os
import sys
import shutil
import paramiko

server_ip = 'xxx.xxx.xxx.xxx'
server_port = xx
server_username = 'xxx'
server_private = '/xxx/yyy'
archive_folder_local = '/zzz'
archive_folder_remote = '/zzz'
inflate_folder = '/xxxxx'

if len(sys.argv) != 2:
    print('Need one argument! ')
    sys.exit()

package_folder = sys.argv[1]

folder_name = os.path.basename(package_folder)
archive = os.path.join(archive_folder_local, folder_name)
archive_local = archive + '.tar.gz'
archive_remote = archive_folder_remote + '/' + folder_name + '.tar.gz'
report_folder = inflate_folder + '/' + folder_name


class ConnectByKey(object):

    def __init__(self, ip, port, username, private_key):
        self.ip = ip
        self.port = port
        self.username = username
        self.private_key = private_key

    def command(self, instruction):
        result = ''
        key = paramiko.RSAKey.from_private_key_file(self.private_key)
        server = paramiko.SSHClient()
        server.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        server.connect(self.ip, self.port, self.username, pkey=key)
        (stdin, stdout, stderr) = server.exec_command(instruction)
        if len(stderr.readlines()) == 0:
            for line in stdout.readlines():
                result += line
            return result
        else:
            print('failed to execute remote command! ')
        server.close()

    def sftp_put(self, localfile, remotefile):
        key = paramiko.RSAKey.from_private_key_file(self.private_key)
        tran = paramiko.Transport(self.ip, self.port)
        tran.connect(username=self.username, pkey=key)
        sftp = paramiko.SFTPClient.from_transport(tran)
        try:
            sftp.put(localfile, remotefile)
        except OSError:
            print('upload file failure! ')
        finally:
            tran.close()


def file_transfer():
    try:
        shutil.make_archive(archive, 'gztar', r'%s' % package_folder)
        server = ConnectByKey(server_ip, server_port, server_username, server_private)
        server.sftp_put(archive_local, archive_remote)
        server.command('mkdir -p %s' % report_folder)
        server.command('tar -zxf %s -C %s' % (archive_remote, report_folder))
    except Exception:
        print('file transfer failure! ')
        sys.exit()
    else:
        print('file transfer success! ')


file_transfer()
