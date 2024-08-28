'''
Created on 7 Dec 2018

@author: emaidns
'''
from com_ericsson_do_auto_integration_utilities.Logger import Logger
from com_ericsson_do_auto_integration_utilities.Report_file import Report_file
import paramiko
import socket
import re

log = Logger.get_logger('ShellHandler.py')
class ShellHandler:

    def __init__(self, host, user, psw):

        try:
            log.info('Connecting with server :' + host)
            self.ssh = paramiko.SSHClient()
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh.connect(host, username=user, password=psw, port=22)

            channel = self.ssh.invoke_shell()
            self.stdin = channel.makefile('wb')
            self.stdout = channel.makefile('r')
            log.info('Connected with server :' + host)

        except paramiko.SSHException as e:
            log.debug(e)
            log.error("Login issue: Please check the password , "+host)
            Report_file.add_line('Script terminated due to error ')
            log.info('Script terminated due to error printed above.')
            exit(-1)
        except paramiko.AuthenticationException as e:
            log.debug(e)
            log.error ("Login issue: Please check the password, "  +host)
            Report_file.add_line('Script terminated due to error ')
            log.info('Script terminated due to error printed above.')
            exit(-1)
        except (socket.error, paramiko.AuthenticationException) as e:
            log.debug(e)
            log.error ("Connection refused with server :"+host)
            Report_file.add_line('Script terminated due to error ')
            log.info('Script terminated due to error printed above.')
            exit(-1)


    def shell_put_file_sftp(self, source, destination):
        log.info('Putting source :  ' + source + ' to destination : ' + destination)
        sftp = self.ssh.open_sftp()
        sftp.put(source, destination)
        sftp.close()

    def __del__(self):
        self.ssh.close()

    def execute(self, cmd):
        """

        :param cmd: the command to be executed on the remote computer
        :examples:  execute('ls')
                    execute('finger')
                    execute('cd folder_name')
        """
        log.info('Executing the command  :' + cmd)
        cmd = cmd.strip('\n')
        self.stdin.write(cmd + '\n')
        finish = 'end of stdOUT buffer. finished with exit status'
        echo_cmd = 'echo {} $?'.format(finish)
        self.stdin.write(echo_cmd + '\n')
        shin = self.stdin
        self.stdin.flush()

        shout = []
        sherr = []
        exit_status = 0
        for line in self.stdout:
            if str(line).startswith(cmd) or str(line).startswith(echo_cmd):
                # up for now filled with shell junk from stdin
                shout = []
            elif str(line).startswith(finish):
                # our finish command ends with the exit status
                exit_status = int(str(line).rsplit(maxsplit=1)[1])
                if exit_status:
                    # stderr is combined with stdout.
                    # thus, swap sherr with shout in a case of failure.
                    sherr = shout
                    shout = []
                break
            else:
                # get rid of 'coloring and formatting' special characters
                shout.append(re.compile(r'(\x9B|\x1B\[)[0-?]*[ -/]*[@-~]').sub('', line).
                             replace('\b', '').replace('\r', ''))

        # first and last lines of shout/sherr contain a prompt
        if shout and echo_cmd in shout[-1]:
            shout.pop()
        if shout and cmd in shout[0]:
            shout.pop(0)
        if sherr and echo_cmd in sherr[-1]:
            sherr.pop()
        if sherr and cmd in sherr[0]:
            sherr.pop(0)

        return shin, shout, sherr