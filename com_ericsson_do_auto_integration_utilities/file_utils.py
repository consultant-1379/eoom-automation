from tempfile import mkstemp
from shutil import move
from os import fdopen, remove
import paramiko
import os
from com_ericsson_do_auto_integration_utilities.Error_handler import handle_stderr
from com_ericsson_do_auto_integration_utilities.Logger import Logger

log = Logger.get_logger('file_utils')

def replace(file_path, pattern, subst):
    #Create temp file
    fh, abs_path = mkstemp()
    with fdopen(fh,'w') as new_file:
        with open(file_path) as old_file:
            for line in old_file:
                new_file.write(line.replace(pattern, subst))
    #Remove original file
    remove(file_path)
    #Move new file
    move(abs_path, file_path)


def create_temp_dir(connection, command='mktemp -d'):
    """Creates temporary directory"""
    log.info('creating temp folder with command : %s', command)
    stdin, stdout, stderr = connection.exec_command(command)
    tmp_dir_path = stdout.read().decode('utf-8')
    log.info('created tmp directory path : %s ', tmp_dir_path)
    return tmp_dir_path


def del_dir(connection, dir_name):
    """Deletes directory"""
    stdin, stdout, stderr = connection.exec_command(f'/bin/rm -rf {dir_name}')
    return stderr


class MySFTPClient(paramiko.SFTPClient):
    def put_dir(self, source, target):
        ''' Uploads the contents of the source directory to the target path. The
            target directory needs to exists. All subdirectories in source are
            created under target.
        '''
        for item in os.listdir(source):
            if os.path.isfile(os.path.join(source, item)):
                self.put(os.path.join(source, item), '%s/%s' % (target, item))
            else:
                self.mkdir('%s/%s' % (target, item), ignore_existing=True)
                self.put_dir(os.path.join(source, item), '%s/%s' % (target, item))

    def mkdir(self, path, mode=511, ignore_existing=False):
        ''' Augments mkdir by adding an option to not fail if the folder exists  '''
        try:
            super(MySFTPClient, self).mkdir(path, mode)
        except IOError:
            if ignore_existing:
                pass
            else:
                raise